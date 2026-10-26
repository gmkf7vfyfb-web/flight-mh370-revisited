"""Derived metrics for the Metz 2023 F-35A records: near field (Fig. 2, this digitisation) and far field (Fig. 3, the
project's digitisation, results-data/digitised/metz2023). Same functions for both, so near and far are comparable.
Envelope conventions follow prepare/metz_f35a/obs.py (noise = median outside +/-8 s of the peak; arrival = L > noise+1 dB;
-3/-6/-10 dB widths; 5-95 % span of the noise-subtracted energy). Additions: onset, rise time, decay rate, sub-event
peaks, spectral slope (dB/octave, third-octave bands 5-40 Hz), the 18-24 Hz gap, per-band timing.
Usage: python derive_nearfield.py <near_dir> <far_digitised_dir> <out_dir>
"""
import sys, json, pathlib
import numpy as np, pandas as pd
from scipy.signal import find_peaks

near, far, out = map(pathlib.Path, sys.argv[1:4]); out.mkdir(parents=True, exist_ok=True)
NOISE_EXCL_S, ARR_DB = 8.0, 1.0
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
RANGE_KM = {"DSOH": 180.0, "KSP1": 184.6, "KSP2": 243.7, "KSP3": 255.0, "H11N": 3249.0, "H11S": 3341.0}  # KSP1/2 from the solved point

def env_metrics(t, L, dt):
    ipk = int(np.argmax(L)); tpk = t[ipk]
    outm = (t < tpk - NOISE_EXCL_S) | (t > tpk + NOISE_EXCL_S); Ln = float(np.median(L[outm]))
    a = ipk
    while a > 0 and L[a - 1] > Ln + ARR_DB: a -= 1
    b = ipk
    while b < len(L) - 1 and L[b + 1] > Ln + ARR_DB: b += 1
    def width(drop):
        thr = L[ipk] - drop; i = ipk; j = ipk
        while i > 0 and L[i - 1] >= thr: i -= 1
        while j < len(L) - 1 and L[j + 1] >= thr: j += 1
        return float(t[j] - t[i] + dt)
    ex = np.clip(10 ** (L / 10) - 10 ** (Ln / 10), 0, None); w = np.zeros_like(ex); w[a:b + 1] = ex[a:b + 1]
    se = float(w.sum() * dt * 1e-12); c = np.cumsum(w) / w.sum()
    t05, t95 = float(np.interp(0.05, c, t)), float(np.interp(0.95, c, t))
    # onset: last sample before the peak at or below noise + 3 dB
    i3 = ipk
    while i3 > 0 and L[i3] > Ln + 3.0: i3 -= 1
    t_on = float(t[i3])
    # pre-onset noise (second definition): median of the 4 s that end 1 s before onset
    pre = (t >= t_on - 5.0) & (t < t_on - 1.0); Ln_pre = float(np.median(L[pre])) if pre.sum() > 10 else np.nan
    # rise: onset -> first sample >= peak - 3 dB; 10-90 % of the excess power to the first such sample
    j = i3
    while L[j] < L[ipk] - 3.0: j += 1
    rise_3 = float(t[j] - t_on)
    seg = ex[i3:j + 1]; top = seg.max()
    r10 = float(t[i3 + np.argmax(seg >= 0.1 * top)]); r90 = float(t[i3 + np.argmax(seg >= 0.9 * top)])
    # decay after the peak: slope of L (dB/s) while L > noise + 3 dB
    k = ipk
    while k < len(L) - 1 and L[k + 1] > Ln + 3.0: k += 1
    dec = np.polyfit(t[ipk:k + 1] - t[ipk], L[ipk:k + 1], 1)[0] if k - ipk > 10 else np.nan
    end3 = float(t[k])
    pk, pr = find_peaks(L[a:b + 1], prominence=2.0)
    subs = [dict(t_rel_onset_s=float(t[a + p] - t_on), level_db=float(L[a + p]), prominence_db=float(pr["prominences"][n])) for n, p in enumerate(pk)]
    return dict(peak_db=float(L[ipk]), peak_utc_s=float(tpk), noise_db=Ln, noise_pre_onset_db=Ln_pre, snr_peak_db=float(L[ipk] - Ln),
                snr_peak_pre_onset_db=float(L[ipk] - Ln_pre), onset_utc_s=t_on, arr_len_s=float(t[b] - t[a] + dt),
                above3_len_s=end3 - t_on, w3_s=width(3), w6_s=width(6), w10_s=width(10), span_5_95_s=t95 - t05, t05_rel_onset_s=t05 - t_on,
                t95_rel_onset_s=t95 - t_on, se_pa2s=se, sel_db=float(10 * np.log10(se / 1e-12)), rise_onset_to_peak3_s=rise_3,
                rise_10_90_s=r90 - r10, peak_rel_onset_s=float(tpk - t_on), decay_db_per_s=float(dec), n_subpeaks_2db=len(subs), subpeaks=subs,
                window=(float(t[a]), float(t[b])))

