"""Search and request windows over core strata (flight families), fixed and re-weighted P(family). DISCLOSED AMENDMENT.

PRE-REGISTERED (10 Oct 2026, evening), committed before its first run. It amends the module's window method
(`search_windows.py`, prereg 55eb191), which pools the seeds of one run and has no notion of strata. That script is
not edited; this file adds the stratum layer.

ORIGIN. The stratum mixture is the architecture stand-in's (`results/hydroacoustics-next-run-b-standin/
standin_mixture.py`, sha256 b04b54c6...), adopted by the module at 2152191. Its arithmetic is kept as it is:
  per stratum s, seed k:  the per-seed CDF F_{s,k} of every series on the 2 s grid, exactly as search_windows.py.
  replicate k:            R_k = sum_s w_s F_{s,k}  (seed k of every stratum), used in the 5-min convergence rule.
  mixture:                F_mix = mean_k R_k.
  Kish ESS:               1 / sum_{s,k} (w_s / n_k)^2 / ESS_{s,k}.
  window rule, receivers, speeds, quantiles, ESS gate: imported unchanged from search_windows.py.
ADDITIONS.
  1. Family weights per option (architecture ruling ~19:10 UTC 10 Oct, part C):
       fixed:       w_s = P(family) from core's mixture.json, the same for every option;
       re-weighted: w_{s,o} = P(family)_s * Zhat_{s,o} / sum_s' (...), with log Zhat from --family-evidence, a JSON
                    {arm_key: {stratum: log_Zhat}} (arm keys as option_posteriors yields them, e.g. "none__other+alive").
                    Arms not in that file are reported fixed-weight only. Under 00:19 Held Out the factor is 1.
     Both are written when --family-evidence is given (ruling: show both while core is unconverged).
  2. Core-set outputs under the plain names, via core_set_windows.py.
REGRESSION GATE (pre-registered): run with fixed weights on end-of-flight/next-run, the per-arm table must reproduce
  the stand-in's `mixture/windows_by_arm.csv` exactly, every column of every row as a string (--regress-against).
  A failure is reported as FAILED-REGRESSION, and nothing from that run is posted as a result.
AMENDMENT 1 (10 Oct, before its run on these inputs): end of flight exposed ruling B's variant (b) as `unpowered`
  (EoF 43262c3) and published Ẑ_00:19 per family (summary/family-evidence-next-run-b.json, keyed by plain names).
  --variants sets the constraint list (here alive, unpowered, silent). --family-evidence also accepts EoF's file: the
  core options 1-3 map to none__other, r600-bto__other, r600_no-offset__other; their "+alive" ln Ẑ is applied to the
  `+alive` arms AND to the `+unpowered` arms (declared approximation: the 01:15:56 factor keeps the same 0.90 as
  alive to within 0.003, EoF ~20:40); `+silent` and H1/H2 are reported fixed-weight only.
AMENDMENT 2 (11 Oct 2026, FORMAT ONLY, before its first run C use): --compact-reader as in search_windows.py
  (impacts32.npy through end of flight's reader; time, latitude, longitude only); the full-format path is untouched.
  --mixture-json may be core's early-families-mixture.json ({"P_family": {plain family: p}}); the plain family names
  map to the run's stratum directories by --strata-map (e.g. free=next-c-free).
AMENDMENT 3 (11 Oct 2026, before its first run C use; ruling 1(C) of 20:35 -0600 and EoF's run C evidence file):
  (a) --mixture-json may hold {"p_core": {stratum: p}} (EoF's family-evidence-run-c.json).
  (b) When the evidence file has "+unpowered" entries, they are used for the +unpowered arms (amendment 1's
      "+alive for +unpowered" approximation is then retired).
  (c) --speed-max V adds the "~v212" version: rows with impact speed |v| = sqrt(ve^2 + vn^2 + vu^2) > V are given zero
      weight, each seed's weights are renormalised, and strata are mixed by P(family) * Zhat(option ~v212), whose
      Zhat already carries each stratum's kept share. This version is RE-WEIGHTED ONLY (no fixed-weight ~v212).
      CHECK (pre-registered): per stratum, |ln(kept share, 00:19 Held Out) - ln Zhat(00:19 Held Out ~v212)| <= 0.01;
      otherwise the definition of "contact speed" differs from EoF's and the ~v212 output is labelled CHECK-FAILED.
      Label: "impacts faster than 212 m/s removed (no structural limit in the model)".
LABELS: carried from the inputs: core split-half state, two-tank bookkeeping, uncorrected fuel, provisional sampler,
  PROVISIONAL-OVERNIGHT where they apply; "P(family) held fixed" or "P(family) re-weighted by 00:19 evidence".

Usage (from prepare/, PYTHONPATH=.):
  python search_windows_mixture.py --exchange <end-of-flight/next-run> --mixture-json <summary/mixture.json>
         --eof-module <displacement_hist.py> --out <dir> [--family-evidence <json>] [--regress-against <csv>]
AMENDMENT 4 (11 Oct 2026, before any run-D-he window is computed; architecture 20:55Z ruling). SURVIVAL FACTOR:
  "no in-flight breakup before 00:19:37" is part of the 00:19 data model. When the impact columns carry
  latent:inflight_p_breakup_to_m0019b, each option posterior is multiplied by (1 - P) and renormalised (primary);
  --no-survival gives the labelled sensitivity without it. Runs without the column (run C) are unchanged. Every output
  carries the label "survival factor applied" or "survival factor NOT applied (sensitivity)".
"""
import argparse, csv, hashlib, json, pathlib, sys, time
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import search_windows as sw          # noqa: E402  constants, receivers(), wq(), hms(), window rule
import core_set_windows as cs        # noqa: E402  plain names

