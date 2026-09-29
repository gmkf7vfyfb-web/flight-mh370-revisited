#!/usr/bin/env python3
"""Build the browser-viewable visual briefing pack for the Kadri discussion.

The pack deliberately separates measured/source-reported material, conditional
model outputs, and diagnostic screens.  It is a presentation aid generated
from already archived release artefacts; it does not create new evidence or
alter estimator weights.
"""

from __future__ import annotations

import html
import shutil
import textwrap
import zipfile
from pathlib import Path

import fitz
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon, Rectangle


REPO = Path(__file__).resolve().parents[3]
SOURCE = REPO / ".sources" / "kadri-2024-hydroacoustics"
OUT = SOURCE / "outputs" / "kadri-meeting-visual-pack"
ASSETS = OUT / "assets"

NAVY = "#102A43"
BLUE = "#167D9A"
TEAL = "#18A999"
ORANGE = "#E66A2C"
PURPLE = "#49306B"
RED = "#C63D4F"
INK = "#17212B"
MID = "#536270"
PALE = "#F4F7FA"
LINE = "#CCD6E0"
GREEN = "#3A8D5D"


def prepare() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(ASSETS / f"{stem}.png", dpi=200, facecolor=fig.get_facecolor(), bbox_inches="tight")
    fig.savefig(ASSETS / f"{stem}.svg", facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close(fig)


def base_figure(title: str, subtitle: str | None = None) -> tuple[plt.Figure, plt.Axes]:
    fig, ax = plt.subplots(figsize=(16, 9), facecolor="white")
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.text(0.55, 8.45, title, fontsize=25, fontweight="bold", color=NAVY, va="top")
    if subtitle:
        ax.text(0.57, 8.02, subtitle, fontsize=12.5, color=MID, va="top")
    ax.plot([0.55, 15.45], [7.72, 7.72], color=TEAL, lw=3)
    return fig, ax


def rounded_box(ax: plt.Axes, x: float, y: float, w: float, h: float, *,
                face: str = PALE, edge: str = LINE, radius: float = 0.18,
                lw: float = 1.2) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.02,rounding_size={radius}",
        facecolor=face, edgecolor=edge, linewidth=lw,
    )
    ax.add_patch(patch)
    return patch


def wrapped(ax: plt.Axes, x: float, y: float, text: str, width: int,
            *, size: float = 12, color: str = INK, weight: str = "normal",
            va: str = "top", linespacing: float = 1.25, ha: str = "left") -> None:
    ax.text(x, y, textwrap.fill(text, width), fontsize=size, color=color,
            fontweight=weight, va=va, ha=ha, linespacing=linespacing)


def arrow(ax: plt.Axes, start: tuple[float, float], end: tuple[float, float],
          *, color: str = BLUE, lw: float = 2.3, style: str = "-|>") -> None:
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle=style,
                                mutation_scale=16, linewidth=lw, color=color))


def extract_dissertation_figures() -> None:
    pdf = REPO / ".sources" / "large-2019-antenna-gain" / "paper" / "paper.pdf"
    doc = fitz.open(pdf)
    selections = {
        "01a-dissertation-route-1642-1822": (56, 172),
        "01b-dissertation-bto-arcs-and-solutions": (231, 1039),
    }
    for stem, (_page, xref) in selections.items():
        image = doc.extract_image(xref)
        (ASSETS / f"{stem}.{image['ext']}").write_bytes(image["image"])

    route = plt.imread(ASSETS / "01a-dissertation-route-1642-1822.png")
    arcs = plt.imread(ASSETS / "01b-dissertation-bto-arcs-and-solutions.png")
    fig, ax = base_figure(
        "MH370: from a known radar track to satellite-range arcs",
        "Original dissertation graphics; background charts credited there to SkyVector",
    )
    left = fig.add_axes([0.045, 0.175, 0.42, 0.60])
    left.imshow(route)
    left.axis("off")
    right = fig.add_axes([0.49, 0.175, 0.47, 0.60])
    right.imshow(arcs)
    right.axis("off")
    ax.text(0.72, 0.72, "1  Recorded track to final primary radar contact", fontsize=12,
            fontweight="bold", color=NAVY)
    ax.text(8.05, 0.72, "2  Thereafter: BTO range arcs constrain distance, not a unique path",
            fontsize=12, fontweight="bold", color=NAVY)
    save_figure(fig, "01-mh370-overview-dissertation")


def copy_release_assets() -> None:
    copies = {
        REPO / "runs/mh370/release-v0.1/posterior-search-context/posterior-evolution-search-context.png":
            "02-posterior-evolution-search-context.png",
        REPO / "runs/mh370/release-v0.1/posterior-search-context/posterior-evolution-search-context.svg":
            "02-posterior-evolution-search-context.svg",
        REPO / "runs/mh370/release-v0.1/impact/publication/impact-dynamics-comparison.png":
            "03a-impact-dynamics-comparison.png",
        REPO / "runs/mh370/release-v0.1/impact/publication/impact-dynamics-comparison.svg":
            "03a-impact-dynamics-comparison.svg",
        SOURCE / "outputs/impact-pressure-by-station.png":
            "03c-impact-pressure-by-station.png",
        SOURCE / "outputs/simulated-pressure-time-series.png":
            "03d-simulated-pressure-time-series.png",
        SOURCE / "outputs/simulated-pressure-spectrograms.png":
            "03e-simulated-pressure-spectrograms.png",
        SOURCE / "outputs/release-v0.1/hydroacoustic-forward-reverse-diagnostic.png":
            "04b-forward-reverse-release-diagnostic.png",
        SOURCE / "outputs/release-v0.1/hydroacoustic-forward-reverse-diagnostic.svg":
            "04b-forward-reverse-release-diagnostic.svg",
        SOURCE / "outputs/potential-signals-summary-infographic.png":
            "05-potential-signals-summary.png",
        SOURCE / "outputs/candidate-bearing-and-timing-overview.png":
            "05b-candidate-bearing-and-timing-overview.png",
        SOURCE / "outputs/aligned-local-energy-oscar-v2-final-mode.png":
            "08a-oscar-source-time-alignment.png",
        SOURCE / "outputs/oscar-boundary-aware-coincidence-audit.png":
            "08b-oscar-boundary-aware-audit.png",
        SOURCE / "outputs/filtered-acquisition-response-overview.png":
            "08c-filtered-complete-acquisition-scan.png",
        SOURCE / "outputs/airgun-cycle-energy-distribution.png":
            "09b-airgun-cycle-energy-distribution.png",
        SOURCE / "outputs/subsecond-periodic-mask-comparison.png":
            "09c-subsecond-mask-comparison.png",
    }
    for source, name in copies.items():
        if source.exists():
            shutil.copy2(source, ASSETS / name)


