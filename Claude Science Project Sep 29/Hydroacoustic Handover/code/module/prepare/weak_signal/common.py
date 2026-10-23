"""Shared loaders for the weak-signal trials (preregistration.py). IMOS files are read with the module's
imos_noise.read_volts / decimate (500 Hz) then band-passed 5-40 Hz and decimated to 100 Hz; Kadri panels are the
digitised polylines resampled to 20 Hz; the plot-decimation emulator turns IMOS background into panel-like series."""
from __future__ import annotations
import sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import signal
sys.path.insert(0, str(Path(__file__).parent)); sys.path.insert(0, str(Path(__file__).parent.parent))
import preregistration as R
import imos_noise as N
import imos_preregistration as P

BG_ROOT = Path("/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background")
SOS = signal.butter(4, list(R.BAND), btype="bandpass", fs=N.FS_D, output="sos")
DEC = N.FS_D // R.FS


def bg_files(logger):
    files = sorted((BG_ROOT / str(logger)).glob("2014*/*.DAT"))
    return files[:: R.FILE_STRIDE[logger]]


def load_100(path):
    """5-40 Hz band-passed series at 100 Hz (float32) from an IMOS .DAT; None if unreadable or not 6 kHz."""
    try:
        fs, _, _, _ = P.header(path)
        if fs != 6000:
            return None
        xd = N.decimate(N.read_volts(path))
    except Exception:  # noqa: BLE001
        return None
    y = signal.sosfiltfilt(SOS, xd)
    return signal.decimate(y, DEC, ftype="fir", zero_phase=True).astype(np.float32)


def band_level_1s(x, fs=R.FS, lo=5.0, hi=40.0):
    """1 s Hann periodogram band level (dB re volts^2) per second; also the 5-20 and 10-40 Hz levels."""
    ns = len(x) // fs
    f, p = signal.periodogram(x[: ns * fs].reshape(ns, fs), fs=fs, window="hann", detrend="constant", axis=-1)
    def lev(a, b):
        m = (f >= a) & (f < b)
        return 10 * np.log10(np.maximum(p[:, m].sum(1) * (f[1] - f[0]), 1e-30))
    return lev(lo, hi), lev(5, 20), lev(10, 40)


# ---- Kadri panels -------------------------------------------------------------------------------------------------
KD = Path(__file__).parent.parent.parent / "data" / "kadri_fig9_digitised"
PANELS = {"a": ("H01W", "00:27:00"), "b": ("H01W", "00:37:00"), "c": ("H01W", "00:47:00"), "d": ("H08S", "01:00:00"), "e": ("H08S", "01:10:00")}


def load_panel(pnl, kd=None, fs=R.PANEL_FS):
    kd = Path(kd) if kd else KD
    st, t0 = PANELS[pnl]
    tr = pd.read_csv(kd / f"kadri-2024-figure9-panel-{pnl}-{st}.csv")
    t, p = tr.plotted_time_s.values, tr.pressure_pa.values
    tg = np.arange(0, 600, 1 / fs)
    x = np.interp(tg, t, p)
    utc0 = pd.Timestamp(f"2014-03-08T{t0}Z")
    return tg, x.astype(np.float32), utc0, len(t)


def emulate_plot(x500, fs_out=R.PANEL_FS, bin_s=0.069):
    """Plot-decimation emulator: 5-40 Hz series at 500 Hz -> per-bin min and max as vertices -> linear interp to fs_out."""
    y = signal.sosfiltfilt(SOS, x500)
    nb = int(bin_s * N.FS_D)
    n = len(y) // nb
    Y = y[: n * nb].reshape(n, nb)
    imin, imax = Y.argmin(1), Y.argmax(1)
    base = np.arange(n) * nb
    tv = np.concatenate([base + imin, base + imax]) / N.FS_D
    pv = np.concatenate([Y[np.arange(n), imin], Y[np.arange(n), imax]])
    o = np.argsort(tv)
    tg = np.arange(0, len(y) / N.FS_D, 1 / fs_out)
    return np.interp(tg, tv[o], pv[o]).astype(np.float32)
