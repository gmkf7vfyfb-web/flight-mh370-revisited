"""IMS ambient noise at H01W, H08S and H08N from Blackman et al. (2004) Appendix B, to replace the Perth Canyon proxy.

PRE-REGISTERED (10 Oct 2026, ~20:30 UTC), committed before the full run. Disclosed beforehand: one image (p. 32,
second figure) was used to develop the frame and tick detection; no noise level was computed from it.

SOURCE. [Blackman2004UCRL] UCRL-TR-207323, Appendix B, pp. 27-33 (PDF pages; the report's own pages 25-31), Figures
B1-B11: 2003 cruise, sources at sites A1-A11. Each figure is a raster image (about 3,000 px wide) with three columns:
H01 (Cape Leeuwin), H08S (Diego Garcia South), H08N (Diego Garcia North). The report (p. 27) states that the blue
curve is "spectra of the average over the three sensors of noise, for each station, for a 6-s period, 20 seconds
before the predicted arrival time", in instrument counts, on a linear 0-100 Hz axis. The y axis is logarithmic.

EXTRACTION (per image):
  frames: long dark lines; tops paired with bottoms 600-760 px apart, lefts with rights 900-1,000 px apart.
  y: the decade ticks (dark runs >= 13 px right of the left frame) are fitted as log10(A) = a + b*y by least squares;
     the fit must use >= 3 decade ticks with residual < 2 px, and the fitted value at the frame bottom must be
     10^0 within 0.05 decades (the labelled bottom), else the panel is rejected.
  x: the left frame is 0 Hz and the right frame 100 Hz (checked against the bottom 20-Hz ticks; > 1 % misfit rejects).
  blue pixels: B > 140, R < 110, G < 110 and B - max(R, G) > 60; the legend box (top 12 %, right half) is masked.
  tracking: per pixel column, centres of blue runs; the trace starts at the median column in 40-60 Hz with exactly one
     run, and follows the nearest run (jump <= 40 px, else a gap); gaps <= 3 Hz are interpolated linearly, longer gaps
     stay missing. Output A(f) on a 0.5 Hz grid, 3-99.5 Hz.
  QC per panel: traced fraction of 5-40 Hz >= 0.8, else rejected. Residual check: the traced y against the blue-run
     centre in every column where both exist; the median |residual| must be <= 2 px.
  duplicates: two panels of the same station whose traced log10 A differ by a median < 0.02 over 5-40 Hz are the
     same curve reprinted (p. 30 reprints site A4's H08N column under A5); each such set is counted once.
CALIBRATION (route R, primary):
  The file names in the legend ("...noise.sac.am.ave") are SAC amplitude spectra. SAC's FFT multiplies by the sample
  interval, so A is in counts per Hz. One-sided PSD = 2 A^2 / T, T = 6 s, in counts^2/Hz; divided by |R(f)|^2, the
  full FDSN response of H01W1, H08S1 or H08N1 (channel EDH, one epoch covering 2003 and 2014; 1,839 and 1,845 counts/Pa
  at 10 Hz), gives Pa^2/Hz; reported in dB re 1 uPa^2/Hz. No window correction is applied, and the smoothing used for
  "ave" is unknown (declared).
  SENSITIVITY (route R'): amplitude = |FFT| without the sample-interval factor (counts); PSD = 2 A^2 / (T fs^2),
  fs = 250 Hz, i.e. 20 log10(250) = 48 dB below route R.
PLAUSIBILITY GATE (fixed now): route R band levels at 5-40 Hz must lie within 55-105 dB re 1 uPa^2/Hz (deep-water
  ambient noise range of the Wenz curves) for the median panel of every station; else the route is reported as
  FAILED-PLAUSIBILITY and the proxy stays.
OUTPUTS: per panel A(f); per station x third-octave band (5-40 Hz): median, 10 % and 90 % over unique panels, in dB re
  1 uPa^2/Hz; difference from the Perth Canyon proxy used by the near-limits analysis.
REPLACEMENT RULE: if the extraction QC passes for >= 2/3 of each station's panels and route R passes the gate, the
  traced levels replace the proxy in the near-limits and IMS P_D calculations as the new primary, with the proxy kept
  beside them as a sensitivity. Otherwise the proxy stays primary and the traced levels are a sensitivity.
DECLARED LIMITATIONS: 2003 (May-June) noise, not 8 Mar 2014; 6 s windows chosen before signal arrivals, so the
  sample is of quiet-to-ordinary conditions at the time of each shot; the 2014 H08S record contained an airgun survey
  that these windows do not; the SAC normalisation is inferred from file names, not stated in the report.

Usage (from prepare/, PYTHONPATH=.):  python blackman_noise.py <ucrl-tr-207323.pdf> <response_dir> <out_dir>
"""
import csv, hashlib, json, pathlib, sys
import numpy as np

PAGES = range(27, 34)                 # 1-based PDF pages of Appendix B
STATIONS = ["H01W", "H08S", "H08N"]   # columns, left to right
RESP = {"H01W": "H01W1", "H08S": "H08S1", "H08N": "H08N1"}
F = np.arange(3.0, 100.0, 0.5)
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0]
T_WIN, FS = 6.0, 250.0