def impact_state_graphic() -> None:
    fig, ax = base_figure(
        "From end-of-flight state to a received pressure scale",
        "The present sensitivity model samples vertical contact speed and coupling; impact attitude remains unresolved",
    )

    # Schematic impact angles.
    rounded_box(ax, 0.55, 4.55, 5.15, 2.78, face="#F8FAFC")
    ax.text(0.85, 7.02, "Impact geometry: still an explicit unknown", fontsize=15,
            fontweight="bold", color=NAVY)
    ax.plot([0.9, 5.35], [5.05, 5.05], color=BLUE, lw=5)
    ax.fill_between([0.9, 5.35], 4.6, 5.05, color="#D9F0F7")
    scenarios = [
        ((1.55, 5.52), (2.55, 5.08), "shallow / ditching", TEAL),
        ((2.55, 6.15), (3.55, 5.08), "oblique", ORANGE),
        ((4.55, 6.37), (4.70, 5.08), "steep / high descent", RED),
    ]
    for start, end, label, colour in scenarios:
        arrow(ax, start, end, color=colour, lw=3)
        ax.scatter([start[0]], [start[1]], marker=(3, 0, -35), s=210, color=colour)
        ax.text(start[0], start[1] + 0.20, label, fontsize=10.5, ha="center", color=colour,
                fontweight="bold")
    wrapped(ax, 0.88, 4.84,
            "Current families are vertical-contact-speed families—not recovered pitch, roll, yaw, breakup or water-entry histories.",
            68, size=9.1, color=MID)

    # Transfer chain.
    stages = [
        (6.15, "Impact state", "mass • 3-D velocity\nattitude • duration"),
        (8.52, "Water entry", "force/pressure history\nbreakup • sea state"),
        (10.89, "Coupling", "acoustic + acoustic–\ngravity source modes"),
        (13.26, "Propagation", "bathymetry • ocean\narray response"),
    ]
    for x, heading, body in stages:
        rounded_box(ax, x, 5.05, 1.82, 1.75, face="#EEF4F8", edge="#A7BBCB")
        ax.text(x + 0.91, 6.40, heading, fontsize=11.5, fontweight="bold", ha="center", color=NAVY)
        ax.text(x + 0.91, 5.78, body, fontsize=8.3, ha="center", va="center", color=MID,
                linespacing=1.3)
    for x in [8.01, 10.38, 12.75]:
        arrow(ax, (x, 5.92), (x + 0.35, 5.92), color=TEAL, lw=2)

    # Time/energy tendency.
    rounded_box(ax, 0.55, 0.58, 9.55, 3.45, face="#FAFBFC")
    ax.text(0.85, 3.72, "Timing and energy: a physical tendency, not yet a fitted joint prior", fontsize=15,
            fontweight="bold", color=NAVY)
    x0, x1, y = 1.0, 9.55, 1.55
    ax.plot([x0, x1], [y, y], color=NAVY, lw=2)
    ticks = [(0, "00:19"), (4, "00:23"), (19, "00:38"), (31, "00:50")]
    for minute, label in ticks:
        x = x0 + (minute / 31.0) * (x1 - x0)
        ax.plot([x, x], [y - 0.12, y + 0.12], color=NAVY, lw=1.5)
        ax.text(x, y - 0.35, label, ha="center", fontsize=10.5, color=INK)
    xx = np.linspace(x0, x1, 240)
    centre = 3.1 - 1.25 * (xx - x0) / (x1 - x0)
    width = 0.22 + 0.38 * (xx - x0) / (x1 - x0)
    ax.fill_between(xx, centre - width, centre + width, color=ORANGE, alpha=0.18)
    ax.plot(xx, centre, color=ORANGE, lw=3)
    ax.text(1.05, 3.17, "higher average vertical-energy potential", fontsize=10.5,
            fontweight="bold", color=ORANGE)
    ax.text(6.50, 1.93, "longer glide tends towards lower-energy families", fontsize=9.8,
            fontweight="bold", color=BLUE)
    wrapped(ax, 0.98, 1.05,
            "Important: a long glide can still end in a steep descent; location/time must not deterministically set impact energy.",
            100, size=8.7, color=RED, weight="bold")

    # Numeric summary cards.
    cards = [
        (10.55, 2.65, "0.59–1.71 GJ", "total kinetic-energy medians\nacross tested estimator families"),
        (13.15, 2.65, "10⁻⁸–10⁻²", "source-to-SOFAR coupling\nsensitivity range"),
        (10.55, 0.78, "0.025–0.786 Pa", "H01W median pressure proxies\nacross contact-speed families"),
        (13.15, 0.78, "0.014–0.439 Pa", "H08S median pressure proxies\nacross contact-speed families"),
    ]
    for x, yy, value, label in cards:
        rounded_box(ax, x, yy, 2.30, 1.47, face="#F1F6F9", edge="#9BB3C3")
        ax.text(x + 1.15, yy + 0.94, value, fontsize=14.2, fontweight="bold", color=PURPLE, ha="center")
        ax.text(x + 1.15, yy + 0.42, label, fontsize=8.0, color=MID, ha="center", va="center")
    save_figure(fig, "03b-impact-state-to-pressure")


