"""Audit: trace BOTH curves (red = signal, blue = noise) of Blackman et al. (2004) Appendix B panels for the SUS
shots of sites A6-A11 (Figs B6-B11, printed pp. 28-31), and convert to PSD in dB re 1 uPa^2/Hz by the module's
route R (SAC amplitude spectrum, PSD = 2 A^2 / T, T = 6 s, divided by the FDSN response).

Frame detection, decade-tick calibration and run splitting are the module's (prepare/blackman_noise.py, imported
read-only); the tracing is re-implemented here with a colour argument. Red mask: R > 140, G < 110, B < 110,
R - max(G, B) > 60; legend box (top 12 %, right half) masked. Panels are mapped to events by figure order on the
page (p30 img1 = B6, p31 img0 = B7, p32 img0 = B8, p32 img1 = B9, p33 img0 = B10, p33 img1 = B11; checked by eye
on the p30 render) and by the row order printed in each caption.

ASSUMPTION (declared): the signal spectrum used the same 6 s window and normalisation as the noise. The report
states the window for the noise only (printed p. 25).

Usage: python sus_spectra.py <module_prepare_dir> <ucrl pdf> <response_dir> <out_npz>
"""
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import blackman_noise as BN  # noqa: E402

FIGS = {(30, 1): ["A6sus2", "A6sus3"], (31, 0): ["A7sus2", "A7sus3", "A7sph5"],
        (32, 0): ["A8sph1", "A8sus2", "A8sus2b"], (32, 1): ["A9sus3", "A9suspuf"],
        (33, 0): ["A10sus3", "A10suspuf"], (33, 1): ["A11sus", "A11sph5"]}
STATIONS = ["H01W", "H08S", "H08N"]


def trace_col(img, t, b, l, r, cal, colour):
    sub = img[t + 3:b - 2, l + 3:r - 2].astype(int)
    R, G, B = sub[..., 0], sub[..., 1], sub[..., 2]
    if colour == "blue":
        m = (B > 140) & (R < 110) & (G < 110) & (B - np.maximum(R, G) > 60)
    else:
        m = (R > 140) & (G < 110) & (B < 110) & (R - np.maximum(G, B) > 60)
    h, w = m.shape
    m[: int(0.12 * h), int(0.5 * w):] = False
    cents = [[(a + c) / 2.0 for a, c in BN.runs(m[:, x])] for x in range(w)]
    fx = (np.arange(w) + 3) / (r - l) * 100.0
    cand = [x for x in range(w) if 40 <= fx[x] <= 60 and len(cents[x]) == 1]
    if not cand:
        return None
    x0 = cand[len(cand) // 2]; yv = np.full(w, np.nan); yv[x0] = cents[x0][0]
    for step in (1, -1):
        prev = yv[x0]; x = x0 + step
        while 0 <= x < w:
            if cents[x]:
                c = min(cents[x], key=lambda c_: abs(c_ - prev))
                if abs(c - prev) <= 40:
                    yv[x] = c; prev = c
            x += step
    logA = cal["a"] + cal["b"] * (yv + t + 3)
    A = np.interp(BN.F, fx, np.where(np.isfinite(logA), logA, np.nan), left=np.nan, right=np.nan)
    return A


def main(prep, pdf, resp_dir, out):
    import fitz
    from obspy import read_inventory
    resp = {}
    for st, el in BN.RESP.items():
        inv = read_inventory(f"{resp_dir}/{el}_2003.xml")
        resp[st] = np.abs(inv[0][0][0].response.get_evalresp_response_for_frequencies(BN.F, output="DEF"))
    d = fitz.open(pdf); res = {}; log = []
    for (pn, k), labels in FIGS.items():
        x = d[pn - 1].get_images(full=True)[k]
        pix = fitz.Pixmap(d, x[0])
        if pix.n - pix.alpha > 3:
            pix = fitz.Pixmap(fitz.csRGB, pix)
        img = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[..., :3]
        dark = img.astype(int).sum(2) < 250
        boxes = BN.frames(dark)
        tops = sorted({min(u for u in [bx[0] for bx in boxes] if abs(u - bx[0]) <= 15) for bx in boxes})
        seen = set()
        for (t, b, l, r) in boxes:
            ci = min(2, int(l / (dark.shape[1] / 3.0)))
            ri = tops.index(min(u for u in tops if abs(u - t) <= 15))
            if (ri, ci) in seen or ri >= len(labels):
                continue
            seen.add((ri, ci))
            st = STATIONS[ci]; ev = labels[ri]
            cal = BN.y_cal(dark, t, b, l)
            if cal is None or cal["resid_px"] > 2.0 or abs(cal["log_at_bottom"]) > 0.05:
                log.append((ev, st, "rejected: y calibration")); continue
            out_ = {}
            for colour in ("red", "blue"):
                A = trace_col(img, t, b, l, r, cal, colour)
                out_[colour] = None if A is None else 10 * np.log10(2 * (10 ** A) ** 2 / BN.T_WIN / resp[st] ** 2) + 120.0
            if out_["red"] is None or out_["blue"] is None:
                log.append((ev, st, "rejected: trace")); continue
            res[f"{ev}|{st}|red"] = out_["red"]; res[f"{ev}|{st}|blue"] = out_["blue"]
            log.append((ev, st, f"ok red {np.isfinite(out_['red']).mean():.2f} blue {np.isfinite(out_['blue']).mean():.2f}"))
    np.savez(out, f=BN.F, **res)
    for row in log:
        print(*row)


if __name__ == "__main__":
    main(*sys.argv[1:5])
