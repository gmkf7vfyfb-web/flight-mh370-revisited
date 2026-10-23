"""Amended-sequence item 1d: noise per logger and band from the IMOS raw data, and the clock-sign test, run
EXACTLY as pre-registered in imos_preregistration.py (commit 0ffa244). Recordings with role 'S' are never
opened here (asserted). Outputs to <out>/: clock_test.json, calibration_gain.csv, noise_bands.csv,
noise_per_recording.csv, noise_summary.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import signal, stats

sys.path.insert(0, str(Path(__file__).parent))
import imos_preregistration as P  # noqa: E402

FS_D = 500                     # decimated rate, Hz
Q = 12                         # 6000 / 500
BANDS = [(2, 5), (5, 10), (10, 20), (20, 40), (40, 80), (80, 160), (160, 240)]
NPER = 4 * FS_D                # 4 s Welch segments


def read_volts(path):
    """load_loggerdatanew.m: big-endian uint16, 5 header lines, footer from 'Record'; volts, mean removed."""
    raw = Path(path).read_bytes()
    pos = 0
    for _ in range(5):
        pos = raw.index(b"\n", pos) + 1
    tail = raw[-1000:]
    footer_bytes = 1000 - tail.index(b"Record")
    end = len(raw) - footer_bytes - 2
    n = (end - pos) // 2
    x = np.frombuffer(raw, dtype=">u2", count=n, offset=pos).astype(np.float64) * (5.0 / 65536)
    return x - x.mean()


def decimate(x):
    return signal.resample_poly(x, 1, Q)


def welch(xd):
    f, p = signal.welch(xd, fs=FS_D, window="hann", nperseg=NPER, noverlap=NPER // 2, detrend="constant")
    return f, p


def band_mean(f, p, lo, hi):
    m = (f >= lo) & (f < hi)
    return p[..., m].mean(axis=-1)


def gain_db(cal_path):
    f, p = welch(decimate(read_volts(cal_path)))
    return f, 10 * np.log10(p) + 90.0          # input white noise -90 dB re 1 V^2/Hz


def clock_test(meta3315, recs3315):
    """Pre-registered: 5-40 Hz zero-phase 4th-order Butterworth, |Hilbert|, 2 s moving mean, peak in logger 01:32-01:36."""
    lo, hi = pd.Timestamp("2014-03-08T01:32:00Z"), pd.Timestamp("2014-03-08T01:36:00Z")
    sos = signal.butter(4, [5, 40], btype="bandpass", fs=FS_D, output="sos")
    best = None
    for _, r in recs3315.iterrows():
        t0 = r.start_logger
        t1 = t0 + pd.Timedelta(seconds=r.dur_s)
        if t1 < lo or t0 > hi:
            continue
        assert r.role != "S"
        xd = decimate(read_volts(P.IMOS / r.file))
        env = np.abs(signal.hilbert(signal.sosfiltfilt(sos, xd)))
        env = np.convolve(env, np.ones(2 * FS_D) / (2 * FS_D), mode="same")
        tt = t0 + pd.to_timedelta(np.arange(len(env)) / FS_D, unit="s")
        m = (tt >= lo) & (tt <= hi)
        if m.any():
            i = np.flatnonzero(m)[np.argmax(env[m])]
            if best is None or env[i] > best[1]:
                best = (tt[i], float(env[i]), r.file, float(np.median(env[m])))
    e = P.clock_err(meta3315, best[0])
    tA, tB = best[0] - pd.Timedelta(seconds=e), best[0] + pd.Timedelta(seconds=e)
    dA, dB = (tA - P.CURTIN_RCS_UTC).total_seconds(), (tB - P.CURTIN_RCS_UTC).total_seconds()
    okA, okB = abs(dA) <= P.CURTIN_TOL_S, abs(dB) <= P.CURTIN_TOL_S
    verdict = "A" if okA and not okB else "B" if okB and not okA else "unresolved"
    return dict(peak_logger=str(best[0]), file=best[2], peak_to_median_env=round(best[1] / best[3], 2), clock_err_s=round(e, 2),
                true_A=str(tA), true_B=str(tB), dA_s=round(dA, 2), dB_s=round(dB, 2), verdict=verdict)


def main(out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    pre = json.loads((Path(__file__).parent.parent / "data/imos/preregistration.json").read_text())
    recs = pd.read_csv(Path(__file__).parent.parent / "data/imos/recordings.csv", parse_dates=["start_logger"])
    meta = P.parse_meta()

    ct = clock_test(meta["3315"], recs[recs.logger == 3315])
    (out / "clock_test.json").write_text(json.dumps(ct, indent=1))
    print("clock", ct)

    gains, rows, per_rec, summ = [], [], [], {}
    for cid, L in pre["loggers"].items():
        calp = next(P.IMOS.glob(f"*/*alibration/{L['cal_file']}"))
        fg, G = gain_db(calp)
        g100 = float(np.interp(100, fg, G))
        gb = {f"{lo}-{hi}": float(10 * np.log10(band_mean(fg, 10 ** (G / 10), lo, hi))) for lo, hi in BANDS}
        for k, v in gb.items():
            gains.append(dict(logger=cid, band=k, gain_db=round(v, 2), gain_rel_100Hz_db=round(v - g100, 2), rolloff_flag=v < g100 - 20))
        Gi = lambda f: np.interp(f, fg, G)  # noqa: E731
        sub = recs[(recs.logger == int(cid)) & (recs.role == "B")]
        lev1 = {f"{lo}-{hi}": [] for lo, hi in BANDS}
        for _, r in sub.iterrows():
            assert r.role == "B"
            xd = decimate(read_volts(P.IMOS / r.file))
            f, p = welch(xd)
            # UNITS (deviation, disclosed): the metadata labels sensitivity 'dB re V^2/Pa^2', but -197.8/-196 are
            # the magnitudes of re 1 V^2/uPa^2 (re 1 V/uPa; HTI-90-U class ~ -198). Read literally, every level
            # would sit 120 dB above any measured ocean noise. So dB re 1 uPa^2/Hz = 10 log10(V^2/Hz) - G - S_h.
            cal = 10 ** ((Gi(f) + L["sens_db"]) / 10)    # V^2/Hz -> uPa^2/Hz divisor
            pu = p / cal
            rec = dict(logger=cid, file=r.file, start_logger=str(r.start_logger))
            for lo, hi in BANDS:
                rec[f"{lo}-{hi}"] = round(float(10 * np.log10(band_mean(f, pu, lo, hi))), 2)
            per_rec.append(rec)
            # 1 s Hann periodograms
            nseg = len(xd) // FS_D
            seg = xd[: nseg * FS_D].reshape(nseg, FS_D)
            f1, p1 = signal.periodogram(seg, fs=FS_D, window="hann", detrend="constant", axis=-1)
            p1u = p1 / (10 ** ((Gi(f1) + L["sens_db"]) / 10))
            for lo, hi in BANDS:
                lev1[f"{lo}-{hi}"].append(band_mean(f1, p1u, lo, hi))
        s = {}
        for lo, hi in BANDS:
            k = f"{lo}-{hi}"
            e = np.concatenate(lev1[k])
            db = 10 * np.log10(e)
            wl = np.array([r[k] for r in per_rec if r["logger"] == cid])
            row = dict(logger=cid, band=k, n_recordings=len(sub), n_1s=len(e),
                       p5_1s=round(float(np.percentile(db, 5)), 2), p50_1s=round(float(np.percentile(db, 50)), 2),
                       p95_1s=round(float(np.percentile(db, 95)), 2), p99_minus_p50_db=round(float(np.percentile(db, 99) - np.percentile(db, 50)), 2),
                       excess_kurtosis_1s=round(float(stats.kurtosis(e)), 2),
                       p5_welch=round(float(np.percentile(wl, 5)), 2), p50_welch=round(float(np.percentile(wl, 50)), 2),
                       p95_welch=round(float(np.percentile(wl, 95)), 2),
                       rolloff_flag=bool(gb[k] < g100 - 20))
            rows.append(row)
            s[k] = row
        summ[cid] = s
        print(cid, "B recs", len(sub), {k: (v["p50_1s"], v["rolloff_flag"]) for k, v in s.items()})
    pd.DataFrame(gains).to_csv(out / "calibration_gain.csv", index=False)
    pd.DataFrame(rows).to_csv(out / "noise_bands.csv", index=False)
    pd.DataFrame(per_rec).to_csv(out / "noise_per_recording.csv", index=False)
    (out / "noise_summary.json").write_text(json.dumps(dict(clock_test=ct, units="dB re 1 uPa^2/Hz", bands=summ), indent=1, default=str))


if __name__ == "__main__":
    main(sys.argv[1])