def two_directions_graphic() -> None:
    fig, ax = base_figure(
        "Two complementary questions",
        "Forward prediction asks what the stations should receive; backward reconstruction asks where a measured event could have originated",
    )
    # Forward half.
    rounded_box(ax, 0.55, 0.80, 7.15, 6.45, face="#F0F8F8", edge="#A3D8D1")
    ax.text(1.0, 6.85, "FORWARD", fontsize=20, fontweight="bold", color=TEAL)
    ax.text(1.0, 6.48, "impact particle → station predictions", fontsize=12.5, color=MID)
    fboxes = [
        (1.05, 4.98, "Impact ensemble", "time • place • state"),
        (3.25, 4.98, "Source model", "energy • spectrum\n• duration"),
        (5.45, 4.98, "H01W + H08S", "arrival • bearing\n• waveform"),
    ]
    for x, y, h, b in fboxes:
        rounded_box(ax, x, y, 1.72, 1.06, face="white", edge="#76BEB5")
        ax.text(x + .86, y + .70, h, fontsize=10.8, ha="center", fontweight="bold", color=NAVY)
        ax.text(x + .86, y + .28, b, fontsize=7.6, ha="center", color=MID, va="center")
    arrow(ax, (2.79, 5.51), (3.17, 5.51), color=TEAL)
    arrow(ax, (4.99, 5.51), (5.37, 5.51), color=TEAL)
    ax.text(1.05, 4.28, "Current safe output", fontsize=11.2, fontweight="bold", color=GREEN)
    wrapped(ax, 1.05, 4.00,
            "Station-specific arrival windows and broad energy/pressure observables for every impact state.",
            54, size=11)
    ax.text(1.05, 2.95, "Next calibrated output", fontsize=11.2, fontweight="bold", color=ORANGE)
    wrapped(ax, 1.05, 2.67,
            "A pre-registered coherent detector evaluated through injection recovery and off-source false-alarm controls.",
            54, size=11)
    ax.text(1.05, 1.83, "Question answered", fontsize=9.8, fontweight="bold", color=NAVY)
    wrapped(ax, 1.05, 1.54, "If MH370 ended here in this state, what should each array have seen?", 44, size=10.3, weight="bold")

    # Backward half.
    rounded_box(ax, 8.30, 0.80, 7.15, 6.45, face="#FAF5F1", edge="#E1B898")
    ax.text(8.75, 6.85, "BACKWARD", fontsize=20, fontweight="bold", color=ORANGE)
    ax.text(8.75, 6.48, "station data → conditional source geometry", fontsize=12.5, color=MID)
    bboxes = [
        (8.80, 4.98, "Triad data", "time • pressure\n• phase"),
        (11.00, 4.98, "Array processing", "bearing • event time"),
        (13.20, 4.98, "Source region", "arc crossing\n• impact time"),
    ]
    for x, y, h, b in bboxes:
        rounded_box(ax, x, y, 1.72, 1.06, face="white", edge="#D8A47B")
        ax.text(x + .86, y + .70, h, fontsize=10.8, ha="center", fontweight="bold", color=NAVY)
        ax.text(x + .86, y + .28, b, fontsize=7.6, ha="center", color=MID, va="center")
    arrow(ax, (10.54, 5.51), (10.92, 5.51), color=ORANGE)
    arrow(ax, (12.74, 5.51), (13.12, 5.51), color=ORANGE)
    ax.text(8.80, 4.28, "Publication traces permit", fontsize=11.2, fontweight="bold", color=GREEN)
    wrapped(ax, 8.80, 4.00,
            "Geometry and timing demonstrations, plus conservative signal screens.",
            52, size=11)
    ax.text(8.80, 2.95, "Raw arrays are required for", fontsize=11.2, fontweight="bold", color=ORANGE)
    wrapped(ax, 8.80, 2.67,
            "Coherent bearing recovery, calibrated pressure, propagation-aware association and a defensible likelihood.",
            52, size=11)
    ax.text(8.80, 1.83, "Question answered", fontsize=9.8, fontweight="bold", color=NAVY)
    wrapped(ax, 8.80, 1.54, "If this is a real common event, which source states remain compatible?", 43, size=10.3, weight="bold")
    save_figure(fig, "04-two-complementary-directions")


def backward_workflow_graphic() -> None:
    fig, ax = base_figure(
        "Backward reconstruction: from a coherent arrival to conditional source geometry",
        "Bearing and travel time are complementary constraints; neither alone identifies an aircraft impact",
    )
    stages = [
        (0.65, "1", "Raw triad", "three calibrated\nchannels + timing"),
        (3.15, "2", "Detect +\nbeamform", "arrival • bearing\ncoherence • uncertainty"),
        (5.65, "3", "Propagate\nback", "celerity/dispersion\npath uncertainty"),
        (8.15, "4", "Intersect\ngeometry", "7th arc + spatial prior\nsource-time window"),
        (10.65, "5", "Cross-station\ntest", "predict H08S arrival\n+ bearing from H01W"),
        (13.15, "6", "Conditional\nupdate", "association likelihood\nincluding false alarms"),
    ]
    for i, (x, n, h, b) in enumerate(stages):
        rounded_box(ax, x, 4.55, 2.15, 2.05, face="#F6F9FB", edge="#9DB2C1")
        ax.add_patch(plt.Circle((x + .33, 6.25), .20, color=BLUE))
        ax.text(x + .33, 6.25, n, ha="center", va="center", color="white", fontsize=11, fontweight="bold")
        ax.text(x + 1.08, 5.92, h, ha="center", va="center", fontsize=9.7, fontweight="bold", color=NAVY, linespacing=1.05)
        ax.text(x + 1.08, 5.18, b, ha="center", va="center", fontsize=8.0, color=MID, linespacing=1.28)
        if i < len(stages) - 1:
            arrow(ax, (x + 2.17, 5.56), (x + 2.45, 5.56), color=TEAL, lw=2)

    rounded_box(ax, 0.70, 1.05, 6.85, 2.65, face="#EEF8F5", edge="#A8D2C2")
    ax.text(1.05, 3.33, "A credible H01W-only product", fontsize=14, fontweight="bold", color=GREEN)
    wrapped(ax, 1.05, 2.95,
            "Detect apparent events, estimate a bearing with the H01W three-sensor geometry, project the bearing onto the seventh arc, and calculate an impact-time distribution. Compare—not fuse—this conditional geometry with the independent flight/BTO/BFO/drift posterior.",
            61, size=9.4)

    rounded_box(ax, 8.05, 1.05, 7.25, 2.65, face="#FFF5EE", edge="#E5B38E")
    ax.text(8.40, 3.33, "What changes when H08S is included", fontsize=14, fontweight="bold", color=ORANGE)
    wrapped(ax, 8.40, 2.95,
            "The predicted arrival-time difference and two independent bearings sharply strengthen—or reject—the common-source hypothesis. This is useful only after directional airgun interference is modelled and the full search/selection process is calibrated.",
            62, size=9.4)
    save_figure(fig, "06-backward-reconstruction-workflow")


