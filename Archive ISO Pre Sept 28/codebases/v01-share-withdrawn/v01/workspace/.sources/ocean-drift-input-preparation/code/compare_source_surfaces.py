#!/usr/bin/env python3
"""Compare canonical and superseded source profiles and render cited context."""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D


LEVELS = (0.50, 0.90, 0.95, 0.99)
NAVY = "#17365D"
BLUE = "#2F75B5"
ORANGE = "#D97706"
GREY = "#6B7280"
LIGHT_GREY = "#D1D5DB"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def normalize_logs(log_values: list[float]) -> list[float]:
    maximum = max(log_values)
    values = [math.exp(value - maximum) for value in log_values]
    total = sum(values)
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("source weights do not have positive finite mass")
    return [value / total for value in values]


def load_profiles(path: Path) -> dict:
    document = json.loads(path.read_text(encoding="utf-8"))
    cells = document["cells"]
    ids = [cell["id"] for cell in cells]
    latitudes_s = [-float(cell["position"]["latitude"]) for cell in cells]
    screen = [float(cell["normalized_weight"]) for cell in cells]
    screen_total = sum(screen)
    screen = [value / screen_total for value in screen]
    isotope_values = [
        cell.get(
            "conditional_isotope_log_compatibility",
            cell.get("conditional_isotope_log_likelihood"),
        )
        for cell in cells
    ]
    # A null isotope result means that no represented Reunion arrival existed;
    # the spoke treats that Monte Carlo absence as a neutral, reported screen,
    # so the corresponding debris-only cell must remain in the comparison.
    debris_logs = [
        math.log(float(cell["prior_weight"]))
        + float(cell["debris_log_compatibility"])
        for cell in cells
    ]
    isotope_logs = [float(value) for value in isotope_values if value is not None]
    return {
        "path": str(path),
        "sha256": sha256(path),
        "family": document["family"],
        "seed": document["seed"],
        "particles_per_cell": document["particles_per_cell"],
        "mean_terminated_fraction": float(document["mean_terminated_fraction"]),
        "ids": ids,
        "latitudes_s": latitudes_s,
        "screen": screen,
        "debris_only": normalize_logs(debris_logs),
        "isotope_log_min": min(isotope_logs),
        "isotope_log_max": max(isotope_logs),
    }


def ordered_profile(profile: dict, field: str) -> tuple[list[float], list[float]]:
    rows = sorted(zip(profile["latitudes_s"], profile[field]), key=lambda row: row[0])
    return [row[0] for row in rows], [row[1] for row in rows]


def equal_tail_interval(latitudes: list[float], weights: list[float], level: float) -> dict:
    rows = sorted(zip(latitudes, weights), key=lambda row: row[0])
    tail = 0.5 * (1.0 - level)

    def quantile(probability: float) -> float:
        cumulative = 0.0
        for latitude, weight in rows:
            cumulative += weight
            if cumulative + 1e-15 >= probability:
                return latitude
        return rows[-1][0]

    lower = quantile(tail)
    upper = quantile(1.0 - tail)
    return {
        "latitude_min_s": lower,
        "latitude_max_s": upper,
        "width_degrees": upper - lower,
        "cell_count": sum(lower <= latitude <= upper for latitude, _ in rows),
    }


def highest_mass_interval(latitudes: list[float], weights: list[float], level: float) -> dict:
    chosen: list[float] = []
    cumulative = 0.0
    for latitude, weight in sorted(
        zip(latitudes, weights), key=lambda row: (-row[1], row[0])
    ):
        chosen.append(latitude)
        cumulative += weight
        if cumulative + 1e-15 >= level:
            break
    return {
        "latitude_min_s": min(chosen),
        "latitude_max_s": max(chosen),
        "width_degrees": max(chosen) - min(chosen),
        "cell_count": len(chosen),
        "enclosed_mass": cumulative,
    }


