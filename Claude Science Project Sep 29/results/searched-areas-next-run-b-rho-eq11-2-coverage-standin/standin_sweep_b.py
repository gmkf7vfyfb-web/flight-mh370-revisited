#!/usr/bin/env python3
"""Architecture stand-in driver (10 Oct 2026) for searched areas' next items on core (b).

    cd engine && python ../results/searched-areas-next-run-b-rho-eq11-2-coverage-standin/standin_sweep_b.py \
        <out-dir> runs/b-free runs/b-repro-radar runs/b-descent-climb runs/b-routes

NO METHOD OF ITS OWN. Every scenario, likelihood, density, statistic and Davey eq. (11.2) block comes from
the module's own `hypotheses/seabed-search/report.py` (imported, not copied: scenarios, evaluate,
candidate_areas, smooth, stats, overlap, GRID, PLANNING_PD), and the per-option weights come from end of
flight's `option_posteriors` (imported read-only, exactly as `impact_map_options.py` does), so the derived
"R600 BTO Only" arm (`r600-bto`, not a loglik column) is available. report.py's own accumulation loop is
replicated line for line in `accumulate` below.

Two things differ from running report.py once per (stratum, option), both declared:
  1. `mh370 evaluate` runs ONCE per seed per scenario and its columns are reused for every 00:19 option
     (the module's evaluate output does not depend on the option; report.py would recompute it each time).
  2. The four strata are mixed by the module's own P(family) convention for core (b): 0.69/0.15/0.14/0.01
     renormalised (results/seabed-search-b/README.md), held fixed. Z, mass on Phase 2 etc. mix linearly;
     histograms/maps mix as sum_f P_f * hist_f / n_seeds (so after-search mass sums to Z_f); ESS is Kish over
     the mixed weights; split-half uses seeds 1-2 vs 3-4 of every stratum, mixed.
Only the two module columns report.py uses (loglik and Phase 2 covered fraction) are retained per scenario,
to keep peak RAM low.
"""
import importlib.util, json, sys, time
from pathlib import Path
import numpy as np

ENGINE = Path.cwd()
HERE = ENGINE / "hypotheses" / "seabed-search"
spec = importlib.util.spec_from_file_location("sa_report", HERE / "report.py")
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
sys.path.insert(0, str(ENGINE / "hypotheses" / "end-of-flight" / "smoke"))
from displacement_hist import option_posteriors  # noqa: E402  end of flight's, read-only
import tomllib  # noqa: E402

OPTIONS = {  # ruled core set (architecture ~16:30 UTC 10 Oct); H1/H2 carried for ESS only
    "none__other+alive": "00:19 Held Out",
    "r600-bto__other+alive": "00:19 R600 BTO Only",
    "r600_no-offset__other+alive": "00:19 R600 BTO + Raw BFO",
    "none__other+unpowered": "00:19 Held Out",
    "r600-bto__other+unpowered": "00:19 R600 BTO Only",
    "r600_no-offset__other+unpowered": "00:19 R600 BTO + Raw BFO",
    "both_startup-offset__fuel-exhaustion+alive": "00:19 Holland H1",
    "both_no-offset__other+alive": "00:19 Holland H2",
}
# Re-weighted P(family | 00:19 data, option): end of flight's family-evidence-next-run-b.json (ruling C, ~19:10 UTC),
# `p_family_reweighted` of the +alive keys, used for the +unpowered keys as well (as settling did, 21:50 UTC).
# H1/H2 are not re-weighted (end of flight). The FIXED mixture keeps the module's 0.69/0.15/0.14/0.01 convention.
FAMILY_EVIDENCE = Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/summary/family-evidence-next-run-b.json")
REWEIGHT_KEY = {"none": "00:19 Held Out +alive", "r600-bto": "00:19 R600 BTO Only +alive",
                "r600_no-offset": "00:19 R600 BTO + Raw BFO +alive"}
PFAM = {"b-free": 0.69, "b-repro-radar": 0.15, "b-descent-climb": 0.14, "b-routes": 0.01}
REGIONS = {"north of 33 S": lambda lat, c: lat > -33.0,
           "33 S to 39.5 S": lambda lat, c: (lat <= -33.0) & (lat >= -39.5),
           "south of 39.5 S": lambda lat, c: lat < -39.5,
           "Phase 2 coverage > 0.5": lambda lat, c: c > 0.5,
           "Phase 2 coverage <= 0.5": lambda lat, c: c <= 0.5}
MAP_BINS = [np.arange(82, 106.01, 0.1), np.arange(-44, -12.99, 0.1)]


