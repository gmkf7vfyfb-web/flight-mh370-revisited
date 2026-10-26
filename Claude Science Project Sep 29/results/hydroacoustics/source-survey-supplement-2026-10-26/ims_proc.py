"""Process one IMS hydrophone triplet-day (EarthScope FDSN, net IM, EDH, 250 Hz) into a compact derived product.

Steps (all per station-day, 00:00-24:00 UTC):
 1. Read the three elements, merge, remove the full StationXML response (obspy, output DEF = Pa; pre_filt
    0.3/0.5/110/120 Hz; taper 0.05 % of each contiguous segment). Gaps stay NaN; 60 s at each gap edge -> NaN.
 2. NOISE: per element, per UTC minute without NaN: Welch PSD (Hann, 4 s segments, 50 % overlap, 0.25 Hz bins),
    averaged to 1 Hz bins centred 1..100 Hz; third-octave band levels (base-10 centres 2-80 Hz) and the 5-40 Hz
    band SPL integrated from the 0.25 Hz PSD. Units dB re 1 uPa^2/Hz (PSD) and dB re 1 uPa (band SPL).
 3. DETECTION on the reference element (element 1, else the first with data):
      D1_540: 5-40 Hz Butterworth-4 zero-phase band-pass -> 100 Hz -> energy STA 2 s / LTA 30 s, hop 0.1 s
              (registered run J D1, IMOS path, preregistration.py s.3-4).
      M1b   : 10 Hz envelope (0.5 s smoothing) of the 5-40 Hz 100 Hz series -> envelope matched filter, the
              registered 18-template bank (ranges 1800-3703.5 km x tau 0.1/1/10 s, templates_raw.npz).
      D1_28 : 2-8 Hz band-pass -> 25 Hz -> STA 2 s / LTA 30 s, hop 0.1 s (not registered; brief item 4).
    Window score = max of the statistic in non-overlapping 55 s windows from 32 s after 00:00 (registered rule).
    A window is invalid if any NaN lies in [start-35 s, end+60 s] of the reference element.
 4. FEATURES at the time of each window maximum, in the statistic's band: triplet plane-wave fit on
    cross-correlation lags (back-azimuth, apparent speed, closure, min CC), SNR (1 s power, peak in +-3 s over the
    median of the preceding 60 s), duration above +3 dB, peak excess frequency (2-100 Hz), envelope periodicity
    (autocorrelation peak at 5-15 s and at 40-200 s lag over +-300 s).
"""
from __future__ import annotations
import json, sys, numpy as np, pandas as pd
from pathlib import Path
from scipy import signal
from obspy import read, UTCDateTime

FS = 250.0
NDAY = int(86400 * FS)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import m1b_bank as MB

