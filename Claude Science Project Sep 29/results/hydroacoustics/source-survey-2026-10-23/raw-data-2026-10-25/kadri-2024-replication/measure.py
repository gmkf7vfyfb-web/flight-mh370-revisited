"""Processing and pre-registered statistics (kadri-preregistration.md, saved before data download).

K processing: demean, detrend, cosine taper (5 %, max 30 s; deviation from the pre-registered plain 5 %, which damped 6 min at the end of the 2-h H01W record), remove_response -> Pa (pre_filt 0.5/1/100/115 Hz, water level 60 dB),
Butterworth HP 5 Hz order 4 + BP 2-40 Hz order 4, zero-phase (sosfiltfilt). Net band 5-40 Hz.
"""
import numpy as np
from scipy import signal
from obspy import read, read_inventory, UTCDateTime
from pyproj import Geod
G = Geod(ellps="WGS84")
FS = 250.0

def process_K(st, inv, causal=False):
    st = st.copy()
    st.merge(method=1, fill_value="interpolate")  # 1-sample chunk-join holes interpolated (zero fill made spikes)
    out = {}
    for tr in st:
        tr.data = tr.data.astype(float)
        tr.detrend("demean"); tr.detrend("linear"); tr.taper(max_percentage=0.05, max_length=30.0)  # taper capped at 30 s
        tr.remove_response(inventory=inv, output="DEF", pre_filt=(0.5, 1.0, 100.0, 115.0), water_level=60,
                           taper=True, taper_fraction=min(0.05, 2 * 30.0 / (tr.stats.npts / tr.stats.sampling_rate)))  # obspy default 5 % taper capped at 30 s per end
        fs = tr.stats.sampling_rate
        hp = signal.butter(4, 5.0, btype="highpass", fs=fs, output="sos")
        bp = signal.butter(4, [2.0, 40.0], btype="bandpass", fs=fs, output="sos")
        x = tr.data
        if causal:
            x = signal.sosfilt(bp, signal.sosfilt(hp, x))
        else:
            x = signal.sosfiltfilt(bp, signal.sosfiltfilt(hp, x))
        tr.data = x
        out[tr.stats.station] = tr
    return out

def common_grid(trs):
    t0 = max(tr.stats.starttime for tr in trs.values()); t1 = min(tr.stats.endtime for tr in trs.values())
    n = int((t1 - t0) * FS)
    X = {}
    for k, tr in trs.items():
        i0 = int(round((t0 - tr.stats.starttime) * FS)); X[k] = tr.data[i0:i0 + n]
    return t0, X

def rms1s(x, fs=FS, win=1.0, hop=0.5):
    cs = np.concatenate([[0.0], np.cumsum(x ** 2)])
    w = int(win * fs); h = int(hop * fs)
    i = np.arange(0, len(x) - w, h)
    return (i + w / 2) / fs, np.sqrt((cs[i + w] - cs[i]) / w)

def d1_stalta(x, fs=FS, sta_s=2.0, lta_s=30.0, hop_s=0.1):
    """Copied from module prepare/searches_run_j/detectors.py d1_stalta (STA 2 s / LTA 30 s)."""
    y = np.asarray(x, float) ** 2
    cs = np.concatenate([[0.0], np.cumsum(y)])
    sta, lta, hop = int(sta_s * fs), int(lta_s * fs), max(int(hop_s * fs), 1)
    i = np.arange(lta, len(y) - sta + 1, hop)
    s = ((cs[i + sta] - cs[i]) / sta) / np.maximum((cs[i] - cs[i - lta]) / lta, 1e-30)
    return (i + sta / 2) / fs, s

def enu(inv):
    pos = {}
    for net in inv:
        for sta in net:
            ch = sta[0]; pos[sta.code] = (ch.latitude, ch.longitude)
    la0 = np.mean([p[0] for p in pos.values()]); lo0 = np.mean([p[1] for p in pos.values()])
    out = {}
    for k, (la, lo) in pos.items():
        az, _, d = G.inv(lo0, la0, lo, la)
        out[k] = np.array([d * np.sin(np.radians(az)), d * np.cos(np.radians(az))]) / 1000.0   # km (E, N)
    return out, (la0, lo0)

def xc_delay(a, b, fs=FS, maxlag=2.5):
    """delay of a relative to b (s); positive = a arrives later. Parabolic peak refinement. Returns (delay, peak cc)."""
    a = a - a.mean(); b = b - b.mean()
    c = signal.correlate(a, b, mode="full", method="fft")
    lags = signal.correlation_lags(len(a), len(b), mode="full")
    m = np.abs(lags) <= int(maxlag * fs)
    c = c[m]; lags = lags[m]
    c = c / (np.sqrt(np.sum(a ** 2) * np.sum(b ** 2)) + 1e-30)
    k = int(np.argmax(c))
    if 0 < k < len(c) - 1:
        y0, y1, y2 = c[k - 1], c[k], c[k + 1]; den = y0 - 2 * y1 + y2
        off = 0.5 * (y0 - y2) / den if den != 0 else 0.0
    else:
        off = 0.0
    return (lags[k] + off) / fs, float(c[k])

def bearing(X, pos, i_center, half_s=10.0, fs=FS, use_env=False):
    """Plane-wave back-azimuth from the three pair delays in a 2*half_s segment centred at sample i_center."""
    keys = sorted(X.keys())
    seg = {}
    for k in keys:
        x = X[k][max(0, int(i_center - half_s * fs)): int(i_center + half_s * fs)]
        if use_env:
            e = np.abs(signal.hilbert(x)); k2 = int(0.25 * fs); e = np.convolve(e, np.ones(k2) / k2, "same"); x = e
        seg[k] = x
    pairs = [(keys[0], keys[1]), (keys[1], keys[2]), (keys[0], keys[2])]
    A = []; tau = []; ccs = []
    for a, b in pairs:
        d, cc = xc_delay(seg[a], seg[b], fs)
        A.append(pos[a] - pos[b]); tau.append(d); ccs.append(cc)
    A = np.array(A); tau = np.array(tau)
    s, res, *_ = np.linalg.lstsq(A, tau, rcond=None)          # s/km, propagation direction
    closure = tau[0] + tau[1] - tau[2]
    baz = (np.degrees(np.arctan2(-s[0], -s[1]))) % 360
    vapp = 1.0 / np.linalg.norm(s) if np.linalg.norm(s) > 0 else np.inf
    return dict(baz_deg=float(baz), v_app_km_s=float(vapp), closure_s=float(closure), cc_min=float(min(ccs)), cc_mean=float(np.mean(ccs)), tau_s=tau.tolist())

def angdiff(a, b):
    return float((a - b + 180) % 360 - 180)
