#!/usr/bin/env python3
"""Render vector-first publication figures for the Pléiades morphology screen."""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath
from matplotlib.patches import Polygon, Rectangle
import numpy as np
from mpl_toolkits.mplot3d.art3d import Line3DCollection, Poly3DCollection
from PIL import Image
from scipy import ndimage
from scipy.spatial import Delaunay

from morphology import (
    FIELD_METRES,
    GRID_SIZE,
    PIXEL_SIZE_M,
    mask_integer,
    oriented_dimensions,
    project_segment_polygon,
    radius_profile_from_polygon,
    unpack_mask,
)
from run_screen import FAMILY_LABELS, FAMILY_ORDER


SHORT_LABELS = {
    "wing_flooding_model": "Flooding-Model\nWing",
    "wing_random_pose": "Random-Pose\nWing",
    "nonwing_777_parts": "Other 777\nParts",
    "matched_random_geometry": "Matched Random\nGeometry",
    "ocean_object_combined": "Ocean-Object\nControls",
    "whole_fuselage_shell": "Whole 777\nFuselage",
    "documented_structural_sections": "Documented 777\nFuselage Sections",
    "random_longitudinal_sections": "Random 777\nFuselage Sections",
}
CATEGORY_ORDER = (
    "wing",
    "other_777_parts",
    "matched_random_geometry",
    "ocean_object_controls",
    "fuselage_sections",
)
CATEGORY_HEADERS = {
    "wing": "1  Wing\nFlooding + Random Pose",
    "other_777_parts": "2  Other 777 Parts",
    "matched_random_geometry": "3  Matched Random\nGeometry",
    "ocean_object_controls": "4  Ocean-Object\nControls",
    "fuselage_sections": "5  Fuselage Sections\nWhole + Documented + Random",
}
PCA_DISPLAY_QUARTER_TURNS = {
    ("phr-4-object-18", "wing"): 2,
    ("phr-4-object-18", "ocean_object_controls"): 2,
}
SOURCE_LABELS = {
    "left-wing-complete": "Left Wing, Complete",
    "right-wing-flaperon-absent": "Right Wing, Flaperon Absent",
    "nacelle-side-silhouette": "Engine Nacelle, Side Silhouette",
    "nacelle-plan-silhouette": "Engine Nacelle, Plan Silhouette",
    "vertical-tail-outer-surface": "Vertical Tail",
    "single-horizontal-stabilizer": "Horizontal Stabiliser",
    "matched_random_geometry": "Matched Random Polygon",
    "cargo_or_plastic_cluster": "Cargo/Plastic Cluster",
    "fishing_net_or_rope": "Fishing Net/Rope",
    "freight_container": "Freight Container",
    "timber_or_tree": "Timber/Tree",
    "wreck_or_small_hull": "Wreck/Small Hull",
    "drifting_fad": "Drifting FAD",
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def centered_field(mask: np.ndarray, side: int = int(FIELD_METRES / PIXEL_SIZE_M)) -> np.ndarray:
    ys, xs = np.nonzero(mask)
    output = np.zeros((side, side), dtype=bool)
    if len(xs) == 0:
        return output
    centre_x, centre_y = float(xs.mean()), float(ys.mean())
    target_x = np.floor(xs - centre_x + side / 2.0 + 0.5).astype(int)
    target_y = np.floor(ys - centre_y + side / 2.0 + 0.5).astype(int)
    valid = (target_x >= 0) & (target_x < side) & (target_y >= 0) & (target_y < side)
    output[target_y[valid], target_x[valid]] = True
    return output


def actual_field(view: dict) -> np.ndarray:
    side = int(FIELD_METRES / PIXEL_SIZE_M)
    output = np.zeros((side, side), dtype=bool)
    scale = view["scale_m_per_report_pixel"] / PIXEL_SIZE_M
    points = np.asarray(view["relative_component_pixels"], dtype=float)
    target_x = np.floor(points[:, 0] * scale + side / 2.0 + 0.5).astype(int)
    target_y = np.floor(points[:, 1] * scale + side / 2.0 + 0.5).astype(int)
    valid = (target_x >= 0) & (target_x < side) & (target_y >= 0) & (target_y < side)
    output[target_y[valid], target_x[valid]] = True
    return output


def draw_ruler(ax) -> None:
    y = FIELD_METRES - 1.6
    ax.plot([1.5, 6.5], [y, y], color="white", lw=1.5, solid_capstyle="butt")
    ax.plot([1.5, 1.5], [y - 0.35, y + 0.35], color="white", lw=1.2)
    ax.plot([6.5, 6.5], [y - 0.35, y + 0.35], color="white", lw=1.2)
    ax.text(7.0, y + 0.15, "5 m", color="white", fontsize=6.2, va="center")


def style_field_axis(ax, border: str = "#80919c", linewidth: float = 0.7) -> None:
    ax.set_xlim(0, FIELD_METRES)
    ax.set_ylim(FIELD_METRES, 0)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color(border)
        spine.set_linewidth(linewidth)
    draw_ruler(ax)


def draw_mask(ax, mask: np.ndarray, actual: bool = False) -> None:
    ocean = np.zeros((*mask.shape, 3), dtype=float)
    ocean[:] = mpl.colors.to_rgb("#173e58")
    object_colour = mpl.colors.to_rgb("#e7d8a7" if actual else "#d9b65d")
    ocean[mask] = object_colour
    ax.imshow(ocean, origin="upper", interpolation="nearest", extent=(0, FIELD_METRES, FIELD_METRES, 0))
    style_field_axis(ax)


def common_scale_panel(bundle: Path, targets: dict, results: dict) -> None:
    target_by_id = {record["object_id"]: record for record in targets["objects"]}
    object_ids = list(target_by_id)
    columns = ("actual",) + FAMILY_ORDER
    fig, axes = plt.subplots(len(object_ids), len(columns), figsize=(10.4, 12.6), constrained_layout=False)
    fig.patch.set_facecolor("#f4f0e7")
    fig.suptitle("Pléiades fuselage sensitivity — binary masks at one physical scale", x=0.5, y=0.987, fontsize=14, fontweight="semibold", color="#142c3b")
    fig.text(0.5, 0.963, "Every tile is 24 m × 24 m with a 5 m ruler. Minima must pass the audited area, length and width intervals.", ha="center", fontsize=8.2, color="#334d5c")
    for row, object_id in enumerate(object_ids):
        target = target_by_id[object_id]
        result = results["objects"][object_id]
        draw_mask(axes[row, 0], actual_field(target["views"]["true_colour"]), actual=True)
        axes[row, 0].set_title(f"PHR_4 {object_id[-2:]} Actual Mask\nGA Area {target['ga_area_m2_reported']:.0f} m²", fontsize=7.5, color="#142c3b", pad=4)
        for column, family in enumerate(FAMILY_ORDER, start=1):
            family_result = result["families"][family]
            best = family_result["primary_lowest_strict_size_loss"]
            eligible = best is not None
            shown = best or family_result["closest_size_fallback_for_display_only"]
            mask = unpack_mask(shown["mask_hex"], (GRID_SIZE, GRID_SIZE))
            draw_mask(axes[row, column], centered_field(mask))
            status = f"Loss {shown['loss_lower_is_better']:.4f}" if eligible else "No In-Range Mask"
            axes[row, column].set_title(f"{FAMILY_LABELS[family]}\n{status}", fontsize=7.1, color="#142c3b" if eligible else "#8b2f2f", pad=4)
            axes[row, column].text(0.5, -0.075, f"A {shown['visible_area_m2']:.1f} · L {shown['visible_length_m']:.1f} · W {shown['visible_width_m']:.1f} m", transform=axes[row, column].transAxes, ha="center", va="top", fontsize=6.1, color="#334d5c")
        if row < len(object_ids) - 1:
            y = 0.929 - (row + 1) * 0.177
            fig.add_artist(mpl.lines.Line2D([0.035, 0.985], [y, y], transform=fig.transFigure, color="#c8d0d4", lw=0.6))
    fig.text(0.5, 0.013, "Whole, documented-boundary and random-cut shells are geometry sensitivities, not fracture or flooding probabilities. Candidate colours are display-only.", ha="center", fontsize=7.0, color="#5d4b3e")
    fig.subplots_adjust(left=0.045, right=0.985, top=0.928, bottom=0.047, wspace=0.22, hspace=0.58)
    for suffix in ("pdf", "svg"):
        fig.savefig(bundle / "outputs" / f"fuselage-common-scale-mask-panel.{suffix}", facecolor=fig.get_facecolor())
    fig.savefig(bundle / "outputs" / "fuselage-common-scale-mask-panel.png", dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)


def loss_heatmap(bundle: Path, results: dict) -> None:
    object_ids = list(results["extended_strict_size_rankings"])
    families = list(results["family_summary_with_previous_controls"])
    values = np.full((len(object_ids), len(families)), np.nan)
    counts = np.zeros_like(values, dtype=int)
    for row, object_id in enumerate(object_ids):
        rows = {record["family"]: record for record in results["extended_strict_size_rankings"][object_id]}
        for column, family in enumerate(families):
            if family in rows:
                values[row, column] = rows[family]["primary_loss_lower_is_better"]
                counts[row, column] = rows[family]["strict_size_candidate_count"]
    colour_map = LinearSegmentedColormap.from_list("paper_loss", ["#315b7c", "#d5c79f", "#a54b3f"])
    fig, ax = plt.subplots(figsize=(11.7, 4.9))
    fig.patch.set_facecolor("#f4f0e7")
    ax.set_facecolor("#eee9df")
    image = ax.imshow(values, vmin=0.25, vmax=0.43, cmap=colour_map, aspect="auto")
    for row in range(values.shape[0]):
        finite = np.flatnonzero(np.isfinite(values[row]))
        minimum_column = finite[np.argmin(values[row, finite])]
        for column in range(values.shape[1]):
            if not np.isfinite(values[row, column]):
                ax.text(column, row, "—", ha="center", va="center", fontsize=8, color="#807b72")
                continue
            ax.text(column, row, f"{values[row, column]:.4f}\n(n={counts[row, column]})", ha="center", va="center", fontsize=6.7, color="white" if values[row, column] < 0.29 or values[row, column] > 0.40 else "#172f3c", fontweight="semibold" if column == minimum_column else "normal")
        ax.add_patch(Rectangle((minimum_column - 0.5, row - 0.5), 1, 1, fill=False, edgecolor="#f6e9ae", lw=2.0))
    ax.set_xticks(range(len(families)), [SHORT_LABELS[family] for family in families], fontsize=7.4)
    ax.set_yticks(range(len(object_ids)), [f"PHR_4 {item[-2:]}" for item in object_ids], fontsize=8.5)
    ax.tick_params(length=0)
    ax.set_title("Strict-Size Minimum Two-View Mask Loss Across Aircraft and Control Families", fontsize=12.2, fontweight="semibold", color="#142c3b", pad=22)
    ax.text(0.5, 1.035, "Lower is more similar; n is the number of size-eligible masks. Outlined cells are the lowest loss for that object.", transform=ax.transAxes, ha="center", va="bottom", fontsize=8, color="#334d5c")
    colour_bar = fig.colorbar(image, ax=ax, fraction=0.025, pad=0.015)
    colour_bar.set_label("Loss (Lower Is More Similar)", fontsize=7.5)
    colour_bar.ax.tick_params(labelsize=7)
    fig.text(0.5, 0.018, "Best-of-search values are descriptive controls, not likelihoods or identity probabilities. Family means are not comparable when eligibility differs.", ha="center", fontsize=7.1, color="#5d4b3e")
    fig.subplots_adjust(left=0.09, right=0.955, top=0.79, bottom=0.24)
    for suffix in ("pdf", "svg"):
        fig.savefig(bundle / "outputs" / f"extended-family-loss-comparison.{suffix}", facecolor=fig.get_facecolor())
    fig.savefig(bundle / "outputs" / "extended-family-loss-comparison.png", dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)


def unpack_display_mask(value: str) -> np.ndarray:
    packed = np.frombuffer(bytes.fromhex(value), dtype=np.uint8)
    bits = np.unpackbits(packed, bitorder="big")
    return bits[: 48 * 48].reshape((48, 48)).astype(bool)


def pca_source_image(bundle: Path, view: dict) -> Image.Image:
    return Image.open(bundle / "data" / view["source_file"]).convert("RGB")


def published_pca_field(bundle: Path, view: dict, output_side: int = 384) -> np.ndarray:
    source = pca_source_image(bundle, view)
    component = view["baseline_component"]
    half_side = FIELD_METRES / view["scale_m_per_report_pixel"] / 2.0
    extent = (
        component["centroid_source_x"] - half_side,
        component["centroid_source_y"] - half_side,
        component["centroid_source_x"] + half_side,
        component["centroid_source_y"] + half_side,
    )
    field = source.transform(
        (output_side, output_side),
        Image.Transform.EXTENT,
        extent,
        resample=Image.Resampling.BICUBIC,
    )
    return np.asarray(field)


def published_component_dimensions(view: dict) -> dict:
    """Recover physical PCA-component dimensions before display resampling."""
    points = np.asarray(view["relative_component_pixels"], dtype=float)
    scale = float(view["scale_m_per_report_pixel"])
    angle = math.radians(view["baseline_component"]["orientation_degrees"])
    cosine, sine = math.cos(angle), math.sin(angle)
    first = points[:, 0] * cosine + points[:, 1] * sine
    second = -points[:, 0] * sine + points[:, 1] * cosine
    extents = sorted(
        (
            (float(np.ptp(first)) + 1.0) * scale,
            (float(np.ptp(second)) + 1.0) * scale,
        ),
        reverse=True,
    )
    return {
        "visible_area_m2": len(points) * scale**2,
        "visible_length_m": extents[0],
        "visible_width_m": extents[1],
    }


def pca_palette(bundle: Path, view: dict) -> tuple[np.ndarray, np.ndarray]:
    image = np.asarray(pca_source_image(bundle, view), dtype=float)
    height, width = image.shape[:2]
    component = view["baseline_component"]
    points = np.asarray(view["relative_component_pixels"], dtype=float)
    xs = np.rint(points[:, 0] + component["centroid_source_x"]).astype(int)
    ys = np.rint(points[:, 1] + component["centroid_source_y"]).astype(int)
    valid = (xs >= 0) & (xs < width) & (ys >= 0) & (ys < height)
    object_colour = np.median(image[ys[valid], xs[valid]], axis=0)
    x0, y0 = math.floor(width * 0.06), math.floor(height * 0.18)
    x1, y1 = math.ceil(width * 0.58), math.ceil(height * 0.90)
    crop = image[y0:y1, x0:x1]
    members = np.zeros((height, width), dtype=bool)
    members[ys[valid], xs[valid]] = True
    member_crop = members[y0:y1, x0:x1]
    red, green, blue = crop[..., 0], crop[..., 1], crop[..., 2]
    red_annotation = (red > 70) & (red > green * 1.35) & (red > blue * 1.25)
    background_colour = np.median(crop[~member_crop & ~red_annotation], axis=0)
    return object_colour, background_colour


def pca_proxy(mask: np.ndarray, palette: tuple[np.ndarray, np.ndarray]) -> np.ndarray:
    object_colour, background_colour = palette
    indices = np.arange(mask.size, dtype=float).reshape(mask.shape)
    wave = 5.0 * np.sin(indices * 0.071) + 3.0 * np.cos(indices * 0.137)
    output = background_colour[None, None, :] + wave[..., None]
    output = np.where(mask[..., None], object_colour[None, None, :] + wave[..., None], output)
    return np.clip(np.rint(output), 0, 255).astype(np.uint8)


def integer_iou(first: int, second: int) -> float:
    union = (first | second).bit_count()
    return (first & second).bit_count() / union if union else 0.0


def pca_oriented_fuselage_mask(mask: np.ndarray, pca_view: dict) -> np.ndarray:
    target = int(pca_view["normalized_mask_integer"])
    variants = (mask, np.fliplr(mask), np.flipud(mask), np.flipud(np.fliplr(mask)))
    scored = []
    for variant in variants:
        dimensions = oriented_dimensions(variant)
        scored.append((integer_iou(target, mask_integer(dimensions["normalized"])), variant, dimensions))
    _, selected, dimensions = max(scored, key=lambda item: item[0])
    selected = centered_field(selected, side=GRID_SIZE)
    rotation = pca_view["baseline_component"]["orientation_degrees"] - dimensions["orientation_degrees"]
    rotated = ndimage.rotate(selected.astype(np.uint8), rotation, reshape=False, order=0, mode="constant", cval=0, prefilter=False).astype(bool)
    return centered_field(rotated)


def fuselage_minimum(results: dict, object_id: str) -> dict:
    options = []
    for family in FAMILY_ORDER:
        record = results["objects"][object_id]["families"][family]["primary_lowest_strict_size_loss"]
        if record is not None:
            options.append((record["loss_lower_is_better"], family, record))
    _, family, record = min(options, key=lambda item: item[0])
    output = dict(record)
    output["selected_family"] = family
    output["strict_size_eligible"] = True
    output["source_label"] = FAMILY_LABELS[family]
    return output
def fuselage_pca_minimum(results: dict, object_id: str) -> dict:
    options = []
    fallbacks = []
    for family in FAMILY_ORDER:
        family_result = results["objects"][object_id]["families"][family]
        record = family_result["pca_only_lowest_strict_size_loss"]
        if record is not None:
            options.append(
                (record["pca_loss_lower_is_better"], family, record, True)
            )
            continue
        fallback = family_result[
            "pca_only_closest_size_fallback_for_display_only"
        ]
        if fallback is not None:
            fallbacks.append(
                (
                    fallback["pca_loss_lower_is_better"],
                    family,
                    fallback,
                    False,
                )
            )
    selected = min(options or fallbacks, key=lambda item: item[0])
    _, family, record, eligible = selected
    output = dict(record)
    output["selected_family"] = family
    output["strict_size_eligible"] = eligible
    output["source_label"] = FAMILY_LABELS[family]
    return output


def source_label(record: dict) -> str:
    subtype = record["source_subtype"]
    wing_subtype = subtype.split(":")[0]
    if subtype in SOURCE_LABELS:
        return SOURCE_LABELS[subtype]
    if wing_subtype in SOURCE_LABELS:
        return SOURCE_LABELS[wing_subtype]
    if subtype == "complete-shell":
        return "Whole 777 Fuselage"
    if subtype.startswith("section-"):
        return f"Documented Section {subtype.removeprefix('section-')}"
    if subtype == "sections-44-45":
        return "Documented Sections 44/45"
    if subtype == "random-two-cut-section":
        return f"Random Section, {record['section_length_m']:.2f} m Long"
    return record.get("source_label", subtype.replace("_", " ").title())


def polygon_array(points) -> np.ndarray:
    if isinstance(points, np.ndarray):
        return points.astype(float)
    return np.asarray([[point["x"], point["y"]] for point in points], dtype=float)


def grouped_category_records(results: dict, legacy_masks: dict, object_id: str) -> dict:
    records = {
        category: dict(legacy_masks["objects"][object_id][category])
        for category in CATEGORY_ORDER[:-1]
    }
    records["fuselage_sections"] = fuselage_minimum(results, object_id)
    return records
def grouped_pca_category_records(
    results: dict,
    pca_masks: dict,
    object_id: str,
) -> dict:
    records = {
        category: dict(pca_masks["objects"][object_id][category])
        for category in CATEGORY_ORDER[:-1]
    }
    records["fuselage_sections"] = fuselage_pca_minimum(
        results, object_id
    )
    return records


def display_mask_for_category(category: str, record: dict, pca_view: dict) -> np.ndarray:
    if category == "fuselage_sections":
        raw = unpack_mask(record["mask_hex"], (GRID_SIZE, GRID_SIZE))
        return pca_oriented_fuselage_mask(raw, pca_view)
    return unpack_display_mask(record["mask_hex"])


def orient_pca_display_mask(
    mask: np.ndarray,
    object_id: str,
    category: str,
) -> np.ndarray:
    """Choose a loss-admissible display direction without changing scoring."""
    quarter_turns = PCA_DISPLAY_QUARTER_TURNS.get((object_id, category), 0)
    return np.rot90(mask, quarter_turns).copy() if quarter_turns else mask


def full_component_geometry(
    category: str,
    record: dict,
    component_context: dict,
    profile,
) -> tuple[np.ndarray, list[np.ndarray]]:
    if category == "wing":
        component = component_context["components"][record["source_subtype"].split(":")[0]]
        outline = polygon_array(component["polygon"])
        negatives = [polygon_array(item) for item in component["negative_polygons"]]
    elif category == "other_777_parts":
        component = component_context["components"][record["source_subtype"]]
        outline = polygon_array(component["polygon"])
        negatives = [polygon_array(item) for item in component["negative_polygons"]]
    elif category == "fuselage_sections":
        outline = project_segment_polygon(
            profile,
            record["x0_m"],
            record["x1_m"],
            view_axis_cosine=0.0,
        )
        negatives = []
    else:
        raise ValueError(f"No full-component geometry for category {category}")
    return outline, negatives


def draw_component_sketch(
    ax,
    outline: np.ndarray,
    negatives: list[np.ndarray],
) -> tuple[np.ndarray, list[np.ndarray]]:
    centre = (outline.min(axis=0) + outline.max(axis=0)) / 2.0
    outline = outline - centre
    negatives = [negative - centre for negative in negatives]
    ax.add_patch(
        Polygon(
            outline,
            closed=True,
            facecolor="#dfb955",
            edgecolor="#5e421c",
            lw=1.0,
        )
    )
    for negative in negatives:
        ax.add_patch(
            Polygon(
                negative,
                closed=True,
                facecolor="#fffdf7",
                edgecolor="#5e421c",
                lw=0.55,
            )
        )
    return outline, negatives


def draw_visible_pose_sketch(ax, mask: np.ndarray) -> np.ndarray:
    ys, xs = np.nonzero(mask)
    centre_x, centre_y = float(xs.mean()), float(ys.mean())
    x = (np.arange(mask.shape[1], dtype=float) - centre_x) * PIXEL_SIZE_M
    y = (np.arange(mask.shape[0], dtype=float) - centre_y) * PIXEL_SIZE_M
    ax.contourf(
        x,
        y,
        mask.astype(float),
        levels=(0.5, 1.5),
        colors=("#dfb955",),
    )
    ax.contour(
        x,
        y,
        mask.astype(float),
        levels=(0.5,),
        colors=("#5e421c",),
        linewidths=(1.0,),
    )
    return np.column_stack(
        (
            (xs - centre_x) * PIXEL_SIZE_M,
            (ys - centre_y) * PIXEL_SIZE_M,
        )
    )


def style_sketch_axis(ax, span: float) -> None:
    half = span / 2.0
    ax.set_xlim(-half, half)
    ax.set_ylim(half, -half)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_facecolor("#fffdf7")
    for spine in ax.spines.values():
        spine.set_color("#9a8b74")
        spine.set_linewidth(0.65)
    bar = 5.0 if span >= 12.0 else 2.0
    start = -half + span * 0.08
    y = half - span * 0.09
    ax.plot(
        [start, start + bar],
        [y, y],
        color="#334d5c",
        lw=1.4,
        solid_capstyle="butt",
    )
    ax.text(
        start + bar / 2.0,
        y - span * 0.035,
        f"{bar:g} m",
        ha="center",
        va="bottom",
        fontsize=6.2,
        color="#334d5c",
    )


def selected_pca_panel(
    bundle: Path,
    targets: dict,
    results: dict,
    pca_masks: dict,
) -> None:
    target_by_id = {record["object_id"]: record for record in targets["objects"]}
    object_ids = list(target_by_id)
    fig, axes = plt.subplots(len(object_ids), 1 + len(CATEGORY_ORDER), figsize=(13.4, 11.8), constrained_layout=False)
    fig.patch.set_facecolor("#f4f0e7")
    fig.suptitle("Published Pléiades PCA Panels and Lowest PCA-Loss Category Proxies", y=0.988, fontsize=14.2, fontweight="semibold", color="#142c3b")
    fig.text(0.5, 0.963, "Five retained PHR_4 rating-5 objects; every image field is 24 m × 24 m and carries the same 5 m ruler.", ha="center", fontsize=8.4, color="#334d5c")
    for row, object_id in enumerate(object_ids):
        target = target_by_id[object_id]
        pca_view = target["views"]["pca"]
        palette = pca_palette(bundle, pca_view)
        ax = axes[row, 0]
        ax.imshow(published_pca_field(bundle, pca_view), origin="upper", interpolation="bicubic", extent=(0, FIELD_METRES, FIELD_METRES, 0))
        style_field_axis(ax)
        ax.set_title(f"Published PCA\nGA Area {target['ga_area_m2_reported']:.0f} m²", fontsize=6.8, color="#142c3b", pad=3)
        reference_dimensions = published_component_dimensions(pca_view)
        ax.text(
            0.5,
            -0.075,
            f"A {reference_dimensions['visible_area_m2']:.1f} · "
            f"L {reference_dimensions['visible_length_m']:.1f} · "
            f"W {reference_dimensions['visible_width_m']:.1f} m",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=5.7,
            color="#334d5c",
        )
        ax.text(-0.23, 0.5, f"PHR_4\n{object_id[-2:]}", transform=ax.transAxes, ha="center", va="center", fontsize=8.2, fontweight="semibold", color="#142c3b")
        records = grouped_pca_category_records(results, pca_masks, object_id)
        winner = min(
            (record["pca_loss_lower_is_better"], category)
            for category, record in records.items()
            if record["strict_size_eligible"]
        )[1]
        for column, category in enumerate(CATEGORY_ORDER, start=1):
            record = records[category]
            display_mask = display_mask_for_category(category, record, pca_view)
            display_mask = orient_pca_display_mask(
                display_mask,
                object_id,
                category,
            )
            ax = axes[row, column]
            ax.imshow(pca_proxy(display_mask, palette), origin="upper", interpolation="nearest", extent=(0, FIELD_METRES, FIELD_METRES, 0))
            is_winner = category == winner
            eligible = record["strict_size_eligible"]
            border = "#b68522" if is_winner else ("#9a3f3f" if not eligible else "#80919c")
            style_field_axis(ax, border=border, linewidth=1.8 if is_winner else 0.8)
            label = source_label(record)
            if eligible:
                title, title_colour = f"{label}\nPCA Loss {record['pca_loss_lower_is_better']:.4f}", "#142c3b"
            else:
                title, title_colour = f"No In-Range Mask\nClosest: {label} · {record['pca_loss_lower_is_better']:.4f}", "#8b2f2f"
            ax.set_title(title, fontsize=6.5, color=title_colour, pad=3)
            ax.text(0.5, -0.075, f"A {record['visible_area_m2']:.1f} · L {record['visible_length_m']:.1f} · W {record['visible_width_m']:.1f} m", transform=ax.transAxes, ha="center", va="top", fontsize=5.7, color="#334d5c")
    axes[0, 0].text(0.5, 1.30, "Published Reference", transform=axes[0, 0].transAxes, ha="center", va="bottom", fontsize=8.2, fontweight="semibold", color="#142c3b")
    for column, category in enumerate(CATEGORY_ORDER, start=1):
        axes[0, column].text(0.5, 1.30, CATEGORY_HEADERS[category], transform=axes[0, column].transAxes, ha="center", va="bottom", fontsize=7.5, fontweight="semibold", color="#142c3b", linespacing=1.05)
    fig.text(0.5, 0.041, "Simulated colours and loss-equivalent orientations are display proxies; PCA loss is 1 − reflected PCA-mask IoU after the strict area–length–width gate. Red cells are closest-size displays only.", ha="center", fontsize=7.0, color="#5d4b3e")
    fig.text(0.5, 0.020, "Gold borders mark the lowest eligible category. Eligibility is two-sided: area, length and width must each fall between the audited lower and upper limits.", ha="center", fontsize=6.7, color="#5d4b3e")
    fig.subplots_adjust(left=0.065, right=0.99, top=0.905, bottom=0.075, wspace=0.13, hspace=0.52)
    for suffix in ("pdf", "svg"):
        fig.savefig(bundle / "outputs" / f"published-pca-category-minima-panel.{suffix}", facecolor=fig.get_facecolor())
    fig.savefig(bundle / "outputs" / "published-pca-category-minima-panel.png", dpi=300, facecolor=fig.get_facecolor())
    plt.close(fig)


def selected_aircraft_sketches(
    bundle: Path,
    targets: dict,
    results: dict,
    legacy_masks: dict,
    component_context: dict,
    geometry: dict,
) -> None:
    profile = radius_profile_from_polygon(
        geometry["coordinates_m"]["full_fuselage_shell"]
    )
    selected = []
    for target in targets["objects"]:
        object_id = target["object_id"]
        records = grouped_category_records(results, legacy_masks, object_id)
        _, category = min(
            (record["loss_lower_is_better"], category)
            for category, record in records.items()
            if record["strict_size_eligible"]
        )
        if category in {"wing", "other_777_parts", "fuselage_sections"}:
            selected.append((target, category, records[category]))

    fig, axes = plt.subplots(
        2,
        len(selected),
        figsize=(11.0, 6.8),
        constrained_layout=False,
    )
    fig.patch.set_facecolor("#f4f0e7")
    fig.suptitle(
        "Full 777 Components and Their Lowest-Loss Visible Poses",
        y=0.982,
        fontsize=13.2,
        fontweight="semibold",
        color="#142c3b",
    )
    fig.text(
        0.5,
        0.947,
        "Each top–bottom pair shares one physical scale; scales differ between columns.",
        ha="center",
        fontsize=8.2,
        color="#334d5c",
    )
    for column, (target, category, record) in enumerate(selected):
        pca_view = target["views"]["pca"]
        outline, negatives = full_component_geometry(
            category,
            record,
            component_context,
            profile,
        )
        centred_outline, _ = draw_component_sketch(
            axes[0, column],
            outline,
            negatives,
        )
        display_mask = display_mask_for_category(category, record, pca_view)
        visible_points = draw_visible_pose_sketch(
            axes[1, column],
            display_mask,
        )
        full_span = float(np.ptp(centred_outline, axis=0).max())
        visible_span = float(np.ptp(visible_points, axis=0).max() + PIXEL_SIZE_M)
        shared_span = max(full_span, visible_span) * 1.22
        style_sketch_axis(axes[0, column], shared_span)
        style_sketch_axis(axes[1, column], shared_span)
        axes[0, column].set_title(
            f"PHR_4 {target['object_id'][-2:]} · {source_label(record)}\n"
            "Full Component Outline",
            fontsize=8.2,
            color="#142c3b",
            pad=6,
            fontweight="semibold",
        )
        axes[1, column].set_title(
            f"Matched Visible Pose · Loss {record['loss_lower_is_better']:.4f}\n"
            f"A {record['visible_area_m2']:.1f} · "
            f"L {record['visible_length_m']:.1f} · "
            f"W {record['visible_width_m']:.1f} m",
            fontsize=7.4,
            color="#142c3b",
            pad=6,
        )
    fig.text(
        0.5,
        0.020,
        "Section 47 is the documented BS 1832–2150 interval (8.08 m), "
        "immediately forward of the BS 2150 aft pressure bulkhead; "
        "it is not a claimed fracture weak point.",
        ha="center",
        fontsize=7.0,
        color="#5d4b3e",
    )
    fig.subplots_adjust(
        left=0.045,
        right=0.985,
        top=0.875,
        bottom=0.065,
        wspace=0.20,
        hspace=0.28,
    )
    for suffix in ("pdf", "svg"):
        fig.savefig(
            bundle / "outputs" / f"selected-777-full-and-matched-sketches.{suffix}",
            facecolor=fig.get_facecolor(),
        )
    fig.savefig(
        bundle / "outputs" / "selected-777-full-and-matched-sketches.png",
        dpi=400,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)
def _point_in_polygon(x: float, y: float, polygon: np.ndarray) -> bool:
    inside = False
    second = len(polygon) - 1
    for first in range(len(polygon)):
        a = polygon[first]
        b = polygon[second]
        if ((a[1] > y) != (b[1] > y)) and (
            x
            < (b[0] - a[0]) * (y - a[1]) / (b[1] - a[1] + 1e-12)
            + a[0]
        ):
            inside = not inside
        second = first
    return inside


def _line_intersections_at_y(polygon: np.ndarray, y: float) -> list[float]:
    intersections = []
    second = len(polygon) - 1
    for first in range(len(polygon)):
        a = polygon[second]
        b = polygon[first]
        if (a[1] <= y < b[1]) or (b[1] <= y < a[1]):
            intersections.append(
                float(a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1]))
            )
        second = first
    return sorted(intersections)