def summarize(name: str, profile: dict, field: str) -> dict:
    latitudes = profile["latitudes_s"]
    weights = profile[field]
    peak_index = max(range(len(weights)), key=lambda index: weights[index])
    entropy = -sum(weight * math.log(weight) for weight in weights if weight > 0.0)
    return {
        "name": name,
        "field": field,
        "peak_cell": profile["ids"][peak_index],
        "peak_latitude_s": latitudes[peak_index],
        "effective_source_cells": math.exp(entropy),
        "equal_tail": {
            f"{int(level * 100)}": equal_tail_interval(latitudes, weights, level)
            for level in LEVELS
        },
        "highest_mass": {
            f"{int(level * 100)}": highest_mass_interval(latitudes, weights, level)
            for level in LEVELS
        },
    }


def aligned_weights(left: dict, left_field: str, right: dict, right_field: str):
    left_by_id = dict(zip(left["ids"], left[left_field]))
    right_by_id = dict(zip(right["ids"], right[right_field]))
    identifiers = sorted(set(left_by_id) | set(right_by_id))
    return (
        [left_by_id.get(identifier, 0.0) for identifier in identifiers],
        [right_by_id.get(identifier, 0.0) for identifier in identifiers],
    )


def total_variation(left: list[float], right: list[float]) -> float:
    return 0.5 * sum(abs(a - b) for a, b in zip(left, right))


def jensen_shannon(left: list[float], right: list[float]) -> float:
    midpoint = [0.5 * (a + b) for a, b in zip(left, right)]

    def divergence(values: list[float]) -> float:
        return sum(
            value * math.log(value / middle)
            for value, middle in zip(values, midpoint)
            if value > 0.0 and middle > 0.0
        )

    return 0.5 * (divergence(left) + divergence(right))


def optional_float(row: dict, name: str) -> float | None:
    value = row.get(name, "").strip()
    return None if value == "" else float(value)


