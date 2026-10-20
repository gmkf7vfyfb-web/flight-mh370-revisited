#!/usr/bin/env python3
"""Extract the exact selected 48×48 PCA display masks from the preserved panel."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage

from morphology import GRID_SIZE, mask_integer, oriented_dimensions


FAMILY_X = {
    "wing_flooding_model": 409,
    "wing_random_pose": 699,
    "nonwing_777_parts": 989,
    "matched_random_geometry": 1279,
    "ocean_object_combined": 1569,
}
CATEGORY_FAMILIES = {
    "wing": ("wing_flooding_model", "wing_random_pose"),
    "other_777_parts": ("nonwing_777_parts",),
    "matched_random_geometry": ("matched_random_geometry",),
    "ocean_object_controls": ("ocean_object_combined",),
}
PANEL_NAME = "all-family-strict-size-pca-common-scale.jpg"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def selected_record(object_result: dict, families: tuple[str, ...]):
    eligible = []
    for family in families:
        record = object_result["families"][family]["primary_best_strict_size"]
        if record is not None:
            eligible.append((record["loss_lower_is_better"], family, record, True))
    if eligible:
        return min(eligible, key=lambda item: item[0])
    fallbacks = []
    for family in families:
        record = object_result["families"][family][
            "closest_size_fallback_for_display_only"
        ]
        if record is not None:
            fallbacks.append((record["loss_lower_is_better"], family, record, False))
    if not fallbacks:
        raise ValueError(f"No eligible record or display fallback for {families}")
    return min(fallbacks, key=lambda item: item[0])
def pca_selected_record(object_result: dict, families: tuple[str, ...]):
    """Select the strict PCA-IoU minimum, or the PCA-ranked size fallback."""
    eligible = []
    for family in families:
        record = object_result["families"][family]["primary_best_strict_size"]
        if record is not None:
            eligible.append(
                (record["pca_loss_lower_is_better"], family, record, True)
            )
    if eligible:
        return min(eligible, key=lambda item: item[0])
    fallbacks = []
    for family in families:
        record = object_result["families"][family][
            "closest_size_fallback_for_display_only"
        ]
        if record is not None:
            fallbacks.append(
                (record["pca_loss_lower_is_better"], family, record, False)
            )
    if not fallbacks:
        raise ValueError(f"No PCA record or display fallback for {families}")
    return min(fallbacks, key=lambda item: item[0])


def centered_field(mask: np.ndarray, side: int = 48) -> np.ndarray:
    ys, xs = np.nonzero(mask)
    output = np.zeros((side, side), dtype=bool)
    if not len(xs):
        return output
    target_x = np.floor(xs - xs.mean() + side / 2.0 + 0.5).astype(int)
    target_y = np.floor(ys - ys.mean() + side / 2.0 + 0.5).astype(int)
    valid = (
        (target_x >= 0)
        & (target_x < side)
        & (target_y >= 0)
        & (target_y < side)
    )
    output[target_y[valid], target_x[valid]] = True
    return output


def integer_iou(first: int, second: int) -> float:
    union = (first | second).bit_count()
    return (first & second).bit_count() / union if union else 0.0


def pca_aligned_field(record: dict, pca_view: dict) -> np.ndarray:
    size = int(record["mask_grid_size"])
    values = np.frombuffer(
        bytes.fromhex(record["mask_u8_hex"]), dtype=np.uint8
    )
    if values.size != size * size:
        raise ValueError(
            f"{record['candidate_id']} mask has {values.size} values, expected {size**2}"
        )
    raw = values.reshape((size, size)).astype(bool)
    target = int(pca_view["normalized_mask_integer"])
    scored = []
    for variant in (
        raw,
        np.fliplr(raw),
        np.flipud(raw),
        np.flipud(np.fliplr(raw)),
    ):
        dimensions = oriented_dimensions(variant)
        scored.append(
            (
                integer_iou(target, mask_integer(dimensions["normalized"])),
                variant,
                dimensions,
            )
        )
    _, selected, dimensions = max(scored, key=lambda item: item[0])
    selected = centered_field(selected, side=GRID_SIZE)
    rotation = (
        pca_view["baseline_component"]["orientation_degrees"]
        - dimensions["orientation_degrees"]
    )
    rotated = ndimage.rotate(
        selected.astype(np.uint8),
        rotation,
        reshape=False,
        order=0,
        mode="constant",
        cval=0,
        prefilter=False,
    ).astype(bool)
    return centered_field(rotated)


def write_pca_only_masks(
    bundle: Path,
    legacy_analysis: Path,
    results_path: Path,
) -> Path:
    if not legacy_analysis.is_dir():
        raise ValueError("PCA-only preparation requires the legacy analysis directory")
    results = read_json(results_path)
    targets = read_json(bundle / "data" / "targets.json")
    target_by_id = {
        record["object_id"]: record for record in targets["objects"]
    }
    analyses_directory = legacy_analysis.parent
    states_path = (
        analyses_directory
        / "D-0025-parametric-wing-flotation"
        / "outputs"
        / "random-pose-states.json"
    )
    priors_path = (
        analyses_directory
        / "D-0025-parametric-wing-flotation"
        / "inputs"
        / "model-priors.json"
    )
    states = read_json(states_path)
    priors = read_json(priors_path)
    state_by_id = {record["id"]: record for record in states["states"]}
    output = {
        "schema_version": 1,
        "status": (
            "DISPLAY_INPUT_ONLY; candidates independently re-ranked by PCA IoU "
            "after the unchanged two-sided size gate"
        ),
        "source": {
            "pca_only_results_sha256": hashlib.sha256(
                results_path.read_bytes()
            ).hexdigest(),
            "legacy_source_hashes_sha256": results["source_hashes_sha256"],
            "random_pose_states_sha256": hashlib.sha256(
                states_path.read_bytes()
            ).hexdigest(),
            "model_priors_sha256": hashlib.sha256(
                priors_path.read_bytes()
            ).hexdigest(),
            "selection": (
                "Within each original family, minimize 1 - reflected PCA-mask IoU "
                "over candidates whose area, length and width all pass the audited "
                "p10-p90 intervals; then take the lower PCA loss within grouped categories."
            ),
            "display_alignment": (
                "Choose the loss-admissible reflection with greatest PCA IoU, align "
                "principal axes to the published PCA component and centre on a "
                "48 x 48 grid at 0.5 m per pixel. Display resampling never enters scoring."
            ),
            "field_dimensions_metres": [24, 24],
            "field_grid_pixels": [48, 48],
        },
        "objects": {},
    }
    for object_id, object_result in results["objects"].items():
        output["objects"][object_id] = {}
        pca_view = target_by_id[object_id]["views"]["pca"]
        for category, families in CATEGORY_FAMILIES.items():
            _, family, record, eligible = pca_selected_record(
                object_result, families
            )
            mask = pca_aligned_field(record, pca_view)
            metadata = dict(record.get("metadata", {}))
            state = state_by_id.get(record["candidate_id"])
            if state is not None:
                metadata["model_parameters"] = state["parameters"]
                metadata["model_mass_kg"] = state["mass_kg"]
                metadata["shallow_underwater_visibility_m"] = priors[
                    "sensor_surrogate"
                ]["shallow_underwater_visibility_m"]
            output["objects"][object_id][category] = {
                "selected_family": family,
                "strict_size_eligible": eligible,
                "candidate_id": record["candidate_id"],
                "source_subtype": record["source_subtype"],
                "source_label": record["source_label"],
                "silhouette_iou_pca": record["silhouette_iou_pca"],
                "pca_loss_lower_is_better": record[
                    "pca_loss_lower_is_better"
                ],
                "two_view_loss_lower_is_better": record[
                    "loss_lower_is_better"
                ],
                "visible_area_m2": record["visible_area_m2"],
                "visible_length_m": record["visible_length_m"],
                "visible_width_m": record["visible_width_m"],
                "metadata": metadata,
                "display_mask_pixel_count": int(mask.sum()),
                "mask_hex": np.packbits(
                    mask.ravel(), bitorder="big"
                ).tobytes().hex(),
            }
    destination = bundle / "data" / "pca-only-selected-display-masks.json"
    destination.write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "legacy_analysis",
        type=Path,
        help="Preserved five-family analysis directory, or its PCA panel JPEG",
    )
    parser.add_argument(
        "--pca-only-results",
        type=Path,
        help="Full five-family result rerun independently ranked by PCA IoU",
    )
    arguments = parser.parse_args()
    bundle = Path(__file__).resolve().parent.parent
    if arguments.pca_only_results is not None:
        destination = write_pca_only_masks(
            bundle,
            arguments.legacy_analysis,
            arguments.pca_only_results,
        )
        print(destination)
        return
    panel_path = arguments.legacy_analysis
    if panel_path.is_dir():
        panel_path = panel_path / "outputs" / "panels" / PANEL_NAME
    previous_path = bundle / "data" / "previous-five-family-results.json"
    previous = read_json(previous_path)
    panel = np.asarray(Image.open(panel_path).convert("RGB"))
    if panel.shape[:2] != (2025, 1900):
        raise ValueError(f"Unexpected preserved panel dimensions: {panel.shape[:2]}")
    source_coordinates = np.clip(
        ((np.arange(48) + 0.5) * 262 / 48).astype(int), 0, 261
    )
    output = {
        "schema_version": 1,
        "status": (
            "DISPLAY_INPUT_ONLY; exact selected candidate identities and loss values "
            "come from previous-five-family-results.json"
        ),
        "source": {
            "legacy_pca_panel_sha256": hashlib.sha256(panel_path.read_bytes()).hexdigest(),
            "legacy_pca_panel_dimensions_pixels": [1900, 2025],
            "field_dimensions_metres": [24, 24],
            "field_grid_pixels": [48, 48],
            "extraction": (
                "Sample the centre of each nearest-neighbour-upscaled 48x48 source "
                "pixel in the preserved panel; select the recorded candidate pixel "
                "count with smallest R+G. This recovers display orientation only and "
                "is never used for loss calculation."
            ),
        },
        "objects": {},
    }
    for row, (object_id, object_result) in enumerate(previous["objects"].items()):
        output["objects"][object_id] = {}
        image_y = 148 + row * 380
        for category, families in CATEGORY_FAMILIES.items():
            _, family, record, eligible = selected_record(object_result, families)
            image_x = FAMILY_X[family]
            tile = panel[image_y : image_y + 262, image_x : image_x + 262]
            sampled = tile[np.ix_(source_coordinates, source_coordinates)].astype(
                np.uint8
            )
            expected_pixels = int(round(record["visible_area_m2"] / 0.25))
            score = sampled[..., 0].astype(int) + sampled[..., 1].astype(int)
            order = np.argsort(score.ravel(), kind="stable")
            mask = np.zeros(48 * 48, dtype=np.uint8)
            mask[order[:expected_pixels]] = 1
            mask = mask.reshape((48, 48))
            output["objects"][object_id][category] = {
                "selected_family": family,
                "strict_size_eligible": eligible,
                "candidate_id": record["candidate_id"],
                "source_subtype": record["source_subtype"],
                "source_label": record["source_label"],
                "loss_lower_is_better": record["loss_lower_is_better"],
                "visible_area_m2": record["visible_area_m2"],
                "visible_length_m": record["visible_length_m"],
                "visible_width_m": record["visible_width_m"],
                "recovered_display_mask_pixel_count": int(mask.sum()),
                "mask_hex": np.packbits(
                    mask.ravel(), bitorder="big"
                ).tobytes().hex(),
            }
    destination = bundle / "data" / "legacy-selected-pca-display-masks.json"
    destination.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(destination)


if __name__ == "__main__":
    main()