def forward_workflow_graphic() -> None:
    fig, ax = base_figure(
        "Forward prediction: carry complete impact particles to both arrays",
        "The scientifically useful unit is a weighted impact state—not a two-dimensional crash map",
    )
    x_positions = [0.65, 3.15, 5.65, 8.15, 10.65, 13.15]
    headings = [
        ("Estimator\nparticle", "time • latitude • longitude\nmass • 3-D velocity • attitude"),
        ("Water-entry\nfamily", "duration • breakup • sea state\nsource pressure history"),
        ("Mode\ncoupling", "acoustic / AGW alternatives\nexplicit η uncertainty"),
        ("Path\nmodel", "bathymetry • sound speed\nGreen function / emulator"),
        ("Station\nprediction", "H01W + H08S arrival\nbearing • pressure • waveform"),
        ("Detection\nmodel", "coherent statistic\ninjection recovery • PFA"),
    ]
    colours = [BLUE, ORANGE, PURPLE, TEAL, BLUE, RED]
    for i, (x, (h, b), colour) in enumerate(zip(x_positions, headings, colours)):
        rounded_box(ax, x, 4.57, 2.15, 2.12, face="white", edge=colour, lw=1.8)
        ax.add_patch(Rectangle((x, 6.35), 2.15, .34, color=colour, clip_on=False))
        ax.text(x + 1.075, 5.93, h, ha="center", va="center", fontsize=9.8, fontweight="bold", color=NAVY, linespacing=1.0)
        ax.text(x + 1.075, 5.15, b, ha="center", va="center", fontsize=7.7, color=MID, linespacing=1.25)
        if i < 5:
            arrow(ax, (x + 2.17, 5.62), (x + 2.45, 5.62), color="#78909C", lw=2)

    rounded_box(ax, 0.70, 1.03, 7.25, 2.72, face="#EFF8F5", edge="#A1D0BE")
    ax.text(1.05, 3.39, "Implemented predictive-only boundary", fontsize=14.5, fontweight="bold", color=GREEN)
    wrapped(ax, 1.05, 3.00,
            "The lean spoke already returns station-specific arrival windows, coupled-energy, pressure-squared exposure and RMS-pressure intervals under named source, propagation, path and station-response families. It accepts no observed signal and therefore cannot silently manufacture a likelihood.",
            64, size=9.3)

    rounded_box(ax, 8.45, 1.03, 6.85, 2.72, face="#FFF4EE", edge="#E6AF87")
    ax.text(8.80, 3.39, "Next-generation scientific increment", fontsize=14.5, fontweight="bold", color=ORANGE)
    wrapped(ax, 8.80, 3.00,
            "Replace range-only pressure scaling with source spectra from water-entry simulations and path-specific transfer functions, then run a pre-registered matched-subspace search at both arrays. Calibrate complete-search maxima using blinded injections and contemporaneous noise.",
            59, size=9.3)
    save_figure(fig, "07-forward-prediction-workflow")


def airgun_filter_graphic() -> None:
    fig, ax = base_figure(
        "Diego Garcia: turn the airgun train into a modelled nuisance source",
        "The 9.9-second periodicity is information: a vessel-track-informed shot clock can improve prediction, masking and subtraction",
    )

    # Survey vessel geometry.
    sea = Polygon([(0.55, 4.55), (7.55, 4.55), (7.55, 7.18), (0.55, 7.18)], closed=True,
                  facecolor="#E8F5F9", edgecolor="#A5C8D5")
    ax.add_patch(sea)
    for i, yy in enumerate([4.92, 5.45, 5.98, 6.51]):
        if i % 2 == 0:
            xs = [1.0, 6.8]
        else:
            xs = [6.8, 1.0]
        ax.plot(xs, [yy, yy], color=BLUE, lw=2.5)
        ax.scatter(np.linspace(min(xs), max(xs), 10), [yy] * 10, s=20, color=ORANGE, zorder=3)
    ax.scatter([6.8], [6.51], marker=(3, 0, -30), s=330, color=NAVY, zorder=5)
    ax.text(0.85, 6.93, "1  AIS / navigation track", fontsize=13.5, fontweight="bold", color=NAVY)
    ax.text(0.85, 4.68, "parallel survey lines • shots triggered by distance • GPS/UTC timestamps", fontsize=10.5, color=MID)

    # Clock model.
    rounded_box(ax, 8.02, 4.55, 3.22, 2.63, face="#F8FAFC", edge="#A7BBCB")
    ax.text(8.32, 6.83, "2  Reconstruct shot clock", fontsize=11.8, fontweight="bold", color=NAVY)
    ax.text(8.42, 6.35, "sₙ = s₀ + nΔs", fontsize=18, color=PURPLE, fontweight="bold")
    ax.text(8.42, 5.93, "tₙ from interpolated vessel speed", fontsize=9.2, color=MID)
    ax.text(8.42, 5.52, "τⱼ(tₙ) from moving-source propagation", fontsize=9.2, color=MID)
    ax.text(8.42, 5.10, "predict arrival, bearing and drift", fontsize=9.2, color=MID)
    arrow(ax, (7.64, 5.84), (8.02, 5.84), color=TEAL)

    # Array.
    rounded_box(ax, 11.72, 4.55, 3.73, 2.63, face="#FFF8F3", edge="#DDB18F")
    ax.text(12.04, 6.83, "3  Use the H08S triad", fontsize=11.8, fontweight="bold", color=NAVY)
    pts = np.array([[12.55, 5.52], [13.55, 6.02], [14.45, 5.28]])
    ax.scatter(pts[:, 0], pts[:, 1], s=110, color=ORANGE, edgecolor="white", lw=1.2)
    for i, (xx, yy) in enumerate(pts, start=1):
        ax.text(xx, yy - .28, f"H{i}", ha="center", fontsize=9.5, color=MID)
    ax.text(12.02, 4.86, "exploit TDOA + direction—not only time masks", fontsize=8.6, color=MID)
    arrow(ax, (11.32, 5.84), (11.77, 5.84), color=TEAL)

    strategies = [
        (0.70, "A  Directional null / beamforming", "Estimate the airgun bearing on each shot and form a coherent spatial null while preserving arrivals from other bearings."),
        (5.85, "B  Cycle-synchronous subtraction", "Fit robust multi-channel shot templates with slowly varying amplitude, phase and path; subtract with held-out cycles."),
        (11.00, "C  Mask + multi-channel reconstruction", "Mask only predicted contaminated samples, then use unmasked sensors/time-frequency bins; never treat interpolation as observed data."),
    ]
    for x, h, body in strategies:
        rounded_box(ax, x, 1.02, 4.35, 2.73, face="#F7F9FB", edge="#B7C4CF")
        ax.text(x + .28, 3.37, h, fontsize=13.2, fontweight="bold", color=NAVY)
        wrapped(ax, x + .28, 3.00, body, 45, size=9.2)
    ax.text(0.75, 0.63,
            "Proof of concept: hourly AIS can locate the survey. For shot-level filtering, request the highest-rate navigation/shot log—ideally 1 s or better—with array geometry and raw channels.",
            fontsize=10.5, color=RED, fontweight="bold")
    save_figure(fig, "09-airgun-nuisance-source-model")