def runs(v):
    idx = np.where(v)[0]
    if len(idx) == 0:
        return []
    out, s, p = [], idx[0], idx[0]
    for i in idx[1:]:
        if i > p + 1:
            out.append((s, p)); s = i
        p = i
    out.append((s, p)); return out


def frames(dark):
    H, W = dark.shape
    rows = [int((a + b) / 2) for a, b in runs(dark.sum(1) > W * 0.25)]
    cols = [int((a + b) / 2) for a, b in runs(dark.sum(0) > H * 0.25)]
    tb = [(t, b) for t in rows for b in rows if 600 <= b - t <= 760]
    lr = [(l, r) for l in cols for r in cols if 900 <= r - l <= 1000]
    tb = [p for p in tb if not any(q != p and q[0] == p[0] and q[1] < p[1] for q in tb)]
    lr = [p for p in lr if not any(q != p and q[0] == p[0] and q[1] < p[1] for q in lr)]
    return sorted(tb), sorted(lr)


def y_cal(dark, t, b, l):
    ys, lens = [], []
    for y in range(t + 5, b - 4):
        n = 0
        while n < 40 and dark[y, l + 2 + n]:
            n += 1
        lens.append(n); ys.append(y)
    lens = np.array(lens); ys = np.array(ys)
    major = [int(np.mean(ys[a:b_ + 1])) for a, b_ in runs(lens >= 13)]
    major = sorted(major)[::-1]                       # bottom (10^1) upwards
    if len(major) < 3:
        return None
    # decades: the lowest major tick above the frame bottom is 10^1 if the bottom is 10^0
    dec = np.arange(1, len(major) + 1, dtype=float)
    A = np.vstack([np.ones(len(major)), np.array(major, float)]).T
    coef, *_ = np.linalg.lstsq(A, dec, rcond=None)
    res = dec - A @ coef
    bottom_val = coef[0] + coef[1] * b
    return dict(a=float(coef[0]), b=float(coef[1]), resid_px=float(np.max(np.abs(res / coef[1]))), n=len(major),
                log_at_bottom=float(bottom_val), major_px=major)


def trace(img, t, b, l, r, cal):
    sub = img[t + 3:b - 2, l + 3:r - 2].astype(int)
    R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
    blue = (B > 140) & (R < 110) & (G < 110) & (B - np.maximum(R, G) > 60)
    h, w = blue.shape
    blue[: int(0.12 * h), int(0.5 * w):] = False
    cents = [[(a + c) / 2.0 for a, c in runs(blue[:, x])] for x in range(w)]
    fx = (np.arange(w) + 3) / (r - l) * 100.0
    cand = [x for x in range(w) if 40 <= fx[x] <= 60 and len(cents[x]) == 1]
    if not cand:
        return None
    x0 = int(np.median(cand)); yv = np.full(w, np.nan); yv[x0] = cents[x0][0]
    for step in (1, -1):
        prev = yv[x0]; x = x0 + step
        while 0 <= x < w:
            if cents[x]:
                c = min(cents[x], key=lambda c_: abs(c_ - prev))
                if abs(c - prev) <= 40:
                    yv[x] = c; prev = c
            x += step
    good = np.isfinite(yv)
    # residual check against the nearest blue-run centre (identity where tracked; kept for the record)
    resid = np.array([min(abs(c - yv[x]) for c in cents[x]) for x in range(w) if good[x] and cents[x]])
    # gaps <= 3 Hz interpolated
    xs = np.arange(w); yi = yv.copy()
    gi = runs(~good)
    for a, c in gi:
        if a > 0 and c < w - 1 and (fx[c] - fx[a]) <= 3.0:
            yi[a:c + 1] = np.interp(xs[a:c + 1], [a - 1, c + 1], [yv[a - 1], yv[c + 1]])
    ypx = yi + t + 3
    logA = cal["a"] + cal["b"] * ypx
    A = np.interp(F, fx, np.where(np.isfinite(logA), logA, np.nan), left=np.nan, right=np.nan)
    ok = np.isfinite(A)
    band = (F >= 5) & (F <= 40)
    return dict(logA=A, frac_5_40=float(ok[band].mean()), resid_med_px=float(np.median(resid)) if len(resid) else np.nan)


def band_db(f, psd_db):
    out = {}
    for fc in BANDS:
        m = (f >= fc * 2 ** (-1 / 6)) & (f < fc * 2 ** (1 / 6)) & np.isfinite(psd_db)
        out[fc] = float(10 * np.log10(np.mean(10 ** (psd_db[m] / 10)))) if m.any() else np.nan
    return out