GRID = np.arange(1394236800.0 - 3600.0, 1394236800.0 + 6 * 3600.0, 2.0)   # as search_windows.py


def gq(g):
    g = g / g[-1] if g[-1] > 0 else g
    return GRID[np.minimum(np.searchsorted(g, sw.QS, side="left"), len(GRID) - 1)]


def windows(mix_rep, mix_stats, weights, rx, n_strata):
    rows, summary = [], {}
    for key, reps in mix_rep.items():
        st = mix_stats[key]
        if len(set(x[5] for x in st)) < n_strata:
            continue
        ks = sorted(reps); w = weights(key)
        ess = float(1.0 / sum((w[s] / nk) ** 2 / e for nk, e, sb, sa, _k, s in st))
        pooled = {s_: sum(reps[k][s_] for k in ks) / len(ks) for s_ in reps[ks[0]]}
        base, _, var = key.partition("+"); var = var or "plain"
        imp = gq(pooled["impact"])
        summary[key] = dict(variant=var, ess_mixture_kish=ess, n_replicates=len(ks), weights=w,
                            share_before_001937=float(sum(w[s] * sb / nk for nk, e, sb, sa, _k, s in st)),
                            share_after_011556=float(sum(w[s] * sa / nk for nk, e, sb, sa, _k, s in st)),
                            impact_q_pooled_utc=[sw.hms(v) for v in imp], mass_beyond_grid=float(1.0 - pooled["impact"][-1]))
        for nm in rx:
            for br in ("sofar", "agw"):
                sk = f"{nm}|{br}"; q = gq(pooled[sk])
                rq = [gq(reps[k][sk]) for k in ks]; lo_s = [r_[0] for r_ in rq]; hi_s = [r_[-1] for r_ in rq]
                unconv = (max(lo_s) - min(lo_s) > sw.CONV_S) or (max(hi_s) - min(hi_s) > sw.CONV_S)
                lo, hi = (min(q[0], min(lo_s)), max(q[-1], max(hi_s))) if unconv else (q[0], q[-1])
                w0 = np.floor((lo - sw.PAD_PRE_S) / sw.ROUND_S) * sw.ROUND_S; w1 = np.ceil((hi + sw.PAD_POST_S) / sw.ROUND_S) * sw.ROUND_S
                rows.append(dict(arm=base, variant=var, receiver=nm, branch=br, ess_pooled=round(ess),
                                 **{f"q{100 * qq:g}": sw.hms(v) for qq, v in zip(sw.QS, q)},
                                 seed_spread_q0p5_s=round(max(lo_s) - min(lo_s), 1), seed_spread_q99p5_s=round(max(hi_s) - min(hi_s), 1),
                                 converged="no" if unconv else "yes", window_start=sw.hms(w0), window_end=sw.hms(w1),
                                 window_start_unix=w0, window_end_unix=w1))
    return rows, summary