def load_comparators(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    for row in rows:
        for field in (
            "latitude_min_s",
            "latitude_max_s",
            "core_min_s",
            "core_max_s",
            "reported_peak_s",
            "reported_reference_s",
            "secondary_mode_s",
            "tertiary_mode_s",
        ):
            row[field] = optional_float(row, field)
    return rows


def draw_range(axis, y: float, lower: float, upper: float, color: str, width: float):
    axis.plot([lower, upper], [y, y], color=color, linewidth=width, solid_capstyle="butt")
    axis.plot([lower, lower], [y - 0.12, y + 0.12], color=color, linewidth=1.3)
    axis.plot([upper, upper], [y - 0.12, y + 0.12], color=color, linewidth=1.3)


def render_figure(
    current: dict,
    earlier: dict,
    summaries: dict,
    comparators: list[dict],
    comparison: dict,
    output_dir: Path,
    current_label: str,
    current_description: str,
    output_stem: str,
    plot_title: str,
    earlier_label: str,
    debris_profile_label: str,
    screen_profile_label: str,
) -> dict:
    matplotlib.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 10,
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "axes.edgecolor": "#374151",
            "axes.linewidth": 0.8,
            "axes.grid": True,
            "grid.color": "#D1D5DB",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.8,
            "legend.frameon": False,
            "svg.hashsalt": "mh370-ocean-drift-comparison",
        }
    )
    figure = plt.figure(figsize=(14.5, 10.0), facecolor="white")
    grid = figure.add_gridspec(2, 1, height_ratios=(2.05, 1.55), hspace=0.10)
    profile_axis = figure.add_subplot(grid[0])
    lane_axis = figure.add_subplot(grid[1], sharex=profile_axis)

    current_x, current_screen = ordered_profile(current, "screen")
    _, current_debris = ordered_profile(current, "debris_only")
    earlier_x, earlier_screen = ordered_profile(earlier, "screen")
    profile_axis.step(
        earlier_x,
        earlier_screen,
        where="mid",
        color=GREY,
        linestyle=(0, (5, 3)),
        linewidth=1.7,
        label=earlier_label,
        zorder=2,
    )
    profile_axis.step(
        current_x,
        current_debris,
        where="mid",
        color=ORANGE,
        linestyle=(0, (3, 2)),
        linewidth=3.0,
        label=debris_profile_label,
        zorder=3,
    )
    profile_axis.step(
        current_x,
        current_screen,
        where="mid",
        color=NAVY,
        linewidth=1.7,
        label=screen_profile_label,
        zorder=4,
    )
    profile_axis.set_ylabel("Normalized source mass\nper seventh-arc cell", labelpad=25)
    profile_axis.yaxis.set_label_coords(-0.095, 0.5)
    profile_axis.set_title(
        "Source profile and conditional isotope effect", loc="left", pad=10
    )
    profile_axis.tick_params(axis="x", labelbottom=False)
    profile_axis.spines[["top", "right"]].set_visible(False)
    profile_axis.set_ylim(bottom=0.0)
    profile_axis.legend(loc="upper left", fontsize=9.3)
    profile_axis.text(
        0.99,
        0.96,
        "Current screen vs no isotope\n"
        f"TV = {comparison['current_isotope_effect']['total_variation']:.2e}\n"
        "No compatible path receives a boost\n"
        f"Entropy-effective cells: {summaries['earlier_density_ranked']['effective_source_cells']:.1f} → "
        f"{summaries['current_screen']['effective_source_cells']:.1f}",
        transform=profile_axis.transAxes,
        ha="right",
        va="top",
        fontsize=9,
        color=NAVY,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": "white", "edgecolor": LIGHT_GREY},
    )

    current_summary = summaries["current_screen"]
    lane_labels = [f"{current_label}\n(current diagnostic)"] + [
        row["label"] for row in comparators
    ]
    y_values = list(reversed(range(len(lane_labels))))
    current_y = y_values[0]
    level_styles = {
        "99": ("#B7C9DF", 2.0),
        "95": ("#7DA2CE", 3.5),
        "90": (BLUE, 5.5),
        "50": (NAVY, 8.0),
    }
    for level in ("99", "95", "90", "50"):
        interval = current_summary["equal_tail"][level]
        color, width = level_styles[level]
        draw_range(
            lane_axis,
            current_y,
            interval["latitude_min_s"],
            interval["latitude_max_s"],
            color,
            width,
        )
    lane_axis.scatter(
        [current_summary["peak_latitude_s"]],
        [current_y],
        marker="*",
        s=95,
        color=ORANGE,
        edgecolor="white",
        linewidth=0.7,
        zorder=8,
    )

    class_colors = {
        "peer_reviewed_debris_drift": "#6D5AA7",
        "official_debris_drift": "#2A6F97",
        "image_conditioned_drift": "#111827",
        "report_debris_drift": "#168C8C",
        "multi_evidence_compound": ORANGE,
    }
    for y, row in zip(y_values[1:], comparators):
        color = class_colors[row["comparison_class"]]
        lower = row["latitude_min_s"]
        upper = row["latitude_max_s"]
        if lower is not None and upper is not None:
            draw_range(lane_axis, y, lower, upper, color, 3.0)
        if row["core_min_s"] is not None and row["core_max_s"] is not None:
            lane_axis.plot(
                [row["core_min_s"], row["core_max_s"]],
                [y, y],
                color=color,
                linewidth=7.0,
                solid_capstyle="butt",
            )
        marker_value = row["reported_peak_s"]
        marker = "o"
        if marker_value is None:
            marker_value = row["reported_reference_s"]
            marker = "s"
        if row["comparison_class"] == "image_conditioned_drift":
            marker = "D"
        if marker_value is not None:
            lane_axis.scatter(
                [marker_value],
                [y],
                marker=marker,
                s=52,
                color=color,
                edgecolor="white",
                linewidth=0.7,
                zorder=7,
            )
        for field in ("secondary_mode_s", "tertiary_mode_s"):
            if row[field] is not None:
                lane_axis.scatter(
                    [row[field]],
                    [y],
                    marker="o",
                    s=44,
                    facecolor="white",
                    edgecolor=color,
                    linewidth=1.5,
                    zorder=7,
                )

    lane_axis.axhline(current_y - 0.5, color="#9CA3AF", linewidth=0.8)
    lane_axis.set_yticks(y_values, labels=lane_labels)
    lane_axis.tick_params(axis="y", pad=10, length=0)
    lane_axis.set_ylim(-0.7, y_values[0] + 0.7)
    lane_axis.set_xlim(9.5, 46.5)
    lane_axis.set_xlabel("Seventh-arc latitude (degrees south)", labelpad=9)
    lane_axis.set_title(
        f"Published study outputs beneath the {current_label} diagnostic",
        loc="left",
        pad=10,
    )
    lane_axis.spines[["top", "right", "left"]].set_visible(False)
    lane_axis.grid(axis="y", visible=False)
    lane_axis.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5.0))
    lane_axis.xaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(1.0))

    legend_handles = [
        Line2D(
            [0], [0], color=NAVY, linewidth=8, label="50% equal-tail"
        ),
        Line2D(
            [0], [0], color=BLUE, linewidth=5, label="90% equal-tail"
        ),
        Line2D(
            [0], [0], color="#7DA2CE", linewidth=4, label="95% equal-tail"
        ),
        Line2D(
            [0], [0], color="#B7C9DF", linewidth=2, label="99% equal-tail"
        ),
        Line2D([0], [0], marker="o", color="none", markerfacecolor="#6D5AA7", label="Reported peak", markersize=7),
        Line2D([0], [0], marker="s", color="none", markerfacecolor="#168C8C", label="Reported reference", markersize=7),
        Line2D([0], [0], marker="D", color="none", markerfacecolor="#111827", label="Image-conditioned point", markersize=7),
    ]
    interval_legend = lane_axis.legend(
        handles=legend_handles,
        loc="lower left",
        bbox_to_anchor=(0.0, -0.34),
        ncol=4,
        fontsize=8.5,
    )

    figure.suptitle(
        plot_title,
        x=0.245,
        y=0.972,
        ha="left",
        fontsize=18,
        fontweight="bold",
        color=NAVY,
    )
    figure.text(
        0.245,
        0.945,
        current_description,
        ha="left",
        va="top",
        fontsize=10.5,
        color=GREY,
    )
    footer = figure.text(
        0.245,
        0.022,
        f"Diagnostic only: mean importance-weighted termination is {100.0 * current['mean_terminated_fraction']:.1f}%; motion and recovery-kernel calibration limitations remain. Published lanes are context, not pooled evidence.",
        ha="left",
        va="bottom",
        fontsize=8.6,
        color=GREY,
    )
    figure.subplots_adjust(left=0.245, right=0.975, top=0.905, bottom=0.145)
    figure.canvas.draw()

    renderer = figure.canvas.get_renderer()
    y_label_box = profile_axis.yaxis.label.get_window_extent(renderer)
    tick_boxes = [
        label.get_window_extent(renderer)
        for label in profile_axis.get_yticklabels()
        if label.get_visible() and label.get_text()
    ]
    label_tick_gap = min(box.x0 for box in tick_boxes) - y_label_box.x1
    lane_boxes = [
        label.get_window_extent(renderer)
        for label in lane_axis.get_yticklabels()
        if label.get_visible()
    ]
    lane_labels_inside_canvas = min(box.x0 for box in lane_boxes) >= 0.0
    legend_box = interval_legend.get_window_extent(renderer)
    x_label_box = lane_axis.xaxis.label.get_window_extent(renderer)
    footer_box = footer.get_window_extent(renderer)
    x_label_legend_gap = x_label_box.y0 - legend_box.y1
    legend_footer_gap = legend_box.y0 - footer_box.y1
    layout_audit = {
        "profile_y_label_to_tick_gap_pixels": float(label_tick_gap),
        "profile_y_label_does_not_overlap_ticks": bool(label_tick_gap >= 8.0),
        "study_labels_inside_canvas": bool(lane_labels_inside_canvas),
        "x_label_to_legend_gap_pixels": float(x_label_legend_gap),
        "x_label_does_not_overlap_legend": bool(x_label_legend_gap >= 6.0),
        "legend_to_footer_gap_pixels": float(legend_footer_gap),
        "legend_does_not_overlap_footer": bool(legend_footer_gap >= 6.0),
    }
    layout_audit["all_pass"] = all(
        value for key, value in layout_audit.items() if isinstance(value, bool)
    )
    if not layout_audit["all_pass"]:
        raise RuntimeError(f"figure layout audit failed: {layout_audit}")

    stem = output_dir / f"{output_stem}-football-field"
    deterministic_date = dt.datetime(2014, 3, 8, tzinfo=dt.timezone.utc)
    figure.savefig(
        stem.with_suffix(".png"),
        dpi=300,
        facecolor="white",
        metadata={"Software": "MH370 ocean-drift source comparison"},
    )
    figure.savefig(
        stem.with_suffix(".svg"),
        facecolor="white",
        metadata={
            "Creator": "MH370 ocean-drift source comparison",
            "Date": "2014-03-08T00:00:00Z",
        },
    )
    figure.savefig(
        stem.with_suffix(".pdf"),
        facecolor="white",
        metadata={
            "Title": plot_title,
            "Author": "MH370 canonical ocean-drift spoke",
            "Creator": "MH370 ocean-drift source comparison",
            "CreationDate": deterministic_date,
            "ModDate": deterministic_date,
        },
    )
    plt.close(figure)
    return layout_audit