def _transform_world(
    points: np.ndarray,
    matrix: np.ndarray,
    heave_m: float,
) -> np.ndarray:
    world = np.asarray(points, dtype=float) @ matrix.T
    world[:, 2] += heave_m
    return world


def wing_pose_surface_geometry(
    component: dict,
    parameters: dict,
    pose: dict,
    step_m: float = 1.0,
) -> dict:
    """Recreate the first-order wing cells and transform the complete 3D shell."""
    outline = polygon_array(component["polygon"])
    negatives = [
        polygon_array(item) for item in component.get("negative_polygons", [])
    ]
    minimum = outline.min(axis=0)
    maximum = outline.max(axis=0)
    centre = (minimum + maximum) / 2.0
    root_absolute_y = float(np.min(np.abs(outline[:, 1])))
    tip_absolute_y = float(np.max(np.abs(outline[:, 1])))
    plan_xy = []
    thickness = []
    span_fraction = []
    chord_fraction = []
    y_values = np.arange(
        minimum[1] + step_m / 2.0,
        maximum[1],
        step_m,
    )
    x_values = np.arange(
        minimum[0] + step_m / 2.0,
        maximum[0],
        step_m,
    )
    for y in y_values:
        intersections = _line_intersections_at_y(outline, float(y))
        if len(intersections) < 2:
            continue
        leading_x = intersections[0]
        trailing_x = intersections[-1]
        for x in x_values:
            if not _point_in_polygon(float(x), float(y), outline):
                continue
            if any(
                _point_in_polygon(float(x), float(y), negative)
                for negative in negatives
            ):
                continue
            span = float(
                np.clip(
                    (abs(y) - root_absolute_y)
                    / (tip_absolute_y - root_absolute_y),
                    0.0,
                    1.0,
                )
            )
            chord = float(
                np.clip(
                    (x - leading_x) / max(1e-6, trailing_x - leading_x),
                    0.0,
                    1.0,
                )
            )
            maximum_thickness = (
                parameters["root_max_thickness_m"]
                + (
                    parameters["tip_max_thickness_m"]
                    - parameters["root_max_thickness_m"]
                )
                * span**0.8
            )
            airfoil_factor = max(0.12, 4.0 * chord * (1.0 - chord))
            plan_xy.append((x - centre[0], y - centre[1]))
            thickness.append(maximum_thickness * airfoil_factor)
            span_fraction.append(span)
            chord_fraction.append(chord)
    plan_xy = np.asarray(plan_xy, dtype=float)
    thickness = np.asarray(thickness, dtype=float)
    span_fraction = np.asarray(span_fraction, dtype=float)
    chord_fraction = np.asarray(chord_fraction, dtype=float)
    if len(plan_xy) < 30:
        raise ValueError("Too few plan cells to render wing attitude")

    triangles = Delaunay(plan_xy).simplices
    centroids = plan_xy[triangles].mean(axis=1) + centre
    inside = MplPath(outline).contains_points(centroids, radius=1e-7)
    for negative in negatives:
        inside &= ~MplPath(negative).contains_points(centroids, radius=1e-7)
    triangle_points = plan_xy[triangles]
    edge_lengths = np.stack(
        (
            np.linalg.norm(triangle_points[:, 0] - triangle_points[:, 1], axis=1),
            np.linalg.norm(triangle_points[:, 1] - triangle_points[:, 2], axis=1),
            np.linalg.norm(triangle_points[:, 2] - triangle_points[:, 0], axis=1),
        ),
        axis=1,
    )
    triangles = triangles[inside & (edge_lengths.max(axis=1) <= step_m * 1.8)]

    top_local = np.column_stack((plan_xy, thickness / 2.0))
    bottom_local = np.column_stack((plan_xy, -thickness / 2.0))
    matrix = np.asarray(pose["matrix"], dtype=float)
    heave_m = float(pose["heave_m"])
    top_world = _transform_world(top_local, matrix, heave_m)
    bottom_world = _transform_world(bottom_local, matrix, heave_m)
    faces = [top_world[index] for index in triangles]
    faces.extend(bottom_world[index[::-1]] for index in triangles)

    boundary_local_xy = outline - centre

    def boundary_thickness(x: float, y: float) -> float:
        evaluation_y = float(
            np.clip(y, minimum[1] + 1e-6, maximum[1] - 1e-6)
        )
        intersections = _line_intersections_at_y(outline, evaluation_y)
        if len(intersections) < 2:
            chord = 0.0
        else:
            chord = float(
                np.clip(
                    (x - intersections[0])
                    / max(1e-6, intersections[-1] - intersections[0]),
                    0.0,
                    1.0,
                )
            )
        span = float(
            np.clip(
                (abs(y) - root_absolute_y)
                / (tip_absolute_y - root_absolute_y),
                0.0,
                1.0,
            )
        )
        maximum_thickness = (
            parameters["root_max_thickness_m"]
            + (
                parameters["tip_max_thickness_m"]
                - parameters["root_max_thickness_m"]
            )
            * span**0.8
        )
        return maximum_thickness * max(0.12, 4.0 * chord * (1.0 - chord))

    boundary_t = np.asarray(
        [boundary_thickness(x, y) for x, y in outline],
        dtype=float,
    )
    boundary_top = _transform_world(
        np.column_stack((boundary_local_xy, boundary_t / 2.0)),
        matrix,
        heave_m,
    )
    boundary_bottom = _transform_world(
        np.column_stack((boundary_local_xy, -boundary_t / 2.0)),
        matrix,
        heave_m,
    )
    for index in range(len(outline)):
        following = (index + 1) % len(outline)
        faces.append(
            np.asarray(
                (
                    boundary_top[index],
                    boundary_top[following],
                    boundary_bottom[following],
                    boundary_bottom[index],
                )
            )
        )

    reference_masks = {
        "root": span_fraction < 0.12,
        "tip": span_fraction > 0.88,
        "leading": chord_fraction < 0.12,
        "trailing": chord_fraction > 0.88,
    }
    references = {}
    for name, mask in reference_masks.items():
        local = np.asarray(
            [[plan_xy[mask, 0].mean(), plan_xy[mask, 1].mean(), 0.0]]
        )
        references[name] = _transform_world(local, matrix, heave_m)[0]
    return {
        "faces": faces,
        "references": references,
        "plan_cell_count": len(plan_xy),
    }


