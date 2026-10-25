"""Transair 810 at H11: shared processing (pre-registration v986504a4, sections 2-3).
Raw IM EDH 250 Hz -> full StationXML response removed to Pa (pre-filt 1/2/110/120 Hz) -> 5-40 Hz Butterworth 4-pole
zero-phase -> 100 Hz. D1 and M1b are the module's functions (prepare/searches_run_j/detectors.py, imported unchanged);
C3 (triad coherence) and the plane-wave fit are new here."""
from __future__ import annotations
import sys, pathlib
import numpy as np, pandas as pd
from scipy import signal
from obspy import read, read_inventory, UTCDateTime
from pyproj import Geod
WS = pathlib.Path(__file__).resolve().parent.parent
MOD = WS / "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sys.path.insert(0, str(MOD / "prepare/searches_run_j"))
import detectors as DET                     # module D1 (d1_stalta), M1b (m1b_env, envelope)
G = Geod(ellps="WGS84")
FS0, FS = 250, 100
SOS = signal.butter(4, [5.0, 40.0], btype="bandpass", fs=FS0, output="sos")
PRE_FILT = (1.0, 2.0, 110.0, 120.0)
TRIADS = {"H11N": ["H11N1", "H11N2", "H11N3"], "H11S": ["H11S1", "H11S2", "H11S3"]}
SRC = dict(lat=21.27616, lon=-158.02565)
T0 = UTCDateTime("2021-07-02T11:45:17")
C, C_SD = 1.482, 0.006
WIN = 90.0
PW = {"H11N": UTCDateTime("2021-07-02T12:25:39"), "H11S": UTCDateTime("2021-07-02T12:26:08")}
KW = {"H11N": UTCDateTime("2021-07-02T12:32:12"), "H11S": UTCDateTime("2021-07-02T12:31:10")}
LEVELS = ((0.05, "report"), (0.1, "mark"), (0.3, "screen"))


def label(p):
    for th, nm in LEVELS:
        if p < th:
            return nm
    return "none"


def element_geometry(inv):
    """Element offsets (east, north, m) from the triad centroid, back-azimuth to the source."""
    out = {}
    for tri, els in TRIADS.items():
        ch = {e: inv.select(station=e, channel="EDH")[0][0][0] for e in els}
        la = np.mean([c.latitude for c in ch.values()]); lo = np.mean([c.longitude for c in ch.values()])
        xy = {}
        for e, c in ch.items():
            az, _, d = G.inv(lo, la, c.longitude, c.latitude)
            xy[e] = np.array([d * np.sin(np.radians(az)), d * np.cos(np.radians(az))])
        baz = G.inv(lo, la, SRC["lon"], SRC["lat"])[0] % 360
        out[tri] = dict(xy=xy, baz=baz, lat=la, lon=lo)
    return out


def plane_wave_delays(xy, baz, c_kms=C):
    u = np.array([np.sin(np.radians(baz)), np.cos(np.radians(baz))])
    return {e: -float(v @ u) / (c_kms * 1000.0) for e, v in xy.items()}


