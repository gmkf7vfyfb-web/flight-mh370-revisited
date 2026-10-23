"""Whale-call detectors for low-frequency (5-120 Hz) hydroacoustic spectrograms.

Reusable: the functions take a calibrated or uncalibrated spectrogram in dB (L[f, t]) with its frequency and time
axes, so they can run on IMOS raw-record spectrograms, on the deskstar spectrogram cubes, or on digitised
figure grids (with coarser resolution, see `min_res`).

Feature set
-----------
1. Tonal-track extraction (`tonal_tracks`): spectral peaks that stand >= `thr_db` above their +/-1.5 Hz flanks
   (flank contrast removes broadband transients such as impacts, airguns and ships' cavitation bursts), linked
   frame to frame into tracks. Per track: start, end, duration, f_start, f_end, f_mean, slope, mean contrast,
   harmonic support at 2f and 3f.
2. Track classification (`classify_tracks`) by published call descriptions (references in METHODS.md):
   - PB_SEIO_II  pygmy blue whale, south-east Indian Ocean ('Australian') song unit II: upsweep, fundamental
                 ~19.5-21.5 -> 22-24.5 Hz over 12-30 s, 3rd harmonic ~60-72 Hz (Gavrilov 2011; Jolliffe 2019).
   - PB_SEIO_III unit III: flat tone 17.3-19.8 Hz lasting >= 15 s (26-28 s typical) with harmonics.
   - PB_SEIO_I   unit I: tone 18.5-22 Hz lasting >= 15 s, flat or one upward step (~19 -> 21 Hz), slight pulsing.
   - ABW_Z_A     Antarctic blue whale Z-call unit A: flat tone 25.4-26.7 Hz (26.07-26.11 Hz daily means in week 10
                 of 2014, Leroy et al. SEANOE 51007), 4-15 s.
   - ABW_Z_C     Z-call unit C: tone 18-20.5 Hz, 4-15 s, starting <= 4 s after a unit A track ends.
   - OMURA_TONE  Omura's whale (Australian song, Leroy 2021 Fig. 6d): tone 24.6-25.6 Hz 1.5-6 s then 19.4-20.4 Hz.
   - CHAGOS_U1   'Chagos' pygmy blue song unit 1 subunit 3: down-tone ~31 -> 28 Hz, 3-9 s.
   - TONAL_LONG  any tone >= 60 s (ship or other persistent line) - not a whale class.
   - TONAL_OTHER any other track (unclassified).
3. Pulse detectors on a short-window spectrogram (`pulse_events`): band-energy excess with time-over-threshold
   limits; used for fin whale 20 Hz pulses (15-30 Hz, 0.4-2.5 s, flanks 35-45 Hz) with regular inter-pulse
   intervals (7-26 s, Watkins 1987; 12-15 s Southern Hemisphere) and optional 94-99 Hz upper component, and for
   Omura's whale noisy pulsed units (20-45 Hz, 2.5-9 s).
4. Song-level aggregation (`song_events`): unit detections are merged into phrase / call events, and inter-phrase
   intervals tested against published inter-song intervals (P3 170-200 s, P2 84-96 s, P1 45-49 s; Z-call ~60-70 s).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import ndimage

# ----------------------------------------------------------------------------------------------- normalisation

def noise_normalise(L, q=25):
    """Per-frequency noise floor = q-th percentile over time; returns L - floor (dB). q < 50 so that a record
    largely filled by song does not lift its own floor."""
    return L - np.percentile(L, q, axis=1, keepdims=True)


def flank_contrast(N, f, half_bw=0.35, flank=(0.9, 1.6)):
    """Peak-minus-flank contrast (dB): mean of N within +/-half_bw minus mean of N in the flank rings."""
    df = f[1] - f[0]
    k_in = max(1, int(round(half_bw / df)))
    k0, k1 = int(round(flank[0] / df)), int(round(flank[1] / df))
    lin = N
    c_in = ndimage.uniform_filter1d(lin, 2 * k_in + 1, axis=0, mode="nearest")
    # flanks: mean over [k0, k1] above and below
    up = np.zeros_like(lin)
    dn = np.zeros_like(lin)
    for k in range(k0, k1 + 1):
        up += np.roll(lin, -k, axis=0)
        dn += np.roll(lin, k, axis=0)
    n = k1 - k0 + 1
    fl = np.minimum(up, dn) / n          # the lower flank: robust when a neighbouring line sits on one side
    fl = np.maximum(fl, (up + dn) / (2 * n) - 3.0)
    C = c_in - fl
    C[:k1] = 0
    C[-k1:] = 0
    return C


# ----------------------------------------------------------------------------------------------- tonal tracks

def tonal_tracks(L, f, t, fband=(14.0, 34.0), thr_db=5.0, max_jump_hz=0.6, max_gap_frames=3, min_frames=4,
                 q=25):
    """Extract tonal tracks from spectrogram L (dB, [f, t]). Returns DataFrame of tracks."""
    N = noise_normalise(L, q)
    C = flank_contrast(N, f)
    fb = (f >= fband[0]) & (f <= fband[1])
    Cb, fbv = C[fb], f[fb]
    # local maxima along frequency above threshold
    mx = ndimage.maximum_filter1d(Cb, size=5, axis=0)
    pk = (Cb >= thr_db) & (Cb == mx)
    tracks = []          # each: list of (ti, f, contrast)
    active = []
    for ti in range(Cb.shape[1]):
        idx = np.flatnonzero(pk[:, ti])
        used = set()
        new_active = []
        for tr in active:
            last_ti, last_f = tr[-1][0], tr[-1][1]
            if ti - last_ti > max_gap_frames:
                tracks.append(tr)
                continue
            if len(idx):
                d = np.abs(fbv[idx] - last_f)
                j = int(np.argmin(d))
                if d[j] <= max_jump_hz * (ti - last_ti) and idx[j] not in used:
                    used.add(idx[j])
                    tr.append((ti, fbv[idx[j]], Cb[idx[j], ti]))
            new_active.append(tr)
        for i in idx:
            if i not in used:
                new_active.append([(ti, fbv[i], Cb[i, ti])])
        active = new_active
    tracks.extend(active)
    rows = []
    dt = t[1] - t[0]
    for tr in tracks:
        if len(tr) < min_frames:
            continue
        a = np.array(tr)
        ti, ff, cc = a[:, 0].astype(int), a[:, 1], a[:, 2]
        tt = t[ti]
        slope = np.polyfit(tt, ff, 1)[0] if len(tt) > 2 else 0.0
        n_edge = max(2, len(ff) // 5)
        # harmonic support: contrast at 2f and 3f along the track (nearest bin, +/-1 bin max)
        h = {}
        for m in (2, 3):
            fi = np.clip(np.searchsorted(f, m * ff), 1, len(f) - 2)
            ok = m * ff < f[-1] - 1
            if ok.sum() >= 2:
                v = np.max(np.stack([C[fi - 1, ti], C[fi, ti], C[fi + 1, ti]]), axis=0)[ok]
                h[m] = float(np.median(v))
            else:
                h[m] = np.nan
        rows.append(dict(t_start=float(tt[0] - dt / 2), t_end=float(tt[-1] + dt / 2), dur=float(tt[-1] - tt[0] + dt),
                         f_start=float(np.median(ff[:n_edge])), f_end=float(np.median(ff[-n_edge:])),
                         f_mean=float(ff.mean()), f_min=float(ff.min()), f_max=float(ff.max()), slope=float(slope),
                         contrast=float(cc.mean()), contrast_max=float(cc.max()), n=len(tr), h2=h[2], h3=h[3]))
    return pd.DataFrame(rows)


def merge_collinear(tr, max_gap_s=3.0, max_df=0.6):
    """Join tracks that continue one another (same frequency trend) after short drop-outs."""
    if tr.empty:
        return tr
    tr = tr.sort_values("t_start").reset_index(drop=True)
    keep = []
    used = np.zeros(len(tr), bool)
    for i in range(len(tr)):
        if used[i]:
            continue
        cur = tr.loc[i].to_dict()
        for j in range(i + 1, len(tr)):
            if used[j]:
                continue
            g = tr.at[j, "t_start"] - cur["t_end"]
            if g > max_gap_s:
                break
            if -1.0 <= g and abs(tr.at[j, "f_start"] - cur["f_end"]) <= max_df:
                o = tr.loc[j]
                w1, w2 = cur["n"], o["n"]
                cur.update(t_end=o["t_end"], dur=o["t_end"] - cur["t_start"], f_end=o["f_end"],
                           f_min=min(cur["f_min"], o["f_min"]), f_max=max(cur["f_max"], o["f_max"]),
                           f_mean=(cur["f_mean"] * w1 + o["f_mean"] * w2) / (w1 + w2),
                           contrast=(cur["contrast"] * w1 + o["contrast"] * w2) / (w1 + w2),
                           contrast_max=max(cur["contrast_max"], o["contrast_max"]), n=w1 + w2,
                           h2=np.nanmean([cur["h2"], o["h2"]]), h3=np.nanmean([cur["h3"], o["h3"]]))
                cur["slope"] = (cur["f_end"] - cur["f_start"]) / max(cur["dur"], 1e-6)
                used[j] = True
        keep.append(cur)
    return pd.DataFrame(keep)


# ----------------------------------------------------------------------------------------------- classification

def classify_tracks(tr):
    """Rule classification of tonal tracks. Adds columns cls, cls_score (0-1 rule fit)."""
    if tr.empty:
        tr = tr.copy()
        tr["cls"] = []
        tr["cls_score"] = []
        return tr
    tr = tr.copy()
    cls = np.array(["TONAL_OTHER"] * len(tr), dtype=object)
    sc = np.zeros(len(tr))
    d, fs_, fe, fm, sl, c, h3 = (tr[k].values for k in ["dur", "f_start", "f_end", "f_mean", "slope", "contrast", "h3"])
    rise = fe - fs_
    h3 = np.nan_to_num(h3, nan=0.0)
    # pygmy blue unit II
    m2 = (d >= 10) & (d <= 35) & (fs_ >= 19.0) & (fs_ <= 22.0) & (fe >= 21.8) & (fe <= 25.0) & (rise >= 1.2) & (rise <= 4.5)
    cls[m2], sc[m2] = "PB_SEIO_II", np.clip(0.5 + 0.05 * (c[m2] - 5) + 0.05 * h3[m2], 0, 1)
    # pygmy blue unit III (flat 17.3-19.8, long)
    m3 = (cls == "TONAL_OTHER") & (d >= 15) & (d <= 45) & (fm >= 17.3) & (fm <= 19.8) & (np.abs(rise) <= 1.0)
    cls[m3], sc[m3] = "PB_SEIO_III", np.clip(0.4 + 0.05 * (c[m3] - 5) + 0.01 * (d[m3] - 15), 0, 1)
    # pygmy blue unit I (19-22 Hz, long, flat or stepping up)
    m1 = (cls == "TONAL_OTHER") & (d >= 15) & (d <= 55) & (fm >= 18.8) & (fm <= 22.2) & (rise >= -0.5) & (rise <= 3.0)
    cls[m1], sc[m1] = "PB_SEIO_I", np.clip(0.35 + 0.05 * (c[m1] - 5) + 0.01 * (d[m1] - 15), 0, 1)
    # Antarctic blue whale Z unit A
    ma = (cls == "TONAL_OTHER") & (d >= 3.5) & (d <= 16) & (fm >= 25.4) & (fm <= 26.8) & (np.abs(rise) <= 0.8)
    cls[ma], sc[ma] = "ABW_Z_A", np.clip(0.4 + 0.05 * (c[ma] - 5), 0, 1)
    # Omura's whale tonal end (25 Hz part)
    mo = (cls == "TONAL_OTHER") & (d >= 1.5) & (d <= 6) & (fm >= 24.5) & (fm <= 25.7)
    cls[mo], sc[mo] = "OMURA_TONE", np.clip(0.3 + 0.05 * (c[mo] - 5), 0, 1)
    # Chagos unit 1 subunit 3 (down-tone ~31 -> 28)
    mc = (cls == "TONAL_OTHER") & (d >= 3) & (d <= 10) & (fs_ >= 28.5) & (fs_ <= 32) & (rise <= -0.8) & (rise >= -3.5)
    cls[mc], sc[mc] = "CHAGOS_U1", np.clip(0.3 + 0.05 * (c[mc] - 5), 0, 1)
    # long persistent tone
    ml = (d >= 60) & np.isin(cls, ["TONAL_OTHER", "PB_SEIO_I", "PB_SEIO_III"])
    cls[ml], sc[ml] = "TONAL_LONG", 0.0
    tr["cls"], tr["cls_score"] = cls, sc
    # Z-call unit C: 18-20.5 Hz tone starting within 4 s after an ABW_Z_A end
    a_end = tr.loc[tr.cls == "ABW_Z_A", "t_end"].values
    for i in np.flatnonzero((tr.cls.isin(["TONAL_OTHER", "PB_SEIO_III"])).values):
        r = tr.iloc[i]
        if 3.5 <= r.dur <= 16 and 18.0 <= r.f_mean <= 20.6 and len(a_end):
            g = r.t_start - a_end
            if np.any((g >= -1.5) & (g <= 4.5)):
                tr.iat[i, tr.columns.get_loc("cls")] = "ABW_Z_C"
                tr.iat[i, tr.columns.get_loc("cls_score")] = 0.7
    # Omura's: 19.4-20.4 tone right after OMURA_TONE
    o_end = tr.loc[tr.cls == "OMURA_TONE", "t_end"].values
    for i in np.flatnonzero((tr.cls == "TONAL_OTHER").values):
        r = tr.iloc[i]
        if 2 <= r.dur <= 9 and 19.3 <= r.f_mean <= 20.5 and len(o_end):
            g = r.t_start - o_end
            if np.any((g >= -1.5) & (g <= 2.5)):
                tr.iat[i, tr.columns.get_loc("cls")] = "OMURA_TONE_LOW"
                tr.iat[i, tr.columns.get_loc("cls_score")] = 0.6
    return tr


# ----------------------------------------------------------------------------------------------- pulses

def band_db(L, f, lo, hi):
    m = (f >= lo) & (f < hi)
    return 10 * np.log10(np.mean(10 ** (L[m] / 10), axis=0))


def pulse_events(Ls, fs_, ts_, band=(15, 30), flanks=((35, 45),), thr_db=4.0, min_dur=0.4, max_dur=2.5,
                 bg_win_s=30.0):
    """Short-window band-excess events. Excess = band level - max(flank levels) relative to its running median."""
    b = band_db(Ls, fs_, *band)
    fl = np.max(np.stack([band_db(Ls, fs_, *fb) for fb in flanks]), axis=0)
    x = b - fl
    dt = ts_[1] - ts_[0]
    w = max(3, int(bg_win_s / dt) | 1)
    x = x - ndimage.median_filter(x, size=w, mode="nearest")
    on = x >= thr_db
    lab, n = ndimage.label(on)
    rows = []
    for k in range(1, n + 1):
        ii = np.flatnonzero(lab == k)
        dur = (ii[-1] - ii[0] + 1) * dt
        if min_dur <= dur <= max_dur:
            j = ii[np.argmax(x[ii])]
            rows.append(dict(t_peak=float(ts_[j]), dur=float(dur), excess_db=float(x[j]), level_db=float(b[j])))
    return pd.DataFrame(rows), x


def regular_train(tp, ipi_range=(7.0, 26.0), tol=1.5, min_pulses=4):
    """Find runs of pulses with near-constant inter-pulse interval. Returns list of (i_start, i_end, ipi)."""
    tp = np.sort(np.asarray(tp))
    out = []
    if len(tp) < min_pulses:
        return out
    d = np.diff(tp)
    i = 0
    while i < len(d):
        if ipi_range[0] <= d[i] <= ipi_range[1]:
            j = i
            ref = d[i]
            while j + 1 < len(d) and abs(d[j + 1] - ref) <= tol:
                j += 1
                ref = np.median(d[i:j + 1])
            if j - i + 2 >= min_pulses:
                out.append((i, j + 1, float(np.median(d[i:j + 1]))))
            i = j + 1
        else:
            i += 1
    return out


# ----------------------------------------------------------------------------------------------- song level

ISI = {"PB_SEIO_P3": (165, 210), "PB_SEIO_P2": (80, 100), "PB_SEIO_P1": (43, 52), "ABW_Z": (55, 80)}


def periodicity_support(times, rng):
    """Fraction of events that have a neighbour (same class) at an interval inside rng (or 2x rng)."""
    times = np.sort(np.asarray(times))
    if len(times) < 2:
        return 0.0
    ok = 0
    for ti in times:
        d = np.abs(times - ti)
        if np.any(((d >= rng[0]) & (d <= rng[1])) | ((d >= 2 * rng[0]) & (d <= 2 * rng[1]))):
            ok += 1
    return ok / len(times)


# ----------------------------------------------------------------------------------------------- template (kernel) detectors

def smoothed_contrast(L, f, t, q=25, t_smooth_s=2.5, half_bw=0.35, flank=(0.9, 1.6)):
    """Flank-contrast map (dB) of the noise-normalised spectrogram after linear averaging over t_smooth_s.
    Averaging reduces the per-bin chi-square scatter (about 5.6 dB s.d. for a single Hann frame)."""
    N = noise_normalise(L, q)
    dt = t[1] - t[0]
    k = max(1, int(round(t_smooth_s / dt)))
    Nl = ndimage.uniform_filter1d(10 ** (N / 10), k, axis=1, mode="nearest")
    return flank_contrast(10 * np.log10(np.maximum(Nl, 1e-12)), f, half_bw=half_bw, flank=flank)


def contour_score(C, f, t, segs, harmonics=(1,), weights=None, return_min=False):
    """Mean contrast along a piecewise-linear contour, per component (segment x harmonic).
    segs: list of (t_rel_start, t_rel_end, f_start, f_end) in s and Hz (fundamental).
    Returns score[t_index] (weighted mean of component means) for templates anchored at frame index (contour
    start); with return_min=True also the minimum component mean (all parts of a multi-part call must be present)."""
    dt = t[1] - t[0]
    weights = list(weights or [1.0] * len(harmonics))
    comps = []
    K = 0
    for (a, b, fa, fb) in segs:
        kk = np.arange(int(round(a / dt)), int(round(b / dt)) + 1)
        K = max(K, kk.max() + 1)
        ff = fa + (fb - fa) * (kk * dt - a) / max(b - a, 1e-9)
        for h, w in zip(harmonics, weights):
            fh = h * ff
            ok = (fh > f[0] + 1.7) & (fh < f[-1] - 1.7)
            if ok.sum() >= 2:
                comps.append((kk[ok], np.searchsorted(f, fh[ok]), w))
    T = C.shape[1] - K
    s = np.full(C.shape[1], np.nan)
    smin = np.full(C.shape[1], np.nan)
    if T <= 0 or not comps:
        return (s, smin) if return_min else s
    means, ws = [], []
    for kk, fi, w in comps:
        idx_t = kk[:, None] + np.arange(T)[None, :]
        means.append(C[fi[:, None], idx_t].mean(0))
        ws.append(w)
    M = np.array(means)
    W = np.array(ws)[:, None]
    s[:T] = (W * M).sum(0) / W.sum()
    smin[:T] = M.min(0)
    return (s, smin) if return_min else s


def template_bank(year=2014.2):
    """Templates (fundamental contours) from the published call descriptions, frequencies set for March 2014.
    Grids span the reported variability; each entry: name, list of variants (segs, harmonics, weights, duration)."""
    bank = {}
    v = []
    for fa in np.arange(19.5, 21.51, 0.25):                       # PB unit II: upsweep
        for rise in (2.0, 2.75, 3.5):
            for D in (18.0, 23.0, 28.0):
                v.append(([(0, D, fa, fa + rise)], (1, 3), (1.0, 1.0), D))
    bank["PB_SEIO_II"] = v
    v = []
    for fa in np.arange(17.25, 19.76, 0.25):                      # PB unit III: flat tone, harmonics strong
        v.append(([(0, 22.0, fa, fa)], (1, 2, 3), (1.0, 0.7, 0.7), 22.0))
    bank["PB_SEIO_III"] = v
    v = []
    for fa in np.arange(18.5, 20.01, 0.25):                       # PB unit I: tone then ~ +1.5 Hz step
        for step in (1.0, 1.75):
            v.append(([(0, 18.0, fa, fa), (19.0, 38.0, fa + step, fa + step)], (1, 2), (1.0, 0.7), 38.0))
    bank["PB_SEIO_I"] = v
    v = []
    for fa in np.arange(25.75, 26.46, 0.15):                      # ABW Z-call: A 8 s, sweep 1.5 s, B 8 s
        for fb in (18.5, 19.0):
            v.append(([(0, 8.0, fa, fa - 0.1), (8.0, 9.5, fa - 0.1, fb + 0.3), (9.5, 17.5, fb + 0.3, fb)], (1,), (1.0,), 17.5))
    bank["ABW_Z"] = v
    v = []
    for fa in np.arange(24.75, 25.51, 0.25):                      # Omura's (Australian song) tonal end, z-shape
        v.append(([(0, 3.3, fa, fa - 0.1), (3.5, 8.4, 19.8, 19.8)], (1,), (1.0,), 8.4))
    bank["OMURA_TONE"] = v
    v = []
    for fa in np.arange(29.5, 31.01, 0.5):                        # Chagos unit 1 subunit 3 + unit 2 (22.3 + ~1 Hz in 2014)
        v.append(([(0, 3.5, fa, fa - 0.2), (3.5, 6.5, fa - 0.2, fa - 1.9), (9.5, 12.7, 23.0, 23.0)], (1,), (1.0,), 12.7))
    bank["CHAGOS"] = v
    v = []
    for fa in np.arange(33.5, 34.31, 0.2):                         # Madagascan pygmy blue unit 1 (35 Hz unit; 33.9 Hz
        v.append(([(0, 12.0, fa, fa + 0.3)], (1,), (1.0,), 12.0))   # weekly mean in March 2014, SEANOE 51007)
    bank["PB_SWIO_U1"] = v
    return bank


NULL_SHIFT_HZ = {"PB_SEIO_II": None, "PB_SEIO_III": +13.0, "PB_SEIO_I": +12.0, "ABW_Z": None,
                 "OMURA_TONE": +8.0, "CHAGOS": +9.0, "PB_SWIO_U1": -5.5}


def mirrored(segs, D):
    """Time-reversed contour (null template): same shape statistics, physically not a call of the target type."""
    return [(D - b, D - a, fb, fa) for (a, b, fa, fb) in segs]


def shifted(segs, df):
    return [(a, b, fa + df, fb + df) for (a, b, fa, fb) in segs]


def run_templates(L, f, t, bank=None, null=False, min_comp_db=1.5, contrast_kw=None):
    """Best score over each template family per frame (anchor = call start). A template variant counts only where
    its weakest component mean >= min_comp_db. With null=True the null-template family is used instead
    (time-reversed contour for swept calls; frequency-shifted contour for flat tones).
    Returns {name: (score, variant_index)}, contrast map C."""
    bank = bank or template_bank()
    C = smoothed_contrast(L, f, t, **(contrast_kw or {}))
    out = {}
    for name, variants in bank.items():
        best = np.full(C.shape[1], -np.inf)
        arg = np.zeros(C.shape[1], int)
        for i, (segs, harm, w, D) in enumerate(variants):
            if null:
                sh = NULL_SHIFT_HZ.get(name)
                segs = mirrored(segs, D) if sh is None else shifted(segs, sh)
            s, smin = contour_score(C, f, t, segs, harm, list(w), return_min=True)
            s = np.where(np.nan_to_num(smin, nan=-np.inf) >= min_comp_db, s, -np.inf)
            s = np.nan_to_num(s, nan=-np.inf)
            upd = s > best
            best[upd] = s[upd]
            arg[upd] = i
        out[name] = (best, arg)
    return out, C


def peaks_from_score(score, t, thr, min_sep_s):
    """Non-maximum suppression: local maxima above thr separated by >= min_sep_s."""
    dt = t[1] - t[0]
    w = max(1, int(round(min_sep_s / dt)))
    mx = ndimage.maximum_filter1d(np.where(np.isfinite(score), score, -np.inf), 2 * w + 1, mode="nearest")
    ii = np.flatnonzero((score >= thr) & (score == mx) & np.isfinite(score))
    keep = []
    for i in ii:
        if not keep or i - keep[-1] >= w:
            keep.append(i)
    return np.array(keep, int)