def _clip_face_at_sea_level(
    face: np.ndarray,
    keep_above: bool,
) -> np.ndarray:
    output = []
    previous = face[-1]
    previous_inside = previous[2] >= 0.0 if keep_above else previous[2] <= 0.0
    for current in face:
        current_inside = (
            current[2] >= 0.0 if keep_above else current[2] <= 0.0
        )
        if current_inside != previous_inside:
            fraction = -previous[2] / (current[2] - previous[2])
            output.append(previous + fraction * (current - previous))
        if current_inside:
            output.append(current)
        previous = current
        previous_inside = current_inside
    return np.asarray(output, dtype=float)


def _sea_level_segment(face: np.ndarray) -> np.ndarray | None:
    points = []
    for index in range(len(face)):
        first = face[index]
        second = face[(index + 1) % len(face)]
        if abs(first[2]) <= 1e-10:
            points.append(first.copy())
        if first[2] * second[2] < 0.0:
            fraction = -first[2] / (second[2] - first[2])
            points.append(first + fraction * (second - first))
    unique = []
    for point in points:
        if not any(np.linalg.norm(point - other) < 1e-7 for other in unique):
            unique.append(point)
    if len(unique) < 2:
        return None
    farthest = None
    maximum_distance = -1.0
    for first in range(len(unique)):
        for second in range(first + 1, len(unique)):
            distance = float(np.linalg.norm(unique[first] - unique[second]))
            if distance > maximum_distance:
                maximum_distance = distance
                farthest = np.asarray((unique[first], unique[second]))
    return farthest


