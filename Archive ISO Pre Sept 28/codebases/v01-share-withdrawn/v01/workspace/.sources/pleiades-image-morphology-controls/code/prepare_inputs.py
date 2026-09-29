#!/usr/bin/env python3
"""Prepare compact, audited morphology inputs from the preserved legacy corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np

from morphology import (
    BASELINE_CROP,
    BASELINE_QUANTILE,
    CROP_HYPOTHESES,
    SEGMENTATION_QUANTILES,
    component_source_mask,
    mask_integer,
    mask_iou,
    normalize_mask,
    segment_candidate,
)


OBJECT_IDS = (
    "phr-4-object-06",
    "phr-4-object-18",
    "phr-4-object-19",
    "phr-4-object-26",
    "phr-4-object-27",
)
VIEW_DEFINITIONS = (
    ("true_color_half_panel", "true_colour", "true_color"),
    ("pca_half_panel", "pca", "pca"),
)
MINIMUM_BASELINE_COMPONENT_IOU = 0.25
INTERVAL_QUANTILES = (0.10, 0.90)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def round_numbers(value):
    if isinstance(value, float):
        return round(value, 8)
    if isinstance(value, list):
        return [round_numbers(item) for item in value]
    if isinstance(value, dict):
        return {key: round_numbers(item) for key, item in value.items()}
    return value


def central_interval(records: list[dict], key: str) -> dict:
    values = [record[key] for record in records]
    low, high = np.quantile(values, INTERVAL_QUANTILES, method="linear")
    return {"p10": round(float(low), 2), "p90": round(float(high), 2)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("legacy_root", type=Path)
    args = parser.parse_args()
    legacy = args.legacy_root.resolve()
    bundle = Path(__file__).resolve().parent.parent
    data_directory = bundle / "data"
    data_directory.mkdir(parents=True, exist_ok=True)

    imagery = legacy / "corpus/imagery/french-pleiades-2014"
    manifest_path = imagery / "derived/vlm-views/manifest.json"
    features_path = (
        legacy
        / "analyses/D-0015-pleiades-public-candidate-audit/outputs/candidate-features.json"
    )
    ranges_path = (
        legacy
        / "analyses/D-0018-rating5-boeing-detachable-screen/outputs/"
        "rating5-visible-geometry.json"
    )
    geometry_path = (
        legacy
        / "analyses/D-0017-777-fuselage-tail-phr4-object20/outputs/"
        "boeing-derived-fuselage-tail-geometry.json"
    )
    dxf_path = legacy / "corpus/papers/primary/boeing-777/777-200.dxf"

    manifest = read_json(manifest_path)
    features = read_json(features_path)
    ranges = read_json(ranges_path)
    geometry = read_json(geometry_path)
    feature_by_id = {record["sample_id"]: record for record in features["records"]}
    range_by_id = {record["sample_id"]: record for record in ranges["objects"]}

    objects = []
    calibration_objects = []
    for object_id in OBJECT_IDS:
        sample = next(
            record
            for record in manifest["samples"]
            if record["sample_id"] == object_id
        )
        feature = feature_by_id[object_id]
        size_record = range_by_id[object_id]
        views = {}
        trial_records = []
        for view_name, output_name, feature_name in VIEW_DEFINITIONS:
            view = next(
                record for record in sample["views"] if record["view"] == view_name
            )
            source_path = imagery / view["path"]
            if sha256(source_path) != view["sha256"]:
                raise RuntimeError(f"Image hash mismatch: {source_path}")

            component = segment_candidate(str(source_path))
            expected = feature[feature_name]["baseline"]["component"]
            checks = {
                "area": abs(component["area"] - expected["area"]),
                "centroid_x": abs(
                    component["centroid_source_x"]
                    - expected["centroid_source_x"]
                ),
                "centroid_y": abs(
                    component["centroid_source_y"]
                    - expected["centroid_source_y"]
                ),
                "orientation": abs(
                    component["orientation_degrees"]
                    - expected["orientation_degrees"]
                ),
            }
            if checks["area"] != 0 or max(checks.values()) > 5e-4:
                raise RuntimeError(
                    f"Python segmentation disagrees for "
                    f"{object_id}/{output_name}: {checks}"
                )

            legacy_view_name = (
                "true-colour" if output_name == "true_colour" else "PCA"
            )
            baseline_trial = next(
                trial
                for trial in size_record["trials"]
                if trial["view"] == legacy_view_name
                and trial["crop"] == BASELINE_CROP
                and trial["threshold_quantile"] == BASELINE_QUANTILE
            )
            scale = baseline_trial["scale_m_per_report_pixel"]
            baseline_source_mask = component_source_mask(component)
            for crop_name, crop_bounds in CROP_HYPOTHESES.items():
                for threshold_quantile in SEGMENTATION_QUANTILES:
                    trial = segment_candidate(
                        str(source_path),
                        crop_bounds=crop_bounds,
                        threshold_quantile=threshold_quantile,
                    )
                    overlap = mask_iou(
                        baseline_source_mask,
                        component_source_mask(trial),
                    )
                    corresponds = overlap >= MINIMUM_BASELINE_COMPONENT_IOU
                    legacy_trial = next(
                        record
                        for record in size_record["trials"]
                        if record["view"] == legacy_view_name
                        and record["crop"] == crop_name
                        and record["threshold_quantile"] == threshold_quantile
                    )
                    trial_records.append(
                        {
                            "view": output_name,
                            "crop": crop_name,
                            "threshold_quantile": threshold_quantile,
                            "baseline_component_iou": overlap,
                            "corresponds_to_baseline": corresponds,
                            "rejection_reason": (
                                None
                                if corresponds
                                else "baseline_component_iou_below_0.25"
                            ),
                            "visible_area_m2": legacy_trial["area_m2"],
                            "visible_length_m": legacy_trial["length_m"],
                            "visible_width_m": legacy_trial["width_m"],
                        }
                    )

            normalized = normalize_mask(
                component["mask"],
                component["orientation_degrees"],
                component["centroid_x"],
                component["centroid_y"],
            )
            ys, xs = component["mask"].nonzero()
            relative_pixels = [
                [
                    round(float(x - component["centroid_x"]), 6),
                    round(float(y - component["centroid_y"]), 6),
                ]
                for y, x in zip(ys, xs, strict=True)
            ]
            copied_name = f"{object_id}-{output_name}.png"
            shutil.copy2(source_path, data_directory / copied_name)
            views[output_name] = {
                "source_file": copied_name,
                "source_sha256": view["sha256"],
                "normalized_size": int(normalized.shape[0]),
                "normalized_mask_integer": str(mask_integer(normalized)),
                "relative_component_pixels": relative_pixels,
                "scale_m_per_report_pixel": scale,
                "baseline_component": {
                    key: component[key]
                    for key in (
                        "area",
                        "centroid_source_x",
                        "centroid_source_y",
                        "aspect_ratio",
                        "orientation_degrees",
                        "compactness",
                        "fill_ratio",
                    )
                },
            }

        retained = [
            record for record in trial_records if record["corresponds_to_baseline"]
        ]
        if len(retained) < 10:
            raise RuntimeError(
                f"Too few correspondence-qualified trials for {object_id}: "
                f"{len(retained)}"
            )
        strict_intervals = {
            key: central_interval(retained, key)
            for key in (
                "visible_area_m2",
                "visible_length_m",
                "visible_width_m",
            )
        }
        calibration_summary = {
            "total_trials": len(trial_records),
            "retained_trials": len(retained),
            "rejected_trials": len(trial_records) - len(retained),
            "minimum_baseline_component_iou": MINIMUM_BASELINE_COMPONENT_IOU,
        }
        objects.append(
            {
                "object_id": object_id,
                "ga_area_m2_reported": size_record["ga_area_m2_reported"],
                "strict_intervals": strict_intervals,
                "size_calibration": calibration_summary,
                "views": views,
            }
        )
        calibration_objects.append(
            {
                "object_id": object_id,
                "ga_area_m2_reported": size_record["ga_area_m2_reported"],
                "summary": calibration_summary,
                "strict_intervals": strict_intervals,
                "trials": trial_records,
            }
        )

    calibration_manifest = {
        "schema_version": 1,
        "status": "DERIVED_SIZE_INTERVAL_CALIBRATION; OBJECT_IDENTITY_UNKNOWN",
        "method": {
            "views": ["true_colour", "pca"],
            "crop_hypotheses": CROP_HYPOTHESES,
            "threshold_quantiles": SEGMENTATION_QUANTILES,
            "baseline": {
                "crop": BASELINE_CROP,
                "threshold_quantile": BASELINE_QUANTILE,
            },
            "component_correspondence": (
                "Retain a perturbation only when its source-coordinate binary "
                "mask has IoU >= 0.25 with that view's standard-q0.975 baseline."
            ),
            "interval": (
                "p10-p90 across correspondence-qualified trials, pooled across "
                "both report-embedded views; lower and upper limits apply "
                "jointly to area, oriented length and oriented width."
            ),
        },
        "objects": calibration_objects,
    }
    calibration_path = data_directory / "size-interval-calibration.json"
    calibration_path.write_text(
        json.dumps(round_numbers(calibration_manifest), indent=2) + "\n",
        encoding="utf-8",
    )

    input_manifest = {
        "schema_version": 2,
        "status": "DERIVED_BINARY_MASKS; OBJECT_IDENTITY_UNKNOWN",
        "segmentation": (
            "standard fractional crop; robust luminance anomaly threshold at "
            "q=0.975; nearby-component merge; principal-axis normalisation to "
            "40 x 40 pixels"
        ),
        "size_intervals": (
            "Two-sided p10-p90 area, oriented-length and oriented-width "
            "intervals across crop/threshold perturbations with baseline "
            "component IoU >= 0.25."
        ),
        "source_hashes_sha256": {
            "view_manifest": sha256(manifest_path),
            "candidate_features": sha256(features_path),
            "legacy_visible_geometry": sha256(ranges_path),
            "size_interval_calibration": sha256(calibration_path),
            "boeing_777_200_dxf": sha256(dxf_path),
            "derived_fuselage_geometry": sha256(geometry_path),
        },
        "objects": objects,
    }
    (data_directory / "targets.json").write_text(
        json.dumps(round_numbers(input_manifest), indent=2) + "\n",
        encoding="utf-8",
    )
    shutil.copy2(
        geometry_path,
        data_directory / "boeing-derived-fuselage-geometry.json",
    )
    print(
        json.dumps(
            {
                "objects": len(objects),
                "calibration": str(calibration_path),
                "data_directory": str(data_directory),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