def spec_metrics(P, tt, ff, win, floor_fill):
    lin = 10 ** (np.where(np.isfinite(P), P, floor_fill) / 10)
    inw = (tt >= win[0]) & (tt <= win[1]); nzw = (tt < win[0] - 1.0) | (tt > win[1] + 1.0)
    S = lin[:, inw].mean(1); N = np.median(lin[:, nzw], axis=1) if nzw.sum() > 5 else np.full(len(ff), np.nan)
    X = np.clip(S - N, 0, None)
    rows = []
    for fc in BANDS:
        lo, hi = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6); m = (ff >= lo) & (ff < hi)
        frac = float(np.isfinite(P[m][:, inw]).mean())
        rows.append(dict(fc_hz=fc, sig_psd_db=10 * np.log10(S[m].mean()), noise_psd_db=10 * np.log10(N[m].mean()),
                         excess_psd_db=10 * np.log10(max(X[m].mean(), 1e-3)), frac_above_floor=frac))
    B = pd.DataFrame(rows)
    def slope(col, fmin=4.0, fmax=41.0, need=None):
        g = B[(B.fc_hz >= fmin) & (B.fc_hz <= fmax)]
        if need is not None: g = g[g.sig_psd_db - g.noise_psd_db >= need]
        if len(g) < 3: return np.nan, np.nan, len(g)
        x = np.log2(g.fc_hz.values); y = g[col].values; A = np.vstack([np.ones_like(x), x]).T
        c, *_ = np.linalg.lstsq(A, y, rcond=None); r = y - A @ c
        se = np.sqrt(np.sum(r ** 2) / max(len(y) - 2, 1) * np.linalg.inv(A.T @ A)[1, 1]); return float(c[1]), float(se), len(g)
    s_sig = slope("sig_psd_db"); s_exc = slope("excess_psd_db", need=3.0); s_lo = slope("sig_psd_db", 4.0, 17.0)
    band = lambda lo, hi: float(10 * np.log10(S[(ff >= lo) & (ff < hi)].mean()))
    gap = dict(psd_12_17=band(12, 17), psd_18_24=band(18, 24), psd_26_34=band(26, 34), psd_34_40=band(34, 40))
    gap["gap_depth_db"] = float(0.5 * (gap["psd_12_17"] + gap["psd_26_34"]) - gap["psd_18_24"])
    # per-band timing (excess energy per column)
    tim = {}
    for name, lo, hi in (("4-10", 4, 10), ("10-17", 10, 17), ("18-24", 18, 24), ("25-40", 25, 40)):
        m = (ff >= lo) & (ff < hi); e = np.clip(lin[m].mean(0) - np.median(lin[m][:, nzw], axis=1).mean(), 0, None) if nzw.sum() > 5 else lin[m].mean(0)
        e = np.where(inw | ((tt > win[0] - 2) & (tt < win[1] + 2)), e, 0.0)
        if e.sum() <= 0: tim[name] = dict(); continue
        c = np.cumsum(e) / e.sum()
        tim[name] = dict(t05=float(np.interp(0.05, c, tt)), t50=float(np.interp(0.5, c, tt)), t95=float(np.interp(0.95, c, tt)),
                         centroid=float((e * tt).sum() / e.sum()), share_of_4_40=float(e.sum()))
    tot = sum(v.get("share_of_4_40", 0) for v in tim.values())
    for v in tim.values():
        if v: v["share_of_4_40"] /= tot
    # spectrogram 4-40 Hz excess vs envelope exposure (calibration check)
    m4 = (ff >= 4) & (ff < 40); df = float(abs(np.median(np.diff(ff)))); dtt = float(np.median(np.diff(tt)))
    se_spec = float(np.clip(lin[m4][:, inw] - N[m4][:, None], 0, None).sum() * df * dtt * 1e-12)
    return B, dict(slope_sig_db_oct=s_sig[0], slope_sig_se=s_sig[1], slope_sig_n=s_sig[2], slope_excess_db_oct=s_exc[0],
                   slope_excess_se=s_exc[1], slope_excess_n=s_exc[2], slope_sig_4_17_db_oct=s_lo[0], slope_sig_4_17_se=s_lo[1],
                   se_spec_4_40_pa2s=se_spec, **gap), tim