def split_wing_faces_at_waterline(faces: list[np.ndarray]) -> dict:
    above = []
    below = []
    segments = []
    segment_keys = set()
    for face in faces:
        clipped_above = _clip_face_at_sea_level(face, True)
        clipped_below = _clip_face_at_sea_level(face, False)
        if len(clipped_above) >= 3:
            above.append(clipped_above)
        if len(clipped_below) >= 3:
            below.append(clipped_below)
        segment = _sea_level_segment(face)
        if segment is None:
            continue
        endpoints = [
            tuple(np.round(point, 6))
            for point in segment
        ]
        key = tuple(sorted(endpoints))
        if key not in segment_keys:
            segment_keys.add(key)
            segments.append(segment)
    return {"above": above, "below": below, "waterline": segments}


def phr4_18_wing_attitude_figure(
    bundle: Path,
    pca_masks: dict,
    component_context: dict,
) -> None:
    record = pca_masks["objects"]["phr-4-object-18"]["wing"]
    if not record["strict_size_eligible"]:
        raise ValueError("PHR_4 18 PCA-only wing minimum is not size eligible")
    metadata = record["metadata"]
    pose = metadata["pose"]
    parameters = metadata["model_parameters"]
    component = component_context["components"][record["source_subtype"]]
    geometry = wing_pose_surface_geometry(
        component,
        parameters,
        pose,
    )
    split = split_wing_faces_at_waterline(geometry["faces"])

    fig = plt.figure(figsize=(12.6, 8.2))
    fig.patch.set_facecolor("#f4f0e7")
    ax = fig.add_axes((0.035, 0.105, 0.71, 0.79), projection="3d")
    ax.set_facecolor("#f4f0e7")
    ax.computed_zorder = False
    below = Poly3DCollection(
        split["below"],
        facecolor="#2f8194",
        edgecolor="#1e5868",
        linewidth=0.16,
        alpha=0.80,
        zorder=1,
    )
    above = Poly3DCollection(
        split["above"],
        facecolor="#dcae4d",
        edgecolor="#72521d",
        linewidth=0.18,
        alpha=0.97,
        zorder=4,
    )
    ax.add_collection3d(below)
    ax.add_collection3d(above)

    all_points = np.concatenate(geometry["faces"], axis=0)
    x_limits = (float(all_points[:, 0].min()), float(all_points[:, 0].max()))
    y_limits = (float(all_points[:, 1].min()), float(all_points[:, 1].max()))
    z_limits = (float(all_points[:, 2].min()), float(all_points[:, 2].max()))
    margin = 2.3
    plane_x, plane_y = np.meshgrid(
        np.linspace(x_limits[0] - margin, x_limits[1] + margin, 2),
        np.linspace(y_limits[0] - margin, y_limits[1] + margin, 2),
    )
    ax.plot_surface(
        plane_x,
        plane_y,
        np.zeros_like(plane_x),
        color="#80bfd4",
        alpha=0.20,
        edgecolor="#4f8ea4",
        linewidth=0.55,
        shade=False,
        zorder=2,
    )
    plane_boundary = [
        (
            (x_limits[0] - margin, y_limits[0] - margin, 0.0),
            (x_limits[1] + margin, y_limits[0] - margin, 0.0),
            (x_limits[1] + margin, y_limits[1] + margin, 0.0),
            (x_limits[0] - margin, y_limits[1] + margin, 0.0),
            (x_limits[0] - margin, y_limits[0] - margin, 0.0),
        )
    ]
    ax.add_collection3d(
        Line3DCollection(
            plane_boundary,
            colors="#39758b",
            linewidths=0.8,
            alpha=0.65,
            zorder=3,
        )
    )
    if split["waterline"]:
        ax.add_collection3d(
            Line3DCollection(
                split["waterline"],
                colors="#16475b",
                linewidths=3.0,
                zorder=6,
            )
        )
        ax.add_collection3d(
            Line3DCollection(
                split["waterline"],
                colors="#f8fcff",
                linewidths=1.45,
                zorder=7,
            )
        )

    references = geometry["references"]
    for name, label in (
        ("root", "Root"),
        ("tip", "Tip"),
        ("leading", "Leading edge"),
        ("trailing", "Trailing edge"),
    ):
        point = references[name]
        ax.scatter(
            [point[0]],
            [point[1]],
            [point[2]],
            s=14,
            color="#152f3d",
            depthshade=False,
            zorder=8,
        )
        ax.text(
            point[0],
            point[1],
            point[2] + 0.45,
            label,
            fontsize=7.0,
            color="#152f3d",
            zorder=9,
        )

    ax.set_xlim(x_limits[0] - margin, x_limits[1] + margin)
    ax.set_ylim(y_limits[0] - margin, y_limits[1] + margin)
    ax.set_zlim(z_limits[0] - 1.0, z_limits[1] + 1.0)
    ax.set_box_aspect(
        (
            x_limits[1] - x_limits[0] + 2 * margin,
            y_limits[1] - y_limits[0] + 2 * margin,
            z_limits[1] - z_limits[0] + 2.0,
        )
    )
    ax.set_proj_type("persp", focal_length=0.92)
    ax.view_init(elev=22, azim=-57)
    ax.set_xlabel("World x (m)", fontsize=7.5, labelpad=7)
    ax.set_ylabel("World y (m)", fontsize=7.5, labelpad=7)
    ax.set_zlabel("Height relative to sea level (m)", fontsize=7.5, labelpad=8)
    ax.tick_params(labelsize=6.5, colors="#334d5c", pad=1)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("#aeb8bc")
        axis._axinfo["grid"]["color"] = (0.67, 0.72, 0.74, 0.45)

    fig.suptitle(
        "PHR_4 18 — Complete Wing Attitude for the PCA-Only Minimum",
        y=0.975,
        fontsize=14.0,
        fontweight="semibold",
        color="#142c3b",
    )
    fig.text(
        0.5,
        0.943,
        "Model-derived 3D perspective; the level sea surface and its intersection with the wing are shown explicitly.",
        ha="center",
        fontsize=8.6,
        color="#334d5c",
    )
    fig.text(
        0.765,
        0.865,
        "Exact simulation record",
        fontsize=10.0,
        fontweight="semibold",
        color="#142c3b",
    )
    fig.text(
        0.765,
        0.825,
        f"{record['candidate_id']}\n"
        f"{source_label(record)}\n"
        f"PCA IoU {record['silhouette_iou_pca']:.4f}\n"
        f"PCA loss {record['pca_loss_lower_is_better']:.4f}",
        fontsize=8.5,
        linespacing=1.45,
        color="#263f4d",
        va="top",
    )
    fig.text(
        0.765,
        0.675,
        "Attitude and immersion",
        fontsize=10.0,
        fontweight="semibold",
        color="#142c3b",
    )
    fig.text(
        0.765,
        0.635,
        f"Roll {pose['roll_degrees']:+.2f}°\n"
        f"Pitch {pose['pitch_degrees']:+.2f}°\n"
        f"Heave {pose['heave_m']:+.3f} m\n"
        f"Tip {abs(pose['root_to_tip_height_difference_m']):.3f} m below root\n"
        f"Trailing edge {abs(pose['leading_to_trailing_height_difference_m']):.3f} m below leading edge",
        fontsize=8.5,
        linespacing=1.45,
        color="#263f4d",
        va="top",
    )
    fig.legend(
        handles=[
            mpl.patches.Patch(
                facecolor="#dcae4d",
                edgecolor="#72521d",
                label="Wing above sea level",
            ),
            mpl.patches.Patch(
                facecolor="#2f8194",
                edgecolor="#1e5868",
                label="Wing below sea level",
            ),
            Line2D(
                (0,),
                (0,),
                color="#16475b",
                lw=3.0,
                marker=None,
                label="Waterline on wing",
            ),
            mpl.patches.Patch(
                facecolor="#80bfd4",
                edgecolor="#39758b",
                alpha=0.35,
                label="Level sea surface, z = 0",
            ),
        ],
        loc="lower left",
        bbox_to_anchor=(0.755, 0.22),
        frameon=False,
        fontsize=8.0,
        handlelength=2.3,
    )
    fig.text(
        0.5,
        0.025,
        "The complete wing shell is shown. The image-mask simulation retained geometry down to 0.5 m below sea level as a shallow-underwater visibility assumption. "
        "This random pose is a geometric sensitivity, not a hydrostatic-equilibrium prediction.",
        ha="center",
        fontsize=7.2,
        color="#5d4b3e",
        wrap=True,
    )
    for suffix in ("pdf", "svg"):
        fig.savefig(
            bundle
            / "outputs"
            / f"phr4-18-pca-wing-attitude-waterline.{suffix}",
            facecolor=fig.get_facecolor(),
        )
    fig.savefig(
        bundle / "outputs" / "phr4-18-pca-wing-attitude-waterline.png",
        dpi=400,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)