def bayesian_integration_graphic() -> None:
    fig, ax = base_figure(
        "How hydroacoustics can enter the Bayesian estimator",
        "Two routes are valid—but they answer different questions and require different evidence",
    )

    # Prior/core.
    rounded_box(ax, 0.70, 5.17, 3.10, 1.72, face="#EEF4F8", edge="#9DB7C8")
    ax.text(2.25, 6.43, "Core impact particles", fontsize=12.0, fontweight="bold", color=NAVY, ha="center")
    ax.text(2.25, 5.82, "flight + BTO/BFO + terminal flight\n+ optional drift conditionals", fontsize=10.2,
            color=MID, ha="center", va="center")
    arrow(ax, (3.85, 6.03), (4.45, 6.03), color=BLUE)

    # Conditional path.
    rounded_box(ax, 4.52, 4.30, 4.72, 2.87, face="#EFF8F5", edge="#9FCEBA")
    ax.text(4.88, 6.77, "ROUTE A — conditional / predictive now", fontsize=11.6, fontweight="bold", color=GREEN)
    ax.text(4.90, 6.26, "p(ŷhydro | x, M)", fontsize=17, color=PURPLE, fontweight="bold")
    wrapped(ax, 4.90, 5.83,
            "For each weighted impact particle, generate arrival, bearing and pressure/waveform envelopes under explicit model families. Compare candidate events as conditional hypotheses or posterior-predictive checks.",
            47, size=9.2)
    ax.text(4.90, 4.62, "No change to particle weights", fontsize=11.2, color=GREEN, fontweight="bold")

    # Integrated path.
    rounded_box(ax, 9.72, 4.30, 5.58, 2.87, face="#FFF4EE", edge="#E2AE86")
    ax.text(10.08, 6.77, "ROUTE B — integrated evidence later", fontsize=11.6, fontweight="bold", color=ORANGE)
    ax.text(10.10, 6.26, "wᵢ′ ∝ wᵢ · p(y | xᵢ, H₁) / p(y | H₀)", fontsize=15.5,
            color=PURPLE, fontweight="bold")
    wrapped(ax, 10.10, 5.83,
            "Update weights only through a named observed-signal model that includes event association, detectability, no-detection probability, background/interference and complete-search selection correction.",
            57, size=9.2)
    ax.text(10.10, 4.62, "Can change location and end-of-flight posteriors", fontsize=11.2, color=ORANGE, fontweight="bold")

    # Requirements.
    rounded_box(ax, 0.70, 0.86, 14.60, 2.78, face="#F8FAFC", edge="#BBC8D2")
    ax.text(1.05, 3.28, "Minimum evidence needed before Route B is defensible", fontsize=14.5, fontweight="bold", color=NAVY)
    requirements = [
        "raw calibrated H01W and H08S triad channels with clocks, geometry and response",
        "complete candidate catalogue and exact original filters / selection rule",
        "contemporaneous off-source noise plus explicit airgun source timing and direction",
        "path- and mode-specific propagation uncertainty or Green functions",
        "blinded source injections and end-to-end recovery / false-alarm calibration",
        "a pre-registered search bank covering the full time, position and template trials",
    ]
    for i, item in enumerate(requirements):
        col = 0 if i < 3 else 1
        row = i if i < 3 else i - 3
        x = 1.05 + col * 7.05
        y = 2.80 - row * .62
        ax.add_patch(plt.Circle((x + .10, y + .03), .09, color=TEAL if col == 0 else ORANGE))
        wrapped(ax, x + .30, y + .12, item, 49, size=9.0, va="top")
    ax.text(8.0, 0.53,
            "Present status: publication-trace diagnostics receive zero evidential weight (likelihood_evaluated = false).",
            fontsize=10.8, color=RED, fontweight="bold", ha="center")
    save_figure(fig, "10-bayesian-integration-routes")


def collaboration_graphic() -> None:
    fig, ax = base_figure(
        "Proposed collaboration: smallest steps that can change the science",
        "A staged programme keeps reproducibility, selection correction and model-family uncertainty explicit",
    )
    columns = [
        (0.65, "1  Data\nhandoff", "Raw H01W/H08S triads\n+ adjacent control windows\n+ timing/response metadata", BLUE),
        (3.65, "2  Exact\nreproduction", "Kadri processing chain\n+ candidate catalogue\n+ extended reception window", TEAL),
        (6.65, "3  Interference\nmodel", "Airgun shot clock + bearing\n+ vessel/shot navigation\n+ coherent subtraction controls", ORANGE),
        (9.65, "4  Physical\ntemplate bank", "impact-state emulator\n+ acoustic/AGW families\n+ path-specific propagation", PURPLE),
        (12.65, "5  Blinded\nvalidation", "injection recovery\n+ complete-search false alarms\n+ conditional Bayes factors", RED),
    ]
    for x, h, b, colour in columns:
        rounded_box(ax, x, 3.72, 2.70, 3.10, face="white", edge=colour, lw=1.8)
        ax.add_patch(Rectangle((x, 6.49), 2.70, .33, color=colour))
        ax.text(x + 1.35, 6.02, h, fontsize=10.2, ha="center", va="center", fontweight="bold", color=NAVY, linespacing=1.0)
        ax.text(x + 1.35, 4.98, b, fontsize=8.3, ha="center", va="center", color=MID, linespacing=1.35)
        if x < 12:
            arrow(ax, (x + 2.72, 5.25), (x + 2.95, 5.25), color="#8296A6", lw=1.8)

    rounded_box(ax, 0.70, 1.05, 7.05, 1.90, face="#EEF8F5", edge="#9FCEBA")
    ax.text(1.05, 2.58, "Useful result even if no event is identified", fontsize=14, fontweight="bold", color=GREEN)
    wrapped(ax, 1.05, 2.17,
            "Calibrated upper limits on detectable impact-energy/coupling families can provide disconfirming evidence about high-energy end-of-flight scenarios.",
            58, size=9.3)

    rounded_box(ax, 8.25, 1.05, 7.05, 1.90, face="#FFF4EE", edge="#E2AE86")
    ax.text(8.60, 2.58, "Meeting decision to seek", fontsize=14, fontweight="bold", color=ORANGE)
    wrapped(ax, 8.60, 2.17,
            "Agree a limited raw-data pilot: one station, one control window, one blinded injection protocol—then expand to two-station association only if the pilot recovers direction and false-alarm behaviour.",
            58, size=9.3)
    save_figure(fig, "11-collaboration-roadmap")