rows, bands, timing = [], [], {}
for st in ["DSOH", "KSP1", "KSP2", "KSP3"]:
    E = pd.read_csv(near / f"metz-fig2-digitised-{st}.csv"); t, L = E.utc_s_of_day.values, E.rms_db_re_1uPa.values
    M = env_metrics(t, L, 0.02); z = np.load(near / f"metz-fig2-spectrogram-{st}.npz")
    for fill in (90.0, 80.0):
        B, S, T = spec_metrics(z["psd_db_re_1uPa2_Hz"].astype(float), z["utc_s_of_day"], z["freq_hz"], M["window"], fill)
        B.insert(0, "station", st); B.insert(1, "floor_fill_db", fill); bands.append(B); timing[f"{st}|{fill:g}"] = T
        rows.append(dict(station=st, field="near", range_km=RANGE_KM[st], floor_fill_db=fill, **{k: v for k, v in M.items() if k not in ("subpeaks", "window")},
                         subpeaks=json.dumps([{k: round(v, 2) for k, v in s.items()} for s in M["subpeaks"]]), **S,
                         se_spec_minus_env_db=10 * np.log10(S["se_spec_4_40_pa2s"] / M["se_pa2s"])))
g = pd.read_csv(far / "fig3CD_rms_envelopes_0p05s_DIGITISED.csv")
for el in ["H11N1", "H11N2", "H11N3", "H11S1", "H11S2", "H11S3"]:
    e = g[g.element == el].sort_values("utc_s_of_day"); t, L = e.utc_s_of_day.values, e.rms_db_re_1uPa.values
    M = env_metrics(t, L, 0.05)
    fills = (80.0, 70.0) if el in ("H11N1", "H11S1") else (None,)
    for fill in fills:
        S = {}
        if fill is not None:
            z = np.load(far / f"fig3AB_spectrogram_{el}_DIGITISED.npz")
            B, S, T = spec_metrics(z["psd_db_re_1uPa2_Hz"].astype(float), z["utc_s_of_day"], z["freq_hz"], M["window"], fill)
            B.insert(0, "station", el); B.insert(1, "floor_fill_db", fill); bands.append(B); timing[f"{el}|{fill:g}"] = T
            S["se_spec_minus_env_db"] = 10 * np.log10(S["se_spec_4_40_pa2s"] / M["se_pa2s"])
        rows.append(dict(station=el, field="far", range_km=RANGE_KM[el[:4]], floor_fill_db=fill, **{k: v for k, v in M.items() if k not in ("subpeaks", "window")},
                         subpeaks=json.dumps([{k: round(v, 2) for k, v in s.items()} for s in M["subpeaks"]]), **S))
D = pd.DataFrame(rows); D.to_csv(out / "metz-nearfield-derived.csv", index=False)
pd.concat(bands).to_csv(out / "metz-band-spectra.csv", index=False)
json.dump(timing, open(out / "metz-band-timing.json", "w"), indent=1)
cols = ["station", "floor_fill_db", "peak_db", "noise_db", "noise_pre_onset_db", "snr_peak_db", "snr_peak_pre_onset_db", "w6_s", "w10_s", "span_5_95_s", "arr_len_s",
        "rise_onset_to_peak3_s", "rise_10_90_s", "peak_rel_onset_s", "decay_db_per_s", "n_subpeaks_2db", "sel_db"]
pd.set_option("display.width", 250); print(D[cols].round(2).to_string())
cols2 = ["station", "floor_fill_db", "slope_sig_db_oct", "slope_sig_se", "slope_excess_db_oct", "slope_excess_se", "slope_excess_n", "slope_sig_4_17_db_oct", "gap_depth_db", "psd_12_17", "psd_18_24", "psd_26_34", "se_spec_minus_env_db"]
print(D[D.floor_fill_db.notna()][cols2].round(2).to_string())
