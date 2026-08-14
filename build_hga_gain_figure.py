#!/usr/bin/env python3
"""Build the MH370 HGA installation/gain-envelope explanatory figure.

The aircraft pixels are retained from the supplied transparent PNG.  The gain
surface is a surface of revolution made from the measured peak-gain trace in
Figure 19 of the dissertation (adapted there from Westfeldt & Konrad, 1992).
Radius is proportional to normalized power gain, 10**((G-Gmax)/10).
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
AIRCRAFT = ROOT / "upload" / "D9284C33-B1D1-42B7-817F-40EE94FDAD8B.png"
GAIN_FIGURE = ROOT / "tmp" / "pdfs" / "received_power_figs" / "dissertation-110.png"
OUT = ROOT / "output" / "graphics"


def digitize_gain() -> tuple[np.ndarray, np.ndarray]:
    """Digitize both halves of the grey trace and average them at 1 degree."""
    image = np.asarray(Image.open(GAIN_FIGURE).convert("RGB"), dtype=float)
    grey = image.mean(axis=2)
    neutral = image.max(axis=2) - image.min(axis=2) < 8

    # Pixel calibration of the plot: -90..+90 degrees and 0..16 dB.
    x_left, x_mid, x_right = 337.0, 683.5, 1030.0
    y_top, y_bottom = 342.0, 1051.0

    def curve_y(x: float, expected: float | None) -> float:
        values: list[tuple[float, float]] = []
        for xx in range(max(0, int(round(x)) - 3), min(image.shape[1], int(round(x)) + 4)):
            ys = np.where((grey[350:910, xx] < 205) & neutral[350:910, xx])[0] + 350
            for yy in ys:
                # Prefer dark antialiased trace pixels and continuity.
                continuity = 0.0 if expected is None else 0.15 * abs(float(yy) - expected)
                values.append((float(grey[yy, xx]) + continuity, float(yy)))
        if not values:
            return float("nan")
        values.sort(key=lambda item: item[0])
        best = [yy for _, yy in values[: min(4, len(values))]]
        return float(np.median(best))

    theta_dense = np.linspace(0.0, 90.0, 361)
    y_left: list[float] = []
    y_right: list[float] = []
    prior_l = prior_r = None
    for theta in theta_dense:
        xl = x_mid - (theta / 90.0) * (x_mid - x_left)
        xr = x_mid + (theta / 90.0) * (x_right - x_mid)
        prior_l = curve_y(xl, prior_l)
        prior_r = curve_y(xr, prior_r)
        y_left.append(prior_l)
        y_right.append(prior_r)

    y = np.nanmean(np.vstack([y_left, y_right]), axis=0)
    good = np.isfinite(y)
    y = np.interp(theta_dense, theta_dense[good], y[good])
    gain_dense = 16.0 * (y_bottom - y) / (y_bottom - y_top)

    # A very light 1-degree moving average suppresses pixel staircase only.
    kernel = np.ones(5) / 5.0
    gain_dense = np.convolve(np.pad(gain_dense, (2, 2), mode="edge"), kernel, mode="valid")
    theta = np.arange(0.0, 91.0, 1.0)
    gain = np.interp(theta, theta_dense, gain_dense)
    return theta, gain


def rgba_line(draw: ImageDraw.ImageDraw, points, fill, width=1):
    draw.line([(float(x), float(y)) for x, y in points], fill=fill, width=width, joint="curve")


def local_panel_point(cx, cy, along, across, angle):
    ca, sa = math.cos(angle), math.sin(angle)
    return cx + along * ca - across * sa, cy + along * sa + across * ca


def draw_panel(draw: ImageDraw.ImageDraw, scale: int, origin: tuple[float, float]):
    """A shallow 2:1 conformal racetrack panel, enlarged slightly for legibility."""
    cx, cy = origin[0] * scale, origin[1] * scale
    angle = math.radians(-13.5)
    half_length, half_width = 18.0 * scale, 9.0 * scale

    # Capsule outline sampled in its own surface plane.
    pts = []
    radius = half_width
    straight = half_length - radius
    for a in np.linspace(-math.pi / 2, math.pi / 2, 24):
        pts.append(local_panel_point(cx, cy, straight + radius * math.cos(a), radius * math.sin(a), angle))
    for a in np.linspace(math.pi / 2, 3 * math.pi / 2, 24):
        pts.append(local_panel_point(cx, cy, -straight + radius * math.cos(a), radius * math.sin(a), angle))

    shadow = [(x + 1.4 * scale, y + 1.7 * scale) for x, y in pts]
    draw.polygon(shadow, fill=(20, 49, 66, 78))
    draw.polygon(pts, fill=(218, 230, 235, 246), outline=(52, 87, 105, 235), width=max(1, scale))

    inner = []
    shrink = 0.78
    for along, across in [
        (straight + radius * math.cos(a), radius * math.sin(a))
        for a in np.linspace(-math.pi / 2, math.pi / 2, 24)
    ] + [
        (-straight + radius * math.cos(a), radius * math.sin(a))
        for a in np.linspace(math.pi / 2, 3 * math.pi / 2, 24)
    ]:
        inner.append(local_panel_point(cx, cy, along * shrink, across * shrink, angle))
    draw.line(inner + [inner[0]], fill=(255, 255, 255, 176), width=max(1, scale))

    # Restrained perimeter fastener marks.
    fasteners = [(-11.5, -5.7), (0.0, -7.0), (11.5, -5.7),
                 (-11.5, 5.7), (0.0, 7.0), (11.5, 5.7)]
    for along, across in fasteners:
        x, y = local_panel_point(cx, cy, along * scale, across * scale, angle)
        rr = 0.65 * scale
        draw.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(70, 100, 115, 210))


def render(theta_deg: np.ndarray, gain_db: np.ndarray) -> tuple[Path, Path]:
    aircraft = Image.open(AIRCRAFT).convert("RGBA")
    aa = 4
    large = aircraft.resize((aircraft.width * aa, aircraft.height * aa), Image.Resampling.LANCZOS)
    overlay = Image.new("RGBA", large.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay, "RGBA")

    # Exact installation registration on the visible upper sidewall, above Door 3.
    origin = np.array([814.0, 435.0])
    origin_s = origin * aa

    # Screen projection of the antenna coordinate frame.  B is the documented
    # outward/upward 45-degree boresight; U and V span its transverse plane.
    reach = 245.0 * aa
    B = reach * np.array([math.cos(math.radians(-43.0)), math.sin(math.radians(-43.0))])
    U = reach * np.array([0.50, 0.56])
    V = reach * np.array([-0.25, 0.14])

    gmax = float(np.max(gain_db))

    def gain_at(theta):
        return float(np.interp(theta, theta_deg, gain_db))

    def point(theta, phi):
        # A conventional normalized-power polar radius makes the measured
        # fall-off at large scan angle visible without inventing beam limits.
        radius = 10.0 ** ((gain_at(theta) - gmax) / 10.0)
        t = math.radians(theta)
        p = origin_s + radius * (
            math.cos(t) * B
            + math.sin(t) * (math.cos(phi) * U + math.sin(phi) * V)
        )
        return float(p[0]), float(p[1])

    # Surface mesh first, so the physical panel remains clearly in front.
    cyan = (0, 151, 205, 132)
    cyan_faint = (0, 151, 205, 90)
    cyan_bold = (0, 127, 181, 205)

    # Meridians: data-deformed, not circular arcs.
    thetas = np.linspace(0.0, 90.0, 181)
    for phi in np.linspace(0.0, 2.0 * math.pi, 10, endpoint=False):
        rgba_line(draw, [point(t, phi) for t in thetas], cyan_faint, width=3 * aa // 2)

    # Scan-angle rings.  Ring spacing is angular; physical spacing reflects gain.
    for theta in range(15, 91, 15):
        phis = np.linspace(0.0, 2.0 * math.pi, 241)
        alpha = cyan_bold if theta in (30, 60, 90) else cyan
        rgba_line(draw, [point(theta, p) for p in phis], alpha, width=2 * aa)

    # Boresight from panel centre to the measured-pattern pole.
    pole = point(0.0, 0.0)
    rgba_line(draw, [origin_s, pole], (0, 91, 143, 230), width=2 * aa)
    direction = B / np.linalg.norm(B)
    normal = np.array([-direction[1], direction[0]])
    tip = np.array(pole)
    arrow = [
        tuple(tip),
        tuple(tip - 10.0 * aa * direction + 4.0 * aa * normal),
        tuple(tip - 10.0 * aa * direction - 4.0 * aa * normal),
    ]
    draw.polygon(arrow, fill=(0, 91, 143, 230))
    rr = 3.0 * aa
    draw.ellipse((pole[0] - rr, pole[1] - rr, pole[0] + rr, pole[1] + rr),
                 fill=(0, 91, 143, 235), outline=(230, 250, 255, 245), width=aa)

    draw_panel(draw, aa, tuple(origin))
    composed = Image.alpha_composite(large, overlay)
    composed = composed.resize(aircraft.size, Image.Resampling.LANCZOS)

    transparent = OUT / "MH370_HGA_measured_gain_overlay.png"
    white = OUT / "MH370_HGA_measured_gain_overlay_white.jpg"
    composed.save(transparent, optimize=True)
    white_bg = Image.new("RGBA", composed.size, (255, 255, 255, 255))
    flattened = Image.alpha_composite(white_bg, composed).convert("RGB")
    flattened.save(white, format="JPEG", quality=96, subsampling=0)
    return transparent, white


def save_curve(theta: np.ndarray, gain: np.ndarray) -> Path:
    path = OUT / "MH370_HGA_digitized_gain_curve.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["theta_deg", "gain_db", "normalized_field_amplitude", "normalized_power_gain"])
        gmax = float(np.max(gain))
        for t, g in zip(theta, gain):
            writer.writerow([
                f"{t:.0f}", f"{g:.4f}",
                f"{10 ** ((g - gmax) / 20):.6f}",
                f"{10 ** ((g - gmax) / 10):.6f}",
            ])
    return path


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    theta, gain = digitize_gain()
    csv_path = save_curve(theta, gain)
    transparent, white = render(theta, gain)
    print(f"gain range: {gain.min():.2f} to {gain.max():.2f} dB")
    print(transparent)
    print(white)
    print(csv_path)


if __name__ == "__main__":
    main()