PRE_FILT = (0.3, 0.5, 110.0, 120.0)
SOS540 = signal.butter(4, [5.0, 40.0], btype="bandpass", fs=FS, output="sos")
SOS28 = signal.butter(4, [2.0, 8.0], btype="bandpass", fs=FS, output="sos")
TO_C = np.array([2, 2.5, 3.15, 4, 5, 6.3, 8, 10, 12.5, 16, 20, 25, 31.5, 40, 50, 63, 80])
TO_LO, TO_HI = TO_C * 10 ** (-0.05), TO_C * 10 ** (0.05)
WIN_S, WARM_S = 55.0, 32.0
NWIN = int((86400 - WARM_S) // WIN_S)
ELEM = json.load(open(HERE.parent / "meta" / "elements.json"))   # name -> (lat, lon, depth_m)


def enu(names):
    lat0 = np.mean([ELEM[n][0] for n in names]); lon0 = np.mean([ELEM[n][1] for n in names])
    a, e2 = 6378137.0, 6.69437999014e-3
    s = np.sin(np.radians(lat0)); N = a / np.sqrt(1 - e2 * s * s); M = a * (1 - e2) / (1 - e2 * s * s) ** 1.5
    return np.array([[np.radians(ELEM[n][1] - lon0) * N * np.cos(np.radians(lat0)), np.radians(ELEM[n][0] - lat0) * M] for n in names])


def load_day(files: dict, day: str, inv):
    """files: element -> path. Returns dict element -> (x Pa float64 with NaN, frac_offset_s), and gap summary."""
    d0 = UTCDateTime(day)
    out, info = {}, {}
    for el, fp in files.items():
        try:
            st = read(str(fp))
        except Exception as ex:
            info[el] = f"read_error:{ex}"; continue
        st = st.select(channel="EDH")
        st.merge(method=1, fill_value=None)
        st = st.split()
        x = np.full(NDAY, np.nan)
        offs = []
        for tr in st:
            if tr.stats.npts < FS * 300:
                continue
            tr.data = tr.data.astype(np.float64)
            tr.remove_response(inventory=inv, output="DEF", pre_filt=PRE_FILT, water_level=None, zero_mean=True,
                               taper=True, taper_fraction=0.0005)
            i0f = (tr.stats.starttime - d0) * FS
            i0 = int(round(i0f)); offs.append((i0f - i0) / FS)
            a, b = max(i0, 0), min(i0 + tr.stats.npts, NDAY)
            if b <= a:
                continue
            seg = tr.data[a - i0: b - i0].copy()
            e = int(60 * FS)
            seg[:e] = np.nan; seg[-e:] = np.nan     # taper / edge guard
            x[a:b] = seg
        if np.isfinite(x).any():
            out[el] = (x, float(np.median(offs)) if offs else 0.0)
            info[el] = f"ok:{np.isfinite(x).mean():.4f}"
        else:
            info[el] = "no_data"
    return out, info


def noise_minutes(x):
    """Per-minute 1-Hz PSD (1..100 Hz), third-octave band levels, 5-40 Hz SPL; NaN minutes stay NaN."""
    X = x.reshape(1440, int(60 * FS))
    ok = np.isfinite(X).all(1)
    P1 = np.full((1440, 100), np.nan, np.float32); TO = np.full((1440, len(TO_C)), np.nan, np.float32)
    SPL = np.full(1440, np.nan, np.float32)
    if ok.any():
        f, P = signal.welch(X[ok], fs=FS, window="hann", nperseg=1000, noverlap=500, detrend="constant", axis=1)
        df = f[1] - f[0]
        db = lambda p: 10 * np.log10(np.maximum(p, 1e-30) / 1e-12)
        # 1 Hz bins centred on k Hz: f in [k-0.5, k+0.5)
        P1k = np.stack([P[:, (f >= k - 0.5) & (f < k + 0.5)].mean(1) for k in range(1, 101)], 1)
        P1[ok] = db(P1k)
        for j, (lo, hi) in enumerate(zip(TO_LO, TO_HI)):
            m = (f >= lo) & (f < hi)
            TO[ok, j] = db(P[:, m].sum(1) * df)
        m = (f >= 5) & (f < 40)
        SPL[ok] = db(P[:, m].sum(1) * df)
    return P1, TO, SPL, ok


def stalta(x, fs, sta_s=2.0, lta_s=30.0, hop_s=0.1):
    y = np.nan_to_num(np.asarray(x, float)) ** 2
    cs = np.concatenate([[0.0], np.cumsum(y)])
    sta, lta, hop = int(sta_s * fs), int(lta_s * fs), max(int(hop_s * fs), 1)
    i = np.arange(lta, len(y) - sta + 1, hop)
    s = ((cs[i + sta] - cs[i]) / sta) / np.maximum((cs[i] - cs[i - lta]) / lta, 1e-30)
    return (i + sta / 2) / fs, s


def window_max(t, s):
    k = np.floor((t - WARM_S) / WIN_S).astype(int)
    m = (k >= 0) & (k < NWIN) & np.isfinite(s)
    k, tt, ss = k[m], t[m], s[m]
    o = np.lexsort((-ss, k))
    k, tt, ss = k[o], tt[o], ss[o]
    first = np.r_[True, k[1:] != k[:-1]]
    sc = np.full(NWIN, np.nan); tm = np.full(NWIN, np.nan)
    sc[k[first]] = ss[first]; tm[k[first]] = tt[first]
    return sc, tm


def xcorr_lag(a, b, maxlag):
    """lag (samples, float) maximising sum a[n+k] b[n] -> tau_a - tau_b = k/fs; and normalised CC."""
    n = len(a)
    A = np.fft.rfft(a, 2 * n); B = np.fft.rfft(b, 2 * n)
    c = np.fft.irfft(A * np.conj(B), 2 * n)
    c = np.r_[c[-maxlag:], c[:maxlag + 1]]
    nrm = np.sqrt(np.sum(a * a) * np.sum(b * b)) + 1e-30
    j = int(np.argmax(c)); k = j - maxlag
    if 0 < j < len(c) - 1:
        y0, y1, y2 = c[j - 1], c[j], c[j + 1]
        den = y0 - 2 * y1 + y2
        k = k + (0.5 * (y0 - y2) / den if den != 0 else 0.0)
    return k, c[j] / nrm


def plane_fit(segs, offs, xy, fs):
    """segs: list of 3 band-passed arrays (same sample grid); xy: 3x2 m. Returns baz, v_app, closure_s, cc_min."""
    pairs = [(0, 1), (1, 2), (2, 0)]
    maxlag = int(np.ceil((np.max(np.linalg.norm(xy[:, None] - xy[None], axis=2)) / 1200.0 + 0.1) * fs))
    taus, ccs = [], []
    for i, j in pairs:
        k, cc = xcorr_lag(segs[i], segs[j], maxlag)
        taus.append(k / fs + (offs[i] - offs[j])); ccs.append(cc)
    taus = np.array(taus)
    closure = float(taus.sum())
    D = np.array([xy[i] - xy[j] for i, j in pairs])       # tau_i - tau_j = s . (r_i - r_j)
    s, *_ = np.linalg.lstsq(D, taus, rcond=None)
    sn = np.linalg.norm(s)
    baz = float(np.degrees(np.arctan2(-s[0], -s[1])) % 360)   # direction toward the source
    return baz, float(1.0 / sn / 1000.0) if sn > 0 else np.inf, closure, float(np.min(ccs))


def features(t, band, refx, trip, offs, xy, fs_b):
    """band: '540' or '28'. refx: dict of band-passed decimated reference series; trip: list of 3 band-passed 250 Hz arrays."""
    out = {}
    # bearing
    if trip is not None:
        pre, post = (2.0, 4.0) if band == "540" else (3.0, 7.0)
        a, b = int((t - pre) * FS), int((t + post) * FS)
        if a > 0 and b < NDAY:
            segs = [s[a:b] for s in trip]
            if all(np.isfinite(sg).all() for sg in segs):
                segs = [sg * signal.windows.tukey(len(sg), 0.2) for sg in segs]
                out["baz"], out["v_app_kms"], out["closure_s"], out["cc_min"] = plane_fit(segs, offs, xy, FS)
    # SNR, duration, periodicity from 1 s power and 10 Hz envelope of the band series
    xb, fsb = refx["x"], fs_b
    p1 = refx["p1"]                        # 1 s mean power, 1 Hz sampling
    i = int(t)
    if 63 <= i < len(p1) - 300:
        bg = np.nanmedian(p1[i - 63:i - 3])
        pk = np.nanmax(p1[i - 3:i + 4])
        out["snr_db"] = float(10 * np.log10(pk / bg)) if bg > 0 else np.nan
        ip = i - 3 + int(np.nanargmax(p1[i - 3:i + 4]))
        thr = 2.0 * bg
        lo = ip
        while lo > ip - 300 and p1[lo - 1] > thr: lo -= 1
        hi = ip
        while hi < min(ip + 300, len(p1) - 1) and p1[hi + 1] > thr: hi += 1
        out["dur_s"] = float(hi - lo + 1)
    e10 = refx["e10"]
    j = int(t * 10)
    if 3000 <= j < len(e10) - 3000:
        seg = np.log10(np.maximum(e10[j - 3000:j + 3000], 1e-30))
        seg = seg - signal.medfilt(seg, 601) if False else seg - np.convolve(seg, np.ones(601) / 601, "same")
        seg = seg[300:-300] - seg[300:-300].mean()
        n = len(seg)
        F = np.fft.rfft(seg, 2 * n); ac = np.fft.irfft(F * np.conj(F))[:n]; ac = ac / ac[0]
        for key, lo, hi in (("per_10s", 50, 150), ("per_song", 400, 2000)):
            pk, _ = signal.find_peaks(ac[lo - 1:hi + 2])
            pk = pk + lo - 1
            pk = pk[(pk >= lo) & (pk <= hi)]
            if len(pk):
                j0 = pk[np.argmax(ac[pk])]
                prom = ac[j0] - ac[max(j0 // 2, 1):j0].min()     # height above the trough between lag/2 and the peak
                out[f"{key}_lag"] = float(j0 / 10); out[f"{key}_ac"] = float(ac[j0]); out[f"{key}_prom"] = float(prom)
    # peak excess frequency on the raw (response-removed) reference trace
    raw = refx["raw"]
    a, b, c0 = int((t - 2) * FS), int((t + 4) * FS), int((t - 62) * FS)
    if c0 > 0 and b < NDAY:
        s1, s0 = raw[a:b], raw[c0:a]
        if np.isfinite(s1).all() and np.isfinite(s0).all():
            f, P1 = signal.welch(s1, fs=FS, nperseg=250); _, P0 = signal.welch(s0, fs=FS, nperseg=250)
            m = (f >= 2) & (f <= 100)
            r = P1[m] / np.maximum(P0[m], 1e-30)
            out["fpk_hz"] = float(f[m][np.argmax(r)]); out["fpk_excess_db"] = float(10 * np.log10(r.max()))
    return out


def envelope(x, fs, smooth_s=0.5, out_fs=10):
    e = np.asarray(x, float) ** 2
    k = max(int(smooth_s * fs), 1)
    e = signal.fftconvolve(e, np.ones(k) / k, "same")
    d = int(fs // out_fs); n = len(e) // d
    return e[: n * d].reshape(n, d).mean(1)


def process_day(station: str, day: str, files: dict, inv, bank):
    data, info = load_day(files, day, inv)
    els = [f"{station}{i}" for i in (1, 2, 3)]
    res = {"station": station, "day": day, "info": info}
    noise = {}
    for el in els:
        if el in data:
            noise[el] = noise_minutes(data[el][0])
    ref = next((e for e in els if e in data), None)
    res["ref"] = ref
    if ref is None:
        return res, noise, None
    x0 = data[ref][0]
    nanmask = ~np.isfinite(x0)
    trip_ok = all(e in data for e in els)
    xy = enu(els)
    offs = [data[e][1] if e in data else 0.0 for e in els]
    rows = []
    for band, sos, fsd in (("540", SOS540, 100), ("28", SOS28, 25)):
        bp = {e: signal.sosfiltfilt(sos, np.nan_to_num(data[e][0])) for e in els if e in data}
        for e in bp:
            bp[e][~np.isfinite(data[e][0])] = np.nan
        xr = bp[ref]
        xd = signal.resample_poly(np.nan_to_num(xr), int(fsd), int(FS)) if fsd == 100 else signal.resample_poly(np.nan_to_num(xr), 1, 10)
        p1 = np.nan_to_num(xr).reshape(86400, int(FS)); p1 = (p1 ** 2).mean(1)
        e10 = envelope(xd, fsd)
        refx = {"x": xd, "p1": p1, "e10": e10, "raw": x0}
        stats = {}
        t, s = stalta(xd, fsd); stats[f"D1_{band}"] = (t, s)
        if band == "540":
            stats["M1b"] = MB.m1b_env(e10, bank)
        trip = [bp[e] for e in els] if trip_ok else None
        # invalid windows: NaN in [start-35, end+60] (LTA, template length)
        nan_s = nanmask.reshape(86400, int(FS)).any(1)
        cs = np.r_[0, np.cumsum(nan_s)]
        for name, (t, s) in stats.items():
            sc, tm = window_max(t, s)
            for k in range(NWIN):
                a = WARM_S + k * WIN_S
                lo, hi = max(int(a - 35), 0), min(int(a + WIN_S + 60), 86400)
                valid = (cs[hi] - cs[lo]) == 0 and np.isfinite(sc[k])
                r = {"station": station, "day": day, "stat": name, "win": k, "win_start_s": a, "score": sc[k], "t_max_s": tm[k], "valid": bool(valid), "ref": ref}
                if valid:
                    r.update(features(tm[k], band, refx, trip, offs, xy, fsd))
                rows.append(r)
        del bp
    return res, noise, pd.DataFrame(rows)
