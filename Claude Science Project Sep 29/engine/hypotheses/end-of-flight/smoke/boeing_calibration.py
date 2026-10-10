"""Deliverable 1: the module's free dynamics against the ten Boeing engineering-simulator cases.

    python3 boeing_calibration.py <dir of 'Case NN.csv'> <dir of module free-*.csv traces> <out.json>

Both sets are measured by the SAME event-free code, with no flame-out timing (the simulator files carry
none, and their runs start in powered flight):
  - high-rate flag: 1-s backward differences exceed 15,000 ft/min down AND 0.67 g down (Iannello 2018's
    published partition: cases 3, 4, 5, 6, 10);
  - chord from the first 15,000 ft/min crossing to the last row, NM (published 4.7-7.9 NM);
  - peak descent rate; phugoid period = median spacing of vertical-speed extrema (prominence >= 1,000 ft/min)
    before any 15,000 ft/min crossing; peak bank from the ground track, atan(V omega / g), still air.
Licence: the simulator files are validation-only (shared publicly by Iannello with ATSB permission, no
downstream archive licence located); only summary statistics are used and the files are not redistributed.
"""
import glob, json, os, sys
import numpy as np
from scipy.signal import savgol_filter, find_peaks

G, NM, FT = 9.80665, 1852.0, 0.3048
# Holland arXiv:1702.02432v3 descent-rate bounds (ft/min, negative down) at 00:19:29 and 8.027 s later:
# H1 Table IV p. 9, H2 Table VI p. 9 (rounded to 100 ft/min by Holland).
HOLLAND = {"H1": ((-14800.0, -3900.0), (-25300.0, -14800.0)), "H2": ((-6800.0, -2900.0), (-17600.0, -13800.0))}


def window_occupancy(t, alt_ft, lag_s=8):
    """Diagnostic smoke 3 (Pete, 10 Oct ~18:10 UTC): the fraction of 8-s windows during the descent whose (start, end)
    vertical speeds fall inside Holland's H1 and H2 bounds. Same estimator as the architecture 00:19 study, Table 6
    (reproduced exactly on the ten Boeing cases): 1-Hz altitude, 3-s moving average, central differences; windows
    from the first sample 200 ft below the starting altitude to the end of the record."""
    t = np.asarray(t, float); h = np.asarray(alt_ft, float)
    keep = np.r_[True, np.diff(t) > 0]; t, h = t[keep], h[keep]
    tt = np.arange(t[0], t[-1] + 1e-9, 1.0); h = np.interp(tt, t, h)
    if len(h) < lag_s + 4:
        return None
    vs = np.gradient(np.convolve(h, np.ones(3) / 3, mode="same")) * 60.0; vs[0] = vs[1]; vs[-1] = vs[-2]
    i0 = int(np.argmax(h < h[0] - 200.0)) if (h < h[0] - 200.0).any() else len(h)
    a, b = vs[i0:-lag_s], vs[i0 + lag_s:]
    out = {"windows": int(len(a)), "min_8s_dv_fpm": float((b - a).min()) if len(a) else None,
           "windows_dv_le_9400": int(((b - a) <= -9400).sum())}
    for k, ((a0, a1), (b0, b1)) in HOLLAND.items():
        m = (a >= a0) & (a <= a1) & (b >= b0) & (b <= b1)
        out[f"windows_{k}"] = int(m.sum()); out[f"fraction_{k}"] = float(m.mean()) if len(a) else None
        idx = np.where(m)[0]
        out[f"first_{k}_s_before_end"] = float(tt[-1] - tt[i0 + idx[0]]) if len(idx) else None
        out[f"first_{k}_altitude_ft"] = float(h[i0 + idx[0]]) if len(idx) else None
    return out


