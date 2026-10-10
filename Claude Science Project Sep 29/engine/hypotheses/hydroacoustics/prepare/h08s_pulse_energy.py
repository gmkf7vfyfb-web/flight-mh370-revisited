"""PRE-REGISTRATION and implementation (Pete, 10 Oct): ENERGY-ONLY outlier test on the H08S airgun-like
pulses, with no use of shot timing or cadence. Pete's point: received shot timing varies with the source
vessel's range and speed. Supersedes, as the energy test, the cycle-based statistic of
h08s_shot_outliers.py (whose 9-11 s cycle rule used timing and discarded loud arrivals). Committed before
it was run.

DATA: Kadri (2024) Figure 9 H08S polylines, panels d (01:00-01:10) and e (01:10-01:20), resampled at 40 Hz
  (as h08s_shot_outliers.load). Approximate in absolute energy.
PULSES: every maximum of the envelope (p^2, 0.5 s boxcar) with prominence >= 2 x the panel's median
  envelope and at least 3 s from a higher neighbour (scipy find_peaks, distance 3 s). No cadence, interval
  or grid rule.
ENERGY MEASURES per pulse, all referenced to the pulse peak tp (integrals of p^2, Pa^2 s):
  - E_peak over [tp - 1, tp + 1] s: constructive or destructive interference on the peak;
  - E_pre over [tp - 3, tp - 1] s: the leading shoulder;
  - E_post over [tp + 1, tp + 4] s: the trailing shoulder or coda.
OUTLIERS:
  - Residual r = log10(E) minus its running median over 13 pulses (centred, in pulse order), per panel and
    per measure.
  - z = r / (1.4826 MAD(r)).
  - HIGH: z >= 3 (primary). LOW: z <= -3 (secondary).
  - Outlier time = tp.
COINCIDENCE:
  - Primary rule, exactly as h08s_shot_outliers.coincident: t2 - t1 in [855.93, 1346.50] s AND
    log10 BF >= 1. The scorer is identical: both arrival times against impact 00:19:37 + 300 +- 180 s, and
    the H01W bearing for Table 1 events.
  - Pulse time t2 is matched against H01W triggers t1 (strict, loose and Table 1-gated).
  - BF-THRESHOLD SWEEP (reported, not used for the verdict): log10 BF >= {-inf (span only), 0, 0.5, 1,
    1.3, 2}.
  - STATISTIC per (measure x sign x H01W variant): the number of outlier pulses with at least one
    coincident trigger.
NULL: cyclic shifts of the outlier flags over the pulse list (k = 1 .. n-1). A flag moves to another
  pulse and takes that pulse's time. p = (1 + #{N_null >= N}) / n.
SENSITIVITY:
  - T_C2 template, injected at uniform random times, 300 per SNR in {0, 3, 6, 10, 15, 20, 25} dB.
  - SNR is now relative to the median E_peak of the panel's pulses (a signal-to-shot ratio), with gap-level
    equivalents also reported.
  - Detected if a pulse within 2 s of the injection maximum has any measure at z >= +3.
OUTPUTS: h08s_pulses.csv (every pulse with its energies and z), h08s_pulse_energy.json (counts, p, BF
  sweep, injection P_D), and the energy histogram statistics: mode (KDE peak of log10 E_peak), median, and
  mean (of the linear energy, quoted in dB).
READING as before: p < 0.05 is a candidate, not a detection. No likelihood is returned (gate).
PROVENANCE: impact PDF = stand-in from run no-exhaustion-prior (b3dd44b), prior track 295.66 +- 1.0 deg.
Usage: python h08s_pulse_energy.py <kadri data dir> <stand-in summary json> <out dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal, stats

sys.path.insert(0, str(Path(__file__).parent))
import h08s_shot_outliers as H  # noqa: E402
import kadri_table1_test as KT  # noqa: E402
import kadri_trace_pairs as T  # noqa: E402

MEASURES = {"E_peak": (-1.0, 1.0), "E_pre": (-3.0, -1.0), "E_post": (1.0, 4.0)}
BF_SWEEP = [-np.inf, 0.0, 0.5, 1.0, 1.3, 2.0]


def pulses(tg, p):
    k = int(0.5 * H.FS)
    env = np.convolve(p ** 2, np.ones(k) / k, "same")
    pk, _ = signal.find_peaks(env, distance=int(3 * H.FS), prominence=2 * np.median(env))
    rows = []
    for i in pk:
        tp = tg[i]
        if tp - 3 < tg[0] or tp + 4 > tg[-1]:
            continue
        r = dict(t=float(tp))
        for m, (a, b) in MEASURES.items():
            sel = (tg >= tp + a) & (tg < tp + b)
            r[m] = float(np.sum(p[sel] ** 2) / H.FS)
        rows.append(r)
    c = pd.DataFrame(rows, columns=["t"] + list(MEASURES))
    for m in MEASURES:
        lg = np.log10(np.maximum(c[m].values, 1e-30))
        med = pd.Series(lg).rolling(13, center=True, min_periods=5).median().values
        r = lg - med
        c[f"z_{m}"] = r / (1.4826 * np.nanmedian(np.abs(r - np.nanmedian(r))))
    return c


def coincident_thr(t2, h01, l10bf, thr):
    for a, bear in h01:
        if H.SPAN[0] <= t2 - a <= H.SPAN[1] and (thr == -np.inf or l10bf(float(a), float(t2), bear) >= thr):
            return True
    return False


def main(kd, summary, out_dir):
    kd, out = Path(kd), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    _bf, _cache = H.scorer(summary), {}

    def l10bf(a, b, bear=None):           # memoised: pulse times are fixed, only flags move under the null
        key = (round(a, 3), round(b, 3), bear)
        if key not in _cache:
            _cache[key] = _bf(a, b, bear)
        return _cache[key]
    h01 = {}
    for op, ratio in T.RATIOS.items():
        ts = []
        for pnl in "abc":
            t, s = T.triggers(kd, pnl, ratio)
            ts.append(t[(t >= s[0]) & (t <= s[1])])
        h01[op] = [(a, None) for a in np.concatenate(ts)]
    tab = pd.read_csv(kd / "kadri-table1-transients.csv")
    tab["t_s"] = [KT.secs(x) for x in tab.time_utc]
    g = tab[(tab.bearing_deg >= 246.03) & (tab.bearing_deg <= 284.25)]
    h01["table1_gated"] = [(r.t_s, r.bearing_deg) for r in g.itertuples()]
    ser, Ps = {}, []
    for pnl in "de":
        tg, p = H.load(kd, pnl)
        c = pulses(tg, p)
        c["panel"] = pnl
        ser[pnl] = (tg, p, c)
        Ps.append(c)
    C = pd.concat(Ps, ignore_index=True)
    n = len(C)
    res, sweep, outl = {}, [], []
    for m in MEASURES:
        for sgn, lab in [(1, "high"), (-1, "low")]:
            flag = sgn * np.nan_to_num(C[f"z_{m}"].values) >= 3.0
            for v, h in h01.items():
                for thr in BF_SWEEP:
                    obs = sum(coincident_thr(C.t.values[i], h, l10bf, thr) for i in np.flatnonzero(flag))
                    nl = np.array([sum(coincident_thr(C.t.values[i], h, l10bf, thr) for i in np.flatnonzero(np.roll(flag, k))) for k in range(1, n)])
                    p = float((1 + (nl >= obs).sum()) / n)
                    row = dict(measure=m, sign=lab, h01w=v, log10_bf_min=thr, n_outliers=int(flag.sum()), n_coincident=int(obs), null_mean=float(nl.mean()), p=p)
                    sweep.append(row)
                    if thr == 1.0:
                        res[f"{m}_{lab}|{v}"] = row | {"reading": "candidate: more coincidences than chance" if p < 0.05 else "consistent with chance"}
            for i in np.flatnonzero(flag):
                outl.append(dict(measure=m, sign=lab, panel=C.panel.iloc[i], t_utc=str(KT.DAY0 + pd.Timedelta(seconds=float(C.t.iloc[i])))[11:21],
                                 t_s=float(C.t.iloc[i]), z=float(C[f"z_{m}"].iloc[i])))
    # sensitivity
    tm = H.template()
    w2 = int(2 * H.FS)
    e2 = np.convolve(tm ** 2, np.ones(w2), "valid").max() / H.FS
    rng = np.random.default_rng(H.SEED)
    pdr = []
    for snr in H.SNRS:
        hit = 0
        for _ in range(H.N_INJ):
            pnl = rng.choice(["d", "e"])
            tg, p, c0 = ser[pnl]
            gn = np.sqrt(10 ** (snr / 10) * float(np.median(c0.E_peak)) / e2)
            i0 = int(rng.uniform(20 * H.FS, len(tg) - len(tm) - 20 * H.FS))
            x = p.copy()
            x[i0: i0 + len(tm)] += gn * tm
            tinj = tg[i0 + int(np.argmax(np.convolve(tm ** 2, np.ones(int(0.5 * H.FS)), "same")))]
            c1 = pulses(tg, x)
            j = np.flatnonzero(np.abs(c1.t.values - tinj) <= 2.0)
            if len(j) and any(np.nan_to_num(c1[f"z_{m}"].values[j]).max() >= 3 for m in MEASURES):
                hit += 1
        pdr.append(dict(snr_vs_median_peak_db=snr, pd=hit / H.N_INJ))
    lg = np.log10(C.E_peak.values)
    kde = stats.gaussian_kde(lg)
    xs = np.linspace(lg.min(), lg.max(), 2000)
    hist = dict(mode_log10=float(xs[np.argmax(kde(xs))]), median_log10=float(np.median(lg)), mean_log10_of_linear=float(np.log10(np.mean(C.E_peak.values))),
                per_panel={pnl: dict(n=int((C.panel == pnl).sum()), median_log10=float(np.median(lg[C.panel == pnl]))) for pnl in "de"})
    gap_ref = {pnl: float(10 * np.log10(np.median(H.cycles(*ser[pnl][:2])[0].P_gap) * 2.0 / np.median(ser[pnl][2].E_peak))) for pnl in "de"}
    summ = dict(n_pulses=int(n), pulses_per_panel=C.groupby("panel").size().to_dict(), results=res, injection_pd=pdr,
                gap_level_2s_vs_median_peak_db=gap_ref, energy_histogram=hist,
                provenance="stand-in prior, run no-exhaustion-prior (b3dd44b), track 295.66 +- 1.0 deg; Kadri Fig 9 vectors")
    (out / "h08s_pulse_energy.json").write_text(json.dumps(summ, indent=1, default=str))
    pd.DataFrame(sweep).to_csv(out / "h08s_pulse_bf_sweep.csv", index=False)
    C.to_csv(out / "h08s_pulses.csv", index=False)
    pd.DataFrame(outl).to_csv(out / "h08s_pulse_outliers.csv", index=False)
    print(json.dumps(summ, indent=1, default=str))


if __name__ == "__main__":
    main(*sys.argv[1:4])