SLIDES = [
    {
        "n": "01", "title": "MH370 overview: known track → range arcs",
        "asset": "01-mh370-overview-dissertation.png",
        "alt": ["01a-dissertation-route-1642-1822.png", "01b-dissertation-bto-arcs-and-solutions.png"],
        "tag": "Source graphic",
        "takeaway": "Radar substantially constrains the early diversion; the later Inmarsat BTO observations constrain range to the satellite, leaving a family of possible tracks and a final seventh arc rather than a unique point.",
        "notes": "Open with the distinction between observations and inference. The left graphic is Figure 2 from Large (2019): the route from Kuala Lumpur through IGARI, across Peninsular Malaysia, past Penang and west towards the final primary-radar region. The right graphic is Figure 77 from the same dissertation and shows how successive BTO arcs admit multiple locations and headings. Both graphics retain their SkyVector background and the original ‘Not for Navigation’ status. This slide is context, not a current posterior result.",
    },
    {
        "n": "02", "title": "Posterior evolution: 00:11 state to conditional impact",
        "asset": "02-posterior-evolution-search-context.png", "alt": [], "tag": "Estimator output",
        "takeaway": "The archived release moves from a 00:11 BTO+BFO posterior (purple), through the corrected 00:19 BTO constraint (teal), to a conditional terminal-flight impact family (orange), shown against the seventh arc and search context.",
        "notes": "Emphasise that the states are sequential and dependent. The impact contours are conditional on the selected end-of-flight family; they are not a universal crash posterior. The primary release family has a median impact near 00:37:49 UTC and a mean near 38.16°S, 89.41°E. The figure also shows why the independent location posterior is valuable when screening hydroacoustic geometry: it provides an external compatibility distribution without letting the acoustic candidate define its own prior.",
    },
    {
        "n": "03", "title": "Impact state, timing, energy and received pressure",
        "asset": "03b-impact-state-to-pressure.png",
        "alt": ["03a-impact-dynamics-comparison.png", "03c-impact-pressure-by-station.png", "03d-simulated-pressure-time-series.png", "03e-simulated-pressure-spectrograms.png"],
        "tag": "Conditional sensitivity",
        "takeaway": "Earlier impacts are more likely, on average, to retain high vertical energy; longer glides tend towards gentler families, but this is a tendency—not a deterministic mapping. The current acoustic experiment models vertical contact speed and coupling, not impact attitude.",
        "notes": "The estimator’s tested family medians span about 0.59–1.71 GJ total kinetic energy and approximately 00:23–00:50 UTC impact times. The reduced acoustic study instead uses normal kinetic energy E_n = ½mv_z² with 174,369 kg as a fuel-exhaustion mass surrogate. It samples four vertical-speed families and coupling from 10⁻⁸ to 10⁻²; one sensitivity prior is centred near 10⁻⁴. Median pressure proxies span 0.025–0.786 Pa at H01W and 0.014–0.439 Pa at H08S. These are amplitude scales, not detection probabilities. Pitch, roll, yaw, horizontal speed, breakup, contact duration, sea state and path-specific response remain unresolved.",
    },
    {
        "n": "04", "title": "Forward and backward analyses answer different questions",
        "asset": "04-two-complementary-directions.png", "alt": ["04b-forward-reverse-release-diagnostic.png"],
        "tag": "Analysis architecture",
        "takeaway": "Forward modelling starts with impact hypotheses and predicts station observables; backward analysis starts with a coherent measured event and reconstructs compatible source states. Agreement is powerful only when selection and false alarms are handled end to end.",
        "notes": "Use the GPS analogy carefully. We can step a template bank across source position, source time and propagation state, but we do not have a known PRN waveform and the two ocean paths can distort the source differently. A matched-subspace or generalised-likelihood search is therefore more defensible than simple pressure-trace correlation. The archived 5 NM grid contains 5,289 source boxes, 32 unweighted scenario templates, 169,248 source-scenario combinations and 338,496 station predictions. All current publication-trace comparisons have zero estimator weight.",
    },
    {
        "n": "05", "title": "Signals and intersections already discussed",
        "asset": "05-potential-signals-summary.png", "alt": ["05b-candidate-bearing-and-timing-overview.png"],
        "tag": "Source report + diagnostic",
        "takeaway": "Two Table 1 bearings cross independent spatial-PDF support, but neither time is a q99 peak in the published H01W trace. The preferred 306.18° candidate meets the seventh arc far north of high posterior density. All H08S examples remain airgun-confounded.",
        "notes": "Keep the candidate identities separate. Kadri Figure 9 rectangle 1 is approximately 00:52 UTC at 57°. Rectangle 2 is the preferred approximately 00:54:30 UTC at 306.18°; the prose appears to conflate them. Table 1 includes 00:49:58 at 260.41° and 00:53:31 at 257.58°; their arc crossings lie near 35.88°S and 36.74°S and within 64% and 40% HPD respectively, but the signals are not visually recovered as high local-energy peaks from the published trace. The visually interesting OSCAR pair implies about 00:29:40 UTC, but the H08S feature is boundary/periodic-airgun affected and has a matched-window empirical p-value of 0.632.",
    },
    {
        "n": "06", "title": "Backward method: measured event → source constraints",
        "asset": "06-backward-reconstruction-workflow.png", "alt": [], "tag": "Proposed method",
        "takeaway": "H01W alone can yield a conditional bearing–arc intersection and source-time distribution. H08S adds a strong independent test through arrival-time difference and a second bearing—provided the airgun field is controlled.",
        "notes": "A rigorous backward pipeline begins with raw calibrated triad channels, not digitised plot lines. Detection and beamforming should jointly return arrival time, bearing, coherence and uncertainty. Travel-time and acoustic/AGW model families then map the arrival back to a source-time and spatial band. The seventh-arc intersection and independent location posterior are compatibility tests. When H08S is added, the H01W candidate predicts a narrow arrival/bearing family at Diego Garcia; non-observation can be informative only after station sensitivity and interference-dependent detectability are calibrated.",
    },
    {
        "n": "07", "title": "Forward method: impact ensemble → both arrays",
        "asset": "07-forward-prediction-workflow.png", "alt": [], "tag": "Implemented boundary + proposal",
        "takeaway": "Carry each complete impact particle through water-entry, coupling, path and station-response families. Search the raw arrays with the resulting uncertain template subspace and calibrate the maximum over the whole bank.",
        "notes": "The first lean spoke already predicts station-specific arrival intervals, coupled-energy, pressure-squared exposure and RMS pressure without reading an observed trace. The next useful scientific increment is to propagate complete weighted impact particles—not a uniform source grid—and replace the range-only pressure law with a source emulator and path transfer functions. Model families must remain explicit: ordinary acoustic versus acoustic–gravity propagation, alternative ocean states, bathymetric coupling and station response are structural alternatives, not ordinary sampling error.",
    },
    {
        "n": "08", "title": "Correlation idea: interesting alignment, failed association control",
        "asset": "08a-oscar-source-time-alignment.png",
        "alt": ["08b-oscar-boundary-aware-audit.png", "08c-filtered-complete-acquisition-scan.png"],
        "tag": "Diagnostic only",
        "takeaway": "A visually close H01W–H08S source-time alignment exists near 00:29:40 UTC for an OSCAR-conditioned location, but H08S is dominated by periodic structure and the apparent match is not unusual under matched controls.",
        "notes": "This is a useful example of why the complete search matters. The H01W feature is strong in the digitised panel, while the apparent H08S partner sits at the cropped boundary of a 9.93-second airgun train. The boundary-aware matched-window control gives p = 0.632. Across 5,289 cells and 41 propagation offsets, the rank-8 filtered maximum correlation is r = 0.109 versus an IAAFT null q95 of 0.160, scan-adjusted p = 0.964; the unfiltered maximum is r = 0.120, scan-adjusted p = 1.000. The plots therefore motivate a raw-data search but do not establish a common event or source location.",
    },
    {
        "n": "09", "title": "Airgun interference: predict, beamform and subtract",
        "asset": "09-airgun-nuisance-source-model.png", "alt": ["09b-airgun-cycle-energy-distribution.png", "09c-subsecond-mask-comparison.png"],
        "tag": "Proposed method",
        "takeaway": "Treat the seismic survey as a moving, directional nuisance source. A vessel/shot navigation log can predict each shot’s emission and station arrival, while the triad geometry provides an independent directional discriminator.",
        "notes": "The nearly fixed 9.9-second station cadence probably varies because shots are triggered by distance rather than by a perfect clock and because the vessel and path move. Interpolated high-rate AIS or, preferably, the original navigation/shot log can reconstruct emission times. From the moving source we predict travel time and bearing to each H08S element. Three complementary filters should be compared on held-out shots: a directional beamforming null; cycle-synchronous multi-channel template subtraction; and tightly predicted masks followed by analysis of only genuinely observed, uncontaminated channels/time-frequency bins. Hourly AIS is enough to locate the survey, not to time individual shots.",
    },
    {
        "n": "10", "title": "Bayesian use: conditional hypotheses now, likelihood later",
        "asset": "10-bayesian-integration-routes.png", "alt": [], "tag": "Estimator boundary",
        "takeaway": "Use hydroacoustics now as a predictive/conditional layer with zero weight. Promote it to an observable only after raw-array processing, interference modelling, injection recovery and complete-search false-alarm calibration define p(y|x,H₁) and p(y|H₀).",
        "notes": "Route A is already defensible: for each existing impact particle, report predicted arrival, bearing and amplitude/waveform intervals and ask whether named source candidates are conditionally compatible. This can guide data requests and experimental design without changing the posterior. Route B is a formal update. It must include the probability of detecting—or failing to detect—each impact family, event association uncertainty, airgun and background processes, and the same selection rule applied to real and null data. Ocean-drift products can remain explicit conditional alternatives; present searched-area geometry is context rather than negative evidence until target-specific probability of detection is calibrated. A named observed-signal model is the firewall between an interesting diagnostic and evidential weighting.",
    },
    {
        "n": "11", "title": "Proposed collaboration and next decisions",
        "asset": "11-collaboration-roadmap.png", "alt": [], "tag": "Discussion proposal",
        "takeaway": "Start with a small raw-data pilot that can fail cleanly: reproduce one station/window, recover injected directions and quantify complete-search false alarms before attempting a two-station MH370 association.",
        "notes": "Suggested requests for Dr Kadri: raw calibrated three-channel H01W and H08S arrays plus adjacent control windows; channel coordinates, response and clock metadata; the exact Figure 9 processing chain and complete candidate catalogue; an extended reception window covering longer post-00:19 flight; and any available path Green functions or preferred acoustic–gravity propagation model. The first joint deliverable could be a blinded H01W bearing-recovery and false-alarm benchmark. If that works, add the H08S nuisance-source model and two-station association. Even a null result can constrain very high-energy/coupling end-of-flight families if detectability is calibrated.",
    },
]


