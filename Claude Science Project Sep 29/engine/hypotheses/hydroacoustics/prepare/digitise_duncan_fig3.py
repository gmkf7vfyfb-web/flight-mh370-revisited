"""Digitise Duncan & Dall'Osto (2023) figure 3 as held in the repo, by colour masking.

DIGITISED DATA, NOT MEASUREMENTS. Source image: 'ISO Sept 28 Status/inputs/papers/hydroacoustics/
duncan-fig3.png' (912 x 849 px). Top panel: modelled relative signal strength (dB) against distance
from the hydrophones for their "MH370" path and the F-35 path. Bottom panel: water depth and
deep-sound-channel (DSC) axis depth along both paths.

GEOMETRY CAVEAT, binding on every use: their "MH370" path is the Curtin 301.6 deg HA01 bearing, which
crosses the 7th arc near 24-26 S. It is NOT a path from the core estimate near 37 S, and the 20-30 dB
gap it shows must not be imported as a detectability prior for the core region.

METHOD. Series colours are MATLAB defaults, MH370 (0,114,189) and F35 (217,83,25). Each pixel is
projected onto the white-to-series-colour line; it belongs to a series if the projection residual
is under 18 RGB units and the blend fraction is >= 0.5 (top) or >= 0.6 (bottom). Axis calibration
is from the detected spine pixels: x 119..824 px = 0..3500 km; top y 64..409 px = -80..-180 dB;
bottom y 492..755 px = 0..7000 m. Legend boxes and the magenta source marker are masked.
Resolution: 4.96 km, 0.29 dB, 26.6 m per pixel.

Top panel: per 25 km bin, the pixel-weighted median, 10/90 percentiles, min, max and power mean
(10 log10 of the mean of 10^(L/10)) of the trace. The trace is a 1-px polyline drawn through rapid
interference fading, so the pixel distribution stands for the level distribution within a bin only
approximately. OCCLUSION: F35 is drawn after MH370 (legend order), so where the traces overlap
(mostly below ~500 km, and the upper excursions of MH370 elsewhere) MH370 levels are biased LOW.

Bottom panel: per pixel column, vertical clusters of series pixels. With two clusters the shallower
is the DSC axis and the deeper the seafloor; with one, it is seafloor if deeper than 1,400 m, else
axis. Dashed axis lines leave gaps, which are left as NaN and never interpolated here.

Run: python prepare/digitise_duncan_fig3.py <png> <out_dir>
"""

import pathlib
import sys

import numpy as np
import pandas as pd
from PIL import Image

X0, X1, KM_MAX = 119, 824, 3500.0
T0, T1 = 64, 409          # -80 dB, -180 dB
B0, B1 = 492, 755         # 0 m, 7000 m
WHITE = np.array([255, 255, 255.0])
SERIES = {"MH370": np.array([0, 114, 189.0]), "F35": np.array([217, 83, 25.0])}


def km(x):
    return (x - X0) / (X1 - X0) * KM_MAX


def blend(im, colour):
    d = colour - WHITE
    v = im - WHITE
    a = (v @ d) / (d @ d)
    res = np.linalg.norm(v - a[..., None] * d, axis=2)
    return np.where(res < 18, a, 0.0)


def main(png, out_dir):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    im = np.array(Image.open(png).convert("RGB")).astype(float)
    h, w, _ = im.shape
    legend_top = np.zeros((h, w), bool); legend_top[66:120, 688:800] = True
    legend_bot = np.zeros((h, w), bool); legend_bot[550:615, 560:730] = True
    magenta = (im[..., 0] > 200) & (im[..., 1] < 80) & (im[..., 2] > 150)
    inside = np.zeros((h, w), bool); inside[:, X0 + 2:X1 - 1] = True

    rows = []
    bins = np.arange(0.0, KM_MAX + 25.0, 25.0)
    for name, colour in SERIES.items():
        a = blend(im, colour)
        m = (a >= 0.5) & ~legend_top & inside
        m[:T0 + 1] = False; m[T1:] = False
        ys, xs = np.nonzero(m)
        r, db = km(xs), -80.0 - (ys - T0) / (T1 - T0) * 100.0
        idx = np.digitize(r, bins) - 1
        for i in range(len(bins) - 1):
            v = db[idx == i]
            if len(v) == 0:
                rows.append((name, bins[i] + 12.5, 0) + (np.nan,) * 6)
                continue
            rows.append((name, bins[i] + 12.5, len(v), np.median(v), np.quantile(v, 0.1),
                         np.quantile(v, 0.9), v.min(), v.max(), 10 * np.log10(np.mean(10 ** (v / 10)))))
    top = pd.DataFrame(rows, columns=["path", "range_km", "n_pixels", "median_db", "p10_db", "p90_db",
                                      "min_db", "max_db", "power_mean_db"])

    picks = []
    for name, colour in SERIES.items():
        a = blend(im, colour)
        m = (a >= 0.6) & ~legend_bot & ~magenta & inside
        m[:B0 + 1] = False; m[B1:] = False
        for x in range(X0 + 2, X1 - 1):
            ys = np.nonzero(m[:, x])[0]
            depth = axis = np.nan
            if len(ys):
                cl = np.split(ys, np.where(np.diff(ys) > 3)[0] + 1)
                cen = [(c.mean() - B0) / (B1 - B0) * 7000.0 for c in cl]
                if len(cl) >= 2:
                    axis, depth = cen[0], cen[-1]
                elif cen[0] > 1400.0:
                    depth = cen[0]
                else:
                    axis = cen[0]
            picks.append((name, km(x), depth, axis))
    bot = pd.DataFrame(picks, columns=["path", "range_km", "water_depth_m", "dsc_axis_depth_m"])

    head = ("# DIGITISED from Duncan & Dall'Osto (2023) fig. 3 as held at 'ISO Sept 28 Status/inputs/papers/"
            "hydroacoustics/duncan-fig3.png' by prepare/digitise_duncan_fig3.py (colour masking; see its docstring).\n"
            "# Not a measurement. Their 'MH370' path is the 301.6 deg HA01 bearing (arc crossing ~24-26 S), not the core region.\n")
    for df, fn in [(top, "duncan-fig3-signal-digitised.csv"), (bot, "duncan-fig3-depth-digitised.csv")]:
        with open(out / fn, "w") as f:
            f.write(head)
            df.to_csv(f, index=False, float_format="%.2f")

    gap = top.pivot(index="range_km", columns="path", values="power_mean_db").dropna()
    gap = gap["F35"] - gap["MH370"]
    for lo, hi in [(500, 1000), (1000, 2000), (2000, 3000), (3000, 3250)]:
        g = gap[(gap.index >= lo) & (gap.index < hi)]
        print(f"F35 - MH370 power-mean gap {lo}-{hi} km: median {g.median():.1f} dB, range {g.min():.1f}..{g.max():.1f}")
    return top, bot


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