def write_table(path: Path, summaries: dict) -> None:
    columns = [
        "scenario",
        "profile",
        "peak_cell",
        "peak_latitude_s",
        "effective_source_cells",
        "interval_type",
        "probability",
        "latitude_min_s",
        "latitude_max_s",
        "width_degrees",
        "cell_count",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for scenario, summary in summaries.items():
            for interval_type in ("equal_tail", "highest_mass"):
                for level in LEVELS:
                    interval = summary[interval_type][f"{int(level * 100)}"]
                    writer.writerow(
                        {
                            "scenario": scenario,
                            "profile": summary["field"],
                            "peak_cell": summary["peak_cell"],
                            "peak_latitude_s": f"{summary['peak_latitude_s']:.9g}",
                            "effective_source_cells": f"{summary['effective_source_cells']:.9g}",
                            "interval_type": interval_type,
                            "probability": f"{level:.2f}",
                            "latitude_min_s": f"{interval['latitude_min_s']:.9g}",
                            "latitude_max_s": f"{interval['latitude_max_s']:.9g}",
                            "width_degrees": f"{interval['width_degrees']:.9g}",
                            "cell_count": interval["cell_count"],
                        }
                    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--current", type=Path, required=True)
    parser.add_argument("--earlier", type=Path, required=True)
    parser.add_argument("--comparators", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--current-label", default="Native HYCOM")
    parser.add_argument(
        "--current-description",
        default="Native time-varying HYCOM + adaptive SMC; isotope is a conditional compatibility screen",
    )
    parser.add_argument("--output-stem", default="native-hycom")
    parser.add_argument("--plot-title", default="MH370 flaperon source-area comparison")
    parser.add_argument(
        "--earlier-label",
        default="Earlier ~0.96° / 64-particle density-ranked diagnostic",
    )
    parser.add_argument(
        "--debris-profile-label",
        default="Current recovery evidence without isotope screen",
    )
    parser.add_argument(
        "--screen-profile-label",
        default="Current recovery evidence plus conservative isotope screen",
    )
    args = parser.parse_args()

    current = load_profiles(args.current)
    earlier = load_profiles(args.earlier)
    comparators = load_comparators(args.comparators)
    summaries = {
        "current_screen": summarize("current_screen", current, "screen"),
        "current_debris_only": summarize(
            "current_debris_only", current, "debris_only"
        ),
        "earlier_density_ranked": summarize(
            "earlier_density_ranked", earlier, "screen"
        ),
        "earlier_debris_only": summarize(
            "earlier_debris_only", earlier, "debris_only"
        ),
    }

    current_screen, current_debris = aligned_weights(
        current, "screen", current, "debris_only"
    )
    earlier_screen, earlier_debris = aligned_weights(
        earlier, "screen", earlier, "debris_only"
    )
    old_screen, new_screen = aligned_weights(earlier, "screen", current, "screen")
    comparison = {
        "current_isotope_effect": {
            "total_variation": total_variation(current_screen, current_debris),
            "jensen_shannon_nats": jensen_shannon(current_screen, current_debris),
            "isotope_log_penalty_span": current["isotope_log_max"]
            - current["isotope_log_min"],
        },
        "earlier_isotope_effect": {
            "total_variation": total_variation(earlier_screen, earlier_debris),
            "jensen_shannon_nats": jensen_shannon(earlier_screen, earlier_debris),
            "isotope_log_likelihood_span": earlier["isotope_log_max"]
            - earlier["isotope_log_min"],
        },
        "earlier_screen_vs_current_screen": {
            "total_variation": total_variation(old_screen, new_screen),
            "jensen_shannon_nats": jensen_shannon(old_screen, new_screen),
            "not_like_for_like": True,
        },
    }
    comparison["screened_profile_expansion"] = {
        "effective_source_cell_ratio": summaries["current_screen"][
            "effective_source_cells"
        ]
        / summaries["earlier_density_ranked"]["effective_source_cells"],
        "equal_tail": {
            f"{int(level * 100)}": {
                "earlier_width_degrees": summaries["earlier_density_ranked"][
                    "equal_tail"
                ][f"{int(level * 100)}"]["width_degrees"],
                "current_width_degrees": summaries["current_screen"]["equal_tail"][
                    f"{int(level * 100)}"
                ]["width_degrees"],
                "width_ratio": summaries["current_screen"]["equal_tail"][
                    f"{int(level * 100)}"
                ]["width_degrees"]
                / summaries["earlier_density_ranked"]["equal_tail"][
                    f"{int(level * 100)}"
                ]["width_degrees"],
            }
            for level in LEVELS
        },
        "highest_mass": {
            f"{int(level * 100)}": {
                "earlier_selected_cells": summaries["earlier_density_ranked"][
                    "highest_mass"
                ][f"{int(level * 100)}"]["cell_count"],
                "current_selected_cells": summaries["current_screen"]["highest_mass"][
                    f"{int(level * 100)}"
                ]["cell_count"],
                "selected_cell_ratio": summaries["current_screen"]["highest_mass"][
                    f"{int(level * 100)}"
                ]["cell_count"]
                / summaries["earlier_density_ranked"]["highest_mass"][
                    f"{int(level * 100)}"
                ]["cell_count"],
            }
            for level in LEVELS
        },
        "warning": "Earlier and current profiles are not like-for-like: field resolution, sampler, and isotope behavior all changed.",
    }

    args.output.mkdir(parents=True, exist_ok=True)
    table_path = args.output / f"{args.output_stem}-source-comparison.csv"
    write_table(table_path, summaries)
    layout_audit = render_figure(
        current,
        earlier,
        summaries,
        comparators,
        comparison,
        args.output,
        args.current_label,
        args.current_description,
        args.output_stem,
        args.plot_title,
        args.earlier_label,
        args.debris_profile_label,
        args.screen_profile_label,
    )
    plot_paths = [
        args.output / f"{args.output_stem}-football-field.{suffix}"
        for suffix in ("png", "svg", "pdf")
    ]
    receipt = {
        "schema": "mh370-ocean-drift-source-comparison-v1",
        "purpose": "diagnostic comparison; not central-estimator evidence",
        "labels": {
            "plot_title": args.plot_title,
            "current": args.current_label,
            "earlier": args.earlier_label,
            "debris_profile": args.debris_profile_label,
            "screen_profile": args.screen_profile_label,
        },
        "inputs": {
            "current": {
                key: current[key]
                for key in (
                    "path",
                    "sha256",
                    "family",
                    "seed",
                    "particles_per_cell",
                    "mean_terminated_fraction",
                )
            },
            "earlier": {
                key: earlier[key]
                for key in ("path", "sha256", "family", "seed", "particles_per_cell")
            },
            "comparators": {
                "path": str(args.comparators),
                "sha256": sha256(args.comparators),
                "count": len(comparators),
            },
        },
        "comparison": comparison,
        "summaries": summaries,
        "layout_audit": layout_audit,
        "software": {
            "python": ".".join(map(str, __import__("sys").version_info[:3])),
            "matplotlib": matplotlib.__version__,
        },
        "outputs": {
            path.name: {"sha256": sha256(path), "bytes": path.stat().st_size}
            for path in [table_path, *plot_paths]
        },
        "interpretation": [
            "The current conservative isotope screen is effectively neutral for this run.",
            "The earlier narrow profile depended on a superseded density-ranking likelihood and rare-arrival samples with very low effective sample size.",
            "The current profile remains diagnostic; field, motion, recovery, and sampling limitations are reported separately.",
            "Published comparators are labelled context and are not pooled or treated as commensurate posterior intervals.",
        ],
    }
    (args.output / f"{args.output_stem}-source-comparison.json").write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