def new_acc(names):
    return {n: {"z": 0.0, "w2": 0.0, "hist": np.zeros((2, len(R.GRID))), "north_33": 0.0, "south_39_5": 0.0,
                "on_p2": 0.0, "off_south": 0.0} for n in names}


def accumulate(acc, maps, w, lat, lon, runs, cover, i, half, nrep):
    """report.py main(), lines 144-159, verbatim in effect."""
    south, bins = lat < -39.5, np.floor((lat + 50.025) / 0.05).astype(np.int64)
    for name, like in [("before", np.ones_like(w))] + [(n, np.exp(r)) for n, r in runs.items()]:
        if np.isnan(like).any():
            raise SystemExit(f"{name}: {np.isnan(like).sum()} samples not computed")
        wl = w * like
        a = acc[name]
        a["z"] += wl.sum() / nrep
        a["w2"] += np.sum(wl ** 2)
        a["hist"][int(i >= half)] += np.bincount(bins, weights=wl, minlength=len(R.GRID))[:len(R.GRID)]
        a["north_33"] += wl[lat > -33.0].sum()
        a["south_39_5"] += wl[south].sum()
        a["on_p2"] += np.sum(wl * cover)
        a["off_south"] += np.sum((wl * (1 - cover))[south])
        if name in maps:
            maps[name] = maps[name] + np.histogram2d(lon, lat, bins=MAP_BINS, weights=wl)[0]
            # stand-in addition (coverage rule, Pete 10 Oct): Kish ESS per region, sums only, no method change
            reg = a.setdefault("regions", {k: [0.0, 0.0] for k in REGIONS})
            for k, f in REGIONS.items():
                m = f(lat, cover)
                reg[k][0] += wl[m].sum(); reg[k][1] += np.sum(wl[m] ** 2)


def result(a, half=True):
    """report.py result()."""
    total = a["hist"].sum()
    d = R.smooth(a["hist"].sum(axis=0))
    halves = R.overlap(R.smooth(a["hist"][0]), R.smooth(a["hist"][1])) if half else float("nan")
    regions = {k: {"share": v[0] / total, "ess": (v[0] ** 2 / v[1]) if v[1] > 0 else 0.0} for k, v in a.get("regions", {}).items()}
    return {"z": a["z"], "density": d, "stats": R.stats(d), "split_half": halves, "ess": total ** 2 / a["w2"], "regions": regions,
            **{k: a[k] / total for k in ("north_33", "south_39_5", "on_p2", "off_south")}}


def planning(maps):
    areas = {"disabled": R.candidate_areas(maps["before"], MAP_BINS),
             "residual": R.candidate_areas(maps["run.toml"], MAP_BINS)}
    out = {"top": areas["residual"][:8], "curve": {}, "thresholds": {}}
    disabled = {(a["west"], a["south"]): a["mass"] for a in areas["disabled"]}
    for a in out["top"]:
        a["mass_search_disabled"] = disabled.get((a["west"], a["south"]), 0.0)
    for key, ar in areas.items():
        cum = np.cumsum([a["p_find"] for a in ar]); km2 = np.cumsum([a["km2"] for a in ar])
        out["curve"][key] = {"km2": km2.tolist(), "p_find": cum.tolist()}
        out["thresholds"][key] = {}
        for t in (0.25, 0.5, 0.75):
            j = int(np.searchsorted(cum, t))
            out["thresholds"][key][f"{t:g}"] = {"blocks": j + 1, "km2": float(km2[j])} if j < len(cum) else None
    return out