def build_notes() -> str:
    lines = [
        "# Dr Usama Kadri meeting — visual briefing pack",
        "",
        "Generated from the archived MH370 estimator and the Kadri hydroacoustic source-recreation bundle. British English is used throughout. Presentation graphics separate source-reported information, conditional model outputs and diagnostics. Publication-trace correlation receives zero evidential weight.",
        "",
    ]
    for slide in SLIDES:
        lines.extend([
            f"## {slide['n']}. {slide['title']}",
            "",
            f"**Suggested on-slide takeaway:** {slide['takeaway']}",
            "",
            f"**Speaker notes:** {slide['notes']}",
            "",
            f"**Primary graphic:** `assets/{slide['asset']}`",
            "",
        ])
        if slide["alt"]:
            lines.append("**Optional supporting graphics:** " + ", ".join(f"`assets/{name}`" for name in slide["alt"]))
            lines.append("")
    lines.extend([
        "## Core equations for an appendix or methods slide",
        "",
        r"Normal-impact energy surrogate: $E_n=\tfrac12mv_z^2$.",
        "",
        r"Reduced coupling: $E_a=\eta E_n$, with explicit coupling-family uncertainty.",
        "",
        r"Forward station model: $\mu_j(f\mid z_k,m,\theta,\phi)=H_{j,m}(f\mid\mathbf{x}_k,\theta)S_m(f\mid z_k,\phi)\exp[-2\pi i f\tau_{j,m}(\mathbf{x}_k,\theta)]$.",
        "",
        r"A future evidential update requires a named observed-signal model, for example $w_i'\propto w_i\,p(y\mid x_i,H_1)/p(y\mid H_0)$, with association, detectability, interference, selection and false-alarm correction included.",
        "",
        "## Source boundaries",
        "",
        "- Large (2019) dissertation, Figures 2 and 77; SkyVector backgrounds are credited in the original captions and are not for navigation.",
        "- Kadri (2024) paper and Figure 9 source-reporting bundle: `.sources/kadri-2024-hydroacoustics/`.",
        "- MH370 release posterior and impact products: `runs/mh370/release-v0.1/`.",
        "- Impact pressure values are conditional sensitivity scales, not calibrated detection probabilities.",
        "- The current impact model does not recover attitude or contact duration; schematic impact angles are illustrative only.",
        "- The publication traces are filtered and digitised figure vectors, not raw CTBTO data.",
    ])
    return "\n".join(lines) + "\n"


