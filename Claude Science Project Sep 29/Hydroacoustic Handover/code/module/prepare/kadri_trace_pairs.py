"""PRE-REGISTRATION and implementation: first two-site pair count on data in hand. Pete, 9 Oct: "how many
pairs we are actually seeing with the data we have, compared to expected by chance". Committed before any
H08S panel was scanned by any detector in this module. (The H01W panels a-c were scanned by the 2a detector
at the strict threshold in kadri_table1_test.py.)

DATA, AND WHAT THEY ARE NOT:
  - Kadri (2024) Figure 9 plotted polylines, recovered from the PDF vectors (kadri-figure-extraction,
    metadata.json; sha256 of the source PDF recorded there).
  - H01W panels a-c cover 00:27-00:57 UTC; H08S panels d-e cover 01:00-01:20 UTC.
  - Each is one channel, already filtered by Kadri (5 Hz high-pass, 2-40 Hz band-pass) and decimated for
    plotting (about 14.5 vertices per second).
  - NOT raw IMS data: no triad bearings at H08S, and no element choice or amplitude processing is known.
DETECTOR: the 2a detector exactly (kadri_table1_test.py: STA 1 s, LTA 20 s trailing, 20 Hz linear
  resample, triggers merged within 3 s) at two operating points fixed now:
  - STRICT, ratio >= 3.0 (2a's);
  - LOOSE, ratio >= 2.0.
  A panel's usable span is [panel start + 20 s, panel end - 1 s].
PAIR: an H01W trigger t1 and an H08S trigger t2 with t2 - t1 inside the stand-in prior's predicted span
  - Prediction: (d_H08S - d_H01W)/c, c = 1.482 km/s, 200,000 samples from synthetic_composer_test's
    stand-in (run no-exhaustion-prior, track 295.66 deg, sigma_x 20 NM).
  - Span: the 2.5-97.5 % quantiles widened by 30 s (2 sqrt 2 x the 10 s pick sd).
  - STATISTIC: N = number of pairs.
NULL (burst-preserving time slides): the H08S trigger list is shifted circularly over the union of the H08S
  usable spans by every integer second 1 .. L-1, and N is recounted.
  - Mean of the null = the 'expected by chance' count.
  - p = (1 + #{N_null >= N}) / (1 + number of shifts).
VARIANTS (fixed now): strict x strict, loose x loose, and BEARING-GATED. The gated variant pairs H01W
  Table 1 events (Kadri's times and bearings, 00:38-00:55) whose bearing lies in the prior's 95 %
  back-azimuth span at H01W, widened by 2 x 3.3 deg, with H08S triggers (strict and loose).
REPORTED PER PAIR: times, dt, and the implied impact latitude and H01W back-azimuth (medians of the prior
  samples with predicted dt within +-15 s).
READING (fixed now): p < 0.05 means "more pairs than chance". It is NOT a detection claim. These data
  cannot support one: they are filtered publication polylines, with no H08S bearing and no injection P_D.
  Otherwise the reading is "pair count consistent with chance". No likelihood is returned either way
  (gate).
AGW: sub-cutoff acoustic-gravity waves (f < f_c, about 0.1 Hz here) are absent from these traces by
  construction (5 Hz high-pass). A predicted-AGW association is NOT ASSESSABLE on these data and is not
  attempted.
Usage: python kadri_trace_pairs.py <kadri data dir> <stand-in summary json> <out dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import kadri_table1_test as KT  # noqa: E402
import synthetic_composer_test as S  # noqa: E402

PANELS = {"a": "H01W", "b": "H01W", "c": "H01W", "d": "H08S", "e": "H08S"}
RATIOS = {"strict": 3.0, "loose": 2.0}
WIDEN_S = 30.0
BEAR_SD = 3.3


def triggers(kd, panel, ratio):
    tr = pd.read_csv(kd / "kadri-figure-extraction" / "figure9-vector-traces" / f"kadri-2024-figure9-panel-{panel}-{PANELS[panel]}.csv")
    t = (pd.to_datetime(tr.utc) - KT.DAY0).dt.total_seconds().values
    o = np.argsort(t)
    t, p = t[o], tr.pressure_pa.values[o]
    FS = KT.FS
    tg = np.arange(t[0], t[-1], 1 / FS)
    e = np.interp(tg, t, p) ** 2
    cs = np.concatenate([[0.0], np.cumsum(e)])
    ns, nl = int(KT.STA * FS), int(KT.LTA * FS)
    idx = np.arange(nl, len(e) - ns)
    r = ((cs[idx + ns] - cs[idx]) / ns) / np.maximum((cs[idx] - cs[idx - nl]) / nl, 1e-30)
    trig = []
    for i in idx[r >= ratio]:
        if not trig or tg[i] - trig[-1] > KT.MERGE:
            trig.append(float(tg[i]))
    return np.array(trig), (float(tg[nl]), float(tg[-ns]))


def count(t1, t2, lo, hi):
    d = t2[None, :] - t1[:, None]
    return int(((d >= lo) & (d <= hi)).sum())


def slide_null(t1, t2, spans, lo, hi):
    """Circular shift of t2 over the concatenated usable spans (gaps removed, then restored)."""
    spans = sorted(spans)
    L = sum(b - a for a, b in spans)

    def to_u(t):
        u, off = [], 0.0
        for a, b in spans:
            m = (t >= a) & (t <= b)
            u.append(t[m] - a + off)
            off += b - a
        return np.concatenate(u) if u else np.array([])

    def from_u(u):
        out, off = [], 0.0
        for a, b in spans:
            m = (u >= off) & (u < off + (b - a))
            out.append(u[m] - off + a)
            off += b - a
        return np.concatenate(out)
    u2 = to_u(t2)
    return np.array([count(t1, from_u(np.mod(u2 + s, L)), lo, hi) for s in range(1, int(L))])


def main(kd, summary, out_dir):
    kd, out = Path(kd), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(S.SEED)
    ridge, grid, dens, _ = S.ridge_and_marginal(summary)
    q, _ = S.fit_small_circle(ridge)
    pr = S.draw_prior(rng, q, grid, dens, S.N_PRIOR, S.BASE["sigma_x_nm"])
    g = S.station_geometry(pr)
    dt = g["H08S"][0] / S.C_KM_S - g["H01W"][0] / S.C_KM_S
    lo, hi = float(np.quantile(dt, 0.025)) - WIDEN_S, float(np.quantile(dt, 0.975)) + WIDEN_S
    b1 = g["H01W"][1]
    blo, bhi = float(np.quantile(b1, 0.025)) - 2 * BEAR_SD, float(np.quantile(b1, 0.975)) + 2 * BEAR_SD
    trig, spans = {}, {}
    for op, ratio in RATIOS.items():
        for st in ["H01W", "H08S"]:
            ts, sp = [], []
            for pnl in [k for k, v in PANELS.items() if v == st]:
                t, s = triggers(kd, pnl, ratio)
                ts.append(t[(t >= s[0]) & (t <= s[1])])
                sp.append(s)
            trig[(op, st)], spans[st] = np.concatenate(ts), sp
    table = pd.read_csv(kd / "kadri-table1-transients.csv")
    table["t_s"] = [KT.secs(x) for x in table.time_utc]
    gated = table[(table.bearing_deg >= blo) & (table.bearing_deg <= bhi)]
    variants = {
        "strict_x_strict": (trig[("strict", "H01W")], trig[("strict", "H08S")]),
        "loose_x_loose": (trig[("loose", "H01W")], trig[("loose", "H08S")]),
        "table1_gated_x_strict": (gated.t_s.values.astype(float), trig[("strict", "H08S")]),
        "table1_gated_x_loose": (gated.t_s.values.astype(float), trig[("loose", "H08S")]),
    }
    res, pairs = {}, []
    for name, (t1, t2) in variants.items():
        n = count(t1, t2, lo, hi)
        nl = slide_null(t1, t2, spans["H08S"], lo, hi)
        res[name] = dict(n_h01w=int(len(t1)), n_h08s=int(len(t2)), n_pairs=n, null_mean=float(nl.mean()),
                         null_q95=float(np.quantile(nl, 0.95)), p=float((1 + (nl >= n).sum()) / (1 + len(nl))),
                         reading="more pairs than chance" if (1 + (nl >= n).sum()) / (1 + len(nl)) < 0.05 else "consistent with chance")
        for a in t1:
            for b in t2:
                d = b - a
                if lo <= d <= hi:
                    m = np.abs(dt - d) <= 15.0
                    pairs.append(dict(variant=name, t_h01w=str(KT.DAY0 + pd.Timedelta(seconds=float(a)))[11:19],
                                      t_h08s=str(KT.DAY0 + pd.Timedelta(seconds=float(b)))[11:19], dt_s=float(d),
                                      implied_lat=float(np.median(pr[m, 0])) if m.sum() > 50 else np.nan,
                                      implied_h01w_baz=float(np.median(b1[m])) if m.sum() > 50 else np.nan, n_prior=int(m.sum())))
    meta = dict(dt_span_s=[lo, hi], dt_prior_q=[float(np.quantile(dt, x)) for x in (0.025, 0.5, 0.975)],
                h01w_bearing_gate_deg=[blo, bhi], n_table1_gated=int(len(gated)),
                h08s_usable_s=float(sum(b - a for a, b in spans["H08S"])), prior="no-exhaustion-prior stand-in (synthetic_composer_test)",
                agw="NOT ASSESSABLE: traces high-passed at 5 Hz by Kadri")
    (out / "kadri_trace_pairs.json").write_text(json.dumps(dict(meta=meta, results=res), indent=1))
    pd.DataFrame(pairs).to_csv(out / "kadri_trace_pairs.csv", index=False)
    print(json.dumps(dict(meta=meta, results=res), indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:4])
