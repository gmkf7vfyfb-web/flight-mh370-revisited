#!/usr/bin/env python3
"""Build the AES gain table used by hypotheses/antenna-gain from Large (2019).

    .venv/bin/python hypotheses/antenna-gain/prepare/build_gain_table.py

Source: "GAIN IN AC COORDS TO 68 EL 360 AZ.xlsx" (P. Large, Feb 2019; sha256 below), CC BY 4.0,
https://huggingface.co/datasets/peteabiome/mh370-dissertation-spreadsheets. A copy is kept in
data/external/antenna/. Sheet1 holds the gain (dBic) of the 9M-MRO high-gain antenna in aircraft
coordinates: rows are the azimuth 1..360 degrees clockwise from the nose, columns the elevation
0..68 degrees above the aircraft's longitudinal-lateral plane.

Large (2019, printed pp. 93-95) built it by digitising the peak-gain-versus-scan-angle curve of
Westfeldt & Konrad (1992, Fig. 8), assuming it rotationally symmetric about the array normal, and
rotating it to two arrays tilted 45 degrees either side of the crown (port and starboard). The
script checks that construction: every cell should equal P(theta), where theta is the angle from
the nearer array normal. It then fills elevations 69..90 from the same P(theta) (the median gain of
the table's own cells in each 1-degree theta bin, linearly interpolated), because a banked aircraft
can see the satellite above 68 degrees. Cells at 0..68 degrees are copied unchanged.

Outputs:
  hypotheses/antenna-gain/gain-aircraft-coordinates.csv    the table the module embeds
  runs/antenna-gain-inputs/gain-aircraft-coordinates.png   the table and the construction check
"""

import csv
import hashlib
import math
from pathlib import Path

import numpy as np
import openpyxl

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "data/external/antenna/GAIN IN AC COORDS TO 68 EL 360 AZ.xlsx"
SOURCE_SHA256 = "1fb1a5090727ace7de3e2fc93313708069da652680cee366e713514823f7f3e5"
TABLE = ROOT / "hypotheses/antenna-gain/gain-aircraft-coordinates.csv"
FIGURE = ROOT / "runs/antenna-gain-inputs/gain-aircraft-coordinates.png"
TILT_DEG = 45.0  # each array's normal, above the lateral axis (Large 2019 p. 94)
SOURCE_TOP_DEG = 68


def read_source():
    digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert digest == SOURCE_SHA256, f"{SOURCE} has sha256 {digest}, expected {SOURCE_SHA256}"
    rows = list(openpyxl.load_workbook(SOURCE, data_only=True).worksheets[0].iter_rows(values_only=True))
    assert rows[0][1 : SOURCE_TOP_DEG + 2] == tuple(range(SOURCE_TOP_DEG + 1)), "elevation header"
    assert [r[0] for r in rows[1:361]] == list(range(1, 361)), "azimuth rows"
    gain = np.array([[float(v) for v in r[1 : SOURCE_TOP_DEG + 2]] for r in rows[1:361]])
    # Row 360 is the nose: reorder to azimuth 0..359.
    return np.roll(gain, 1, axis=0)


def off_normal_deg(azimuth_deg, elevation_deg):
    """Angle between a look direction and the nearer of the two array normals."""
    az, el = np.radians(azimuth_deg), np.radians(elevation_deg)
    tilt = math.radians(TILT_DEG)
    lateral = np.abs(np.cos(el) * np.sin(az)) * math.cos(tilt)
    return np.degrees(np.arccos(np.clip(lateral + np.sin(el) * math.sin(tilt), -1.0, 1.0)))


