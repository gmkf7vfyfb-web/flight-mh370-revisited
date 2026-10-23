"""PRE-REGISTRATION and implementation, amended-sequence item 3, STAGE A: injection-recovery of real
transients into real IMOS background, giving P_D against SNR for the 2b detectors at fixed false-alarm
rates; and STAGE A2: the 2b MH370 windows re-scored against the extended null. Committed BEFORE the
extended background is downloaded or read.

WHY: 2b's full-window null had 25-47 values per logger, so p could not fall below 0.005 (2b note, 6455ba3).

BACKGROUND (fixed now): IMOS public bucket, IMOS/ANMN/Acoustic/{PAPCA/3376, PAPOR/3274, PAKIM/3250}/
  <day>/raw/, days 20140301-20140307 and 20140309-20140315 (14 days, 96 files/day). 8 March is excluded
  (it holds the MH370 windows). 3315 and 3275 are not in the bucket: their nulls stay the 25 h set
  (disclosed), and 3315's P_D is taken from 3376 (same canyon, 2.8 km, noise within 3 dB above 5 Hz; an
  assumption). Fetched by fetch_imos_background.py, sha256 per file. A file is excluded only if it is
  unreadable or its header sample rate is not 6000 Hz (counted and reported).
TIME BASE: as 2b (convention A, sub-second footer field).

TEMPLATES (real far-field SOFAR transients at RCS, from 2b's controls):
  T_C2: 3315 decimated series, true UTC [05:03:01 - 10 s, + 50 s] (CMST p. 15; 2b SNR 19.2 dB).
  T_C1: 3315 decimated series, true UTC [01:33:44 - 10 s, + 50 s] (Curtin event; 2b SNR 14.5 dB).
  Each is used raw (volts at 3315), mean removed, 1 s cosine tapers at both ends. Template noise scales
  with the template; at the target SNRs it is >= 5 dB below the target background (disclosed).
INJECTED SNR: scale g so that max over 1 s frames of the scaled template's 5-40 Hz SPL, computed with the
  TARGET logger's calibration, minus the target's background median 1 s 5-40 Hz SPL (the 2b definition)
  equals the target SNR. Grid: -5, -2.5, 0, ..., +20 dB (11 values).
INJECTION: targets 3376, 3274, 3250. For each (target, template, SNR): 200 injections, each into a
  background recording drawn uniformly (seed 20261009) at an onset time uniform in [35 s, duration - 55 s]
  (so D1 can score it). The detectors are recomputed on the injected recording.
DETECTION: window [onset - 10 s, onset + 40 s] (50 s). Thresholds from the NON-injected extended
  background: the (1 - alpha) quantile of the 50 s window-max statistic over all windows (step 1 s), for
  alpha = 0.05 and 0.005; D1, D2, and 'D1 or D2' (alpha split: each at alpha/2).
OUTPUT: P_D(SNR) per target x template x detector x alpha, with Wilson 95 % intervals, and a logistic fit
  in SNR giving SNR_50 and SNR_90.

STAGE A2: the 11 MH370-window recordings of 2b re-scored for 3376, 3274, 3250 with the 2b statistics,
  window lengths and Bonferroni level (p < 0.005), against the extended null (same window length). 3315
  and 3275 keep the 2b null (reported as such). The 2b result is kept; A2 is reported beside it.

NOT DONE HERE (stage B, blocked on ruling H5 or on shared bathymetry): mapping SNR to eta and C_site
  needs transmission loss on the impact -> IMOS paths.

Usage: python imos_injection.py <out_dir> <background_root>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view
from scipy import signal

sys.path.insert(0, str(Path(__file__).parent))
import imos_detectors as D  # noqa: E402
import imos_noise as N  # noqa: E402
import imos_preregistration as P  # noqa: E402

HERE = Path(__file__).parent.parent
TARGETS = [3376, 3274, 3250]
DAYS = [f"201403{d:02d}" for d in list(range(1, 8)) + list(range(9, 16))]
SNRS = np.arange(-5, 20.01, 2.5)
N_INJ = 200
SEED = 20261009
ALPHAS = [0.05, 0.005]
WIN = (10.0, 40.0)


class Series:
    """D1/D2/SPL per-time statistics for an arbitrary decimated series, as in imos_detectors.Rec."""

    def __init__(self, xd, cal):
        self.n = len(xd)
        y = signal.sosfiltfilt(D.SOS_D1, xd) ** 2
        cs = np.concatenate([[0], np.cumsum(y)])
        i = np.arange(D.LTA, self.n - D.STA + 1, N.FS_D // 10)
        self.d1_t = (i + D.STA / 2) / N.FS_D
        self.d1 = ((cs[i + D.STA] - cs[i]) / D.STA) / np.maximum((cs[i] - cs[i - D.LTA]) / D.LTA, 1e-30)
        ns = self.n // N.FS_D
        f1, p1 = signal.periodogram(xd[: ns * N.FS_D].reshape(ns, N.FS_D), fs=N.FS_D, window="hann", detrend="constant", axis=-1)
        p1u = p1 / (10 ** ((np.interp(f1, *cal["gain"]) + cal["sens"]) / 10))
        lev = lambda lo, hi: 10 * np.log10(p1u[:, (f1 >= lo) & (f1 < hi)].mean(1))  # noqa: E731
        k = np.ones(3) / 3
        self.d2 = np.max([np.convolve(lev(5, 20) - cal["m5_20"], k, "same"), np.convolve(lev(10, 40) - cal["m10_40"], k, "same")], axis=0)
        self.d2_t = np.arange(ns) + 0.5
        band = (f1 >= 5) & (f1 < 40)
        self.spl = 10 * np.log10(p1u[:, band].sum(1) * (f1[1] - f1[0]))

    def wmax(self, sa, sb):
        m1 = (self.d1_t >= sa) & (self.d1_t <= sb)
        m2 = (self.d2_t >= sa) & (self.d2_t <= sb)
        return (float(self.d1[m1].max()) if m1.any() else np.nan, float(self.d2[m2].max()) if m2.any() else np.nan)


def spl_max(x, cal):
    ns = len(x) // N.FS_D
    f1, p1 = signal.periodogram(x[: ns * N.FS_D].reshape(ns, N.FS_D), fs=N.FS_D, window="hann", detrend="constant", axis=-1)
    p1u = p1 / (10 ** ((np.interp(f1, *cal["gain"]) + cal["sens"]) / 10))
    band = (f1 >= 5) & (f1 < 40)
    return float((10 * np.log10(p1u[:, band].sum(1) * (f1[1] - f1[0]))).max())


def wilson(k, n, z=1.96):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def null_windows(series, det, L):
    rate = 10 if det == "d1" else 1
    out = []
    for s in series:
        x = getattr(s, det)
        w = min(max(int(round(L * rate)), 1), len(x))
        out.append(sliding_window_view(x, w)[::rate].max(1))
    return np.concatenate(out)


def main(out_dir, bg_root):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    meta = P.parse_meta()
    nb = pd.read_csv(HERE / "results-data/imos1d/noise_bands.csv")
    cal = {}
    for cid in [3315] + TARGETS:
        m = meta[str(cid)]
        fg, G = N.gain_db(next(P.IMOS.glob(f"*/*alibration/{m['cal_file']}")))
        d = nb[nb.logger == cid].set_index("band").p50_1s
        cal[cid] = dict(gain=(fg, G), sens=m["sens_db"], m5_20=D.pw(d["5-10"], d["10-20"]), m10_40=D.pw(d["10-20"], d["20-40"]))
    # templates from 3315
    recs = pd.read_csv(HERE / "data/imos/recordings.csv", parse_dates=["start_logger"])
    tmpl = {}
    for name, hms in [("T_C2", "05:03:01"), ("T_C1", "01:33:44")]:
        t = D.DAY0 + pd.Timedelta(hms)
        for _, r in recs[recs.logger == 3315].iterrows():
            f = P.IMOS / r.file
            t0 = r.start_logger + pd.Timedelta(seconds=D.subsec(f))
            t0 = t0 - pd.Timedelta(seconds=P.clock_err(meta["3315"], t0))
            s = (t - t0).total_seconds()
            xd = N.decimate(N.read_volts(f))
            if 10 <= s <= len(xd) / N.FS_D - 50:
                seg = xd[int((s - 10) * N.FS_D): int((s + 50) * N.FS_D)].copy()
                seg -= seg.mean()
                tap = np.ones(len(seg))
                ramp = 0.5 * (1 - np.cos(np.linspace(0, np.pi, N.FS_D)))
                tap[: N.FS_D], tap[-N.FS_D:] = ramp, ramp[::-1]
                tmpl[name] = seg * tap
                break
    assert set(tmpl) == {"T_C2", "T_C1"}, tmpl.keys()
    rng = np.random.default_rng(SEED)
    summary = dict(days=DAYS, targets=TARGETS, n_inj=N_INJ, excluded={}, n_background={}, thresholds={}, fits={})
    rows, a2 = [], []
    pre = json.loads((HERE / "data/imos/preregistration.json").read_text())
    mh = pd.read_csv(HERE / "results-data/imos2b/mh370_windows.csv")
    for cid in TARGETS:
        files = sorted((Path(bg_root) / str(cid)).glob("2014*/*.DAT"))
        xs, series, excl = [], [], 0
        for f in files:
            try:
                fs, _, _, _ = P.header(f)
                if fs != 6000:
                    excl += 1
                    continue
                xd = N.decimate(N.read_volts(f))
            except Exception:
                excl += 1
                continue
            xs.append(xd)
            series.append(Series(xd, cal[cid]))
        summary["excluded"][cid], summary["n_background"][cid] = excl, len(series)
        bmed = float(np.median(np.concatenate([s.spl for s in series])))
        L = WIN[0] + WIN[1]
        thr = {}
        for det in ["d1", "d2"]:
            nl = null_windows(series, det, L)
            for a in ALPHAS:
                thr[(det, a)] = float(np.quantile(nl, 1 - a))
                thr[(det, a / 2)] = float(np.quantile(nl, 1 - a / 2))
        summary["thresholds"][cid] = {f"{k[0]}@{k[1]}": v for k, v in thr.items()}
        # STAGE A2: re-score 2b MH370 windows against the extended null
        for _, w in mh[mh.logger == cid].iterrows():
            row = dict(logger=cid, file=w.file, len_s=w.len_s, d1=w.d1, d2=w.d2, p_d1_2b=w.p_d1, p_d2_2b=w.p_d2)
            for det in ["d1", "d2"]:
                nl = null_windows(series, det, w.len_s)
                row[f"p_{det}_ext"] = float((nl >= w[det]).mean()) if np.isfinite(w[det]) else np.nan
                row[f"n_null_{det}"] = int(len(nl))
            row["detected_ext"] = bool(min(row["p_d1_ext"], row["p_d2_ext"]) < 0.005)
            a2.append(row)
        # STAGE A: injections
        for tname, tm in tmpl.items():
            base = spl_max(tm, cal[cid]) - bmed
            for snr in SNRS:
                g = 10 ** ((snr - base) / 20)
                hit = {k: 0 for k in ["d1@0.05", "d2@0.05", "or@0.05", "d1@0.005", "d2@0.005", "or@0.005"]}
                for _ in range(N_INJ):
                    j = rng.integers(len(xs))
                    x = xs[j].copy()
                    on = rng.uniform(35, len(x) / N.FS_D - 55)
                    i0 = int((on - 10) * N.FS_D)
                    x[i0: i0 + len(tm)] += g * tm
                    d1, d2 = Series(x, cal[cid]).wmax(on - WIN[0], on + WIN[1])
                    for a in ALPHAS:
                        hit[f"d1@{a}"] += d1 >= thr[("d1", a)]
                        hit[f"d2@{a}"] += d2 >= thr[("d2", a)]
                        hit[f"or@{a}"] += (d1 >= thr[("d1", a / 2)]) or (d2 >= thr[("d2", a / 2)])
                for k, v in hit.items():
                    lo, hi = wilson(v, N_INJ)
                    rows.append(dict(logger=cid, template=tname, snr_db=float(snr), detector=k.split("@")[0], alpha=float(k.split("@")[1]),
                                     k=int(v), n=N_INJ, pd=v / N_INJ, ci_lo=lo, ci_hi=hi))
            print(cid, tname, "done", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(out / "pd_vs_snr.csv", index=False)
    pd.DataFrame(a2).to_csv(out / "mh370_windows_extended_null.csv", index=False)
    from scipy.optimize import minimize
    for (cid, tn, det, a), g in res.groupby(["logger", "template", "detector", "alpha"]):
        def nll(th):
            p = 1 / (1 + np.exp(-(g.snr_db.values - th[0]) / max(th[1], 0.05)))
            p = np.clip(p, 1e-9, 1 - 1e-9)
            return -np.sum(g.k * np.log(p) + (g.n - g.k) * np.log(1 - p))
        th = minimize(nll, [5.0, 2.0], method="Nelder-Mead").x
        summary["fits"][f"{cid}|{tn}|{det}|{a}"] = dict(snr50=float(th[0]), snr90=float(th[0] + np.log(9) * max(th[1], 0.05)))
    (out / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    print(pd.DataFrame(a2).round(4).to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
