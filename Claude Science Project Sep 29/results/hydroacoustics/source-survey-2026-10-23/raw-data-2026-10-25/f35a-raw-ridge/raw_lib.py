"""Raw F-35A H11 processing library (pre-registration f35a-raw-prereg.md, P1-P9, G1-G5).
Units: pressure Pa; exposure Pa^2 s; levels dB re 1 uPa; PSD dB re 1 uPa^2/Hz; ESD Pa^2 s/Hz."""
import numpy as np, pandas as pd, obspy
from scipy import signal
from pyproj import Geod
FS = 250.0
ELS = ["H11N1", "H11N2", "H11N3", "H11S1", "H11S2", "H11S3"]
DAY = obspy.UTCDateTime("2019-04-09T00:00:00")
FRAME = {"H11N": (DAY + 11*3600 + 2*60 + 55, DAY + 11*3600 + 3*60 + 25), "H11S": (DAY + 11*3600 + 3*60 + 55, DAY + 11*3600 + 4*60 + 25)}
NOISE_SEG = (DAY + 10*3600 + 45*60, DAY + 11*3600 + 1*60)
BANDS = [2.0, 2.5, 3.15, 4.0, 5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0, 100.0]
HOP = 0.02
G = Geod(ellps="WGS84")

def to_pa(tr, inv):
    t = tr.copy(); t.detrend("demean"); t.taper(0.05)
    t.remove_response(inventory=inv, output="DEF", pre_filt=(0.5, 1.0, 110.0, 120.0), water_level=None, zero_mean=True, taper=False)
    return t

def bp(x, lo, hi, order=4):
    sos = signal.butter(order, [lo, hi], btype="bandpass", fs=FS, output="sos")
    return signal.sosfiltfilt(sos, x)

def ms_1s(x):
    """1-s moving mean square (boxcar, centred), sampled every HOP s; returns (t_offset_s, ms)."""
    n = int(FS); c = np.concatenate([[0.0], np.cumsum(x * x)])
    ms = (c[n:] - c[:-n]) / n                      # window [i, i+n)
    tc = (np.arange(len(ms)) + n / 2) / FS        # centre time
    step = int(round(HOP * FS))
    return tc[::step], ms[::step]

def width(t, L, ipk, drop, dt):
    thr = L[ipk] - drop; a = ipk; b = ipk
    while a > 0 and L[a - 1] >= thr: a -= 1
    while b < len(L) - 1 and L[b + 1] >= thr: b += 1
    return float(t[b] - t[a] + dt)

def obs_operator(t, L, dt, noise_db=None, excl=8.0, arr_db=1.0):
    """obs.py element_summary on an arbitrary envelope (unchanged logic)."""
    ipk = int(np.argmax(L)); tpk = t[ipk]
    out = (t < tpk - excl) | (t > tpk + excl)
    Ln = float(np.median(L[out])) if noise_db is None else float(noise_db)
    a = ipk
    while a > 0 and L[a - 1] > Ln + arr_db: a -= 1
    b = ipk
    while b < len(L) - 1 and L[b + 1] > Ln + arr_db: b += 1
    ex = np.clip(10 ** (L / 10) - 10 ** (Ln / 10), 0, None)
    w = np.zeros_like(ex); w[a:b + 1] = ex[a:b + 1]
    se = float(w.sum() * dt * 1e-12)
    c = np.cumsum(w) / max(w.sum(), 1e-30)
    t05, t95 = float(np.interp(0.05, c, t)), float(np.interp(0.95, c, t))
    on = ipk
    while on > 0 and L[on] > Ln + 3.0: on -= 1
    return dict(peak_db=float(L[ipk]), peak_t=float(tpk), noise_db=Ln, snr_db=float(L[ipk] - Ln), arr_start=float(t[a]), arr_end=float(t[b]),
                arr_len_s=float(t[b] - t[a] + dt), se_pa2s=se, sel_db=float(10 * np.log10(max(se, 1e-30) / 1e-12)), w3_s=width(t, L, ipk, 3, dt),
                w6_s=width(t, L, ipk, 6, dt), w10_s=width(t, L, ipk, 10, dt), span_5_95_s=t95 - t05, t05=t05, t95=t95, onset_t=float(t[on]))

def arons_w_kg(P, R):
    return (R / ((P / 52.4e6) ** (-1 / 1.13))) ** 3

def enu(lats, lons, lat0, lon0):
    xy = []
    for la, lo in zip(lats, lons):
        az, _, d = G.inv(lon0, lat0, lo, la)
        xy.append((d * np.sin(np.radians(az)), d * np.cos(np.radians(az))))
    return np.array(xy)

def xcorr_delay(a, b, maxlag):
    """delay of b relative to a (s), parabolic sub-sample; positive = b later."""
    n = len(a); c = signal.correlate(b, a, mode="full", method="fft"); lags = np.arange(-n + 1, n)
    m = np.abs(lags) <= maxlag; c = c[m]; lags = lags[m]
    i = int(np.argmax(c))
    if 0 < i < len(c) - 1:
        y0, y1, y2 = c[i - 1], c[i], c[i + 1]; d = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
    else:
        d = 0.0
    cc = c[i] / np.sqrt(np.sum(a * a) * np.sum(b * b))
    return (lags[i] + d) / FS, float(cc)

def plane_wave(xy, delays_pairs, pairs):
    """LSQ horizontal slowness s from t_j - t_i = s.(x_j - x_i). returns baz (deg), v_app (m/s), closure (s)."""
    A = np.array([xy[j] - xy[i] for i, j in pairs]); d = np.array(delays_pairs)
    s, *_ = np.linalg.lstsq(A, d, rcond=None)
    az_prop = np.degrees(np.arctan2(s[0], s[1])) % 360       # propagation direction
    baz = (az_prop + 180) % 360
    v = 1.0 / np.hypot(*s)
    return baz, v, s

def welch_psd(x, nper=250):
    f, p = signal.welch(x, fs=FS, window="hann", nperseg=nper, noverlap=nper // 2, detrend="constant", scaling="density")
    return f, p

def welch_segments(x, nper=250):
    """per-segment periodograms (for the bootstrap), Hann, 50 % overlap; returns f, P[nseg, nf] (Pa^2/Hz)."""
    f, t, Z = signal.spectrogram(x, fs=FS, window="hann", nperseg=nper, noverlap=nper // 2, detrend="constant", scaling="density", mode="psd")
    return f, Z.T
