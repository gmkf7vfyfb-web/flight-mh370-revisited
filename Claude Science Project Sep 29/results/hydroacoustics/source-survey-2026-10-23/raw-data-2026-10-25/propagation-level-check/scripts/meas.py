"""Measurement library (pre-registration out/prereg.md, sections M1-M8). Units: Pa, Pa^2 s, dB re 1 uPa, dB re 1 uPa^2 s/Hz."""
import numpy as np
from obspy import read, read_inventory, UTCDateTime as U
from scipy.signal import butter, sosfiltfilt
from scipy.signal.windows import tukey
from pyproj import Geod
G = Geod(ellps="WGS84")
FC_ALL = [2.5, 3.15, 4.0, 5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0, 80.0]
FC_SCORED = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]

def band_edges(fc):
    # exact base-2 third-octave about the nominal centre (module convention: fc*2^(+-1/6))
    return fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6)

def load(path, resp, t0=None, t1=None):
    st = read(path); inv = read_inventory(resp)
    st.merge(method=1, fill_value=None)
    tr = st[0]
    gaps = bool(np.ma.isMaskedArray(tr.data) and np.ma.count_masked(tr.data))
    if gaps:
        tr.data = tr.data.filled(0) if False else np.ma.filled(tr.data.astype(float), np.nan)
    tr.data = tr.data.astype(float)
    nan = np.isnan(tr.data)
    if nan.any():
        tr.data[nan] = 0.0
    tr.detrend("demean")
    tr.remove_response(inventory=inv, output="DEF", pre_filt=(0.5, 1.0, 110.0, 120.0), water_level=None, zero_mean=True, taper=True, taper_fraction=0.02)
    ch = inv.get_channel_metadata(tr.id, tr.stats.starttime)
    unit = inv.select(station=tr.stats.station)[0][0][0].response.instrument_sensitivity.input_units
    return tr, dict(lat=ch["latitude"], lon=ch["longitude"], depth_m=-ch["elevation"], unit=unit, gap_samples=int(nan.sum()))

def bp(x, fs, lo, hi, order=4):
    sos = butter(order, [lo, hi], btype="band", fs=fs, output="sos"); return sosfiltfilt(sos, x)

def rms1(x, fs, w=1.0):
    n = int(w * fs); k = np.ones(n) / n
    return np.sqrt(np.convolve(x ** 2, k, mode="same"))

def band_exposure(x, fs, fcs=FC_ALL):
    """one-sided ESD by FFT of a Tukey(0.1)-tapered window, taper energy loss corrected; returns {fc: Pa^2 s}"""
    n = len(x); w = tukey(n, 0.1); corr = n / np.sum(w ** 2)
    X = np.fft.rfft(x * w) / fs; f = np.fft.rfftfreq(n, 1 / fs); df = f[1] - f[0]
    esd = 2 * np.abs(X) ** 2 * corr   # Pa^2 s / Hz, one-sided
    esd[0] /= 2
    out = {}
    for fc in fcs:
        lo, hi = band_edges(fc); m = (f >= lo) & (f < hi)
        out[fc] = float(np.sum(esd[m]) * df)
    return out, float(np.sum(esd) * df)

def db_esd(E, fc):
    lo, hi = band_edges(fc); return 10 * np.log10(max(E, 1e-30) / (hi - lo)) + 120.0

def baz_fit(traces, coords, fs, t_lo, t_hi, c_guess=1.48):
    """plane-wave fit to pair delays (cross-correlation, 4-40 Hz). traces: dict sta->array aligned on same start; t in samples."""
    stas = list(traces); lat0 = np.mean([coords[s]["lat"] for s in stas]); lon0 = np.mean([coords[s]["lon"] for s in stas])
    xy = {}
    for s in stas:
        az, _, d = G.inv(lon0, lat0, coords[s]["lon"], coords[s]["lat"]); xy[s] = (d * np.sin(np.radians(az)), d * np.cos(np.radians(az)))
    rows = []; dts = []; ccs = []
    maxlag = int(3.0 * fs)
    for i in range(len(stas)):
        for j in range(i + 1, len(stas)):
            a = traces[stas[i]][t_lo:t_hi]; b = traces[stas[j]][t_lo:t_hi]
            cc = np.correlate(b - b.mean(), a - a.mean(), mode="full"); mid = len(a) - 1
            seg = cc[mid - maxlag: mid + maxlag + 1]; k = int(np.argmax(seg))
            # parabolic refinement
            if 0 < k < len(seg) - 1:
                y0, y1, y2 = seg[k - 1], seg[k], seg[k + 1]; dk = 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2)
            else:
                dk = 0.0
            lag = (k - maxlag + dk) / fs
            norm = np.sqrt(np.sum((a - a.mean()) ** 2) * np.sum((b - b.mean()) ** 2))
            ccs.append(float(seg[k] / norm)); dts.append(lag)
            rows.append([xy[stas[j]][0] - xy[stas[i]][0], xy[stas[j]][1] - xy[stas[i]][1]])
    A = np.array(rows); d = np.array(dts)
    s, *_ = np.linalg.lstsq(A, d, rcond=None)     # t_j - t_i = s . (x_j - x_i)
    sx, sy = s; spd = 1.0 / np.hypot(sx, sy)
    prop_az = np.degrees(np.arctan2(sx, sy)) % 360   # direction of propagation
    baz = (prop_az + 180) % 360
    resid = d - A @ s
    return dict(baz_deg=float(baz), app_speed_km_s=float(spd / 1000), pair_cc=ccs, pair_lag_s=dts, resid_rms_s=float(np.sqrt(np.mean(resid ** 2))))
