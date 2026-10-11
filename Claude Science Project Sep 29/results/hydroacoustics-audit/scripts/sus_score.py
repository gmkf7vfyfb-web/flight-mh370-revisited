"""Audit C4 (SUS, 2003): score the module's propagation on the deep SUS shots detected at BOTH H01W and H08S.

Band values: power mean of the traced red (signal + noise) and blue (noise) PSD inside f_c 2^(+/-1/6); the blue
curve is interpolated linearly in dB across gaps (it is smooth and is hidden under the red where SNR ~ 0).
Signal S_b = 10 log10(10^(R_b/10) - 10^(B_b/10)) where R_b - B_b >= 3 dB; else the band is not scored.
Implied source energy spectral density at 1 m: SL_b = S_b + TL_b + 10 log10(6 s) (6 s window, declared assumption).
Station difference (source cancels): d_b = SL_b(H01W) - SL_b(H08S) = r_b(H01W) - r_b(H08S).

Usage: python sus_score.py <sus_tl.csv> <sus_spectra.npz> <out_dir>
"""
import json
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from air9_audit import stats, verdict  # noqa: E402

BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
SHOTS = {"A6sus3": ("A6", 915.0), "A7sus2": ("A7", 610.0), "A7sus3": ("A7", 915.0), "A8sus2": ("A8", 610.0),
         "A8sus2b": ("A8", 610.0), "A9sus3": ("A9", 915.0), "A10sus3": ("A10", 915.0), "A11sus": ("A11", 915.0),
         "A6sus2": ("A6", 610.0)}


def band_vals(f, red, blue):
    ok = np.isfinite(blue)
    bl = np.interp(f, f[ok], blue[ok]) if ok.sum() > 10 else blue
    out = {}
    for fc in BANDS:
        m = (f >= fc * 2 ** (-1 / 6)) & (f < fc * 2 ** (1 / 6)) & np.isfinite(red) & np.isfinite(bl)
        if m.sum() >= 2:
            R = 10 * np.log10(np.mean(10 ** (red[m] / 10))); B = 10 * np.log10(np.mean(10 ** (bl[m] / 10)))
            out[fc] = (R, B, R - B, 10 * np.log10(10 ** (R / 10) - 10 ** (B / 10)) if R - B >= 3 else np.nan)
    return out


def main(tl_csv, npz, out):
    tl = pd.read_csv(tl_csv); z = np.load(npz); f = z["f"]
    rows = []
    for shot, (site, zs) in SHOTS.items():
        for st in ("H01W", "H08S"):
            k = f"{shot}|{st}"
            if f"{k}|red" not in z.files:
                rows.append(dict(shot=shot, station=st, status="panel not traced")); continue
            g = tl[(tl.site == site) & (tl.station == st) & np.isclose(tl.src_depth_m, zs)].set_index("fc_hz").tl_db
            for fc, (R, B, snr, S) in band_vals(f, z[f"{k}|red"], z[f"{k}|blue"]).items():
                t = g.get(fc, np.nan)
                rows.append(dict(shot=shot, site=site, src_depth_m=zs, station=st, fc_hz=fc, red_db=R, noise_db=B, snr_db=snr,
                                 signal_db=S, model_tl_db=t, implied_sl_db=S + t + 10 * np.log10(6.0) if np.isfinite(t) else np.nan,
                                 status="ok" if np.isfinite(t) else "no model TL (path blocked)"))
    df = pd.DataFrame(rows); df.to_csv(f"{out}/sus_bands.csv", index=False)
    summ = {}
    for shot in SHOTS:
        a = df[(df.shot == shot) & (df.station == "H01W")].set_index("fc_hz").implied_sl_db if "implied_sl_db" in df else None
        b = df[(df.shot == shot) & (df.station == "H08S")].set_index("fc_hz").implied_sl_db if "implied_sl_db" in df else None
        if a is None or b is None or a.dropna().empty or b.dropna().empty:
            continue
        sh = [fc for fc in BANDS if fc in a.index and fc in b.index and np.isfinite(a[fc]) and np.isfinite(b[fc])]
        if len(sh) >= 3:
            s = stats(sh, [a[fc] - b[fc] for fc in sh]); s["grades"], s["verdict"] = verdict(s, (3.5, 5.0))
            summ[f"{shot}|C2"] = s
        for st, ser in (("H01W", a), ("H08S", b)):
            v = ser.dropna()
            if len(v) >= 3:
                s = stats(list(v.index), list(v.values)); summ[f"{shot}|{st}|implied_sl"] = s
    # pooled station difference over shots: median per band
    d = []
    for k, s in summ.items():
        if k.endswith("|C2"):
            for fc in BANDS:
                pass
    json.dump(summ, open(f"{out}/sus_summary.json", "w"), indent=1)
    for k, s in summ.items():
        print(k, s["n"], s["f_lo"], s["f_hi"], round(s["level_median"], 1), round(s["slope_db_per_oct"], 2), round(s["shape_rms"], 2), s.get("verdict", ""))


if __name__ == "__main__":
    main(*sys.argv[1:4])
