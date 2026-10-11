"""Search and raw-data request windows at the IMS triads and IMOS loggers, from end-of-flight impacts.

PRE-REGISTERED (overnight 10 Oct 2026, ~05:30 UTC). Committed before any run on the large-run impacts. The rules
below are fixed; changes after a run are amendments, committed and disclosed.

WHY: architecture ~03:20 UTC 10 Oct asked hydroacoustics to re-derive its windows from the large-run impacts once end
of flight ruled on impacts before 00:19:37 and after the unanswered 01:15:56 handshake. End of flight answered 04:05
UTC (coordination/HYDROACOUSTICS.md): reference variant `+alive` provisionally, `+silent` as a labelled sensitivity,
plain arms unchanged.

WEIGHTS: end of flight's own `option_posteriors(run, seed_dir, constraints)` from
engine/hypotheses/end-of-flight/smoke/displacement_hist.py, loaded READ-ONLY by path (--eof-module); its sha256 is
recorded. Nothing in it is copied or edited here. Seeds are pooled with equal weight, as end of flight pools them.

RECEIVERS: IMS triads H01W, H08S, H08N at the mean of their element positions (data/stations.csv); IMOS loggers 3315,
3376, 3250, 3274, 3275 at the path endpoints in data/ocean_paths/request.json.

ARRIVAL MODEL:
  SOFAR: t_arr = t_impact + d / c, d the WGS84 geodesic from impact to receiver, c ~ N(1.482, 0.006) km/s drawn per
         row (the group speed used throughout the module). Path lengthening by refraction or blockage is ignored.
  AGW:   same d, c_agw ~ U(1.40, 1.50) km/s per row. ASSUMPTION, not modelled: acoustic-gravity modes travel at or below
         the water sound speed and slow towards their cut-off; the lower bound 1.40 km/s is a stated allowance until a
         mode group-speed computation replaces it.
QUANTILES: weighted, 0.5 2.5 5 25 50 75 95 97.5 99.5 %, of the seed-pooled distribution; per-seed values kept.
POOLED quantiles come from the equal-weight mixture of per-seed weighted CDFs on a 2 s grid,
  23:00 7 Mar to 06:00 8 Mar UTC; mass beyond the grid is reported.
WINDOW RULE, per receiver x option x cause x variant:
  [q0.5 - 10 min, q99.5 + 20 min], start floored and end ceiled to 5 min.
  CONVERGENCE: if the per-seed q0.5 or q99.5 spread (max - min) exceeds 5 min, the row is flagged UNCONVERGED and the
  window is widened to the per-seed envelope of those quantiles before padding.
  RECOMMENDED request per receiver: the union over every option x cause with pooled ESS >= 1000, under `+alive`;
  the same union under `+silent` is reported beside it. Plain arms are reported, not recommended.
VALIDATION GATE (must pass, else the outputs are written as FAILED-VALIDATION and not posted): on the run given by
  --validate-against (end of flight's impact-time-shares JSON for the same impacts), for every row it lists, the plain
  share before 00:19:37.443 must match to |d| <= 1e-6, the share after 01:15:56 to <= 1e-6, and the seed-mean impact
  q05/q50/q95 to <= 5 s (the quantile definition may differ by one sample).
AMENDMENT (11 Oct 2026, FORMAT ONLY, before its first run C use): --compact-reader <compact_impacts.py> lets seed
  directories hold end of flight's compact run C file (impacts32.npy, read with EoF's own reader) instead of
  impacts.npy. Impact time, latitude and longitude are read through the reader; nothing else changes. The full-
  format path is untouched (regression: next-run outputs must reproduce byte for byte).
LABELS: PROVISIONAL-OVERNIGHT; uncorrected fuel; provisional sampler; run, prior track and configs from run.json.

Usage (from prepare/, PYTHONPATH=.):
  python search_windows.py --runs <run_dir> [...] --eof-module <displacement_hist.py> --out <dir>
                           [--validate-against <impact-time-shares.json>] [--tag name]
  <run_dir> holds seed-*/impacts.npy and seed-*/run.json (the end-of-flight exchange layout).
"""
import argparse, csv, hashlib, importlib.util, json, pathlib, sys, time
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
MODULE = HERE.parent
T_ALIVE = 1394237977.443      # 00:19:37.443 (end of flight's T_M0019B)
T_0115 = 1394241356.0         # 01:15:56 (end of flight's T_LOI_0115)
C_SOFAR, C_SOFAR_SD = 1.482, 0.006
C_AGW = (1.40, 1.50)
QS = [0.005, 0.025, 0.05, 0.25, 0.5, 0.75, 0.95, 0.975, 0.995]
PAD_PRE_S, PAD_POST_S, ROUND_S, CONV_S, ESS_MIN = 600.0, 1200.0, 300.0, 300.0, 1000.0
VARIANTS = ("alive", "silent")
SEED = 20261010


