"""Stand-in post-processing (NOT module code): P(family) mixture of hydroacoustics' search windows over core (b) strata.

Written by an architecture stand-in, 11 Oct 2026, PROVISIONAL-OVERNIGHT. The module's pre-registered script
(prepare/search_windows.py @ 438c9e9, sha256 1b05492b...) pools the seeds of ONE run with equal weight and has no
notion of strata. Core (b) has four strata combined by core's P(family). This wrapper imports the module's script
UNCHANGED for its constants, receivers(), wq(), hms(), and end of flight's option_posteriors (15ba915, read-only),
and repeats the script's per-seed arithmetic (lines 274-301) with one addition: each seed's CDF is also accumulated
into a mixture with weight P(family)/n_seeds.

  per-stratum:  identical to the script (fresh rng(SEED) per stratum, seeds sorted). Its pooled quantiles are
                compared with the unchanged script's summary.json as a self-check.
  mixture:      F_mix = sum_s P_s * mean_k F_{s,k}.  Replicate k = sum_s P_s F_{s,k} (seed k of every stratum);
                the 4 replicates play the role of the script's per-seed values in its convergence rule.
  ESS:          Kish ESS of the combined weights, 1 / sum_{s,k} (P_s/n_k)^2 / ESS_{s,k}, as in EoF's mixture.json.
  window rule:  the script's, unchanged (pad -10/+20 min, 5-min rounding, 5-min spread -> envelope, ESS >= 1000).
P(family) is held fixed (core's, unconverged); it is not updated by terminal-stage evidence per option.
"""
import argparse, csv, importlib.util, json, pathlib, sys, time
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--script", required=True); ap.add_argument("--eof-module", required=True)
ap.add_argument("--exchange", required=True); ap.add_argument("--mixture-json", required=True); ap.add_argument("--out", required=True)
a = ap.parse_args()

sys.path.insert(0, str(pathlib.Path(a.script).parent))
spec = importlib.util.spec_from_file_location("search_windows", a.script); sw = importlib.util.module_from_spec(spec); spec.loader.exec_module(sw)
spec = importlib.util.spec_from_file_location("eof_dh", a.eof_module); dh = importlib.util.module_from_spec(spec); spec.loader.exec_module(dh)
dh.SATCOM_CSV = pathlib.Path(a.eof_module).resolve().parents[3] / "data" / "satcom-observations.csv"
from pyproj import Geod
geod = Geod(ellps="WGS84")
PF = json.load(open(a.mixture_json))["p_family"]
rx = sw.receivers(); QS = sw.QS
GRID = np.arange(1394236800.0 - 3600.0, 1394236800.0 + 6 * 3600.0, 2.0)   # as the script
out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)


def gq(g):
    g = g / g[-1] if g[-1] > 0 else g
    return GRID[np.minimum(np.searchsorted(g, QS, side="left"), len(GRID) - 1)]


mix_rep = {}          # key -> k -> series -> sum_s P_s F_{s,k}
mix_stats = {}        # key -> list of (P_s, n_k, ess, share_before, share_after)
strat_q = {}          # stratum -> key -> series -> pooled quantiles (self-check)
for stratum in PF:
    seed_dirs = sorted(d for d in (pathlib.Path(a.exchange) / stratum).glob("seed-*") if (d / "impacts.npy").exists())
    nk = len(seed_dirs); rng = np.random.default_rng(sw.SEED); acc_s = {}
    for kidx, sd in enumerate(seed_dirs):
        t0 = time.time(); meta = json.loads((sd / "run.json").read_text())
        cols = {c: i for i, c in enumerate(meta["impact_columns"])}
        X = np.load(sd / "impacts.npy", mmap_mode="r")
        t = np.asarray(X[:, cols["unix_s"]], float); lat = np.asarray(X[:, cols["latitude_deg"]], float)
        lon = np.asarray(X[:, cols["longitude_deg"]], float); ok = np.isfinite(t) & np.isfinite(lat) & np.isfinite(lon)
        n = len(t); cs = rng.normal(sw.C_SOFAR, sw.C_SOFAR_SD, n); ca = rng.uniform(*sw.C_AGW, n)
        series = {"impact": np.where(ok, t, np.inf)}
        for name, (rl, ro) in rx.items():
            d = np.full(n, np.nan); _, _, d[ok] = geod.inv(lon[ok], lat[ok], np.full(ok.sum(), ro), np.full(ok.sum(), rl))
            for br, c in (("sofar", cs), ("agw", ca)):
                series[f"{name}|{br}"] = np.where(ok, t + d / 1000.0 / c, np.inf)
        srt = {k: (x[o], o, np.searchsorted(x[o], GRID, side="right")) for k, x in series.items() for o in [np.argsort(x)]}
        del series
        for key, p, _c in dh.option_posteriors(sd, sd, constraints=sw.VARIANTS):
            p = np.where(ok, p, 0.0)
            if p.sum() <= 0:
                continue
            p = p / p.sum()
            mix_stats.setdefault(key, []).append((PF[stratum], nk, float(1.0 / np.sum(p ** 2)),
                                                  float(p[t < sw.T_ALIVE].sum()), float(p[t > sw.T_0115].sum()), stratum))
            rep = mix_rep.setdefault(key, {}).setdefault(kidx, {}); a_s = acc_s.setdefault(key, {})
            for k, (xs, o, gi) in srt.items():
                g = np.concatenate([[0.0], np.cumsum(p[o])])[gi]
                a_s[k] = a_s.get(k, 0.0) + g / nk
                rep[k] = rep.get(k, 0.0) + PF[stratum] * g
        del srt
        print(f"{stratum}/{sd.name}: {n} rows, {time.time() - t0:.0f} s", flush=True)
    strat_q[stratum] = {key: {k: [sw.hms(v) for v in gq(g)] for k, g in d.items()} for key, d in acc_s.items()}
    del acc_s