def main():
    out = Path(sys.argv[1])
    if out.name == "sa-work":  # stale lock-queued launch from this stand-in's session: superseded, refuse
        raise SystemExit("superseded output dir sa-work; refusing")
    out.mkdir(parents=True, exist_ok=True)
    runs_dirs = [Path(p) for p in sys.argv[2:]]
    params = tomllib.loads((HERE / "run.toml").read_text())["hypotheses"][R.MODULE]
    oi = tomllib.loads(R.OI_OVERRIDE.read_text())["hypotheses"][R.MODULE]["campaigns"] if R.OI_LAYER.is_file() else None
    cases = R.scenarios(params, oi, R.OI25_LAYER.is_file())
    names = ["before"] + [c[0] for c in cases]
    scratch = out / "scratch"; scratch.mkdir(exist_ok=True)
    raw = {}
    for run in runs_dirs:
        reps = sorted((run / "bto-bfo").glob("seed-*/impacts.npy"), key=lambda p: int(p.parent.name[5:]))
        meta = json.loads((run / "run.json").read_text()); columns = meta["impact_columns"]
        assert not [c for c in columns if c.startswith(R.MODULE + ":")], "double-application guard"
        half, nrep = len(reps) // 2, len(reps)
        acc = {k: new_acc(names) for k in OPTIONS}
        maps = {k: {"before": 0.0, "run.toml": 0.0} for k in OPTIONS}
        n_imp = 0
        for i, path in enumerate(reps):
            t0 = time.time()
            ev = {}
            for name, extra, _ in cases:
                r = R.evaluate(path, extra, scratch)
                ev[name] = (r["loglik"].copy(), r["covered_fraction_phase2-2014-2017"].copy() if name == "run.toml" else None)
                del r
            cover = ev["run.toml"][1]
            runs = {n: v[0] for n, v in ev.items()}
            got, lat_n = set(), 0
            for key, w, c in option_posteriors(run, path.parent, constraints=("alive", "unpowered")):
                if key not in OPTIONS:
                    continue
                got.add(key)
                accumulate(acc[key], maps[key], w, c["lat"], c["lon"], runs, cover, i, half, nrep)
                lat_n = len(w)
            missing = set(OPTIONS) - got
            if missing:
                raise SystemExit(f"{path}: option_posteriors did not produce {missing}")
            n_imp += lat_n
            print(f"  {run.name}/{path.parent.name}: {lat_n:,} impacts, {len(cases)} evaluations, {time.time() - t0:.0f} s", flush=True)
            del ev, runs, cover
        raw[run.name] = {"acc": acc, "maps": maps, "nrep": nrep, "impacts": n_imp}
    ptot = sum(PFAM.get(r.name, 1.0) for r in runs_dirs)
    report = {"cases": [[n, kind] for n, _, kind in cases], "pfamily": {r.name: PFAM.get(r.name, 1.0) / ptot for r in runs_dirs},
              "planning_p_d": R.PLANNING_PD, "rho_reference": params["undetectable_probability"], "strata": {}, "mixture": {}, "mixture_reweighted": {}}
    npz = {}
    for opt in OPTIONS:
        for sname, d in raw.items():
            res = {n: result(d["acc"][opt][n]) for n in names}
            report["strata"].setdefault(sname, {"impacts": d["impacts"], "seeds": d["nrep"]})[opt] = {
                "scenarios": {n: {k: v for k, v in r.items() if k != "density"} for n, r in res.items()},
                "planning": planning(d["maps"][opt])}
            for n, r in res.items():
                npz[f"{sname}|{opt}|{n}"] = r["density"]
        fe = json.loads(FAMILY_EVIDENCE.read_text())["mixtures"]
        rk = REWEIGHT_KEY.get(opt.split("__")[0])
        weightings = {"fixed": {s: PFAM.get(s, 1.0) / ptot for s in raw}}
        if rk:
            pr = fe[rk]["p_family_reweighted"]
            weightings["reweighted"] = {s: pr["next-" + s[2:]] for s in raw}
            report.setdefault("reweighted_p", {})[opt] = weightings["reweighted"]
        for wname, P in weightings.items():
            macc = new_acc(names); mmaps = {"before": 0.0, "run.toml": 0.0}
            ptw = sum(P.values())
            for sname, d in raw.items():
                pf = P[sname] / ptw
                f = pf / d["nrep"]
                for n in names:
                    a, m = d["acc"][opt][n], macc[n]
                    for k in ("north_33", "south_39_5", "on_p2", "off_south"):
                        m[k] += f * a[k]
                    m["z"] += pf * a["z"]
                    m["w2"] += f ** 2 * a["w2"]
                    m["hist"] += f * a["hist"]
                    if "regions" in a:
                        mr = m.setdefault("regions", {k: [0.0, 0.0] for k in REGIONS})
                        for k in REGIONS:
                            mr[k][0] += f * a["regions"][k][0]; mr[k][1] += f ** 2 * a["regions"][k][1]
                for k in mmaps:
                    mmaps[k] = mmaps[k] + f * d["maps"][opt][k]
            res = {n: result(macc[n]) for n in names}
            report["mixture" if wname == "fixed" else "mixture_reweighted"][opt] = {
                "scenarios": {n: {k: v for k, v in r.items() if k != "density"} for n, r in res.items()},
                "planning": planning(mmaps)}
            for n, r in res.items():
                npz[f"mixture-{wname}|{opt}|{n}"] = r["density"]
    (out / "standin-sweep-b.json").write_text(json.dumps(report, indent=1) + "\n")
    np.savez_compressed(out / "standin-sweep-b-densities.npz", grid=R.GRID, **npz)
    import shutil; shutil.rmtree(scratch)
    print("wrote", out)


if __name__ == "__main__":
    main()
