#!/usr/bin/env python3
"""Run the deterministic five-object, three-family 777 fuselage morphology sensitivity screen."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import platform
from pathlib import Path
import statistics
import sys

import numpy as np

from morphology import (
    GRID_SIZE,
    best_iou,
    clip_waterline,
    oriented_dimensions,
    pack_mask,
    project_segment_polygon,
    radius_profile_from_polygon,
    rasterize_polygon,
    shape_transforms,
)


CANDIDATE_COUNT = 3372
BASE_SEED = 0x370F051A
FAMILY_ORDER = (
    "whole_fuselage_shell",
    "documented_structural_sections",
    "random_longitudinal_sections",
)
FAMILY_LABELS = {
    "whole_fuselage_shell": "Whole 777 Fuselage",
    "documented_structural_sections": "Documented 777 Fuselage Sections",
    "random_longitudinal_sections": "Random 777 Fuselage Sections",
}
STRUCTURAL_INTERVALS = (
    ("section-41", 92.5, 655.0),
    ("section-43", 655.0, 1035.0),
    ("sections-44-45", 1035.0, 1434.0),
    ("section-46", 1434.0, 1832.0),
    ("section-47", 1832.0, 2150.0),
    ("section-48", 2150.0, 2570.0),
)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_seed(family: str, index: int) -> int:
    payload = f"{BASE_SEED}:{family}:{index}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "little")


def x_from_body_station(body_station: float) -> float:
    # NTSB defines 777 BS from a point 92.5 inches forward of the nose tip.
    return (body_station - 92.5) * 0.0254


def candidate_interval(family: str, index: int, rng, profile) -> tuple[str, float, float]:
    if family == "whole_fuselage_shell":
        return "complete-shell", profile.minimum_x, profile.maximum_x
    if family == "documented_structural_sections":
        subtype, start_bs, end_bs = STRUCTURAL_INTERVALS[index % len(STRUCTURAL_INTERVALS)]
        x0 = max(profile.minimum_x, x_from_body_station(start_bs))
        x1 = min(profile.maximum_x, x_from_body_station(end_bs))
        return subtype, x0, x1
    if family == "random_longitudinal_sections":
        while True:
            first, second = sorted(rng.uniform(profile.minimum_x, profile.maximum_x, size=2))
            if second - first >= 2.0:
                return "random-two-cut-section", float(first), float(second)
    raise ValueError(f"Unknown family: {family}")


def create_candidate(family: str, index: int, profile) -> dict:
    seed = stable_seed(family, index)
    rng = np.random.default_rng(seed)
    subtype, x0, x1 = candidate_interval(family, index, rng, profile)
    full_visibility = index % 5 == 0
    visible_fraction = 1.0 if full_visibility else float(rng.uniform(0.15, 1.0))
    view_axis_cosine = float(rng.uniform(0.0, 1.0))
    waterline_angle = float(rng.uniform(0.0, 2.0 * math.pi))
    polygon = project_segment_polygon(profile, x0, x1, view_axis_cosine)
    full_mask = rasterize_polygon(polygon)
    mask = clip_waterline(full_mask, visible_fraction, waterline_angle)
    dimensions = oriented_dimensions(mask)
    return {
        "candidate_id": f"{family}-{index:05d}",
        "family": family,
        "source_subtype": subtype,
        "seed": seed,
        "x0_m": x0,
        "x1_m": x1,
        "section_length_m": x1 - x0,
        "visibility_regime": "full" if full_visibility else "linear-waterline",
        "target_visible_fraction": visible_fraction,
        "achieved_visible_fraction": float(mask.sum()) / max(1, full_mask.sum()),
        "view_axis_cosine": view_axis_cosine,
        "projected_axis_factor": math.sqrt(max(0.0, 1.0 - view_axis_cosine**2)),
        "waterline_angle_radians": waterline_angle,
        "visible_area_m2": dimensions["visible_area_m2"],
        "visible_length_m": dimensions["visible_length_m"],
        "visible_width_m": dimensions["visible_width_m"],
        "shape_transforms": shape_transforms(dimensions["normalized"]),
        "mask_hex": pack_mask(mask),
    }


def in_interval(value: float, interval: dict) -> bool:
    return interval["p10"] <= value <= interval["p90"]


def interval_penalty(value: float, interval: dict) -> float:
    if value < interval["p10"]:
        return abs(math.log(max(0.25, value) / interval["p10"]))
    if value > interval["p90"]:
        return abs(math.log(value / interval["p90"]))
    return 0.0


def match(candidate: dict, target: dict) -> dict:
    intervals = target["strict_intervals"]
    true_iou = best_iou(
        int(target["views"]["true_colour"]["normalized_mask_integer"]),
        candidate["shape_transforms"],
    )
    pca_iou = best_iou(
        int(target["views"]["pca"]["normalized_mask_integer"]),
        candidate["shape_transforms"],
    )
    mean_iou = (true_iou + pca_iou) / 2.0
    penalties = (
        interval_penalty(candidate["visible_area_m2"], intervals["visible_area_m2"]),
        interval_penalty(candidate["visible_length_m"], intervals["visible_length_m"]),
        interval_penalty(candidate["visible_width_m"], intervals["visible_width_m"]),
    )
    strict = all(value == 0.0 for value in penalties)
    return {
        "candidate": candidate,
        "strict_size_eligible": strict,
        "silhouette_iou_true_colour": true_iou,
        "silhouette_iou_pca": pca_iou,
        "silhouette_iou_mean": mean_iou,
        "dimension_range_penalty": statistics.mean(penalties),
        "loss_lower_is_better": 1.0 - mean_iou + 0.2 * statistics.mean(penalties),
    }


def public_match(record: dict | None) -> dict | None:
    if record is None:
        return None
    candidate = record["candidate"]
    return {
        "candidate_id": candidate["candidate_id"],
        "source_subtype": candidate["source_subtype"],
        "loss_lower_is_better": round(record["loss_lower_is_better"], 6),
        "silhouette_iou_true_colour": round(record["silhouette_iou_true_colour"], 6),
        "silhouette_iou_pca": round(record["silhouette_iou_pca"], 6),
        "pca_loss_lower_is_better": round(
            1.0 - record["silhouette_iou_pca"], 6
        ),
        "silhouette_iou_mean": round(record["silhouette_iou_mean"], 6),
        "dimension_range_penalty": round(record["dimension_range_penalty"], 6),
        "strict_size_eligible": record["strict_size_eligible"],
        "visible_area_m2": round(candidate["visible_area_m2"], 3),
        "visible_length_m": round(candidate["visible_length_m"], 3),
        "visible_width_m": round(candidate["visible_width_m"], 3),
        "section_length_m": round(candidate["section_length_m"], 3),
        "x0_m": round(candidate["x0_m"], 3),
        "x1_m": round(candidate["x1_m"], 3),
        "visibility_regime": candidate["visibility_regime"],
        "target_visible_fraction": round(candidate["target_visible_fraction"], 6),
        "achieved_visible_fraction": round(candidate["achieved_visible_fraction"], 6),
        "view_axis_cosine": round(candidate["view_axis_cosine"], 6),
        "projected_axis_factor": round(candidate["projected_axis_factor"], 6),
        "waterline_angle_radians": round(candidate["waterline_angle_radians"], 6),
        "mask_grid_size": GRID_SIZE,
        "mask_hex": candidate["mask_hex"],
    }


def quantile_or_none(values: list[float], probability: float):
    return round(float(np.quantile(values, probability, method="linear")), 6) if values else None


def previous_rows(previous: dict, object_id: str) -> list[dict]:
    output = []
    for family, record in previous["objects"][object_id]["families"].items():
        best = record["primary_best_strict_size"]
        output.append(
            {
                "family": family,
                "label": record["label"],
                "candidate_count": record["candidate_count"],
                "strict_size_candidate_count": record["strict_size_candidate_count"],
                "primary_loss_lower_is_better": (
                    best["loss_lower_is_better"] if best is not None else None
                ),
                "source": "previous_five_family_screen",
            }
        )
    return output


def write_candidate_inventory(path: Path, candidates_by_family: dict[str, list[dict]]) -> None:
    columns = (
        "candidate_id",
        "family",
        "source_subtype",
        "seed",
        "x0_m",
        "x1_m",
        "section_length_m",
        "visibility_regime",
        "target_visible_fraction",
        "achieved_visible_fraction",
        "view_axis_cosine",
        "projected_axis_factor",
        "waterline_angle_radians",
        "visible_area_m2",
        "visible_length_m",
        "visible_width_m",
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for family in FAMILY_ORDER:
            for candidate in candidates_by_family[family]:
                writer.writerow({key: candidate[key] for key in columns})


def write_summary_csv(path: Path, rows: list[dict]) -> None:
    columns = tuple(rows[0])
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    code_path = Path(__file__).resolve()
    bundle = code_path.parent.parent
    morphology_code_path = code_path.parent / "morphology.py"
    data_directory = bundle / "data"
    output_directory = bundle / "outputs"
    output_directory.mkdir(parents=True, exist_ok=True)
    targets_path = data_directory / "targets.json"
    calibration_path = data_directory / "size-interval-calibration.json"
    geometry_path = data_directory / "boeing-derived-fuselage-geometry.json"
    previous_path = data_directory / "previous-five-family-results.json"
    targets = read_json(targets_path)
    geometry = read_json(geometry_path)
    previous = read_json(previous_path)
    profile = radius_profile_from_polygon(geometry["coordinates_m"]["full_fuselage_shell"])

    candidates_by_family: dict[str, list[dict]] = {}
    for family in FAMILY_ORDER:
        print(f"Generating {FAMILY_LABELS[family]} ({CANDIDATE_COUNT} masks)", flush=True)
        candidates = []
        for index in range(CANDIDATE_COUNT):
            candidates.append(create_candidate(family, index, profile))
            if (index + 1) % 500 == 0:
                print(f"  {index + 1}/{CANDIDATE_COUNT}", flush=True)
        candidates_by_family[family] = candidates

    write_candidate_inventory(output_directory / "fuselage-candidate-inventory.csv", candidates_by_family)
    objects = {}
    summary_rows = []
    extended_rankings = {}
    for target in targets["objects"]:
        object_id = target["object_id"]
        print(f"Matching {object_id}", flush=True)
        family_results = {}
        new_ranking_rows = []
        for family in FAMILY_ORDER:
            matches = [match(candidate, target) for candidate in candidates_by_family[family]]
            strict = [record for record in matches if record["strict_size_eligible"]]
            strict.sort(key=lambda record: record["loss_lower_is_better"])
            pca_strict = sorted(
                strict,
                key=lambda record: 1.0 - record["silhouette_iou_pca"],
            )
            mostly_visible = [
                record
                for record in strict
                if record["candidate"]["achieved_visible_fraction"] >= 0.5
            ]
            fully_visible = [
                record
                for record in strict
                if record["candidate"]["visibility_regime"] == "full"
            ]
            soft = min(matches, key=lambda record: record["loss_lower_is_better"])
            closest = min(
                matches,
                key=lambda record: (
                    record["dimension_range_penalty"], record["loss_lower_is_better"]
                ),
            )
            pca_closest = min(
                matches,
                key=lambda record: (
                    record["dimension_range_penalty"],
                    1.0 - record["silhouette_iou_pca"],
                ),
            )
            strict_losses = [record["loss_lower_is_better"] for record in strict]
            result = {
                "label": FAMILY_LABELS[family],
                "candidate_count": CANDIDATE_COUNT,
                "strict_size_candidate_count": len(strict),
                "strict_size_candidate_fraction": round(len(strict) / CANDIDATE_COUNT, 6),
                "strict_loss_p05": quantile_or_none(strict_losses, 0.05),
                "strict_loss_p50": quantile_or_none(strict_losses, 0.50),
                "strict_loss_p95": quantile_or_none(strict_losses, 0.95),
                "primary_lowest_strict_size_loss": public_match(strict[0] if strict else None),
                "pca_only_lowest_strict_size_loss": public_match(
                    pca_strict[0] if pca_strict else None
                ),
                "visibility_sensitivity": {
                    "at_least_half_visible_candidate_count": len(mostly_visible),
                    "lowest_loss_at_least_half_visible": public_match(
                        mostly_visible[0] if mostly_visible else None
                    ),
                    "fully_visible_candidate_count": len(fully_visible),
                    "lowest_loss_fully_visible": public_match(
                        fully_visible[0] if fully_visible else None
                    ),
                },
                "closest_size_fallback_for_display_only": public_match(closest if not strict else None),
                "pca_only_closest_size_fallback_for_display_only": public_match(
                    pca_closest if not pca_strict else None
                ),
                "soft_size_penalty_sensitivity": public_match(soft),
            }
            family_results[family] = result
            primary_loss = strict[0]["loss_lower_is_better"] if strict else None
            new_ranking_rows.append(
                {
                    "family": family,
                    "label": FAMILY_LABELS[family],
                    "candidate_count": CANDIDATE_COUNT,
                    "strict_size_candidate_count": len(strict),
                    "primary_loss_lower_is_better": primary_loss,
                    "source": "fuselage_extension",
                }
            )
            summary_rows.append(
                {
                    "object_id": object_id,
                    "family": family,
                    "family_label": FAMILY_LABELS[family],
                    "candidate_count": CANDIDATE_COUNT,
                    "strict_size_candidate_count": len(strict),
                    "strict_size_candidate_fraction": round(len(strict) / CANDIDATE_COUNT, 6),
                    "primary_loss_lower_is_better": round(primary_loss, 6) if primary_loss is not None else "",
                    "primary_source_subtype": strict[0]["candidate"]["source_subtype"] if strict else "",
                    "primary_visible_fraction": round(strict[0]["candidate"]["achieved_visible_fraction"], 6) if strict else "",
                    "primary_view_axis_cosine": round(strict[0]["candidate"]["view_axis_cosine"], 6) if strict else "",
                    "at_least_half_visible_candidate_count": len(mostly_visible),
                    "lowest_loss_at_least_half_visible": round(mostly_visible[0]["loss_lower_is_better"], 6) if mostly_visible else "",
                    "fully_visible_candidate_count": len(fully_visible),
                    "lowest_loss_fully_visible": round(fully_visible[0]["loss_lower_is_better"], 6) if fully_visible else "",
                }
            )
        objects[object_id] = {
            "strict_intervals": target["strict_intervals"],
            "families": family_results,
        }
        combined = previous_rows(previous, object_id) + new_ranking_rows
        combined = [row for row in combined if row["primary_loss_lower_is_better"] is not None]
        combined.sort(key=lambda row: row["primary_loss_lower_is_better"])
        extended_rankings[object_id] = combined

    all_family_names = list(previous["family_summary"]) + list(FAMILY_ORDER)
    extended_family_summary = {}
    for family in all_family_names:
        rows = [
            next((row for row in extended_rankings[object_id] if row["family"] == family), None)
            for object_id in objects
        ]
        available = [row for row in rows if row is not None]
        if family in previous["family_summary"]:
            label = previous["family_summary"][family]["label"]
        else:
            label = FAMILY_LABELS[family]
        losses = [row["primary_loss_lower_is_better"] for row in available]
        extended_family_summary[family] = {
            "label": label,
            "objects_with_strict_size_candidate": len(available),
            "mean_primary_lowest_loss_available_objects": round(statistics.mean(losses), 6) if losses else None,
            "median_primary_lowest_loss_available_objects": round(statistics.median(losses), 6) if losses else None,
            "objects_at_lowest_loss": sum(
                1 for object_id in objects if extended_rankings[object_id][0]["family"] == family
            ),
        }

    output = {
        "schema_version": 1,
        "status": "CONDITIONAL_MORPHOLOGY_SENSITIVITY; NOT AN IDENTITY CLASSIFIER OR BREAKUP POSTERIOR",
        "source_hashes_sha256": {
            "targets": sha256(targets_path),
            "size_interval_calibration": sha256(calibration_path),
            "fuselage_geometry": sha256(geometry_path),
            "previous_five_family_results": sha256(previous_path),
            "simulation_code": sha256(code_path),
            "morphology_code": sha256(morphology_code_path),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "method": {
            "code_revision": "Pinned by simulation_code and morphology_code SHA-256; Git revision unavailable in this exported workspace.",
            "candidate_count_per_family": CANDIDATE_COUNT,
            "seed_definition": f"SHA-256({BASE_SEED}:family:index), first eight bytes little-endian; NumPy PCG64",
            "projection": "Orthographic projection of a CAD-profile-derived axisymmetric fuselage body; absolute cosine between body axis and line of sight is uniform on [0,1], corresponding to isotropic orientation.",
            "visibility": "Every fifth mask is fully visible; otherwise a random linear waterline retains a target fraction uniform on [0.15,1]. These nuisance ranges are coverage assumptions, not pose or flooding probabilities.",
            "documented_sections": "NTSB 777 longitudinal intervals: BS 92.5-655, 655-1035, 1035-1434, 1434-1832, 1832-2150 and 2150-2570; sections 44 and 45 share one longitudinal interval.",
            "random_sections": "Two cut positions drawn independently and uniformly along the shell, sorted and redrawn until at least 2 m apart; this adds location and length flexibility and is a stress-test family, not a physical breakup prior.",
            "primary_selection": "Minimum mean two-view reflected-mask loss only among candidates whose visible area, oriented length and oriented width each lie between the lower and upper limits of the object's audited p10-p90 intervals.",
            "loss": "1 - mean(best reflected true-colour IoU, best reflected PCA IoU); the legacy 0.2 dimension penalty is zero after the hard size gate.",
            "pca_panel_selection": "For the published-PCA comparison panel only, each family is independently re-ranked by 1 - best reflected PCA IoU after the identical hard area-length-width gate. This display-specific ranking does not replace the primary two-view screen.",
            "interpretation": "Equal raw search budget and best-of-search descriptive comparison. Results are not class likelihoods, likelihood ratios, Bayes factors, identity probabilities, fracture probabilities or prevalence estimates.",
            "convergence": "Finite best-of-search screen; no Monte Carlo convergence claim. Candidate counts, strict eligibility, loss quantiles and visibility restrictions are reported for audit.",
        },
        "family_summary_with_previous_controls": extended_family_summary,
        "objects": objects,
        "extended_strict_size_rankings": extended_rankings,
    }
    (output_directory / "fuselage-screen-results.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    write_summary_csv(output_directory / "fuselage-screen-summary.csv", summary_rows)
    print(json.dumps({"family_summary": extended_family_summary}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