def main():
    source = read_source()
    azimuth = np.arange(360.0)
    elevation = np.arange(91.0)
    assert np.array_equal(source[1:], source[:0:-1]), "port/starboard mirror symmetry"

    theta = off_normal_deg(azimuth[:, None], elevation[None, : SOURCE_TOP_DEG + 1])
    bins = np.rint(theta).astype(int)
    curve = np.array([np.median(source[bins == k]) for k in range(91)])
    residual = source - np.interp(theta, np.arange(91.0), curve)
    print(f"construction check, {source.size} cells: residual RMS {np.sqrt(np.mean(residual**2)):.3f} dB, "
          f"max |residual| {np.abs(residual).max():.3f} dB (Large 2019 digitisation s.d. 0.5 dB)")

    table = np.empty((360, 91))
    table[:, : SOURCE_TOP_DEG + 1] = source
    theta_top = off_normal_deg(azimuth[:, None], elevation[None, SOURCE_TOP_DEG + 1 :])
    table[:, SOURCE_TOP_DEG + 1 :] = np.interp(theta_top, np.arange(91.0), curve)
    step = table[:, SOURCE_TOP_DEG + 1] - table[:, SOURCE_TOP_DEG]
    print(f"extension: {theta_top.min():.1f}-{theta_top.max():.1f} deg off-normal; "
          f"largest step across 68/69 deg {np.abs(step).max():.2f} dB")

    with TABLE.open("w", newline="") as f:
        f.write(
            "# AES high-gain antenna gain (dBic) of 9M-MRO in aircraft coordinates. Rows: azimuth (deg) clockwise\n"
            "# from the nose. Columns: elevation (deg) above the aircraft's longitudinal-lateral plane.\n"
            "# Elevations 0-68: Large (2019), 'GAIN IN AC COORDS TO 68 EL 360 AZ.xlsx' (sha256 1fb1a509...), CC BY 4.0,\n"
            "# huggingface.co/datasets/peteabiome/mh370-dissertation-spreadsheets (source row 360 is azimuth 0).\n"
            "# Elevations 69-90: derived by the source's own construction (two arrays tilted 45 deg, gain a function of the\n"
            "# angle from the nearer array normal); see prepare/build_gain_table.py.\n"
        )
        writer = csv.writer(f)
        writer.writerow(["azimuth_deg"] + [str(e) for e in range(91)])
        for a in range(360):
            writer.writerow([a] + [f"{g:.4g}" for g in table[a]])
    print(f"wrote {TABLE.relative_to(ROOT)}")
    plot(table, theta, source, curve)


def plot(table, theta, source, curve):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    FIGURE.parent.mkdir(parents=True, exist_ok=True)
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 4.8), gridspec_kw={"width_ratios": [1.9, 1]})
    image = ax.imshow(table.T, origin="lower", extent=(-0.5, 359.5, -0.5, 90.5), aspect="auto", cmap="viridis")
    contours = ax.contour(np.arange(360), np.arange(91), table.T, levels=[6, 8, 10, 12, 13, 14], colors="white", linewidths=0.6)
    ax.clabel(contours, fmt="%g", fontsize=7)
    ax.axhline(SOURCE_TOP_DEG + 0.5, color="white", ls="--", lw=1)
    box = dict(facecolor="black", alpha=0.45, lw=0, pad=1.5)
    ax.text(182, SOURCE_TOP_DEG + 3, "above 68 deg: derived by the source's construction", color="white", fontsize=8, ha="center", bbox=box)
    ax.axhspan(39.6, 55.9, color="white", alpha=0.12, lw=0)
    ax.text(182, 47.7, "satellite 40-56 deg up at the\n19:41-00:11 arcs (level flight)", color="white", fontsize=8, ha="center", va="center", bbox=box)
    ax.set_xticks(range(0, 361, 45))
    ax.set_xlabel("azimuth from the nose, clockwise (deg): 90 = starboard, 270 = port")
    ax.set_ylabel("elevation above the wing plane (deg)")
    ax.set_title("9M-MRO AES high-gain antenna, aircraft coordinates (Large 2019)", fontsize=10)
    fig.colorbar(image, ax=ax, label="gain (dBic)")

    bx.scatter(theta.ravel(), source.ravel(), s=1, alpha=0.15, color="#4a6fa5", label="table cells (elevation 0-68)")
    bx.plot(np.arange(91), curve, color="#d1495b", lw=1.5, label="median per 1 deg (used above 68)")
    bx.set_xlabel("angle from the nearer array normal (deg)")
    bx.set_ylabel("gain (dBic)")
    bx.set_title("Construction check: two arrays tilted 45 deg", fontsize=10)
    bx.legend(fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(FIGURE, dpi=150)
    print(f"wrote {FIGURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
