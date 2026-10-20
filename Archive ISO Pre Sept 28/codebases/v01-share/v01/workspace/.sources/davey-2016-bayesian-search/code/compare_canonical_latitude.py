#!/usr/bin/env python3
"""Compare canonical MH370 latitude marginals with Davey's published result.

Davey et al. publish a final (00:19 UTC) latitude marginal in Figure 10.3,
but do not publish a separate aircraft-position marginal at 00:11 UTC. This
script therefore shows the one-turn model-conditional 00:11 marginal without a
Davey curve and overlays that frozen-continuation result with Davey only at
00:19.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def read_weighted_latitudes(
    paths: list[Path], latitude_column: str, equal_file_weight: bool
) -> tuple[np.ndarray, np.ndarray]:
    latitudes: list[np.ndarray] = []
    weights: list[np.ndarray] = []
    for path in paths:
        table = np.genfromtxt(path, delimiter=",", names=True, dtype=None, encoding="utf-8")
        latitude = np.atleast_1d(table[latitude_column]).astype(float)
        weight = np.atleast_1d(table["weight"]).astype(float)
        weight /= weight.sum()
        if equal_file_weight:
            weight /= len(paths)
        latitudes.append(-latitude)  # report positive degrees south
        weights.append(weight)
    latitude_south = np.concatenate(latitudes)
    combined_weight = np.concatenate(weights)
    combined_weight /= combined_weight.sum()
    return latitude_south, combined_weight


def weighted_quantile(
    values: np.ndarray, weights: np.ndarray, probabilities: list[float]
) -> np.ndarray:
    order = np.argsort(values)
    sorted_values = values[order]
    sorted_weights = weights[order]
    cumulative = np.cumsum(sorted_weights)
    cumulative /= cumulative[-1]
    return np.interp(probabilities, cumulative, sorted_values)


def smooth_histogram(
    values: np.ndarray,
    weights: np.ndarray,
    grid: np.ndarray,
    bandwidth_deg: float,
) -> np.ndarray:
    step = float(grid[1] - grid[0])
    edges = np.concatenate(
        ([grid[0] - step / 2.0], (grid[:-1] + grid[1:]) / 2.0, [grid[-1] + step / 2.0])
    )
    mass, _ = np.histogram(values, bins=edges, weights=weights)
    half_width = int(np.ceil(4.0 * bandwidth_deg / step))
    offsets = np.arange(-half_width, half_width + 1) * step
    kernel = np.exp(-0.5 * (offsets / bandwidth_deg) ** 2)
    kernel /= kernel.sum()
    density = np.convolve(mass, kernel, mode="same") / step
    density /= np.trapezoid(density, grid)
    return density


def read_davey_curve(path: Path, grid: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    table = np.genfromtxt(path, delimiter=",", names=True)
    latitude_south = -np.atleast_1d(table["latitude_deg"]).astype(float)
    density = np.atleast_1d(table["density_per_deg"]).astype(float)
    order = np.argsort(latitude_south)
    latitude_south = latitude_south[order]
    density = density[order]
    density /= np.trapezoid(density, latitude_south)
    interpolated = np.interp(grid, latitude_south, density, left=0.0, right=0.0)
    interpolated /= np.trapezoid(interpolated, grid)
    return interpolated, latitude_south


def density_quantile(grid: np.ndarray, density: np.ndarray, probability: float) -> float:
    increments = 0.5 * (density[:-1] + density[1:]) * np.diff(grid)
    cumulative = np.concatenate(([0.0], np.cumsum(increments)))
    cumulative /= cumulative[-1]
    return float(np.interp(probability, cumulative, grid))


def interval_label(quantiles: np.ndarray) -> str:
    return f"median {quantiles[1]:.2f}°S; 95% {quantiles[0]:.2f}–{quantiles[2]:.2f}°S"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root", type=Path, default=Path(__file__).resolve().parents[3]
    )
    parser.add_argument("--bandwidth-deg", type=float, default=0.10)
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    source = repo / ".sources" / "davey-2016-bayesian-search"
    output = args.output_dir or source / "outputs"
    output.mkdir(parents=True, exist_ok=True)

    canonical_0011_paths = [
        repo
        / "runs/mh370/through-0011-medium-assessment/through-0011-medium-bfo"
        / f"seed-{seed}/posterior.csv"
        for seed in (370023, 370024, 370025)
    ]
    canonical_0019_path = (
        repo / "runs/mh370/0011-to-0019-seventh-arc-bto/posterior.csv"
    )
    davey_path = source / "data/davey_fig10_3_digitized_latitude_pdf.csv"

    latitude_0011, weight_0011 = read_weighted_latitudes(
        canonical_0011_paths, "last_contact_latitude_deg", equal_file_weight=True
    )
    latitude_0019, weight_0019 = read_weighted_latitudes(
        [canonical_0019_path], "end_latitude_deg", equal_file_weight=False
    )

    grid = np.linspace(33.4, 40.4, 1401)
    density_0011 = smooth_histogram(
        latitude_0011, weight_0011, grid, args.bandwidth_deg
    )
    density_0019 = smooth_histogram(
        latitude_0019, weight_0019, grid, args.bandwidth_deg
    )
    density_davey, davey_support = read_davey_curve(davey_path, grid)

    probabilities = [0.025, 0.5, 0.975]
    quantile_0011 = weighted_quantile(latitude_0011, weight_0011, probabilities)
    quantile_0019 = weighted_quantile(latitude_0019, weight_0019, probabilities)
    quantile_davey = np.array(
        [density_quantile(grid, density_davey, probability) for probability in probabilities]
    )
    overlap = float(np.trapezoid(np.minimum(density_0019, density_davey), grid))
    width_0011 = float(quantile_0011[2] - quantile_0011[0])
    width_0019 = float(quantile_0019[2] - quantile_0019[0])
    width_davey = float(quantile_davey[2] - quantile_davey[0])

    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9.0,
            "axes.titlesize": 10.0,
            "axes.labelsize": 9.0,
            "legend.fontsize": 8.0,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "svg.hashsalt": "mh370-davey-latitude-v1",
        }
    )
    fig, axes = plt.subplots(1, 2, figsize=(11.8, 5.3), sharex=True)
    canonical_color = "#5679a6"
    davey_color = "#252525"

    axes[0].fill_between(grid, density_0011, color=canonical_color, alpha=0.16)
    axes[0].plot(grid, density_0011, color=canonical_color, linewidth=1.7)
    axes[0].axvline(quantile_0011[1], color=canonical_color, linewidth=1.0, alpha=0.8)
    axes[0].set_title("00:11 UTC — one-turn model-conditional posterior")
    axes[0].text(
        0.03, 0.95, interval_label(quantile_0011), transform=axes[0].transAxes,
        va="top", color="#25364a", fontsize=8.3,
    )
    axes[0].text(
        0.03, 0.79,
        "No separate Davey 00:11 position PDF was published;\nno comparison curve is inferred.",
        transform=axes[0].transAxes, va="top", color="#555555", fontsize=8.0,
    )

    axes[1].fill_between(grid, density_0019, color=canonical_color, alpha=0.16)
    axes[1].plot(
        grid, density_0019, color=canonical_color, linewidth=1.7,
        label="One-turn + frozen continuation: 00:19 R600 BTO",
    )
    axes[1].plot(
        grid, density_davey, color=davey_color, linewidth=1.5,
        linestyle=(0, (5, 3)), label="Davey et al. (2016), Fig. 10.3 (digitized)",
    )
    axes[1].axvline(quantile_0019[1], color=canonical_color, linewidth=1.0, alpha=0.8)
    axes[1].axvline(
        quantile_davey[1], color=davey_color, linewidth=1.0,
        linestyle=(0, (5, 3)), alpha=0.8,
    )
    axes[1].set_title("00:19 UTC — latitude marginal overlay")
    axes[1].text(
        0.03, 0.95, "Conditional  " + interval_label(quantile_0019),
        transform=axes[1].transAxes, va="top", color="#25364a", fontsize=8.1,
    )
    axes[1].text(
        0.03, 0.88, "Davey       " + interval_label(quantile_davey),
        transform=axes[1].transAxes, va="top", color="#333333", fontsize=8.1,
    )
    axes[1].text(
        0.03, 0.81, f"Density overlap coefficient: {overlap:.3f}",
        transform=axes[1].transAxes, va="top", color="#555555", fontsize=8.1,
    )
    axes[1].legend(loc="upper center", bbox_to_anchor=(0.5, -0.20), frameon=False)

    for axis in axes:
        axis.set_xlim(grid[0], grid[-1])
        axis.set_ylim(bottom=0.0)
        axis.set_xlabel("South latitude (°S)")
        axis.grid(True, color="#d9d9d9", linewidth=0.45, alpha=0.65)
        axis.set_axisbelow(True)
        axis.spines["top"].set_visible(False)
        axis.spines["right"].set_visible(False)
    axes[0].set_ylabel("Probability density (degree⁻¹)")
    axes[1].set_ylabel("Probability density (degree⁻¹)")

    fig.suptitle(
        "MH370 latitude marginals: model-conditional estimator and Davey et al. (2016)",
        y=0.975, fontsize=11.5,
    )
    fig.text(
        0.5, 0.015,
        "Canonical curves condition on one turn and a frozen 00:11–00:19 continuation; quantiles use raw particle weights. "
        "Davey permits richer manoeuvre histories and uses both final BTOs. The interval widths are therefore not comparable confidence claims.",
        ha="center", va="bottom", fontsize=7.3, color="#555555", wrap=True,
    )
    fig.subplots_adjust(left=0.075, right=0.985, top=0.88, bottom=0.285, wspace=0.20)

    stem = output / "canonical-vs-davey-latitude"
    fixed_timestamp = datetime(2026, 8, 25, tzinfo=timezone.utc)
    fig.savefig(
        stem.with_suffix(".png"), dpi=300, facecolor="white",
        metadata={"Software": "MH370 canonical comparison generator"},
    )
    fig.savefig(
        stem.with_suffix(".pdf"), facecolor="white",
        metadata={
            "Creator": "MH370 canonical comparison generator",
            "CreationDate": fixed_timestamp,
            "ModDate": fixed_timestamp,
        },
    )
    fig.savefig(
        stem.with_suffix(".svg"), facecolor="white",
        metadata={
            "Creator": "MH370 canonical comparison generator",
            "Date": "2026-08-25",
        },
    )
    plt.close(fig)

    with stem.with_suffix(".csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(
            [
                "south_latitude_deg",
                "canonical_0011_density_per_deg",
                "canonical_0019_density_per_deg",
                "davey_0019_digitized_density_per_deg",
            ]
        )
        writer.writerows(zip(grid, density_0011, density_0019, density_davey))

    summary = {
        "schema_version": 1,
        "comparison_scope": "latitude marginals only",
        "canonical_model_scope": "one-turn flight family with constant-track, speed, and altitude continuation from 00:11 to 00:19",
        "display_bandwidth_deg": args.bandwidth_deg,
        "canonical_0011": {
            "particles": int(latitude_0011.size),
            "seeds": [370023, 370024, 370025],
            "evidence": "BTO plus medium BFO through 00:11 UTC, conditional on the one-turn family",
            "south_latitude_deg": {
                "q025": float(quantile_0011[0]),
                "median": float(quantile_0011[1]),
                "q975": float(quantile_0011[2]),
            },
            "davey_comparison": "NOT_AVAILABLE_DAVEY_DID_NOT_PUBLISH_0011_POSITION_PDF",
        },
        "canonical_0019": {
            "particles": int(latitude_0019.size),
            "evidence": "one-turn 00:11 posterior frozen in track, speed, and altitude, then selected with 00:19:29 R600 BTO only",
            "south_latitude_deg": {
                "q025": float(quantile_0019[0]),
                "median": float(quantile_0019[1]),
                "q975": float(quantile_0019[2]),
            },
        },
        "davey_0019": {
            "source": "Davey et al. (2016), Figure 10.3 bottom panel, digitized",
            "source_pdf_pages": [101, 102],
            "book_pages": [89, 90],
            "south_latitude_deg": {
                "q025": float(quantile_davey[0]),
                "median": float(quantile_davey[1]),
                "q975": float(quantile_davey[2]),
            },
            "digitized_support_south_latitude_deg": [
                float(davey_support.min()), float(davey_support.max())
            ],
        },
        "canonical_0019_vs_davey_0019": {
            "overlap_coefficient": overlap,
            "median_absolute_difference_deg": float(
                abs(quantile_0019[1] - quantile_davey[1])
            ),
            "canonical_95_width_deg": width_0019,
            "davey_95_width_deg": width_davey,
            "davey_to_canonical_95_width_ratio": width_davey / width_0019,
            "canonical_0011_to_0019_width_change_percent": 100.0
            * (width_0019 / width_0011 - 1.0),
        },
        "limitations": [
            "Davey et al. do not publish a separate 00:11 aircraft-position marginal.",
            "The Davey comparison is a digitized one-dimensional latitude marginal, not a two-dimensional particle set.",
            "The canonical continuation introduces no new manoeuvre, speed, altitude, or process uncertainty after 00:11 and then uses one R600 BTO selection.",
            "Davey's model permits a broader set of manoeuvre histories and used both 00:19 BTO messages.",
            "The model families differ, so the narrower canonical curve is model-conditioned and is not an unconditional confidence interval or a reproduction acceptance test.",
        ],
    }
    stem.with_name(stem.name + "-summary.json").write_text(
        json.dumps(summary, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
