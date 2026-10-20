#!/usr/bin/env python3
"""Publication figures for trajectory-blind post-restart WSPR controls.

This renderer is deliberately separate from the known-flight figures: no
post-18:22 aircraft truth or trajectory is available, so none is drawn or
scored.  It consumes the frozen PHaRLAP cluster, comparison and run-metadata
artifacts and draws residual cluster centres for the minus-60-minute,
arc-time and plus-60-minute windows at the seven conventional BTO epochs.

The output includes paginated PNG/PDF/SVG figures, a compact raw-versus-
residual table, a row-level plot audit, publication captions and a hash
manifest.  Plotting never changes clustering or residual membership.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import median
from typing import Mapping, Sequence

import plot_known_flight_pharlap_residuals as shared


METADATA_SCHEMA = "mh370.wspr.pharlap.post-restart-control-run.v1"
PLOT_SCHEMA = "mh370.wspr.pharlap.post-restart-publication-plots.v1"
EXPECTED_EPOCHS = (
    "m1825", "m1941", "m2041", "m2141", "m2241", "m0011", "m0019a",
)
CONDITIONS = shared.CONDITIONS
CONDITION_LABELS = shared.CONDITION_LABELS
SCREENS = shared.SCREENS
SCREEN_LABELS = shared.SCREEN_LABELS
MEASURES = ("raw_clusters", "residual_clusters")
EPOCH_LABELS = {
    "m1825": "Restart / first arc",
    "m1941": "Second arc",
    "m2041": "Third arc",
    "m2141": "Fourth arc",
    "m2241": "Fifth arc",
    "m0011": "Sixth arc",
    "m0019a": "Seventh arc",
}

COMPARISON_COLUMNS = {
    "epoch_id", "sequence", "flight", "arc_time_utc", "screen", "measure",
    "minus_60_min", "actual_time", "plus_60_min", "control_mean",
    "actual_minus_control_mean", "actual_to_control_mean_ratio",
}
TABLE_COLUMNS = (
    "epoch_id", "sequence", "arc_time_utc", "screen",
    "minus_60_min_raw", "minus_60_min_residual",
    "actual_time_raw", "actual_time_residual",
    "plus_60_min_raw", "plus_60_min_residual",
    "raw_actual_minus_control_mean", "raw_actual_to_control_mean_ratio",
    "residual_actual_minus_control_mean",
    "residual_actual_to_control_mean_ratio",
)
AUDIT_COLUMNS = shared.CLUSTER_PLOT_AUDIT_COLUMNS


@dataclass(frozen=True)
class ComparisonRow:
    epoch_id: str
    sequence: int
    flight: str
    arc_time_utc: str
    screen: str
    measure: str
    counts: Mapping[str, int]
    control_mean: float
    actual_minus_control_mean: float
    actual_to_control_mean_ratio: float | None


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_comparisons(path: Path) -> tuple[ComparisonRow, ...]:
    raw_rows = shared._read_csv(path, COMPARISON_COLUMNS)
    rows: list[ComparisonRow] = []
    seen: set[tuple[str, str, str]] = set()
    for line, raw in enumerate(raw_rows, 2):
        key = raw["epoch_id"], raw["screen"], raw["measure"]
        if key in seen:
            raise ValueError(f"{path}:{line}: duplicate comparison row {key}")
        seen.add(key)
        if raw["screen"] not in SCREENS:
            raise ValueError(f"{path}:{line}: unknown screen {raw['screen']}")
        if raw["measure"] not in MEASURES:
            raise ValueError(f"{path}:{line}: unknown measure {raw['measure']}")
        counts = {condition: int(raw[condition]) for condition in CONDITIONS}
        if any(value < 0 for value in counts.values()):
            raise ValueError(f"{path}:{line}: negative cluster count")
        control_mean = float(raw["control_mean"])
        difference = float(raw["actual_minus_control_mean"])
        ratio = (
            None if raw["actual_to_control_mean_ratio"].strip() == ""
            else float(raw["actual_to_control_mean_ratio"])
        )
        expected_mean = (counts["minus_60_min"] + counts["plus_60_min"]) / 2.0
        expected_difference = counts["actual_time"] - expected_mean
        expected_ratio = counts["actual_time"] / expected_mean if expected_mean else None
        if not math.isclose(control_mean, expected_mean, abs_tol=1e-12):
            raise ValueError(f"{path}:{line}: control mean does not match counts")
        if not math.isclose(difference, expected_difference, abs_tol=1e-12):
            raise ValueError(f"{path}:{line}: actual-control difference is inconsistent")
        if (ratio is None) != (expected_ratio is None) or (
            ratio is not None
            and not math.isclose(ratio, expected_ratio, rel_tol=1e-12, abs_tol=1e-12)
        ):
            raise ValueError(f"{path}:{line}: actual-control ratio is inconsistent")
        rows.append(ComparisonRow(
            epoch_id=raw["epoch_id"],
            sequence=int(raw["sequence"]),
            flight=raw["flight"],
            arc_time_utc=raw["arc_time_utc"],
            screen=raw["screen"],
            measure=raw["measure"],
            counts=counts,
            control_mean=control_mean,
            actual_minus_control_mean=difference,
            actual_to_control_mean_ratio=ratio,
        ))
    return tuple(rows)


def _positive(value: object, name: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0.0:
        raise ValueError(f"{name} must be positive and finite")
    return parsed


def _read_metadata(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict) or value.get("schema") != METADATA_SCHEMA:
        raise ValueError(f"unexpected post-restart run metadata schema in {path}")
    if value.get("known_aircraft_truth_available") is not False:
        raise ValueError("post-restart publication requires truth_available=false")
    if value.get("known_aircraft_truth_used_in_candidate_selection") is not False:
        raise ValueError("post-restart publication requires blind selection")
    expected_offsets = {
        "minus_60_min": -60, "actual_time": 0, "plus_60_min": 60,
    }
    if value.get("control_offsets_minutes") != expected_offsets:
        raise ValueError(f"control offsets must be {expected_offsets}")
    extent = value.get("map_extent_lon_lat")
    if not (
        isinstance(extent, list) and len(extent) == 4
        and all(math.isfinite(float(item)) for item in extent)
        and float(extent[0]) < float(extent[1])
        and float(extent[2]) < float(extent[3])
    ):
        raise ValueError("map_extent_lon_lat must be [west, east, south, north]")
    settings = value.get("assembly_scientific_settings")
    if not isinstance(settings, dict):
        raise ValueError("assembly_scientific_settings must be an object")
    for field in (
        "surface_endpoint_tolerance_km", "aircraft_path_horizontal_tolerance_km",
        "cluster_radius_km", "source_residual_tolerance_km",
        "altitude_survivor_collapse_radius_km",
    ):
        _positive(settings.get(field), field)
    if int(settings.get("minimum_independent_links", 0)) < 3:
        raise ValueError("minimum_independent_links must be at least three")
    if settings.get("source_residual_altitude_matching") != "ignore_modeled_altitude":
        raise ValueError("primary residualization must match source clusters across height")
    pharlap = value.get("pharlap_batch_scientific_settings")
    if not isinstance(pharlap, dict):
        raise ValueError("pharlap_batch_scientific_settings must be an object")
    altitude_grid = pharlap.get("aircraft_altitudes_km")
    if not (
        isinstance(altitude_grid, list) and altitude_grid
        and all(math.isfinite(float(item)) and float(item) >= 0.0 for item in altitude_grid)
        and [float(item) for item in altitude_grid]
        == sorted(set(float(item) for item in altitude_grid))
    ):
        raise ValueError("PHaRLAP aircraft-altitude grid must be sorted and unique")
    return value


def _arc_epochs(arcs: Sequence[shared.ArcPoint]) -> tuple[shared.ArcPoint, ...]:
    first: dict[str, shared.ArcPoint] = {}
    for point in arcs:
        first.setdefault(point.epoch_id, point)
    ordered = tuple(sorted(first.values(), key=lambda row: row.sequence))
    if tuple(row.epoch_id for row in ordered) != EXPECTED_EPOCHS:
        raise ValueError(
            "post-restart arcs must be the seven canonical epochs in order: "
            f"{EXPECTED_EPOCHS}"
        )
    if tuple(row.sequence for row in ordered) != tuple(range(1, 8)):
        raise ValueError("post-restart arc sequence must be one through seven")
    return ordered


def _validate_contract(
    arcs: Sequence[shared.ArcPoint],
    clusters: Sequence[shared.ClusterRow],
    comparisons: Sequence[ComparisonRow],
) -> tuple[shared.ArcPoint, ...]:
    epochs = _arc_epochs(arcs)
    metadata = {
        row.epoch_id: (row.sequence, row.flight, row.arc_time_utc) for row in epochs
    }
    for cluster in clusters:
        if cluster.epoch_id not in metadata:
            raise ValueError(f"cluster epoch absent from arcs: {cluster.epoch_id}")
        expected = metadata[cluster.epoch_id]
        if (cluster.flight, cluster.arc_time_utc) != expected[1:]:
            raise ValueError(f"cluster metadata differs from arc: {cluster.epoch_id}")
    expected_keys = {
        (epoch, screen, measure)
        for epoch in EXPECTED_EPOCHS for screen in SCREENS for measure in MEASURES
    }
    rows = {(row.epoch_id, row.screen, row.measure): row for row in comparisons}
    if set(rows) != expected_keys:
        raise ValueError(
            "comparison rows do not exactly cover seven epochs, two screens and "
            f"two measures; missing={sorted(expected_keys - set(rows))}, "
            f"foreign={sorted(set(rows) - expected_keys)}"
        )
    for key, row in rows.items():
        expected = metadata[row.epoch_id]
        if (row.sequence, row.flight, row.arc_time_utc) != expected:
            raise ValueError(f"comparison metadata differs from arc: {key}")
        for condition in CONDITIONS:
            residual_count = sum(
                cluster.is_residual
                and cluster.epoch_id == row.epoch_id
                and cluster.screen == row.screen
                and cluster.condition == condition
                for cluster in clusters
            )
            declared_residual = rows[(row.epoch_id, row.screen, "residual_clusters")]
            if residual_count != declared_residual.counts[condition]:
                raise ValueError(
                    f"residual cluster count differs from comparison: "
                    f"{row.epoch_id}/{row.screen}/{condition}"
                )
            if row.screen == "surface_endpoint":
                raw_count = sum(
                    cluster.epoch_id == row.epoch_id
                    and cluster.screen == row.screen
                    and cluster.condition == condition
                    for cluster in clusters
                )
                declared_raw = rows[(row.epoch_id, row.screen, "raw_clusters")]
                if raw_count != declared_raw.counts[condition]:
                    raise ValueError(
                        f"surface raw cluster count differs from comparison: "
                        f"{row.epoch_id}/{condition}"
                    )
    return epochs


def _comparison_lookup(
    rows: Sequence[ComparisonRow],
) -> Mapping[tuple[str, str, str], ComparisonRow]:
    return {(row.epoch_id, row.screen, row.measure): row for row in rows}


def _table_rows(rows: Sequence[ComparisonRow]) -> list[dict[str, object]]:
    lookup = _comparison_lookup(rows)
    output: list[dict[str, object]] = []
    for epoch_id in EXPECTED_EPOCHS:
        for screen in SCREENS:
            raw = lookup[(epoch_id, screen, "raw_clusters")]
            residual = lookup[(epoch_id, screen, "residual_clusters")]
            output.append({
                "epoch_id": epoch_id,
                "sequence": raw.sequence,
                "arc_time_utc": raw.arc_time_utc,
                "screen": screen,
                "minus_60_min_raw": raw.counts["minus_60_min"],
                "minus_60_min_residual": residual.counts["minus_60_min"],
                "actual_time_raw": raw.counts["actual_time"],
                "actual_time_residual": residual.counts["actual_time"],
                "plus_60_min_raw": raw.counts["plus_60_min"],
                "plus_60_min_residual": residual.counts["plus_60_min"],
                "raw_actual_minus_control_mean": raw.actual_minus_control_mean,
                "raw_actual_to_control_mean_ratio": (
                    "" if raw.actual_to_control_mean_ratio is None
                    else raw.actual_to_control_mean_ratio
                ),
                "residual_actual_minus_control_mean": (
                    residual.actual_minus_control_mean
                ),
                "residual_actual_to_control_mean_ratio": (
                    "" if residual.actual_to_control_mean_ratio is None
                    else residual.actual_to_control_mean_ratio
                ),
            })
    return output


def _display_time(value: str) -> str:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%H:%M:%S UTC")
    except ValueError:
        return value


def _page_groups(
    epochs: Sequence[shared.ArcPoint], rows_per_page: int,
) -> tuple[tuple[shared.ArcPoint, ...], ...]:
    if rows_per_page < 1:
        raise ValueError("rows_per_page must be positive")
    return tuple(
        tuple(epochs[start:start + rows_per_page])
        for start in range(0, len(epochs), rows_per_page)
    )


def _decimated(points: Sequence[shared.ArcPoint], maximum: int = 1500) -> tuple[shared.ArcPoint, ...]:
    if len(points) <= maximum:
        return tuple(points)
    stride = math.ceil(len(points) / maximum)
    selected = list(points[::stride])
    if selected[-1] is not points[-1]:
        selected.append(points[-1])
    return tuple(selected)


def _altitude_sizes(
    clusters: Sequence[shared.ClusterRow], altitude_domain: tuple[float, float],
) -> list[float]:
    values = [
        None if row.altitude_minimum_km is None
        else (row.altitude_minimum_km + row.altitude_maximum_km) / 2.0
        for row in clusters
    ]
    return shared._altitude_sizes(values, altitude_domain)


def _figure_stem(screen: str, page_index: int, page_count: int) -> str:
    suffix = "" if page_count == 1 else f"-page-{page_index + 1}-of-{page_count}"
    return f"post-restart-pharlap-{screen.replace('_', '-')}-residual-controls{suffix}"


def _draw_page(
    screen: str,
    page_index: int,
    pages: Sequence[Sequence[shared.ArcPoint]],
    arcs_by_epoch: Mapping[str, Sequence[shared.ArcPoint]],
    clusters: Sequence[shared.ClusterRow],
    comparisons: Mapping[tuple[str, str, str], ComparisonRow],
    metadata: Mapping[str, object],
    support_limits: tuple[int, int],
    output_directory: Path,
) -> tuple[Path, Path, Path]:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.cm import ScalarMappable
    from matplotlib.colors import BoundaryNorm
    from matplotlib.lines import Line2D

    epochs = pages[page_index]
    minimum_support, maximum_support = support_limits
    boundaries = [value - 0.5 for value in range(minimum_support, maximum_support + 2)]
    cmap = plt.get_cmap("viridis", maximum_support - minimum_support + 1)
    norm = BoundaryNorm(boundaries, cmap.N)
    extent = [float(value) for value in metadata["map_extent_lon_lat"]]
    midpoint_latitude = (extent[2] + extent[3]) / 2.0
    altitude_grid = [
        float(value) for value in
        metadata["pharlap_batch_scientific_settings"]["aircraft_altitudes_km"]
    ]
    altitude_domain = min(altitude_grid), max(altitude_grid)
    row_count = len(epochs)
    single_row_page = row_count == 1
    figure_height = 7.8 if single_row_page else 4.55 * row_count + 2.0
    layout_top = 0.80 if single_row_page else 0.90
    layout_bottom = (
        (0.265 if screen == "common_aircraft_altitude" else 0.245)
        if single_row_page
        else (0.145 if screen == "common_aircraft_altitude" else 0.13)
    )
    fig, axes = plt.subplots(
        row_count, 3,
        figsize=(20.5, figure_height),
        sharex=True, sharey=True, squeeze=False,
    )
    for row_index, epoch in enumerate(epochs):
        arc = _decimated(arcs_by_epoch[epoch.epoch_id])
        for column_index, condition in enumerate(CONDITIONS):
            axis = axes[row_index, column_index]
            panel = [
                row for row in clusters
                if row.epoch_id == epoch.epoch_id
                and row.screen == screen
                and row.condition == condition
                and row.is_residual
            ]
            axis.plot(
                [point.longitude_deg_e for point in arc],
                [point.latitude_deg for point in arc],
                color="#151515", linewidth=2.0, zorder=3,
            )
            if panel:
                axis.scatter(
                    [row.longitude_deg_e for row in panel],
                    [row.latitude_deg for row in panel],
                    c=[row.independent_links for row in panel],
                    s=(
                        _altitude_sizes(panel, altitude_domain)
                        if screen == "common_aircraft_altitude"
                        else [38.0] * len(panel)
                    ),
                    cmap=cmap, norm=norm, alpha=0.9,
                    edgecolors="#101010", linewidths=0.5,
                    zorder=5, rasterized=True,
                )
            raw = comparisons[(epoch.epoch_id, screen, "raw_clusters")]
            residual = comparisons[(epoch.epoch_id, screen, "residual_clusters")]
            axis.text(
                0.025, 0.975,
                f"Raw clusters: {raw.counts[condition]}\n"
                f"Residual clusters: {residual.counts[condition]}",
                transform=axis.transAxes, va="top", ha="left",
                fontsize=8.2, linespacing=1.25,
                bbox={
                    "boxstyle": "round,pad=0.34", "facecolor": "white",
                    "edgecolor": "#999999", "alpha": 0.95,
                },
                zorder=8,
            )
            if row_index == 0:
                axis.set_title(CONDITION_LABELS[condition], fontsize=11.5, weight="bold")
            axis.set_xlim(extent[0], extent[1])
            axis.set_ylim(extent[2], extent[3])
            axis.set_aspect(1.0 / max(0.15, math.cos(math.radians(midpoint_latitude))))
            axis.grid(color="#b8b8b8", alpha=0.3, linewidth=0.6, zorder=-1)
            if row_index == row_count - 1:
                axis.set_xlabel("Longitude (°E)")
        axes[row_index, 0].set_ylabel(
            f"{EPOCH_LABELS[epoch.epoch_id]}\n{_display_time(epoch.arc_time_utc)}\nLatitude (°N)",
            fontsize=8.8,
        )

    mappable = ScalarMappable(norm=norm, cmap=cmap)
    mappable.set_array([])
    ticks = list(range(minimum_support, maximum_support + 1))
    if len(ticks) > 12:
        stride = math.ceil(len(ticks) / 10)
        ticks = ticks[::stride]
        if ticks[-1] != maximum_support:
            ticks.append(maximum_support)
    fig.subplots_adjust(
        left=0.065, right=0.90, bottom=layout_bottom,
        top=layout_top, wspace=0.10, hspace=0.14,
    )
    colorbar_axis = fig.add_axes([
        0.918, layout_bottom, 0.012, layout_top - layout_bottom,
    ])
    colorbar = fig.colorbar(mappable, cax=colorbar_axis, ticks=ticks)
    colorbar.set_label("Independent contributing links")

    handles = [Line2D([], [], color="#151515", linewidth=2.0, label="BTO arc at 10 km")]
    if screen == "common_aircraft_altitude":
        levels = sorted({altitude_domain[0], median(altitude_grid), altitude_domain[1]})
        sizes = shared._altitude_sizes(levels, altitude_domain)
        handles.extend(
            Line2D(
                [], [], marker="o", linestyle="none", markersize=math.sqrt(size) * 0.72,
                markerfacecolor="#b8b8b8", markeredgecolor="#101010",
                label=f"Feasible-altitude midpoint {altitude:g} km",
            )
            for altitude, size in zip(levels, sizes)
        )
    fig.legend(
        handles=handles, loc="lower center", ncol=len(handles), fontsize=8.4,
        frameon=True, bbox_to_anchor=(0.48, 0.018),
    )
    settings = metadata["assembly_scientific_settings"]
    fig.suptitle(
        "MH370 post-18:22 WSPR controls\n"
        f"PHaRLAP-filtered residuals: {SCREEN_LABELS[screen]}",
        fontsize=14.5, y=0.97 if single_row_page else 0.985,
    )
    footer = (
        f"Seven trajectory-blind BTO-arc searches; {settings['cluster_radius_km']:g} km "
        f"clustering, {settings['source_residual_tolerance_km']:g} km symmetric "
        f"residualization and ≥{settings['minimum_independent_links']} independent "
        "links. A cluster remains only when neither of the other time panels has a "
        "cluster within the residual tolerance. Only residual centres are drawn; "
        "panel annotations retain the raw "
        "counts. No post-18:22 aircraft truth or trajectory was supplied or overlaid. "
        "A PHaRLAP-feasible mode is a propagation screen, not evidence that the mode "
        "occurred. Adjacent radio windows overlap, so cross-epoch counts are descriptive."
    )
    if screen == "common_aircraft_altitude":
        footer += (
            " Source altitude slices were matched across either control at any height "
            "before surviving co-located slices were collapsed for display; marker size "
            "encodes feasible-altitude midrange, not evidential strength."
        )
    fig.text(
        0.48, 0.115 if single_row_page else 0.064,
        footer, ha="center", va="bottom", fontsize=7.8,
        color="#333333", wrap=True,
    )
    stem = _figure_stem(screen, page_index, len(pages))
    paths = tuple(output_directory / f"{stem}.{suffix}" for suffix in ("png", "pdf", "svg"))
    fig.savefig(paths[0], dpi=300, facecolor="white")
    fig.savefig(paths[1], facecolor="white")
    fig.savefig(paths[2], facecolor="white")
    plt.close(fig)
    return paths  # type: ignore[return-value]


def _write_captions(
    path: Path, pages: Sequence[Sequence[shared.ArcPoint]], metadata: Mapping[str, object],
) -> None:
    settings = metadata["assembly_scientific_settings"]
    lines = ["# Post-restart WSPR/PHaRLAP figure captions", ""]
    for screen in SCREENS:
        for page_index, epochs in enumerate(pages):
            names = ", ".join(EPOCH_LABELS[row.epoch_id] for row in epochs)
            stem = _figure_stem(screen, page_index, len(pages))
            extra = (
                " For the common-aircraft-altitude screen, source height slices were "
                "residualized across any modeled height before surviving co-located "
                "slices were collapsed; marker size encodes feasible-altitude midrange."
                if screen == "common_aircraft_altitude" else ""
            )
            lines.extend((
                f"## {stem}", "",
                "Trajectory-blind WSPR controls at the post-restart BTO epochs "
                f"{names}. Columns show the −60-minute control, arc-time window and "
                "+60-minute control. Points are PHaRLAP-screened residual cluster "
                f"centres having no cluster within {settings['source_residual_tolerance_km']:g} "
                "km in either other time panel; the operation is applied symmetrically. "
                "Colour gives the number of contributing links that share neither "
                "a transmitter nor a receiver. Black curves are equal-BTO arcs calculated at "
                "10 km altitude. Panel labels report both pre-residualization and "
                "residual cluster counts. No post-18:22 aircraft truth or trajectory "
                "was available, supplied to selection or overlaid. PHaRLAP feasibility "
                "does not establish that a modeled ionospheric mode occurred, and "
                "overlapping radio windows make the cross-epoch comparison descriptive."
                + extra,
                "",
            ))
    path.write_text("\n".join(lines), encoding="utf-8")


def generate(
    cluster_path: Path,
    arc_path: Path,
    comparison_path: Path,
    metadata_path: Path,
    output_directory: Path,
    *,
    rows_per_page: int = 3,
    screens: Sequence[str] = SCREENS,
) -> tuple[Path, Path]:
    if (
        not screens or set(screens).difference(SCREENS)
        or len(set(screens)) != len(screens)
    ):
        raise ValueError("screens must be a non-empty unique subset of the two primary screens")
    metadata = _read_metadata(metadata_path)
    clusters = shared.read_clusters(cluster_path)
    arcs = shared.read_arcs(arc_path)
    comparisons = _read_comparisons(comparison_path)
    epochs = _validate_contract(arcs, clusters, comparisons)
    output_directory.mkdir(parents=True, exist_ok=True)
    pages = _page_groups(epochs, rows_per_page)
    arcs_by_epoch: dict[str, list[shared.ArcPoint]] = {}
    for point in arcs:
        arcs_by_epoch.setdefault(point.epoch_id, []).append(point)
    comparison_lookup = _comparison_lookup(comparisons)
    residuals = [
        row for row in clusters if row.is_residual and row.screen in screens
    ]
    minimum = int(metadata["assembly_scientific_settings"]["minimum_independent_links"])
    if any(row.independent_links < minimum for row in residuals):
        raise ValueError("a residual cluster is below the declared independent-link minimum")
    support_limits = minimum, max(
        (row.independent_links for row in residuals), default=minimum
    )
    output_paths: list[Path] = []
    figure_lookup: dict[tuple[str, str], tuple[Path, Path, Path]] = {}
    for screen in screens:
        for page_index, page in enumerate(pages):
            paths = _draw_page(
                screen, page_index, pages, arcs_by_epoch, clusters,
                comparison_lookup, metadata, support_limits, output_directory,
            )
            output_paths.extend(paths)
            for epoch in page:
                figure_lookup[(epoch.epoch_id, screen)] = paths

    table_path = output_directory / "post-restart-pharlap-raw-residual-comparison.csv"
    with table_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TABLE_COLUMNS)
        writer.writeheader()
        writer.writerows(_table_rows(comparisons))
    output_paths.append(table_path)

    audit_path = output_directory / "post-restart-pharlap-residual-cluster-plot-audit.csv"
    with audit_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=AUDIT_COLUMNS)
        writer.writeheader()
        for row in clusters:
            paths = figure_lookup.get((row.epoch_id, row.screen))
            plotted = row.is_residual and row.screen in screens
            writer.writerow({
                "input_row_number": row.input_row_number,
                "epoch_id": row.epoch_id,
                "flight": row.flight,
                "arc_time_utc": row.arc_time_utc,
                "screen": row.screen,
                "condition": row.condition,
                "physical_slot": row.physical_slot,
                "cluster_rank": row.cluster_rank,
                "center_candidate_id": row.center_candidate_id,
                "latitude_deg": row.latitude_deg,
                "longitude_deg_e": row.longitude_deg_e,
                "altitude_km": "" if row.altitude_km is None else row.altitude_km,
                "altitude_minimum_km": (
                    "" if row.altitude_minimum_km is None else row.altitude_minimum_km
                ),
                "altitude_maximum_km": (
                    "" if row.altitude_maximum_km is None else row.altitude_maximum_km
                ),
                "feasible_altitude_count": row.feasible_altitude_count,
                "feasible_altitudes_km": ";".join(f"{v:g}" for v in row.feasible_altitudes_km),
                "source_altitude_clusters": row.source_altitude_clusters,
                "source_altitude_cluster_ids": ";".join(row.source_altitude_cluster_ids),
                "support_spot_ids": ";".join(str(v) for v in row.support_spot_ids),
                "pair_intersections": row.pair_intersections,
                "support_links": row.support_links,
                "independent_links": row.independent_links,
                "nearest_other_condition_km": row.nearest_other_condition_km,
                "is_residual": str(row.is_residual).lower(),
                "plotted": str(plotted).lower(),
                "figure_png": "" if paths is None else paths[0].name,
                "figure_pdf": "" if paths is None else paths[1].name,
                "figure_svg": "" if paths is None else paths[2].name,
            })
    output_paths.append(audit_path)

    caption_path = output_directory / "post-restart-pharlap-figure-captions.md"
    _write_captions(caption_path, pages, metadata)
    output_paths.append(caption_path)

    manifest_path = output_directory / "post-restart-pharlap-residual-plot-manifest.json"
    manifest = {
        "schema": PLOT_SCHEMA,
        "run_id": metadata["run_id"],
        "inputs": {
            str(path): _sha256(path)
            for path in (cluster_path, arc_path, comparison_path, metadata_path)
        },
        "outputs": {path.name: _sha256(path) for path in output_paths},
        "figure_contract": {
            "epochs": list(EXPECTED_EPOCHS),
            "conditions": list(CONDITIONS),
            "screens": list(screens),
            "rows_per_page": rows_per_page,
            "pages": [[row.epoch_id for row in page] for page in pages],
            "truth_or_trajectory_overlay": "none; unavailable post-18:22",
            "plotted_rows": "residual clusters only",
            "panel_annotation": "raw and residual cluster counts",
            "support_colour_scale": list(support_limits),
            "arc_display_maximum_points": 1500,
            "png_dpi": 300,
        },
        "interpretation": (
            "PHaRLAP propagation feasibility is a screen rather than evidence that "
            "a returned mode occurred; adjacent radio windows are dependent."
        ),
        "runtime": {
            "python": platform.python_version(),
            "matplotlib": __import__("matplotlib").__version__,
        },
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return table_path, manifest_path


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clusters", required=True, type=Path)
    parser.add_argument("--arcs", required=True, type=Path)
    parser.add_argument("--comparison", required=True, type=Path)
    parser.add_argument("--run-metadata", required=True, type=Path)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument("--rows-per-page", type=int, default=3)
    parser.add_argument("--screens", nargs="+", choices=SCREENS, default=list(SCREENS))
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    arguments = _parser().parse_args(argv)
    table, manifest = generate(
        arguments.clusters, arguments.arcs, arguments.comparison,
        arguments.run_metadata, arguments.output_directory,
        rows_per_page=arguments.rows_per_page, screens=arguments.screens,
    )
    print(json.dumps({"comparison_table": str(table), "manifest": str(manifest)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
