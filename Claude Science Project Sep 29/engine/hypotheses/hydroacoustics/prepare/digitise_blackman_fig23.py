"""Digitise the air9 curves of Blackman et al. (2004) Fig. 23 (DGS = H08S, CL = H01W panels).

DIGITISED DATA, NOT MEASUREMENTS. Input: the embedded page image p23_img0.png (351 x 458 px, artifact
99b55187-e5c8-4c37-abff-0482499b5a7f). Panel boxes come from long dark spine rows and columns
(DGS y 149-274, CL y 289-414, x 51-339). Calibration is from the tick-label centres: 150 dB at
y = 148.5 (DGS) / 288.5 (CL), 3.6 px/dB; 0 Hz at x = 51.5, 2.875 px/Hz.

Trace: in each pixel column, dark clusters (< 140 of 255; air7's thick light grey is about 190 and
excluded). Legend boxes and panel labels are masked. The cluster within 30 px of the previous pick is
taken, the darkest first, with ties broken by continuity. The trace was checked visually by overlay
(fig23_trace_check.png).

Run: python prepare/digitise_blackman_fig23.py <p23_img0.png> <out.csv>
"""

import sys

import numpy as np
import pandas as pd
from PIL import Image

PANELS = {"H08S": dict(y0=149, y1=274, ytop=148.5, legend=(222, 268, 215, 338)),
          "H01W": dict(y0=289, y1=414, ytop=288.5, legend=(368, 410, 215, 338))}
THR, JUMP = 140, 30


def clusters(idx):
    out, s, p = [], idx[0], idx[0]
    for v in idx[1:]:
        if v > p + 1:
            out.append((s, p)); s = v
        p = v
    out.append((s, p))
    return out


def trace(im, P):
    sub = im.copy()
    a, b, c, d = P["legend"]; sub[a:b, c:d] = 255
    sub[P["y0"]:P["y0"] + 24, 52:115] = 255
    pts, prev = [], None
    for x in range(54, 337):
        ys = np.where(sub[P["y0"] + 2:P["y1"] - 1, x] < THR)[0] + P["y0"] + 2
        if len(ys) == 0:
            continue
        cl = [((s + e) / 2, sub[s:e + 1, x].min()) for s, e in clusters(ys)]
        if prev is None:
            y = cl[0][0]
        else:
            near = [t for t in cl if abs(t[0] - prev) <= JUMP]
            if not near:
                continue
            y = min(near, key=lambda t: (t[1] // 25, abs(t[0] - prev)))[0]
        prev = y
        pts.append((x, (x - 51.5) / 2.875, 150 - (y - P["ytop"]) / 3.6))
    return pd.DataFrame(pts, columns=["x_px", "f_hz", "tl_db"])


def main(png, out):
    im = np.array(Image.open(png).convert("L")).astype(int)
    df = pd.concat([trace(im, P).assign(station=st) for st, P in [("H01W", PANELS["H01W"]), ("H08S", PANELS["H08S"])]])
    with open(out, "w") as f:
        f.write("# DIGITISED from Blackman et al. (2004) UCRL-TR-207323 Fig. 23 (observed TL, median over shots, shown only where SNR > 3 dB),\n"
                "# page image artifact p23_img0.png (99b55187-e5c8-4c37-abff-0482499b5a7f). air9 curve only; H01W = 'CL' panel, H08S = 'DGS' panel.\n"
                "# Method: darkest thin curve per pixel column with continuity (threshold 140/255, max jump 30 px), legend and panel labels masked;\n"
                "# calibration from tick-label centres: 3.6 px/dB, 2.875 px/Hz, 0 Hz at x=51.5 px. Chart reading +/-2 dB. Not a measurement.\n"
                "# Script: prepare/air9_tl_validation.py docstring. DGS: air8 dotted curve may capture the trace where they cross.\n")
        df[["station", "f_hz", "tl_db", "x_px"]].to_csv(f, index=False, float_format="%.3f")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
