"""PRE-REGISTRATION and implementation: loose-threshold two-site coincidence search on the IMOS data in
hand, Perth Canyon (3376) x Portland (3274). This is the protocol rehearsal proposed in
results/hydroacoustics-near-limits-planning.md. Committed before any coincidence count was computed.

WHY THIS PAIR: these are the only loggers with a 14-day background (stage A), so the null is like for
  like. 3315 and 3275 have no background; they are reported descriptively only (MH370 day, borrowed
  thresholds 3315 <- 3376, 3275 <- 3274) and are not tested.
EVENTS: the stage A 'or' detector at false alarm alpha per 50 s window.
  - Trigger rule: D1 >= its alpha/2 threshold OR D2 >= its alpha/2 threshold. Thresholds are taken from
    stage A (results-data/stageA/summary_union.json), computed on the 14-day background.
  - Scoring: the statistic r(t) = max(D1/thr_D1, D2/thr_D2) is formed on a 1 s grid (the D1 maximum within
    each second).
  - Events: exceedances (r >= 1) closer than 50 s are merged into one event, timed at its maximum r.
  - Operating points, fixed now: LOOSE alpha = 0.05 (primary) and STRICT alpha = 0.005.
WINDOWS: 2b's pre-registered MH370 windows for each logger (results-data/imos2b/mh370_windows.csv,
  win_a-win_b). Time base convention A (true = logger - e(t), sub-second footer field).
PAIR: a 3376 event t1 and a 3274 event t2 with t2 - t1 inside the stand-in prior's predicted span.
  - Prediction: (d_3274 - d_3376)/c, c = 1.482 km/s, 200,000 samples (synthetic_composer_test stand-in,
    run no-exhaustion-prior).
  - Span: the 2.5-97.5 % quantiles widened by 30 s.
  - STATISTIC: N = number of pairs.
NULL: the identical procedure on each of the 14 background days (1-7 and 9-15 March 2014), with the two
  windows moved to the same clock time and also offset by -3, -2, -1, +1, +2, +3 h together: 98 null
  realisations.
  - p = (1 + #{N_null >= N}) / (1 + 98).
  - Expected by chance = the null mean.
  - Time of day is held approximately fixed; tidal and diurnal noise differences across days are a
    declared limitation.
READING (fixed now): p < 0.05 means "more pairs than chance" (candidates listed, with implied latitude).
  Otherwise "consistent with chance". Neither returns a likelihood (gate). The expected value of this
  test is small: each logger records 307 s of every 15 min, so joint coverage of a real pair is about
  0.1; the planning note puts it at <= 0.1 bit. It is a rehearsal of the protocol on real data.
AGW: not assessable on IMOS (8 Hz analogue high-pass).
Usage: python imos_coincidence.py <out dir> <background root> <stand-in summary json>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import imos_detectors as D  # noqa: E402
import imos_injection as I  # noqa: E402
import imos_noise as N  # noqa: E402
import imos_preregistration as P  # noqa: E402
import synthetic_composer_test as S  # noqa: E402

HERE = Path(__file__).parent.parent
PAIR = ("3376", "3274")
ALPHAS = {"loose": 0.05, "strict": 0.005}
OFFSETS_H = [-3, -2, -1, 0, 1, 2, 3]
MERGE_S = 50.0
WIDEN_S = 30.0


def cal_for(meta):
    nb = pd.read_csv(HERE / "results-data/imos1d/noise_bands.csv")
    cal = {}
    for cid in [3376, 3274, 3315, 3275]:
        m = meta[str(cid)]
        fg, G = N.gain_db(next(P.IMOS.glob(f"*/*alibration/{m['cal_file']}")))
        d = nb[nb.logger == cid].set_index("band").p50_1s
        cal[cid] = dict(gain=(fg, G), sens=m["sens_db"], m5_20=D.pw(d["5-10"], d["10-20"]), m10_40=D.pw(d["10-20"], d["20-40"]))
    return cal


def rec_events(path, cid, meta, cal, thr):
    """Events (true UTC seconds since DAY0 and r-max) in one recording, for each operating point."""
    fs, first, n, _ = P.header(path)
    if fs != 6000:
        return None
    t0 = first + pd.Timedelta(seconds=D.subsec(path))
    t0 = t0 - pd.Timedelta(seconds=P.clock_err(meta[str(cid)], t0))
    base = (t0 - D.DAY0).total_seconds()
    s = I.Series(N.decimate(N.read_volts(path)), cal[cid])
    sec = np.floor(s.d1_t).astype(int)
    nsec = int(np.ceil(s.d2_t[-1])) + 1
    d1s = np.full(nsec, -np.inf)
    np.maximum.at(d1s, np.clip(sec, 0, nsec - 1), s.d1)
    d2s = np.full(nsec, -np.inf)
    d2s[np.floor(s.d2_t).astype(int)] = s.d2
    out = {}
    for op, a in ALPHAS.items():
        r = np.maximum(d1s / thr[f"d1@{a / 2}"], d2s / thr[f"d2@{a / 2}"])
        r[:32] = -np.inf                       # D1 unscorable in the first 32 s (2b)
        ev, cur = [], None
        for k in np.flatnonzero(r >= 1.0):
            if cur and k - cur[-1][0] <= MERGE_S:
                cur.append((k, r[k]))
            else:
                if cur:
                    ev.append(max(cur, key=lambda z: z[1]))
                cur = [(k, r[k])]
        if cur:
            ev.append(max(cur, key=lambda z: z[1]))
        out[op] = [(base + k + 0.5, float(v)) for k, v in ev]
    return base, base + n / 6000.0, out


def count(t1, t2, lo, hi):
    if len(t1) == 0 or len(t2) == 0:
        return 0
    d = np.asarray(t2)[None, :] - np.asarray(t1)[:, None]
    return int(((d >= lo) & (d <= hi)).sum())


def main(out_dir, bg_root, summary):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta = P.parse_meta()
    cal = cal_for(meta)
    thr_all = json.loads((HERE / "results-data/stageA/summary_union.json").read_text())["thresholds"]
    thr = {3376: thr_all["3376"], 3274: thr_all["3274"], 3315: thr_all["3376"], 3275: thr_all["3274"]}
    mh = pd.read_csv(HERE / "results-data/imos2b/mh370_windows.csv", parse_dates=["win_a", "win_b"])
    win = {int(c): ((g.win_a.iloc[0] - D.DAY0).total_seconds(), (g.win_b.iloc[0] - D.DAY0).total_seconds()) for c, g in mh.groupby("logger")}
    rng = np.random.default_rng(S.SEED)
    ridge, grid, dens, _ = S.ridge_and_marginal(summary)
    q, _ = S.fit_small_circle(ridge)
    pr = S.draw_prior(rng, q, grid, dens, S.N_PRIOR, S.BASE["sigma_x_nm"])
    pos = {c: (meta[c]["lat"], meta[c]["lon"]) for c in PAIR}
    _, _, dA = P.GEOD.inv(np.full(len(pr), pos["3376"][1]), np.full(len(pr), pos["3376"][0]), pr[:, 1], pr[:, 0])
    _, _, dB = P.GEOD.inv(np.full(len(pr), pos["3274"][1]), np.full(len(pr), pos["3274"][0]), pr[:, 1], pr[:, 0])
    dt = (dB - dA) / 1000.0 / S.C_KM_S
    lo, hi = float(np.quantile(dt, 0.025)) - WIDEN_S, float(np.quantile(dt, 0.975)) + WIDEN_S
    # MH370 day
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    mh_ev, mh_cov = {}, {}
    for cid in [3376, 3274, 3315, 3275]:
        a, b = win[cid]
        evs = {op: [] for op in ALPHAS}
        cov = 0.0
        for _, r in recs[recs.logger == cid].iterrows():
            res = rec_events(P.IMOS / r.file, cid, meta, cal, thr[cid])
            if res is None:
                continue
            s0, s1, ev = res
            if s1 < a or s0 > b:
                continue
            cov += max(0.0, min(s1, b) - max(s0 + 32, a))
            for op in ALPHAS:
                evs[op] += [e for e in ev[op] if a <= e[0] <= b]
        mh_ev[cid], mh_cov[cid] = evs, cov
    obs = {op: count([e[0] for e in mh_ev[3376][op]], [e[0] for e in mh_ev[3274][op]], lo, hi) for op in ALPHAS}
    # null: background days x offsets
    null = {op: [] for op in ALPHAS}
    null_rows = []
    days = I.DAYS
    cache = {}
    for cid in [3376, 3274]:
        for f in sorted((Path(bg_root) / str(cid)).glob("2014*/*.DAT")):
            try:
                res = rec_events(f, cid, meta, cal, thr[cid])
            except Exception:
                continue
            if res is not None:
                cache.setdefault(cid, []).append(res)
        print(cid, "background recordings scored:", len(cache[cid]), flush=True)
    for dstr in days:
        dd = (pd.Timestamp(dstr, tz="UTC") - D.DAY0).total_seconds()
        for oh in OFFSETS_H:
            sh = dd + 3600.0 * oh
            ev = {}
            for cid in [3376, 3274]:
                a, b = win[cid][0] + sh, win[cid][1] + sh
                ev[cid] = {op: [e[0] for (s0, s1, E) in cache[cid] if not (s1 < a or s0 > b) for e in E[op] if a <= e[0] <= b] for op in ALPHAS}
            row = dict(day=dstr, offset_h=oh)
            for op in ALPHAS:
                c = count(ev[3376][op], ev[3274][op], lo, hi)
                null[op].append(c)
                row[f"n_pairs_{op}"] = c
                row[f"n3376_{op}"], row[f"n3274_{op}"] = len(ev[3376][op]), len(ev[3274][op])
            null_rows.append(row)
    res = {}
    for op in ALPHAS:
        nl = np.array(null[op])
        p = float((1 + (nl >= obs[op]).sum()) / (1 + len(nl)))
        res[op] = dict(alpha=ALPHAS[op], n_pairs=obs[op], n_events_3376=len(mh_ev[3376][op]), n_events_3274=len(mh_ev[3274][op]),
                       null_mean=float(nl.mean()), null_q95=float(np.quantile(nl, 0.95)), null_max=int(nl.max()), p=p,
                       reading="more pairs than chance" if p < 0.05 else "consistent with chance")
    cand = []
    for op in ALPHAS:
        for a, ra in mh_ev[3376][op]:
            for b, rb in mh_ev[3274][op]:
                if lo <= b - a <= hi:
                    m = np.abs(dt - (b - a)) <= 15.0
                    cand.append(dict(op=op, t3376=str(D.DAY0 + pd.Timedelta(seconds=a))[11:19], t3274=str(D.DAY0 + pd.Timedelta(seconds=b))[11:19],
                                     dt_s=b - a, r3376=ra, r3274=rb, implied_lat=float(np.median(pr[m, 0])) if m.sum() > 50 else np.nan))
    desc = {str(c): {op: len(mh_ev[c][op]) for op in ALPHAS} | {"covered_s": mh_cov[c]} for c in mh_ev}
    meta_out = dict(dt_span_s=[lo, hi], dt_prior_q=[float(np.quantile(dt, x)) for x in (0.025, 0.5, 0.975)], windows_s=win,
                    n_null=len(null["loose"]), descriptive_mh370_events=desc,
                    prior="no-exhaustion-prior stand-in (synthetic_composer_test)", agw="NOT ASSESSABLE on IMOS (8 Hz high-pass)")
    (out / "imos_coincidence.json").write_text(json.dumps(dict(meta=meta_out, results=res), indent=1, default=str))
    pd.DataFrame(null_rows).to_csv(out / "imos_coincidence_null.csv", index=False)
    pd.DataFrame(cand).to_csv(out / "imos_coincidence_candidates.csv", index=False)
    print(json.dumps(dict(meta=meta_out, results=res), indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:4])