def write(out, rows, summary, prov):
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "windows_by_arm.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    (out / "summary.json").write_text(json.dumps(dict(provenance=prov, arms=summary), indent=1, default=str))
    cs.main(str(out / "windows_by_arm.csv"), str(out / "core_set"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exchange", required=True); ap.add_argument("--mixture-json", required=True)
    ap.add_argument("--eof-module", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--family-evidence"); ap.add_argument("--regress-against")
    ap.add_argument("--variants", nargs="+", default=list(sw.VARIANTS))
    ap.add_argument("--compact-reader"); ap.add_argument("--strata-map", nargs="+")
    ap.add_argument("--speed-max", type=float)
    ap.add_argument("--no-survival", action="store_true")   # amendment 4
    a = ap.parse_args()
    import importlib.util
    from pyproj import Geod
    spec = importlib.util.spec_from_file_location("eof_dh", a.eof_module); dh = importlib.util.module_from_spec(spec); spec.loader.exec_module(dh)
    dh.SATCOM_CSV = pathlib.Path(a.eof_module).resolve().parents[3] / "data" / "satcom-observations.csv"
    geod = Geod(ellps="WGS84"); rx = sw.receivers(); out = pathlib.Path(a.out)
    _mj = json.load(open(a.mixture_json))
    if "p_family" in _mj:
        PF = _mj["p_family"]
    elif "p_core" in _mj:
        PF = dict(_mj["p_core"])
    else:
        smap = dict(x.split("=", 1) for x in a.strata_map)
        PF = {smap[k]: v for k, v in _mj["P_family"].items()}
    CR = None
    if a.compact_reader:
        sp2 = importlib.util.spec_from_file_location("compact_impacts", a.compact_reader); CR = importlib.util.module_from_spec(sp2)
        sp2.loader.exec_module(CR)
    LZ = json.load(open(a.family_evidence)) if a.family_evidence else {}
    HELD_V = {}; KEPT = {}
    if "strata" in LZ:                       # end of flight's published format (amendment 1)
        MAP = {"00:19 Held Out +alive": "none__other", "00:19 R600 BTO Only +alive": "r600-bto__other",
               "00:19 R600 BTO + Raw BFO +alive": "r600_no-offset__other"}
        lz2 = {}
        ST = LZ["strata"]; s0 = next(iter(ST))
        for plain, arm in MAP.items():
            base = plain.replace(" +alive", "")
            for var in ("alive", "unpowered", "silent"):
                for suf in ("", " ~v212"):
                    pk = f"{base} +{var}{suf}"
                    if var == "unpowered" and pk not in ST[s0]:
                        pk = f"{base} +alive{suf}"          # amendment 1 approximation, only when EoF lacks +unpowered
                    if pk in ST[s0]:
                        lz2[f"{arm}+{var}" + ("~v212" if suf else "")] = {s_: ST[s_][pk]["ln_Zhat"] for s_ in ST}
            if f"{base} ~v212" in ST[s0]:
                lz2[f"{arm}~v212"] = {s_: ST[s_][f"{base} ~v212"]["ln_Zhat"] for s_ in ST}
        HELD_V = {s_: ST[s_]["00:19 Held Out ~v212"]["ln_Zhat"] for s_ in ST} if "00:19 Held Out ~v212" in ST[s0] else {}
        LZ = lz2
    VARIANTS = tuple(a.variants)

    def w_fixed(key):
        return dict(PF)

    def w_rew(key):
        lz = LZ.get(key)
        if lz is None:
            return None
        m = max(lz[s] for s in PF); u = {s: PF[s] * np.exp(lz[s] - m) for s in PF}; t = sum(u.values())
        return {s: float(v / t) for s, v in u.items()}

    rep_f, rep_r, stats = {}, {}, {}
    for stratum in PF:
        seed_dirs = sorted(d for d in (pathlib.Path(a.exchange) / stratum).glob("seed-*")
                           if d.is_dir() and ((d / "impacts.npy").exists() or (CR is not None and (d / "impacts32.npy").exists())))
        nk = len(seed_dirs); rng = np.random.default_rng(sw.SEED)
        for kidx, sd in enumerate(seed_dirs):
            t0 = time.time(); meta = json.loads((sd / "run.json").read_text())
            if (sd / "impacts.npy").exists():
                cols = {c: i for i, c in enumerate(meta["impact_columns"])}
                X = np.load(sd / "impacts.npy", mmap_mode="r")
                t = np.asarray(X[:, cols["unix_s"]], float); lat = np.asarray(X[:, cols["latitude_deg"]], float)
                lon = np.asarray(X[:, cols["longitude_deg"]], float)
            else:
                _m, g = CR.load(sd)
                t, lat, lon = (np.asarray(g(k), float) for k in ("unix_s", "latitude_deg", "longitude_deg"))
            ok = np.isfinite(t) & np.isfinite(lat) & np.isfinite(lon)
            keep = None
            if a.speed_max:
                if (sd / "impacts.npy").exists():
                    vv = [np.asarray(X[:, cols[k]], float) for k in ("velocity_east_mps", "velocity_north_mps", "velocity_up_mps")]
                else:
                    vv = [np.asarray(g(k), float) for k in ("velocity_east_mps", "velocity_north_mps", "velocity_up_mps")]
                keep = np.sqrt(vv[0] ** 2 + vv[1] ** 2 + vv[2] ** 2) <= a.speed_max
            n = len(t); c_s = rng.normal(sw.C_SOFAR, sw.C_SOFAR_SD, n); c_a = rng.uniform(*sw.C_AGW, n)
            series = {"impact": np.where(ok, t, np.inf)}
            for name, (rl, ro) in rx.items():
                d = np.full(n, np.nan); _, _, d[ok] = geod.inv(lon[ok], lat[ok], np.full(ok.sum(), ro), np.full(ok.sum(), rl))
                for br, c in (("sofar", c_s), ("agw", c_a)):
                    series[f"{name}|{br}"] = np.where(ok, t + d / 1000.0 / c, np.inf)
            srt = {k: (x[o], o, np.searchsorted(x[o], GRID, side="right")) for k, x in series.items() for o in [np.argsort(x)]}
            del series
            surv = None   # amendment 4: survival factor (1 - P(in-flight breakup before 00:19:37))
            if not a.no_survival:
                try:
                    pb = np.asarray(g("latent:inflight_p_breakup_to_m0019b"), float) if not (sd / "impacts.npy").exists() else \
                        np.asarray(X[:, cols["latent:inflight_p_breakup_to_m0019b"]], float)
                    surv = np.clip(1.0 - np.nan_to_num(pb, nan=0.0), 0.0, 1.0)
                except (KeyError, ValueError):
                    surv = None
            for key, p, _c in dh.option_posteriors(sd, sd, constraints=VARIANTS):
                p = np.where(ok, p, 0.0)
                if surv is not None:
                    p = p * surv
                if p.sum() <= 0:
                    continue
                p = p / p.sum()
                stats.setdefault(key, []).append((nk, float(1.0 / np.sum(p ** 2)), float(p[t < sw.T_ALIVE].sum()),
                                                  float(p[t > sw.T_0115].sum()), kidx, stratum))
                wr_ = w_rew(key)
                rf = rep_f.setdefault(key, {}).setdefault(kidx, {})
                rr = rep_r.setdefault(key, {}).setdefault(kidx, {}) if wr_ else None
                for k, (xs, o, gi) in srt.items():
                    g_ = np.concatenate([[0.0], np.cumsum(p[o])])[gi]
                    rf[k] = rf.get(k, 0.0) + PF[stratum] * g_
                    if rr is not None:
                        rr[k] = rr.get(k, 0.0) + wr_[stratum] * g_
                if keep is not None:
                    kept = float(p[keep].sum())
                    if key == "none__other":
                        KEPT.setdefault(stratum, []).append(kept)
                    kv = key + "~v212"
                    wv = w_rew(kv)
                    if wv is not None and kept > 0:
                        pv = np.where(keep, p, 0.0) / kept
                        stats.setdefault(kv, []).append((nk, float(1.0 / np.sum(pv ** 2)), float(pv[t < sw.T_ALIVE].sum()),
                                                         float(pv[t > sw.T_0115].sum()), kidx, stratum))
                        rv = rep_r.setdefault(kv, {}).setdefault(kidx, {})
                        for k, (xs, o, gi) in srt.items():
                            g_ = np.concatenate([[0.0], np.cumsum(pv[o])])[gi]
                            rv[k] = rv.get(k, 0.0) + wv[stratum] * g_
            del srt
            print(f"{stratum}/{sd.name}: {n} rows, {time.time() - t0:.0f} s", flush=True)
    prov = dict(script="prepare/search_windows_mixture.py", search_windows_sha256=hashlib.sha256(open(sw.__file__, "rb").read()).hexdigest(),
                eof_module=a.eof_module, eof_module_sha256=hashlib.sha256(open(a.eof_module, "rb").read()).hexdigest(),
                exchange=a.exchange, p_family=PF, family_evidence=a.family_evidence, receivers=rx)
    if a.speed_max and HELD_V:
        chk = {s_: dict(ln_kept=float(np.log(np.mean(v))), ln_Zhat_v212=HELD_V[s_], ok=bool(abs(np.log(np.mean(v)) - HELD_V[s_]) <= 0.01))
               for s_, v in KEPT.items()}
        (out / "v212_check.json").parent.mkdir(parents=True, exist_ok=True)
        (out / "v212_check.json").write_text(json.dumps(chk, indent=1)); print("v212 check", chk, flush=True)
    rows, summ = windows({k: v for k, v in rep_f.items()}, {k: v for k, v in stats.items() if not k.endswith("~v212")}, w_fixed, rx, len(PF))
    write(out / "mixture_fixed", rows, summ, dict(prov, weighting="P(family) held fixed"))
    if LZ:
        r2, s2 = windows(rep_r, stats, lambda k: w_rew(k), rx, len(PF))
        write(out / "mixture_reweighted", r2, s2, dict(prov, weighting="P(family) re-weighted by 00:19 evidence"))
    reg = {"status": "not requested"}
    if a.regress_against:
        ref = list(csv.DictReader(open(a.regress_against))); mine = list(csv.DictReader(open(out / "mixture_fixed" / "windows_by_arm.csv")))
        kf = lambda r: (r["arm"], r["variant"], r["receiver"], r["branch"])
        R_ = {kf(r): r for r in ref}; M_ = {kf(r): r for r in mine}
        diffs = [dict(row=list(k), col=c, ref=R_[k][c], mine=M_[k][c]) for k in R_ if k in M_ for c in R_[k] if R_[k][c] != M_[k].get(c)]
        missing = [list(k) for k in R_ if k not in M_] + [list(k) for k in M_ if k not in R_]
        reg = {"status": "passed" if not diffs and not missing else "FAILED-REGRESSION", "against": a.regress_against,
               "rows_ref": len(ref), "rows_mine": len(mine), "n_diffs": len(diffs), "diffs_first": diffs[:20], "missing": missing[:20]}
    (out / "regression.json").write_text(json.dumps(reg, indent=1))
    print(json.dumps(dict(regression=reg["status"], arms=len(summ), rows=len(rows), reweighted=bool(LZ))))


if __name__ == "__main__":
    main()