def measure(t, x_nm, y_nm, alt_ft):
    t = np.asarray(t, float); h = np.asarray(alt_ft, float) * FT
    keep = np.r_[True, np.diff(t) > 0]; t, h, x, y = t[keep], h[keep], np.asarray(x_nm)[keep], np.asarray(y_nm)[keep]
    tt = np.arange(t[0], t[-1] + 1e-9, 1.0)                      # 1 Hz, as the simulator exports
    h = np.interp(tt, t, h); x = np.interp(tt, t, x); y = np.interp(tt, t, y); t = tt
    vs = np.diff(h) / np.diff(t)                                  # backward differences, m/s
    acc = np.diff(vs) / np.diff(t[1:])
    fpm = vs / FT * 60
    high = bool((fpm <= -15000).any() and (acc <= -0.67 * G).any())
    i15 = np.where(fpm <= -15000)[0]
    chord = float(np.hypot(x[-1] - x[i15[0] + 1], y[-1] - y[i15[0] + 1])) if len(i15) else None
    fs = savgol_filter(h, 15, 3, deriv=1) / FT * 60 if len(h) > 15 else fpm
    lim = i15[0] if len(i15) else len(fs)
    pk, _ = find_peaks(fs[:lim], prominence=1000, distance=20); tr, _ = find_peaks(-fs[:lim], prominence=1000, distance=20)
    sp = np.concatenate([np.diff(t[pk]), np.diff(t[tr])])
    period = float(np.median(sp)) if len(sp) else None
    if len(x) > 40:
        vx = savgol_filter(x * NM, 9, 2, deriv=1); vy = savgol_filter(y * NM, 9, 2, deriv=1)
        hdg = np.unwrap(np.arctan2(vx, vy)); om = savgol_filter(hdg, 31, 2, deriv=1)
        bank = np.degrees(np.arctan(np.hypot(vx, vy) * om / G))[16:-16]
        max_bank = float(np.nanmax(np.abs(bank))) if len(bank) else None
    else:
        max_bank = None
    return {"high_rate": high, "max_descent_fpm": float(-fpm.min()), "max_down_accel_g": float(-acc.min() / G),
            "chord_after_15000_nm": chord, "phugoid_period_s": period, "n_vs_extrema": int(len(pk) + len(tr)),
            "max_bank_deg": max_bank, "duration_s": float(t[-1] - t[0]), "windows_8s": window_occupancy(t, h / FT)}


def main():
    sims, free, out = sys.argv[1:4]
    res = {"boeing": {}, "module": {}}
    for f in sorted(glob.glob(os.path.join(sims, "Case *.csv"))):
        a = np.genfromtxt(f, delimiter=",", skip_header=1)
        res["boeing"][os.path.basename(f)[:-4]] = measure(a[:, 0], a[:, 1], a[:, 2], a[:, 3])
    for f in sorted(glob.glob(os.path.join(free, "free-*.csv"))):
        a = np.genfromtxt(f, delimiter=",", skip_header=1)
        lat0, lon0 = a[0, 1], a[0, 2]
        y = (a[:, 1] - lat0) * 60.0; x = (a[:, 2] - lon0) * 60.0 * np.cos(np.radians(lat0))
        res["module"][os.path.basename(f)[:-4]] = measure(a[:, 0], x, y, a[:, 3])
    with open(out, "w") as fh:
        json.dump(res, fh, indent=1)
    for k in ("boeing", "module"):
        v = list(res[k].values())
        w = [r["windows_8s"] for r in v if r["windows_8s"]]
        print(k, "n", len(v), "high-rate", sum(r["high_rate"] for r in v),
              "pooled 8-s window fraction H1 %.4f H2 %.4f" % (sum(x["windows_H1"] for x in w) / max(1, sum(x["windows"] for x in w)),
                                                              sum(x["windows_H2"] for x in w) / max(1, sum(x["windows"] for x in w))),
              "mean per-trace fraction H1 %.4f H2 %.4f" % (np.mean([x["fraction_H1"] for x in w]), np.mean([x["fraction_H2"] for x in w])))


if __name__ == "__main__":
    main()