def phr4_18_wing_flooding_sensitivity_figure(
    bundle: Path,
    component_context: dict,
) -> None:
    sensitivity = read_json(
        bundle / "outputs" / "phr4-18-wing-flooding-retention-sensitivity.json"
    )
    model_input = read_json(
        bundle / "data" / "wing-flooding-sensitivity-input.json"
    )
    selected = sensitivity["selected_records"][
        "closest_refined_target_like_with_strict_size"
    ]
    if selected is None:
        raise ValueError("No strict-size target-like flooding equilibrium was found")
    parameters = next(
        item
        for item in model_input["parameter_draws"]
        if item["draw_index"] == selected["draw_index"]
    )
    component = component_context["components"]["left-wing-complete"]
    geometry = wing_pose_surface_geometry(
        component,
        parameters,
        selected["pose"],
    )
    split = split_wing_faces_at_waterline(geometry["faces"])

    fig = plt.figure(figsize=(14.2, 8.0))
    fig.patch.set_facecolor("#f4f0e7")
    ax = fig.add_axes((0.025, 0.115, 0.565, 0.79), projection="3d")
    ax.set_facecolor("#f4f0e7")
    ax.computed_zorder = False
    ax.add_collection3d(
        Poly3DCollection(
            split["below"],
            facecolor="#2f8194",
            edgecolor="#1e5868",
            linewidth=0.15,
            alpha=0.80,
            zorder=1,
        )
    )
    ax.add_collection3d(
        Poly3DCollection(
            split["above"],
            facecolor="#dcae4d",
            edgecolor="#72521d",
            linewidth=0.17,
            alpha=0.97,
            zorder=4,
        )
    )
    all_points = np.concatenate(geometry["faces"], axis=0)
    x_limits = (float(all_points[:, 0].min()), float(all_points[:, 0].max()))
    y_limits = (float(all_points[:, 1].min()), float(all_points[:, 1].max()))
    z_limits = (float(all_points[:, 2].min()), float(all_points[:, 2].max()))
    margin = 2.3
    plane_x, plane_y = np.meshgrid(
        np.linspace(x_limits[0] - margin, x_limits[1] + margin, 2),
        np.linspace(y_limits[0] - margin, y_limits[1] + margin, 2),
    )
    ax.plot_surface(
        plane_x,
        plane_y,
        np.zeros_like(plane_x),
        color="#80bfd4",
        alpha=0.20,
        edgecolor="#4f8ea4",
        linewidth=0.55,
        shade=False,
        zorder=2,
    )
    if split["waterline"]:
        ax.add_collection3d(
            Line3DCollection(
                split["waterline"],
                colors="#16475b",
                linewidths=3.0,
                zorder=6,
            )
        )
        ax.add_collection3d(
            Line3DCollection(
                split["waterline"],
                colors="#f8fcff",
                linewidths=1.35,
                zorder=7,
            )
        )
    for name, label in (
        ("root", "Root"),
        ("tip", "Tip"),
        ("leading", "Leading edge"),
        ("trailing", "Trailing edge"),
    ):
        point = geometry["references"][name]
        ax.scatter(
            [point[0]],
            [point[1]],
            [point[2]],
            s=14,
            color="#152f3d",
            depthshade=False,
            zorder=8,
        )
        ax.text(
            point[0],
            point[1],
            point[2] + 0.45,
            label,
            fontsize=6.8,
            color="#152f3d",
            zorder=9,
        )
    ax.set_xlim(x_limits[0] - margin, x_limits[1] + margin)
    ax.set_ylim(y_limits[0] - margin, y_limits[1] + margin)
    ax.set_zlim(z_limits[0] - 1.0, z_limits[1] + 1.0)
    ax.set_box_aspect(
        (
            x_limits[1] - x_limits[0] + 2 * margin,
            y_limits[1] - y_limits[0] + 2 * margin,
            z_limits[1] - z_limits[0] + 2.0,
        )
    )
    ax.set_proj_type("persp", focal_length=0.92)
    ax.view_init(elev=22, azim=-57)
    ax.set_xlabel("World x (m)", fontsize=7.2, labelpad=6)
    ax.set_ylabel("World y (m)", fontsize=7.2, labelpad=6)
    ax.set_zlabel("Height relative to sea level (m)", fontsize=7.2, labelpad=7)
    ax.tick_params(labelsize=6.2, colors="#334d5c", pad=1)
    for axis in (ax.xaxis, ax.yaxis, ax.zaxis):
        axis.pane.fill = False
        axis.pane.set_edgecolor("#aeb8bc")
        axis._axinfo["grid"]["color"] = (0.67, 0.72, 0.74, 0.45)
    ax.set_title(
        "Closest Target-Like Hydrostatic Equilibrium\n"
        f"Roll {selected['pose']['roll_degrees']:+.0f}°, "
        f"pitch {selected['pose']['pitch_degrees']:+.0f}°, "
        f"tilt {selected['pose']['equivalent_tilt_from_face_on_degrees']:.1f}°",
        fontsize=9.2,
        color="#142c3b",
        pad=2,
    )

    retained = np.asarray(selected["retained_air_fraction"], dtype=float).reshape(3, 3)
    heat = fig.add_axes((0.645, 0.575, 0.285, 0.285))
    colour_map = LinearSegmentedColormap.from_list(
        "flooding_retention",
        ("#e9edf0", "#4c9bb0", "#dcae4d"),
    )
    image_artist = heat.imshow(retained, vmin=0.0, vmax=1.0, cmap=colour_map)
    heat.set_xticks(range(3), ("Leading", "Middle", "Trailing"), fontsize=7.4)
    heat.set_yticks(range(3), ("Root", "Midspan", "Tip"), fontsize=7.4)
    heat.set_title(
        "Modeled Retained-Air Fraction by Sensitivity Cell",
        fontsize=9.0,
        color="#142c3b",
        pad=7,
    )
    for row in range(3):
        for column in range(3):
            value = retained[row, column]
            heat.text(
                column,
                row,
                f"{100 * value:.1f}%",
                ha="center",
                va="center",
                fontsize=8.0,
                fontweight="semibold",
                color="white" if value >= 0.45 else "#18313f",
            )
    for spine in heat.spines.values():
        spine.set_color("#81929d")
        spine.set_linewidth(0.7)
    colour_bar = fig.colorbar(
        image_artist,
        ax=heat,
        fraction=0.046,
        pad=0.035,
        ticks=(0.0, 0.5, 1.0),
    )
    colour_bar.ax.tick_params(labelsize=6.7)
    colour_bar.set_label("Retained fraction", fontsize=7.0)

    height_ax = fig.add_axes((0.625, 0.155, 0.345, 0.285))
    labels = ("Root", "Tip", "Leading", "Trailing")
    keys = ("root", "tip", "leading", "trailing")
    target_heights = sensitivity["target"]["pose"]["reference_heights_m"]
    original = sensitivity["selected_records"]["closest_original_waterline"]
    series = (
        (
            "Selected random pose",
            [target_heights[key] for key in keys],
            "#b68522",
            "o",
        ),
        (
            "Closest refined equilibrium",
            [selected["pose"]["reference_heights_m"][key] for key in keys],
            "#226a7d",
            "s",
        ),
        (
            "Closest original schedule",
            [original["pose"]["reference_heights_m"][key] for key in keys],
            "#7d8589",
            "^",
        ),
    )
    positions = np.arange(len(labels))
    height_ax.axhline(0.0, color="#39758b", lw=1.0, ls="--", alpha=0.8)
    for label, values, colour, marker in series:
        height_ax.plot(
            positions,
            values,
            color=colour,
            marker=marker,
            ms=4.7,
            lw=1.35,
            label=label,
        )
    height_ax.set_xticks(positions, labels, fontsize=7.2)
    height_ax.set_ylabel("Reference height relative to sea level (m)", fontsize=7.3)
    height_ax.tick_params(axis="y", labelsize=6.8)
    height_ax.grid(axis="y", color="#b9c2c4", lw=0.5, alpha=0.55)
    height_ax.set_title(
        "Waterline-Relative Reference Heights",
        fontsize=9.0,
        color="#142c3b",
        pad=6,
    )
    height_ax.legend(
        frameon=False,
        fontsize=6.8,
        loc="lower left",
        handlelength=2.0,
    )
    for spine in height_ax.spines.values():
        spine.set_color("#81929d")
        spine.set_linewidth(0.7)

    refined_summary = sensitivity["summaries"][
        "continuous_coordinate_refinement"
    ]
    strict = selected["image_screen"]["best_strict"]
    fig.suptitle(
        "PHR_4 18 — First-Order Complete-Wing Flooding Sensitivity",
        y=0.982,
        fontsize=14.0,
        fontweight="semibold",
        color="#142c3b",
    )
    fig.text(
        0.5,
        0.947,
        "Comparison with the exact PCA-selected random pose; the level sea surface and modeled waterline are explicit.",
        ha="center",
        fontsize=8.5,
        color="#334d5c",
    )
    fig.text(
        0.645,
        0.512,
        f"10/24 refined states met the descriptive attitude and strict size criteria; "
        f"all had the engine absent and all six midspan/tip cells fully flooded.\n"
        f"Selected state: height RMSE {selected['attitude']['reference_height_rmse_m']:.3f} m; "
        f"PCA loss {strict['pca_loss_lower_is_better']:.4f}; "
        f"modeled retained air {selected['retained_air_volume_m3']:.1f} m³.",
        fontsize=7.3,
        color="#334d5c",
        linespacing=1.35,
        va="top",
    )
    fig.legend(
        handles=[
            mpl.patches.Patch(
                facecolor="#dcae4d",
                edgecolor="#72521d",
                label="Wing above sea level",
            ),
            mpl.patches.Patch(
                facecolor="#2f8194",
                edgecolor="#1e5868",
                label="Wing below sea level",
            ),
            Line2D((0,), (0,), color="#16475b", lw=3.0, label="Waterline on wing"),
        ],
        loc="lower left",
        bbox_to_anchor=(0.065, 0.115),
        frameon=False,
        fontsize=7.3,
        ncol=3,
    )
    fig.text(
        0.5,
        0.025,
        "Post-hoc conditional sensitivity, not a flooding probability or global continuous optimum. "
        "The 3 × 3 cells and modeled air volume are coarse equivalent-buoyancy assumptions, not documented Boeing tank bays or tank volume.",
        ha="center",
        fontsize=7.1,
        color="#5d4b3e",
        wrap=True,
    )
    for suffix in ("pdf", "svg"):
        fig.savefig(
            bundle / "outputs" / f"phr4-18-wing-flooding-sensitivity.{suffix}",
            facecolor=fig.get_facecolor(),
        )
    fig.savefig(
        bundle / "outputs" / "phr4-18-wing-flooding-sensitivity.png",
        dpi=400,
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)


