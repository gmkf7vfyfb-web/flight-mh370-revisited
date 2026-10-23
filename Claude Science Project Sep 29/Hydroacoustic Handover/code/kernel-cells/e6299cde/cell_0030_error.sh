cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
cat > detectors.py <<'EOF'
"""Detector statistics for the run J searches, exactly as pre-registered in preregistration.py section 3-4.
IMOS path: 500 Hz decimated volts (imos_noise.read_volts/decimate) -> BE per band (1 s Hann periodogram), and the
5-40 Hz band-passed 100 Hz series -> D1 (STA 2 / LTA 30) and M1b (envelope matched filter, 18-template bank).
Panel path: 20 Hz series -> BE (2-5, 5-9 Hz), D1 on 1-9 Hz, M1b with the station's range templates.
Every statistic returns (t_s, s); a window's score is max(s) in the window, timed at the maximum."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "weak_signal"))
import preregistration as R

SOS_540 = signal.butter(4, list(R.BAND_MAIN), btype="bandpass", fs=R.FS_D, output="sos")
SOS_P = signal.butter(4, list(R.PANEL_BAND), btype="bandpass", fs=R.PANEL_FS, output="sos")
EPS = 1e-30


# ---- template bank ----------------------------------------------------------------------------------------------
def _pulse(T, key, tau, fs):
    import bank as B            # weak_signal/bank.py (pre-registered template conventions)
    return B.pulse(T, key, tau, fs=fs)


def envelope(x, fs, smooth_s=R.ENV_SMOOTH_S, out_fs=R.ENV_FS):
    e = np.asarray(x, float) ** 2
    k = max(int(smooth_s * fs), 1)
    e = np.convolve(e, np.ones(k) / k, "same")
    d = int(fs // out_fs); n = len(e) // d
    return e[: n * d].reshape(n, d).mean(1)


def bank_env(T, ranges, fs):
    """Zero-mean unit-energy envelope templates at 10 Hz for the given ranges x TAUS."""
    out, keys = [], []
    for r in ranges:
        for tau in R.TAUS:
            p = _pulse(T, f"h2_{r:.1f}", tau, 100)
            if fs != 100:
                p = signal.resample_poly(p, fs, 100)
            e = envelope(p, fs); e = e - e.mean(); out.append(e / np.sqrt(np.sum(e ** 2))); keys.append((r, tau))
    return out, keys


PEAK_IDX_10HZ = 350   # bank.PEAK_AT (35 s) at 10 Hz


# ---- statistics -------------------------------------------------------------------------------------------------
def d1_stalta(x, fs, sta_s=R.STA_S, lta_s=R.LTA_S, hop_s=R.HOP_S):
    y = np.asarray(x, float) ** 2
    cs = np.concatenate([[0.0], np.cumsum(y)])
    sta, lta, hop = int(sta_s * fs), int(lta_s * fs), max(int(hop_s * fs), 1)
    i = np.arange(lta, len(y) - sta + 1, hop)
    s = ((cs[i + sta] - cs[i]) / sta) / np.maximum((cs[i] - cs[i - lta]) / lta, EPS)
    return (i + sta / 2) / fs, s


def m1b_env(e10, bank):
    """Envelope matched filter on a 10 Hz envelope e10; returns (t_s at the template energy peak, max rho over bank)."""
    best = None
    for h in bank:
        L = len(h)
        if len(e10) < L + 2:
            return np.array([]), np.array([])
        c = signal.fftconvolve(e10, h[::-1], mode="valid")
        cs1 = np.concatenate([[0.0], np.cumsum(e10)]); cs2 = np.concatenate([[0.0], np.cumsum(e10 ** 2)])
        s1 = cs1[L:] - cs1[:-L]; s2 = cs2[L:] - cs2[:-L]
        var = np.maximum(s2 - s1 ** 2 / L, EPS)
        r = c / np.sqrt(var * np.sum(h ** 2))
        best = r if best is None else np.maximum(best[: len(r)], r[: len(best)])
    i = np.arange(len(best))
    return (i + PEAK_IDX_10HZ) / float(R.ENV_FS), best


def band_levels_1s(x, fs, bands):
    ns = len(x) // fs
    f, p = signal.periodogram(np.asarray(x[: ns * fs], float).reshape(ns, fs), fs=fs, window="hann", detrend="constant", axis=-1)
    df = f[1] - f[0]
    out = {}
    for a, b in bands:
        m = (f >= a) & (f < b)
        out[(a, b)] = 10 * np.log10(np.maximum(p[:, m].sum(1) * df, EPS))
    return np.arange(ns) + 0.5, out


def be_stats(x, fs, bands):
    """Band energy per band: 1 s level minus the median of the preceding 60 s, 3 s running mean (dB)."""
    t, lev = band_levels_1s(x, fs, bands)
    k = np.ones(R.BE_MEAN_S) / R.BE_MEAN_S
    out = {}
    for b, v in lev.items():
        med = pd.Series(v).shift(1).rolling(R.BE_MED_S, min_periods=10).median().values
        out[b] = (t, np.convolve(v - med, k, "same"))
    return out, lev


def window_scores(t, s, t_end, start=R.WARMUP_S, L=R.WINDOW_S):
    """Max of s in each non-overlapping L s window from `start` to t_end; returns (w_start, score, t_of_max)."""
    ws, sc, tm = [], [], []
    a = start
    while a + L <= t_end + 1e-6:
        m = (t >= a) & (t < a + L) & np.isfinite(s)
        if m.any():
            j = np.argmax(np.where(m, s, -np.inf)); ws.append(a); sc.append(float(s[j])); tm.append(float(t[j]))
        a += L
    return np.array(ws), np.array(sc), np.array(tm)


# ---- full pipelines ---------------------------------------------------------------------------------------------
def imos_series(x500):
    """From the 500 Hz series: (x100 band-passed 5-40 Hz, e10 envelope)."""
    y = signal.sosfiltfilt(SOS_540, x500)
    x100 = signal.decimate(y, R.FS_D // R.FS, ftype="fir", zero_phase=True)
    return x100, envelope(x100, R.FS)


def imos_stats(x500, bank):
    x100, e10 = imos_series(x500)
    out = {}
    t, s = d1_stalta(x100, R.FS); out["D1"] = (t, s)
    t, s = m1b_env(e10, bank); out["M1b"] = (t, s)
    be, lev = be_stats(x500, R.FS_D, R.BANDS)
    for b, (t, s) in be.items():
        out[f"BE_{R.BAND_LABEL(b)}"] = (t, s)
    return out, lev


def panel_stats(x20, bank):
    xb = signal.sosfiltfilt(SOS_P, np.asarray(x20, float))
    out = {}
    t, s = d1_stalta(xb, R.PANEL_FS); out["D1"] = (t, s)
    t, s = m1b_env(envelope(xb, R.PANEL_FS), bank); out["M1b"] = (t, s)
    be, lev = be_stats(xb, R.PANEL_FS, R.PANEL_BANDS)
    for b, (t, s) in be.items():
        out[f"BE_{R.BAND_LABEL(b)}"] = (t, s)
    return out, lev


def scores_all(stats, t_end):
    return {k: window_scores(t, s, t_end) for k, (t, s) in stats.items()}
EOF
cat > null_worker.py <<'EOF'
"""Background null worker (preregistration.py section 5): window maxima of every pre-registered statistic on the
IMOS background files of one logger shard; for 3376 also the emulated-panel statistics (null A for the digitised
Kadri panels). Usage: python null_worker.py <logger> <shard> <nshards> <out.npz>"""
from __future__ import annotations
import sys, time
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import preregistration as R, detectors as D
sys.path.insert(0, str(Path(__file__).resolve().parent.parent)); sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "weak_signal"))
import imos_noise as N, imos_preregistration as P
import common as C


def main(logger, shard, nshards, out):
    t0 = time.time()
    files = sorted((R.BG_ROOT / logger).glob("2014*/*.DAT"))[shard::nshards]
    T = np.load(R.TEMPLATES)
    bank_i, _ = D.bank_env(T, R.IMOS_BANK_RANGES, 100)
    bank_p = {st: D.bank_env(T, (R.PANEL_BANK_RANGE[st],), 100)[0] for st in R.IMS}
    acc, accp, nfile, nbad = {}, {st: {} for st in R.IMS}, 0, 0
    for k, f in enumerate(files):
        try:
            fs, _, _, _ = P.header(f)
            if fs != 6000: nbad += 1; continue
            x500 = N.decimate(N.read_volts(f))
        except Exception:  # noqa: BLE001
            nbad += 1; continue
        st, _ = D.imos_stats(x500, bank_i)
        sc = D.scores_all(st, len(x500) / R.FS_D)
        for key, (ws, s, tm) in sc.items():
            acc.setdefault(key, []).append(s)
        if logger == "3376":
            x20 = C.emulate_plot(x500)
            for stn in R.IMS:
                stp, _ = D.panel_stats(x20, bank_p[stn])
                scp = D.scores_all(stp, len(x20) / R.PANEL_FS)
                for key, (ws, s, tm) in scp.items():
                    accp[stn].setdefault(key, []).append(s)
        nfile += 1
        if k % 50 == 0:
            print(logger, shard, k, len(files), round(time.time() - t0), flush=True)
    res = {k: np.concatenate(v) for k, v in acc.items()}
    for stn in R.IMS:
        for k, v in accp[stn].items():
            res[f"panel_{stn}_{k}"] = np.concatenate(v)
    res["n_files"] = np.array([nfile, nbad])
    np.savez_compressed(out, **res)
    print("done", logger, shard, nfile, nbad, round(time.time() - t0), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
EOF
# smoke on 2 files via a tiny shard count to check timing (not quoted as evidence)
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/null
time python null_worker.py 3376 0 672 /tmp/null_smoke.npz 2>&1 | tail -3
python -c "
import numpy as np; z=np.load('/tmp/null_smoke.npz'); print({k:(z[k].shape, np.round(z[k][:3],3)) for k in z.keys()})"