def build_html() -> str:
    cards = []
    for slide in SLIDES:
        alt_links = "".join(
            f'<a class="asset-link" href="assets/{html.escape(name)}" download>{html.escape(name)}</a>'
            for name in slide["alt"]
        )
        cards.append(f"""
        <section class="slide-card" id="slide-{slide['n']}">
          <div class="slide-head">
            <span class="number">{slide['n']}</span>
            <div><h2>{html.escape(slide['title'])}</h2><span class="tag">{html.escape(slide['tag'])}</span></div>
          </div>
          <a href="assets/{html.escape(slide['asset'])}" class="image-link">
            <img src="assets/{html.escape(slide['asset'])}" alt="{html.escape(slide['title'])}">
          </a>
          <div class="takeaway"><strong>Suggested on-slide takeaway</strong><p>{html.escape(slide['takeaway'])}</p></div>
          <details open><summary>Speaker notes</summary><p>{html.escape(slide['notes'])}</p></details>
          <div class="downloads">
            <a class="asset-link primary" href="assets/{html.escape(slide['asset'])}" download>Download primary graphic</a>
            {alt_links}
          </div>
        </section>
        """)
    nav = "".join(f'<a href="#slide-{s["n"]}">{s["n"]}</a>' for s in SLIDES)
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dr Usama Kadri meeting — MH370 hydroacoustic visual briefing</title>
<style>
:root{{--navy:#102A43;--teal:#18A999;--orange:#E66A2C;--ink:#17212B;--muted:#5D6B78;--pale:#F3F6F9;--line:#D5DEE6;}}
*{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:#E9EEF3;color:var(--ink);font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}}
.hero{{background:linear-gradient(135deg,#102A43,#1D4B67);color:white;padding:48px max(5vw,28px) 38px;border-bottom:5px solid var(--teal)}}
.hero h1{{margin:0 0 8px;font-size:clamp(30px,5vw,54px);line-height:1.08}} .hero p{{max-width:980px;font-size:18px;color:#D9E7EF;margin:10px 0}}
.status{{display:inline-block;margin-top:14px;padding:7px 12px;border:1px solid #81C7C0;border-radius:999px;color:#D9FFF9;font-weight:700}}
.toolbar{{position:sticky;top:0;z-index:4;display:flex;gap:8px;align-items:center;overflow:auto;background:rgba(255,255,255,.96);padding:10px max(5vw,28px);border-bottom:1px solid var(--line);box-shadow:0 3px 12px #102a4312}}
.toolbar a{{display:inline-flex;min-width:36px;height:36px;align-items:center;justify-content:center;text-decoration:none;color:var(--navy);border:1px solid var(--line);border-radius:8px;font-weight:750;background:white}}
.toolbar .doc{{padding:0 12px;color:white;background:var(--navy);border-color:var(--navy);min-width:max-content}}
main{{max-width:1420px;margin:28px auto;padding:0 22px 80px}} .slide-card{{background:white;border:1px solid var(--line);border-radius:16px;padding:24px;margin:0 0 30px;box-shadow:0 9px 30px #102a4310;scroll-margin-top:70px}}
.slide-head{{display:flex;gap:16px;align-items:flex-start;margin-bottom:16px}} .number{{display:grid;place-items:center;width:52px;height:52px;border-radius:12px;background:var(--navy);color:white;font-size:20px;font-weight:800;flex:0 0 auto}}
h2{{margin:0;color:var(--navy);font-size:clamp(23px,3vw,34px);line-height:1.2}} .tag{{display:inline-block;margin-top:8px;padding:3px 9px;border-radius:999px;background:#E8F7F4;color:#1B6C61;font-size:13px;font-weight:750}}
.image-link{{display:block;background:#F7F9FB;border:1px solid var(--line);border-radius:10px;overflow:hidden}} img{{display:block;width:100%;height:auto}}
.takeaway{{border-left:5px solid var(--teal);background:#F0F8F7;margin:18px 0 12px;padding:14px 18px;border-radius:5px}} .takeaway p{{margin:4px 0 0;font-size:17px}}
details{{border:1px solid var(--line);border-radius:8px;padding:10px 14px;background:#FAFBFC}} summary{{cursor:pointer;font-weight:800;color:var(--navy)}} details p{{margin:10px 0 2px}}
.downloads{{display:flex;gap:8px;flex-wrap:wrap;margin-top:13px}} .asset-link{{text-decoration:none;color:var(--navy);background:#F4F7FA;border:1px solid var(--line);border-radius:7px;padding:6px 10px;font-size:13px}} .asset-link.primary{{background:var(--navy);color:white;border-color:var(--navy)}}
.foot{{max-width:1420px;margin:0 auto 50px;padding:0 22px;color:var(--muted)}} .foot code{{background:#fff;padding:2px 4px;border-radius:4px}}
@media print{{body{{background:white}}.toolbar{{display:none}}.slide-card{{break-inside:avoid;box-shadow:none;margin-bottom:14px;padding:14px}}.hero{{padding:24px}}details{{display:block}}}}
</style>
</head>
<body>
<header class="hero">
  <h1>MH370 hydroacoustics</h1>
  <p>Visual briefing pack for discussion with Dr Usama Kadri</p>
  <p>Eleven presentation-ready graphics, suggested on-slide messages and speaker notes. British English throughout.</p>
  <span class="status">Scientific status: predictive/conditional; publication-trace diagnostics have zero estimator weight</span>
</header>
<nav class="toolbar">{nav}<a class="doc" href="speaker-notes.md" download>Speaker notes</a><a class="doc" href="kadri-meeting-visual-pack.zip" download>Download pack</a></nav>
<main>{''.join(cards)}</main>
<div class="foot"><strong>Use:</strong> click any graphic for the full-resolution PNG. Vector SVG is supplied for the newly generated diagrams and selected release figures. The ZIP contains this page, notes and assets. Re-run with <code>.venv/bin/python -B .sources/kadri-2024-hydroacoustics/code/kadri_meeting_visual_pack.py</code>.</div>
</body></html>"""


def build_zip() -> None:
    path = OUT / "kadri-meeting-visual-pack.zip"
    if path.exists():
        path.unlink()
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=7) as archive:
        for item in sorted(OUT.rglob("*")):
            if item.is_file() and item != path:
                archive.write(item, item.relative_to(OUT))


def main() -> None:
    prepare()
    extract_dissertation_figures()
    copy_release_assets()
    impact_state_graphic()
    two_directions_graphic()
    backward_workflow_graphic()
    forward_workflow_graphic()
    airgun_filter_graphic()
    bayesian_integration_graphic()
    collaboration_graphic()
    (OUT / "speaker-notes.md").write_text(build_notes(), encoding="utf-8")
    (OUT / "index.html").write_text(build_html(), encoding="utf-8")
    readme = (
        "# Kadri meeting visual pack\n\n"
        "Open `index.html` for the browser-viewable briefing. `speaker-notes.md` contains the same slide order and copy. "
        "The `assets/` directory contains full-resolution PNGs and vector SVGs where available. "
        "`kadri-meeting-visual-pack.zip` is the portable download.\n\n"
        "The pack is a presentation aid. It does not alter estimator weights or convert publication-trace diagnostics into evidence.\n"
    )
    (OUT / "README.md").write_text(readme, encoding="utf-8")
    build_zip()
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