def process_file(fn, inv):
    """One element file -> (UTC start, 100 Hz 5-40 Hz Pa series float32, gap mask bool at 100 Hz)."""
    st = read(fn)
    st.merge(method=1, fill_value=None)
    tr = st[0]
    data = tr.data
    if np.ma.isMaskedArray(data):
        gap = np.ma.getmaskarray(data); tr.data = data.filled(0).astype(float)
    else:
        gap = np.zeros(len(data), bool); tr.data = data.astype(float)
    tr.detrend("demean")
    tr.remove_response(inventory=inv, output="DEF", pre_filt=PRE_FILT, water_level=None, zero_mean=False, taper=True, taper_fraction=0.002)
    y = signal.sosfiltfilt(SOS, tr.data)
    y[gap] = 0.0
    x = signal.resample_poly(y, 2, 5).astype(np.float32)
    g = gap[: len(gap) // 5 * 5].reshape(-1, 5).any(1)
    g = np.repeat(g, 2)[: len(x)]
    if len(g) < len(x):
        g = np.concatenate([g, np.zeros(len(x) - len(g), bool)])
    return tr.stats.starttime, x, g


def triad_block(files, inv):
    """Align three element series on a common 100 Hz grid starting at the latest start."""
    parts = {e: process_file(f, inv) for e, f in files.items()}
    t0 = max(p[0] for p in parts.values())
    n = min(len(p[1]) - int(round((t0 - p[0]) * FS)) for p in parts.values())
    X = {}; M = np.zeros(n, bool)
    for e, (ts, x, g) in parts.items():
        k = int(round((t0 - ts) * FS)); X[e] = x[k: k + n]; M |= g[k: k + n]
    return t0, X, M


# ---------------- statistics ----------------
def d1_triad(X):
    ts = None; acc = None
    for e, x in X.items():
        t, s = DET.d1_stalta(x, FS)
        acc = s if acc is None else acc[: len(s)] + s[: len(acc)]
        ts = t if ts is None else ts[: len(acc)]
    return ts[: len(acc)], acc / len(X)


def env_triad(X):
    es = [DET.envelope(x, FS) for x in X.values()]
    n = min(len(e) for e in es)
    return np.mean([e[:n] for e in es], axis=0)


def m1b_triad(X, bank):
    return DET.m1b_env(env_triad(X), bank)


def c3_triad(X, xy, frame_s=8.0, hop_s=1.0, vmin=1.40):
    els = list(X.keys()); pairs = [(0, 1), (0, 2), (1, 2)]
    L, H = int(frame_s * FS), int(hop_s * FS)
    n = min(len(x) for x in X.values()); starts = np.arange(0, n - L + 1, H)
    nfft = 2 * L
    idx = starts[:, None] + np.arange(L)[None, :]
    F = {}; En = {}
    win = np.hanning(L).astype(np.float32)
    for e in els:
        fr = X[e][idx] * win
        fr = fr - fr.mean(1, keepdims=True)
        F[e] = np.fft.rfft(fr, nfft, axis=1); En[e] = (fr ** 2).sum(1)
    rho_all = []; lag_all = []
    for i, j in pairs:
        ei, ej = els[i], els[j]
        d = float(np.linalg.norm(xy[ej] - xy[ei]))
        maxlag = int(np.ceil((d / (vmin * 1000.0) + 0.1) * FS))
        cc = np.fft.irfft(F[ej] * np.conj(F[ei]), nfft, axis=1)      # cc[k] = sum x_j[n+k] x_i[n]  (lag of j after i)
        cc = np.concatenate([cc[:, -maxlag:], cc[:, : maxlag + 1]], axis=1)
        cc /= np.sqrt(np.maximum(En[ei] * En[ej], 1e-30))[:, None]
        k = np.argmax(cc, axis=1); rmax = cc[np.arange(len(k)), k]
        # parabolic refinement
        km = np.clip(k, 1, cc.shape[1] - 2)
        y0, y1, y2 = cc[np.arange(len(k)), km - 1], cc[np.arange(len(k)), km], cc[np.arange(len(k)), km + 1]
        den = (y0 - 2 * y1 + y2); off = np.where(np.abs(den) > 1e-12, 0.5 * (y0 - y2) / den, 0.0)
        lag = (km + np.clip(off, -1, 1) - maxlag) / FS
        rho_all.append(rmax); lag_all.append(lag)
    rho = np.vstack(rho_all); lag = np.vstack(lag_all)
    t = (starts + L / 2) / FS
    return t, rho.mean(0), lag


def plane_fit(lags, xy):
    """lags: (3,) for pairs (0,1),(0,2),(1,2) = t_j - t_i (s). Returns back-azimuth (deg) and apparent speed (km/s)."""
    els = list(xy.keys()); pairs = [(0, 1), (0, 2), (1, 2)]
    A = np.array([xy[els[j]] - xy[els[i]] for i, j in pairs])
    q, *_ = np.linalg.lstsq(A, np.asarray(lags), rcond=None)    # t_j - t_i = (x_j - x_i) . q, q = propagation slowness
    v = 1.0 / max(np.linalg.norm(q), 1e-12) / 1000.0
    baz = np.degrees(np.arctan2(-q[0], -q[1])) % 360
    return float(baz), float(v)


def ms1(x):
    """1-s mean square (Pa^2) at 100 Hz, per second."""
    n = len(x) // FS
    return (np.asarray(x[: n * FS], float) ** 2).reshape(n, FS).mean(1)


def window_score(t, s, a, b):
    m = (t >= a) & (t < b) & np.isfinite(s)
    if not m.any():
        return np.nan, np.nan
    j = np.argmax(np.where(m, s, -np.inf)); return float(s[j]), float(t[j])
