"""Reference measurement for one hydrophone triad (DRAFT for Pete's review; brief section 9).
Input: an .npz with  t0_utc (ISO string), fs (Hz), x (3 x N pressure, Pa), lat, lon (3 element positions,
deg), and a window [w0_s, w1_s] (s from t0) plus a pre-event noise window [n0_s, n1_s].
Per band (4th-order Butterworth, zero phase): peak |p| (Pa), RMS (Pa), exposure (Pa^2 s) in the window;
noise RMS in the pre-event window; SNR = 20 log10(RMS_window / RMS_noise) (dB). Bearing: plane-wave fit to
the three inter-element delays from the cross-correlation of the band-passed window (parabolic sub-sample
peak); returns back-azimuth (deg from N, towards the source) and apparent speed (m/s). numpy+scipy only.
Usage: python reference_measure.py <input.npz> <w0_s> <w1_s> <n0_s> <n1_s> [out.csv]"""
import sys
import numpy as np
from scipy import signal

BANDS = [(2, 5), (5, 10), (10, 20), (20, 40), (5, 40)]
R_EARTH = 6371008.8


def enu(lat, lon):
    lat0, lon0 = np.mean(lat), np.mean(lon)
    e = np.radians(np.asarray(lon) - lon0) * R_EARTH * np.cos(np.radians(lat0))
    n = np.radians(np.asarray(lat) - lat0) * R_EARTH
    return np.c_[e, n]


def bandpass(x, fs, lo, hi):
    sos = signal.butter(4, [lo, min(hi, 0.45 * fs)], btype="bandpass", fs=fs, output="sos")
    return signal.sosfiltfilt(sos, x, axis=-1)


def delay(a, b, fs, max_lag):
    """Delay of b relative to a (s), positive when b arrives later."""
    c = signal.correlate(b, a, mode="full")
    lags = signal.correlation_lags(len(b), len(a), mode="full")
    m = np.abs(lags) <= max_lag * fs
    c, lags = c[m], lags[m]
    i = int(np.argmax(c))
    if 0 < i < len(c) - 1:                       # parabolic refinement
        d = (c[i - 1] - c[i + 1]) / (2 * (c[i - 1] - 2 * c[i] + c[i + 1]))
    else:
        d = 0.0
    return (lags[i] + d) / fs, float(c[i] / np.sqrt(np.sum(a * a) * np.sum(b * b)))


def plane_wave(xy, x, fs):
    """Slowness s (s/m) from tau_ij = s . (r_j - r_i); back-azimuth points to the source."""
    pairs = [(0, 1), (0, 2), (1, 2)]
    max_lag = np.max(np.linalg.norm(xy[:, None] - xy[None], axis=-1)) / 1300.0
    taus, ccs, G = [], [], []
    for i, j in pairs:
        t, cc = delay(x[i], x[j], fs, max_lag)
        taus.append(t); ccs.append(cc); G.append(xy[j] - xy[i])
    s, *_ = np.linalg.lstsq(np.array(G), np.array(taus), rcond=None)
    baz = np.degrees(np.arctan2(-s[0], -s[1])) % 360
    resid = np.array(taus) - np.array(G) @ s
    return baz, 1 / np.linalg.norm(s), float(np.min(ccs)), float(np.sqrt(np.mean(resid ** 2)))


def measure(d, w0, w1, n0, n1):
    fs, x = float(d["fs"]), np.asarray(d["x"], float)
    xy = enu(d["lat"], d["lon"])
    iw, inn = slice(int(w0 * fs), int(w1 * fs)), slice(int(n0 * fs), int(n1 * fs))
    rows = []
    for lo, hi in BANDS:
        y = bandpass(x, fs, lo, hi)
        yw, yn = y[:, iw], y[:, inn]
        rms, nrms = np.sqrt(np.mean(yw ** 2, 1)), np.sqrt(np.mean(yn ** 2, 1))
        baz, vapp, ccmin, rres = plane_wave(xy, yw, fs)
        rows.append(dict(band=f"{lo}-{hi}", peak_pa=float(np.abs(yw).max()), rms_pa=float(rms.mean()),
                         exposure_pa2s=float(np.mean(np.sum(yw ** 2, 1) / fs)), noise_rms_pa=float(nrms.mean()),
                         snr_db=float(20 * np.log10(rms.mean() / nrms.mean())), backazimuth_deg=float(baz),
                         apparent_speed_m_s=float(vapp), min_xcorr=ccmin, delay_resid_s=rres))
    return rows


if __name__ == "__main__":
    import csv
    d = np.load(sys.argv[1], allow_pickle=False)
    rows = measure(d, *map(float, sys.argv[2:6]))
    out = open(sys.argv[6], "w", newline="") if len(sys.argv) > 6 else sys.stdout
    w = csv.DictWriter(out, fieldnames=list(rows[0]))
    w.writeheader(); w.writerows(rows)