rows, summary = [], {}
for key, reps in mix_rep.items():
    st = mix_stats[key]
    strata_present = sorted(set(x[5] for x in st))
    if len(strata_present) < len(PF):
        print(f"skip {key}: strata {strata_present}"); continue
    ks = sorted(reps)
    ess = float(1.0 / sum((P / nk) ** 2 / e for P, nk, e, *_ in st))
    pooled = {s_: sum(reps[k][s_] for k in ks) / len(ks) for s_ in reps[ks[0]]}
    base, _, var = key.partition("+"); var = var or "plain"
    imp = gq(pooled["impact"])
    summary[key] = dict(variant=var, ess_mixture_kish=ess, n_replicates=len(ks),
                        share_before_001937=float(sum(P * sb / nk for P, nk, e, sb, sa, _ in st)),
                        share_after_011556=float(sum(P * sa / nk for P, nk, e, sb, sa, _ in st)),
                        impact_q_pooled_utc=[sw.hms(v) for v in imp],
                        mass_beyond_grid=float(1.0 - pooled["impact"][-1]))
    for nm in rx:
        for br in ("sofar", "agw"):
            sk = f"{nm}|{br}"; q = gq(pooled[sk])
            rq = [gq(reps[k][sk]) for k in ks]; lo_s = [r_[0] for r_ in rq]; hi_s = [r_[-1] for r_ in rq]
            unconv = (max(lo_s) - min(lo_s) > sw.CONV_S) or (max(hi_s) - min(hi_s) > sw.CONV_S)
            lo, hi = (min(q[0], min(lo_s)), max(q[-1], max(hi_s))) if unconv else (q[0], q[-1])
            w0 = np.floor((lo - sw.PAD_PRE_S) / sw.ROUND_S) * sw.ROUND_S; w1 = np.ceil((hi + sw.PAD_POST_S) / sw.ROUND_S) * sw.ROUND_S
            rows.append(dict(arm=base, variant=var, receiver=nm, branch=br, ess_pooled=round(ess),
                             **{f"q{100 * qq:g}": sw.hms(v) for qq, v in zip(QS, q)},
                             seed_spread_q0p5_s=round(max(lo_s) - min(lo_s), 1), seed_spread_q99p5_s=round(max(hi_s) - min(hi_s), 1),
                             converged="no" if unconv else "yes", window_start=sw.hms(w0), window_end=sw.hms(w1),
                             window_start_unix=w0, window_end_unix=w1))
with open(out / "windows_by_arm.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
rec = []
for var in sw.VARIANTS:
    for nm in rx:
        for br in ("sofar", "agw"):
            sel = [r for r in rows if r["variant"] == var and r["receiver"] == nm and r["branch"] == br and r["ess_pooled"] >= sw.ESS_MIN]
            if sel:
                rec.append(dict(variant=var, receiver=nm, branch=br, n_arms=len(sel),
                                window_start=sw.hms(min(r["window_start_unix"] for r in sel)), window_end=sw.hms(max(r["window_end_unix"] for r in sel)),
                                any_unconverged=any(r["converged"] == "no" for r in sel), arms=";".join(sorted(r["arm"] for r in sel))))
with open(out / "recommended_windows.csv", "w", newline="") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(rec[0])); wr.writeheader(); wr.writerows(rec)
(out / "summary.json").write_text(json.dumps(dict(provenance=dict(wrapper="standin_mixture.py", p_family=PF, receivers=rx,
    labels=["core (b): split-half NOT converged", "two-tank bookkeeping only", "PROVISIONAL-OVERNIGHT",
            "EoF sweep run by a stand-in", "hydroacoustics run by an architecture stand-in; module to review"]),
    arms=summary), indent=1, default=str))
(out / "per_stratum_quantiles_selfcheck.json").write_text(json.dumps(strat_q))
print(json.dumps(dict(arms=len(summary), rows=len(rows), recommended=len(rec))))