def main(pdf, resp_dir, out):
    import fitz
    from obspy import read_inventory
    out = pathlib.Path(out); out.mkdir(parents=True, exist_ok=True)
    sha = hashlib.sha256(open(pdf, "rb").read()).hexdigest()
    resp = {}
    for st, el in RESP.items():
        inv = read_inventory(str(pathlib.Path(resp_dir) / f"{el}_2003.xml"))
        resp[st] = np.abs(inv[0][0][0].response.get_evalresp_response_for_frequencies(F, output="DEF"))
    d = fitz.open(pdf); panels = []
    for pn in PAGES:
        for k, x in enumerate(d[pn - 1].get_images(full=True)):
            pix = fitz.Pixmap(d, x[0])
            if pix.n - pix.alpha > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)
            img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[..., :3]
            dark = img.astype(int).sum(2) < 250
            tb, lr = frames(dark)
            for ri, (t, b) in enumerate(tb):
                for ci, (l, r) in enumerate(lr[:3]):
                    st = STATIONS[ci]; rec = dict(page=pn, image=k, row=ri, col=ci, station=st, status="ok")
                    cal = y_cal(dark, t, b, l)
                    if cal is None or cal["resid_px"] > 2.0 or abs(cal["log_at_bottom"]) > 0.05:
                        rec["status"] = "rejected: y calibration"; panels.append(rec); continue
                    tr = trace(img, t, b, l, r, cal)
                    if tr is None or tr["frac_5_40"] < 0.8 or not (tr["resid_med_px"] <= 2.0):
                        rec.update(status="rejected: trace QC", **({k_: v for k_, v in tr.items() if k_ != "logA"} if tr else {}))
                        panels.append(rec); continue
                    A = 10 ** tr["logA"]
                    psd_R = 10 * np.log10(2 * A ** 2 / T_WIN / resp[st] ** 2) + 120.0
                    psd_Rp = 10 * np.log10(2 * A ** 2 / (T_WIN * FS ** 2) / resp[st] ** 2) + 120.0
                    rec.update(cal_n_decades=cal["n"], cal_resid_px=cal["resid_px"], log_at_bottom=cal["log_at_bottom"],
                               frac_5_40=tr["frac_5_40"], resid_med_px=tr["resid_med_px"],
                               logA=tr["logA"].tolist(), psd_R=psd_R.tolist(), psd_Rp=psd_Rp.tolist())
                    panels.append(rec)
    # duplicates
    for st in STATIONS:
        ok = [p for p in panels if p["station"] == st and p["status"] == "ok"]
        band = (F >= 5) & (F <= 40)
        for i, p in enumerate(ok):
            for q in ok[:i]:
                if q["status"] == "ok" and np.nanmedian(np.abs(np.array(p["logA"])[band] - np.array(q["logA"])[band])) < 0.02:
                    p["status"] = f"duplicate of p{q['page']} img{q['image']} r{q['row']}"; break
    summ = {}
    for st in STATIONS:
        allp = [p for p in panels if p["station"] == st]
        ok = [p for p in allp if p["status"] == "ok"]
        nondup = [p for p in allp if not p["status"].startswith("duplicate")]
        bands = {route: np.array([list(band_db(F, np.array(p[route])).values()) for p in ok]) for route in ("psd_R", "psd_Rp")}
        summ[st] = dict(n_panels=len(allp), n_unique=len(nondup), n_ok=len(ok),
                        qc_pass_fraction=len(ok) / max(1, len(nondup)),
                        **{f"{route}_band_db": {f"{fc:g}": dict(q10=float(np.nanquantile(v[:, i], 0.1)), median=float(np.nanmedian(v[:, i])),
                                                              q90=float(np.nanquantile(v[:, i], 0.9))) for i, fc in enumerate(BANDS)}
                           for route, v in bands.items() if len(v)})
    gate = all(55 <= summ[st]["psd_R_band_db"][f"{fc:g}"]["median"] <= 105 for st in STATIONS if "psd_R_band_db" in summ[st] for fc in BANDS)
    qc = all(summ[st]["qc_pass_fraction"] >= 2 / 3 for st in STATIONS)
    verdict = dict(plausibility_gate="passed" if gate else "FAILED-PLAUSIBILITY", extraction_qc="passed" if qc else "FAILED-QC",
                   replaces_proxy=bool(gate and qc))
    json.dump(dict(provenance=dict(pdf_sha256=sha, pages=list(PAGES), T_win_s=T_WIN, fs_hz=FS, script="prepare/blackman_noise.py"),
                   verdict=verdict, stations=summ), open(out / "blackman_noise_summary.json", "w"), indent=1)
    with open(out / "blackman_noise_panels.csv", "w", newline="") as fh:
        keys = ["page", "image", "row", "col", "station", "status", "cal_n_decades", "cal_resid_px", "log_at_bottom", "frac_5_40", "resid_med_px"]
        w = csv.DictWriter(fh, fieldnames=keys, extrasaction="ignore"); w.writeheader(); w.writerows(panels)
    np.savez(out / "blackman_noise_curves.npz", f=F, **{f"{p['station']}_p{p['page']}_i{p['image']}_r{p['row']}": np.array(p["psd_R"]) for p in panels if "psd_R" in p})
    print(json.dumps(verdict), {st: (summ[st]["n_unique"], summ[st]["n_ok"]) for st in STATIONS})


if __name__ == "__main__":
    main(*sys.argv[1:4])