def main() -> None:
    mpl.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42, "ps.fonttype": 42, "svg.fonttype": "none", "savefig.bbox": "tight"})
    bundle = Path(__file__).resolve().parent.parent
    targets = read_json(bundle / "data" / "targets.json")
    results = read_json(bundle / "outputs" / "fuselage-screen-results.json")
    legacy_masks = read_json(bundle / "data" / "legacy-selected-pca-display-masks.json")
    pca_masks = read_json(bundle / "data" / "pca-only-selected-display-masks.json")
    component_context = read_json(bundle / "data" / "boeing-selected-component-context.json")
    geometry = read_json(bundle / "data" / "boeing-derived-fuselage-geometry.json")
    common_scale_panel(bundle, targets, results)
    loss_heatmap(bundle, results)
    selected_pca_panel(bundle, targets, results, pca_masks)
    selected_aircraft_sketches(
        bundle,
        targets,
        results,
        legacy_masks,
        component_context,
        geometry,
    )
    phr4_18_wing_attitude_figure(bundle, pca_masks, component_context)
    phr4_18_wing_flooding_sensitivity_figure(bundle, component_context)
    print(
        "Rendered fuselage mask panel, extended loss comparison, "
        "PCA-only category panel, component sketches, wing attitude, and flooding sensitivity"
    )


if __name__ == "__main__":
    main()