def receivers():
    rx = {}
    rows = [r for r in csv.reader(open(MODULE / "data" / "stations.csv")) if r and not r[0].startswith("#")]
    hdr, rows = rows[0], rows[1:]
    for triad in ("H01W", "H08S", "H08N"):
        el = [dict(zip(hdr, r)) for r in rows if dict(zip(hdr, r))["triad"] == triad]
        rx[triad] = (float(np.mean([float(e["latitude_deg"]) for e in el])), float(np.mean([float(e["longitude_deg"]) for e in el])))
    req = json.loads((MODULE / "data" / "ocean_paths" / "request.json").read_text())
    for p in req["paths"]:
        lg = p["name"].split("-")[-1]
        if lg in ("3315", "3376", "3250", "3274", "3275") and lg not in rx:
            rx[lg] = (p["b"][1], p["b"][0])
    return rx


def wq(sorted_x, sorted_p, qs):
    cp = np.cumsum(sorted_p); cp /= cp[-1]
    return sorted_x[np.minimum(np.searchsorted(cp, qs, side="left"), len(sorted_x) - 1)]


def hms(t):
    return time.strftime("%H:%M:%S", time.gmtime(float(t))) if np.isfinite(t) else "nan"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", nargs="+", required=True); ap.add_argument("--eof-module", required=True)
    ap.add_argument("--out", required=True); ap.add_argument("--validate-against"); ap.add_argument("--tag", default="")
    ap.add_argument("--compact-reader")
    a = ap.parse_args()
    from pyproj import Geod
    geod = Geod(ellps="WGS84")
    spec = importlib.util.spec_from_file_location("eof_dh", a.eof_module); dh = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dh)
    sat = pathlib.Path(a.eof_module).resolve().parents[3] / "data" / "satcom-observations.csv"
    if not sat.exists():
        raise SystemExit(f"satcom-observations.csv not found at {sat}: the derived BTO options would be wrong")
    dh.SATCOM_CSV = sat
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    rx = receivers(); rng = np.random.default_rng(SEED)
    CR = None
    if a.compact_reader:
        sp2 = importlib.util.spec_from_file_location("compact_impacts", a.compact_reader); CR = importlib.util.module_from_spec(sp2)
        sp2.loader.exec_module(CR)
    seed_dirs = sorted(d for r in a.runs for d in pathlib.Path(r).glob("seed-*")
                       if d.is_dir() and ((d / "impacts.npy").exists() or (CR is not None and (d / "impacts32.npy").exists())))
    prov = dict(script="prepare/search_windows.py", eof_module=str(a.eof_module),
                eof_module_sha256=hashlib.sha256(open(a.eof_module, "rb").read()).hexdigest(),
                satcom_csv_sha256=hashlib.sha256(sat.read_bytes()).hexdigest(), seeds=[str(d) for d in seed_dirs],
                receivers=rx, labels=["PROVISIONAL-OVERNIGHT", "uncorrected fuel", "provisional sampler"], run_json={})
    GRID = np.arange(1394236800.0 - 3600.0, 1394236800.0 + 6 * 3600.0, 2.0)   # 2014-03-07 23:00 to 03-08 06:00, 2 s
    per, cdf = {}, {}   # key -> per-seed stats; key -> {series: summed per-seed CDF on GRID / n_seeds}
    for sd in seed_dirs:
        t0 = time.time(); meta = json.loads((sd / "run.json").read_text())
        prov["run_json"][sd.name] = {k: meta.get(k) for k in ("code_revision", "config_paths", "source_run", "replicates")}
        if (sd / "impacts.npy").exists():
            cols = {c: i for i, c in enumerate(meta["impact_columns"])}
            X = np.load(sd / "impacts.npy", mmap_mode="r")
            t = np.asarray(X[:, cols["unix_s"]], float); lat = np.asarray(X[:, cols["latitude_deg"]], float)
            lon = np.asarray(X[:, cols["longitude_deg"]], float)
        else:
            _m, g = CR.load(sd)
            t, lat, lon = (np.asarray(g(k), float) for k in ("unix_s", "latitude_deg", "longitude_deg"))
        ok = np.isfinite(t) & np.isfinite(lat) & np.isfinite(lon)
        n = len(t); cs = rng.normal(C_SOFAR, C_SOFAR_SD, n); ca = rng.uniform(*C_AGW, n)
        series = {"impact": np.where(ok, t, np.inf)}
        for name, (rl, ro) in rx.items():
            d = np.full(n, np.nan); _, _, d[ok] = geod.inv(lon[ok], lat[ok], np.full(ok.sum(), ro), np.full(ok.sum(), rl))
            for br, c in (("sofar", cs), ("agw", ca)):
                series[f"{name}|{br}"] = np.where(ok, t + d / 1000.0 / c, np.inf)
        srt = {k: (x[o], o, np.searchsorted(x[o], GRID, side="right")) for k, x in series.items() for o in [np.argsort(x)]}
        del series
        for key, p, _c in dh.option_posteriors(sd, sd, constraints=VARIANTS):
            p = np.where(ok, p, 0.0)
            if p.sum() <= 0:
                continue
            p = p / p.sum()
            r = dict(ess=float(1.0 / np.sum(p ** 2)), share_before=float(p[t < T_ALIVE].sum()),
                     share_after=float(p[t > T_0115].sum()), q={})
            acc = cdf.setdefault(key, {})
            for k, (xs, o, gi) in srt.items():
                cp = np.cumsum(p[o]); r["q"][k] = wq(xs, p[o], QS).tolist()
                g = np.concatenate([[0.0], cp])[gi] / len(seed_dirs)
                acc[k] = acc.get(k, 0.0) + g
            per.setdefault(key, []).append(r)
        del srt
        print(f"{sd.name}: {n} rows, {len(per)} arms, {time.time() - t0:.0f} s", flush=True)

    def gq(g):
        g = g / g[-1] if g[-1] > 0 else g
        return GRID[np.minimum(np.searchsorted(g, QS, side="left"), len(GRID) - 1)]
    rows, summary = [], {}
    for key, acc in cdf.items():
        seeds = per[key]
        ess = float(sum(s["ess"] for s in seeds))
        base, _, var = key.partition("+"); var = var or "plain"
        imp = gq(acc["impact"])
        summary[key] = dict(variant=var, ess_pooled=ess, n_seeds=len(seeds),
                            share_before_001937_seed_mean=float(np.mean([s["share_before"] for s in seeds])),
                            share_after_011556_seed_mean=float(np.mean([s["share_after"] for s in seeds])),
                            impact_q_pooled_utc=[hms(v) for v in imp],
                            impact_q05_q50_q95_seed_mean_unix=[float(np.mean([s["q"]["impact"][i] for s in seeds])) for i in (2, 4, 6)],
                            mass_beyond_grid=float(1.0 - acc["impact"][-1]))
        for nm in rx:
            for br in ("sofar", "agw"):
                q = gq(acc[f"{nm}|{br}"]); lo_s = [s["q"][f"{nm}|{br}"][0] for s in seeds]; hi_s = [s["q"][f"{nm}|{br}"][-1] for s in seeds]
                unconv = (max(lo_s) - min(lo_s) > CONV_S) or (max(hi_s) - min(hi_s) > CONV_S)
                lo, hi = (min(q[0], min(lo_s)), max(q[-1], max(hi_s))) if unconv else (q[0], q[-1])
                w0 = np.floor((lo - PAD_PRE_S) / ROUND_S) * ROUND_S; w1 = np.ceil((hi + PAD_POST_S) / ROUND_S) * ROUND_S
                rows.append(dict(arm=base, variant=var, receiver=nm, branch=br, ess_pooled=round(ess),
                                 **{f"q{100 * qq:g}": hms(v) for qq, v in zip(QS, q)},
                                 seed_spread_q0p5_s=round(max(lo_s) - min(lo_s), 1), seed_spread_q99p5_s=round(max(hi_s) - min(hi_s), 1),
                                 converged="no" if unconv else "yes", window_start=hms(w0), window_end=hms(w1),
                                 window_start_unix=w0, window_end_unix=w1))
    with open(out / "windows_by_arm.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rows[0])); wr.writeheader(); wr.writerows(rows)
    rec = []
    for var in VARIANTS:
        for nm in rx:
            for br in ("sofar", "agw"):
                sel = [r for r in rows if r["variant"] == var and r["receiver"] == nm and r["branch"] == br and r["ess_pooled"] >= ESS_MIN]
                if sel:
                    rec.append(dict(variant=var, receiver=nm, branch=br, n_arms=len(sel),
                                    window_start=hms(min(r["window_start_unix"] for r in sel)), window_end=hms(max(r["window_end_unix"] for r in sel)),
                                    any_unconverged=any(r["converged"] == "no" for r in sel), arms=";".join(sorted(r["arm"] for r in sel))))
    with open(out / "recommended_windows.csv", "w", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(rec[0])); wr.writeheader(); wr.writerows(rec)
    val = {"status": "not requested"}
    if a.validate_against:
        ref = json.loads(open(a.validate_against).read()); checks, fail = [], False
        for k, v in ref.items():
            if k not in summary:
                checks.append(dict(arm=k, ok=False, reason="arm missing here")); fail = True; continue
            s = summary[k]
            dq = [abs(s["impact_q05_q50_q95_seed_mean_unix"][i] % 86400 - sum(int(x) * m for x, m in zip(v["impact_q05_q50_q95_utc_seed_mean"][i].split(":"), (3600, 60, 1)))) for i in range(3)]
            d1 = abs(s["share_before_001937_seed_mean"] - v["share_before_001937"]); d2 = abs(s["share_after_011556_seed_mean"] - v["share_after_011556"])
            ok = d1 <= 1e-6 and d2 <= 1e-6 and max(dq) <= 5.0; fail |= not ok
            checks.append(dict(arm=k, ok=ok, d_share_before=d1, d_share_after=d2, d_quantiles_s=dq))
        val = {"status": "FAILED-VALIDATION" if fail else "passed", "against": a.validate_against, "checks": checks}
    prov["validation"] = val["status"]
    (out / "validation.json").write_text(json.dumps(val, indent=1))
    (out / "summary.json").write_text(json.dumps(dict(provenance=prov, arms=summary), indent=1, default=str))
    print(json.dumps(dict(validation=val["status"], arms=len(summary), rows=len(rows), recommended=len(rec))))


if __name__ == "__main__":
    main()
