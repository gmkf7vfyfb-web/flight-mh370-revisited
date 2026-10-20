#!/usr/bin/env python3
"""Run the PHR_4 object-18 compartment-retention wing sensitivity."""

from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import platform
import resource
import time

import numpy as np

from morphology import pack_mask
from wing_flooding import (
    attitude_metrics,
    binary_retention,
    build_wing_template,
    reference_heights,
    render_projected_mask,
    retention_from_start_progress,
    score_pca_mask,
    solve_hydrostatic_pose,
)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_value(value):
    if isinstance(value, np.ndarray):
        return [json_value(item) for item in value.tolist()]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.floating, float)):
        return round(float(value), 8)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, dict):
        return {key: json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_value(item) for item in value]
    return value


def target_pose_record(template, selected_record: dict) -> dict:
    source = selected_record["metadata"]["pose"]
    pose = {
        **source,
        "matrix": np.asarray(source["matrix"], dtype=float),
    }
    pose["reference_heights_m"] = reference_heights(template, pose)
    return pose


def best_image_view(
    template,
    pose: dict,
    target: dict,
    model_input: dict,
) -> dict:
    records = []
    views = model_input["sensor_views"]
    for off_nadir in views["off_nadir_degrees"]:
        for azimuth in views["azimuth_degrees"]:
            rendered = render_projected_mask(
                template,
                pose,
                off_nadir,
                azimuth,
                float(model_input["shallow_underwater_visibility_m"]),
            )
            if rendered is None:
                continue
            score = score_pca_mask(rendered, target)
            records.append({**rendered, **score})
    if not records:
        return {"render_count": 0, "best_any": None, "best_strict": None}
    best_any = min(records, key=lambda item: item["pca_loss_lower_is_better"])
    strict = [record for record in records if record["strict_size_eligible"]]
    best_strict = (
        min(strict, key=lambda item: item["pca_loss_lower_is_better"])
        if strict
        else None
    )

    def compact(record: dict | None) -> dict | None:
        if record is None:
            return None
        return {
            "strict_size_eligible": record["strict_size_eligible"],
            "silhouette_iou_pca": record["silhouette_iou_pca"],
            "pca_loss_lower_is_better": record["pca_loss_lower_is_better"],
            "visible_area_m2": record["visible_area_m2"],
            "visible_length_m": record["visible_length_m"],
            "visible_width_m": record["visible_width_m"],
            "off_nadir_degrees": record["off_nadir_degrees"],
            "view_azimuth_degrees": record["view_azimuth_degrees"],
        }

    return {
        "render_count": len(records),
        "strict_render_count": len(strict),
        "best_any": compact(best_any),
        "best_strict": compact(best_strict),
    }


def state_record(
    family: str,
    state_id: str,
    template,
    retained_air_fraction: np.ndarray,
    target_pose: dict,
    target: dict,
    model_input: dict,
    metadata: dict,
    screen_image: bool = True,
) -> dict:
    retained = np.asarray(retained_air_fraction, dtype=float)
    pose = solve_hydrostatic_pose(
        template,
        retained,
        float(model_input["water_density_kg_m3"]),
    )
    record = {
        "family": family,
        "state_id": state_id,
        "draw_index": template.draw_index,
        "engine_state": template.engine_state,
        "mass_kg": template.mass_kg,
        "solid_volume_m3": float(template.sample_solid_volume_m3.sum()),
        "modeled_air_volume_m3": float(template.sample_air_volume_m3.sum()),
        "retained_air_volume_m3": float(
            np.sum(
                template.sample_air_volume_m3
                * retained[template.sample_compartment_index]
            )
        ),
        "outer_volume_m3": template.outer_volume_m3,
        "retained_air_fraction": retained,
        "retained_cell_count_binary_equivalent": int(np.count_nonzero(retained == 1.0)),
        "mean_plan_cell_retained_air_fraction": float(
            retained[template.compartment_index].mean()
        ),
        "metadata": metadata,
        "pose": pose,
    }
    if pose["afloat"]:
        record["attitude"] = attitude_metrics(pose, target_pose)
        if screen_image:
            record["image_screen"] = best_image_view(
                template,
                pose,
                target,
                model_input,
            )
    return record


def rank(records: list[dict], key: str, require_same_sense: bool = False) -> list[dict]:
    eligible = [record for record in records if record["pose"]["afloat"]]
    if require_same_sense:
        eligible = [
            record
            for record in eligible
            if record["attitude"]["same_span_and_chord_sense"]
        ]
    return sorted(eligible, key=lambda record: record["attitude"][key])


def rank_strict_pca(records: list[dict]) -> list[dict]:
    return sorted(
        [
            record
            for record in records
            if record["pose"]["afloat"]
            and record.get("image_screen", {}).get("best_strict") is not None
        ],
        key=lambda record: record["image_screen"]["best_strict"][
            "pca_loss_lower_is_better"
        ],
    )


def compact_state(record: dict, include_retention: bool = True) -> dict:
    output = {
        "family": record["family"],
        "state_id": record["state_id"],
        "draw_index": record["draw_index"],
        "engine_state": record["engine_state"],
        "mass_kg": record["mass_kg"],
        "modeled_air_volume_m3": record["modeled_air_volume_m3"],
        "retained_air_volume_m3": record["retained_air_volume_m3"],
        "solid_volume_m3": record["solid_volume_m3"],
        "mean_plan_cell_retained_air_fraction": record[
            "mean_plan_cell_retained_air_fraction"
        ],
        "metadata": record["metadata"],
        "pose": record["pose"],
        "attitude": record.get("attitude"),
        "image_screen": record.get("image_screen"),
    }
    if include_retention:
        output["retained_air_fraction"] = record["retained_air_fraction"]
    return output


def family_summary(records: list[dict], compartment_order: list[str]) -> dict:
    afloat = [record for record in records if record["pose"]["afloat"]]
    same = [
        record
        for record in afloat
        if record["attitude"]["same_span_and_chord_sense"]
    ]
    within = [
        record
        for record in same
        if record["attitude"]["within_25_percent_each_slope_component"]
    ]
    waterline = [
        record
        for record in within
        if record["attitude"]["root_above_and_tip_below_sea_level"]
    ]
    target_like_strict = [
        record
        for record in waterline
        if record.get("image_screen", {}).get("best_strict") is not None
    ]
    strict = rank_strict_pca(records)
    summary = {
        "state_count": len(records),
        "afloat_state_count": len(afloat),
        "same_span_and_chord_sense_count": len(same),
        "within_25_percent_each_slope_component_count": len(within),
        "within_25_percent_and_root_above_tip_below_count": len(waterline),
        "within_25_percent_root_above_tip_below_and_strict_size_count": len(
            target_like_strict
        ),
        "states_with_any_strict_size_render": len(strict),
        "closest_same_sense_by_slope": compact_state(
            rank(records, "slope_vector_distance_m", True)[0]
        )
        if same
        else None,
        "closest_by_reference_waterline_rmse": compact_state(
            rank(records, "reference_height_rmse_m")[0]
        )
        if afloat
        else None,
        "lowest_strict_pca_loss": compact_state(strict[0]) if strict else None,
    }
    if within:
        retained = np.asarray(
            [record["retained_air_fraction"] for record in within], dtype=float
        )
        summary["within_25_percent_retention_constraints"] = {
            "retained_in_every_state": [
                compartment_order[index]
                for index in range(9)
                if np.all(retained[:, index] == 1.0)
            ],
            "flooded_in_every_state": [
                compartment_order[index]
                for index in range(9)
                if np.all(retained[:, index] == 0.0)
            ],
            "retained_in_any_state": [
                compartment_order[index]
                for index in range(9)
                if np.any(retained[:, index] > 0.0)
            ],
        }
    if waterline:
        retained = np.asarray(
            [record["retained_air_fraction"] for record in waterline], dtype=float
        )
        summary["target_like_attitude_assumptions"] = {
            "definition": "Each spanwise and chordwise reference-height offset is within 25% of the selected random-pose target, with the modeled root above and tip below sea level.",
            "engine_states": sorted({record["engine_state"] for record in waterline}),
            "draw_indices": sorted({record["draw_index"] for record in waterline}),
            "retained_air_fraction_range_by_sensitivity_cell": {
                compartment_order[index]: {
                    "minimum": float(retained[:, index].min()),
                    "maximum": float(retained[:, index].max()),
                }
                for index in range(9)
            },
            "modeled_retained_air_volume_m3_range": [
                float(min(record["retained_air_volume_m3"] for record in waterline)),
                float(max(record["retained_air_volume_m3"] for record in waterline)),
            ],
            "strict_size_state_count": len(target_like_strict),
        }
    return summary


def refinement_objective(record: dict) -> float:
    if not record["pose"]["afloat"]:
        return math.inf
    return float(record["attitude"]["reference_height_rmse_m"])


def coordinate_refinement(
    start: np.ndarray,
    template,
    target_pose: dict,
    target: dict,
    model_input: dict,
    state_prefix: str,
) -> tuple[dict, int]:
    cache: dict[tuple[float, ...], dict] = {}
    evaluations = 0

    def evaluate(values: np.ndarray) -> dict:
        nonlocal evaluations
        key = tuple(float(round(value, 8)) for value in values)
        if key not in cache:
            evaluations += 1
            cache[key] = state_record(
                "continuous_refinement",
                f"{state_prefix}__eval{evaluations:05d}",
                template,
                np.asarray(key),
                target_pose,
                target,
                model_input,
                {"refinement_evaluation": evaluations},
                screen_image=False,
            )
        return cache[key]

    current = np.asarray(start, dtype=float).copy()
    current_record = evaluate(current)
    settings = model_input["continuous_refinement"]
    levels = [float(value) for value in settings["coarse_levels"]]
    for _ in range(int(settings["maximum_coordinate_sweeps"])):
        previous = refinement_objective(current_record)
        for index in range(9):
            candidates = []
            for value in levels:
                trial = current.copy()
                trial[index] = value
                record = evaluate(trial)
                candidates.append((refinement_objective(record), value, record, trial))
            _, _, current_record, current = min(
                candidates,
                key=lambda item: (item[0], abs(item[1] - current[index]), item[1]),
            )
        if previous - refinement_objective(current_record) < 1e-8:
            break

    step = float(settings["local_step"])
    for _ in range(int(settings["local_sweeps"])):
        for index in range(9):
            values = sorted(
                {
                    max(0.0, min(1.0, current[index] + offset))
                    for offset in (-step, 0.0, step)
                }
            )
            candidates = []
            for value in values:
                trial = current.copy()
                trial[index] = value
                record = evaluate(trial)
                candidates.append((refinement_objective(record), value, record, trial))
            _, _, current_record, current = min(
                candidates,
                key=lambda item: (item[0], abs(item[1] - current[index]), item[1]),
            )
        step /= 2.0

    final = state_record(
        "continuous_refinement",
        f"{state_prefix}__final",
        template,
        current,
        target_pose,
        target,
        model_input,
        {
            "start_binary_pattern": "".join(str(int(value)) for value in start),
            "coordinate_evaluations": evaluations,
            "objective": "minimum RMS error across root, tip, leading and trailing reference heights",
        },
        screen_image=True,
    )
    return final, evaluations


def selected_mask_record(record: dict, template, target: dict, model_input: dict) -> dict:
    best = record.get("image_screen", {}).get("best_strict")
    if best is None:
        return compact_state(record)
    rendered = render_projected_mask(
        template,
        record["pose"],
        best["off_nadir_degrees"],
        best["view_azimuth_degrees"],
        float(model_input["shallow_underwater_visibility_m"]),
    )
    score = score_pca_mask(rendered, target)
    return {
        **compact_state(record),
        "selected_render": {
            **best,
            **score,
            "mask_hex": pack_mask(rendered["mask"]),
            "mask_shape": list(rendered["mask"].shape),
            "mask_pixel_count": int(rendered["mask"].sum()),
        },
    }


def write_state_csv(path: Path, records: list[dict], compartment_order: list[str]) -> None:
    columns = [
        "family",
        "state_id",
        "draw_index",
        "engine_state",
        *[f"retained_{name}" for name in compartment_order],
        "afloat",
        "reserve_buoyancy_kg",
        "roll_degrees",
        "pitch_degrees",
        "equivalent_tilt_degrees",
        "root_height_m",
        "tip_height_m",
        "leading_height_m",
        "trailing_height_m",
        "root_to_tip_m",
        "leading_to_trailing_m",
        "slope_vector_distance_m",
        "reference_height_rmse_m",
        "same_span_and_chord_sense",
        "within_25_percent_each_slope_component",
        "root_above_and_tip_below",
        "best_strict_pca_loss",
        "best_strict_visible_area_m2",
        "best_strict_visible_length_m",
        "best_strict_visible_width_m",
    ]
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        for record in records:
            pose = record["pose"]
            attitude = record.get("attitude", {})
            heights = pose.get("reference_heights_m", {})
            strict = record.get("image_screen", {}).get("best_strict") or {}
            row = {
                "family": record["family"],
                "state_id": record["state_id"],
                "draw_index": record["draw_index"],
                "engine_state": record["engine_state"],
                "afloat": pose["afloat"],
                "reserve_buoyancy_kg": pose.get("reserve_buoyancy_kg", ""),
                "roll_degrees": pose.get("roll_degrees", ""),
                "pitch_degrees": pose.get("pitch_degrees", ""),
                "equivalent_tilt_degrees": pose.get(
                    "equivalent_tilt_from_face_on_degrees", ""
                ),
                "root_height_m": heights.get("root", ""),
                "tip_height_m": heights.get("tip", ""),
                "leading_height_m": heights.get("leading", ""),
                "trailing_height_m": heights.get("trailing", ""),
                "root_to_tip_m": pose.get("root_to_tip_height_difference_m", ""),
                "leading_to_trailing_m": pose.get(
                    "leading_to_trailing_height_difference_m", ""
                ),
                "slope_vector_distance_m": attitude.get(
                    "slope_vector_distance_m", ""
                ),
                "reference_height_rmse_m": attitude.get(
                    "reference_height_rmse_m", ""
                ),
                "same_span_and_chord_sense": attitude.get(
                    "same_span_and_chord_sense", ""
                ),
                "within_25_percent_each_slope_component": attitude.get(
                    "within_25_percent_each_slope_component", ""
                ),
                "root_above_and_tip_below": attitude.get(
                    "root_above_and_tip_below_sea_level", ""
                ),
                "best_strict_pca_loss": strict.get("pca_loss_lower_is_better", ""),
                "best_strict_visible_area_m2": strict.get("visible_area_m2", ""),
                "best_strict_visible_length_m": strict.get(
                    "visible_length_m", ""
                ),
                "best_strict_visible_width_m": strict.get("visible_width_m", ""),
            }
            for index, name in enumerate(compartment_order):
                row[f"retained_{name}"] = record["retained_air_fraction"][index]
            writer.writerow(row)


def main() -> None:
    started = time.perf_counter()
    code_path = Path(__file__).resolve()
    bundle = code_path.parent.parent
    data = bundle / "data"
    outputs = bundle / "outputs"
    outputs.mkdir(parents=True, exist_ok=True)
    input_path = data / "wing-flooding-sensitivity-input.json"
    components_path = data / "boeing-selected-component-context.json"
    targets_path = data / "targets.json"
    pca_path = data / "pca-only-selected-display-masks.json"
    core_path = code_path.parent / "wing_flooding.py"
    model_input = read_json(input_path)
    components = read_json(components_path)
    targets = read_json(targets_path)
    pca = read_json(pca_path)
    target = next(
        record for record in targets["objects"] if record["object_id"] == "phr-4-object-18"
    )
    selected = pca["objects"]["phr-4-object-18"]["wing"]
    component = {
        "id": "left-wing-complete",
        **components["components"]["left-wing-complete"],
    }
    templates = {}
    for parameters in model_input["parameter_draws"]:
        for engine_state in ("absent", "attached"):
            templates[(int(parameters["draw_index"]), engine_state)] = build_wing_template(
                component,
                parameters,
                model_input,
                engine_state,
            )
    target_template = templates[(0, "absent")]
    target_pose = target_pose_record(target_template, selected)
    target_render = render_projected_mask(
        target_template,
        target_pose,
        selected["metadata"]["off_nadir_degrees"],
        selected["metadata"]["view_azimuth_degrees"],
        float(model_input["shallow_underwater_visibility_m"]),
    )
    target_render_score = score_pca_mask(target_render, target)

    original_records = []
    print("Recreating original complete-left-wing flooding schedules", flush=True)
    for name, start_progress in model_input["original_flooding_hypotheses"].items():
        for flood_progress in model_input["original_flood_progress"]:
            retained = retention_from_start_progress(
                np.asarray(start_progress),
                float(flood_progress),
            )
            for (draw_index, engine_state), template in templates.items():
                original_records.append(
                    state_record(
                        "original_progressive_schedule",
                        f"{name}__flood{flood_progress}__draw{draw_index}__{engine_state}",
                        template,
                        retained,
                        target_pose,
                        target,
                        model_input,
                        {
                            "flooding_hypothesis": name,
                            "flood_progress": flood_progress,
                        },
                    )
                )

    binary_records = []
    print("Enumerating all 512 binary compartment patterns x 6 configurations", flush=True)
    for pattern_index in range(512):
        retained = binary_retention(pattern_index)
        for (draw_index, engine_state), template in templates.items():
            binary_records.append(
                state_record(
                    "exhaustive_binary_retention",
                    f"binary{pattern_index:03d}__draw{draw_index}__{engine_state}",
                    template,
                    retained,
                    target_pose,
                    target,
                    model_input,
                    {
                        "binary_pattern_index": pattern_index,
                        "binary_pattern_root_to_tip_leading_to_trailing": "".join(
                            str(int(value)) for value in retained
                        ),
                    },
                )
            )
        if (pattern_index + 1) % 32 == 0:
            print(f"  {pattern_index + 1}/512 patterns", flush=True)

    refined_records = []
    refinement_evaluations = 0
    multistart_count = int(
        model_input["continuous_refinement"][
            "binary_multistart_count_per_configuration"
        ]
    )
    print(
        "Refining retained-air fractions from each configuration's "
        f"{multistart_count} closest binary states",
        flush=True,
    )
    for (draw_index, engine_state), template in templates.items():
        configuration = [
            record
            for record in binary_records
            if record["draw_index"] == draw_index
            and record["engine_state"] == engine_state
            and record["pose"]["afloat"]
        ]
        starts = sorted(
            configuration,
            key=lambda record: (
                refinement_objective(record),
                record["state_id"],
            ),
        )[:multistart_count]
        for start_rank, start_record in enumerate(starts, start=1):
            prefix = (
                f"draw{draw_index}__{engine_state}__start{start_rank:02d}"
            )
            refined, evaluations = coordinate_refinement(
                np.asarray(start_record["retained_air_fraction"], dtype=float),
                template,
                target_pose,
                target,
                model_input,
                prefix,
            )
            refined["metadata"].update(
                {
                    "start_binary_rank_within_configuration": start_rank,
                    "start_binary_state_id": start_record["state_id"],
                    "start_binary_reference_height_rmse_m": refinement_objective(
                        start_record
                    ),
                }
            )
            refined_records.append(refined)
            refinement_evaluations += evaluations
            print(
                f"  draw {draw_index}, engine {engine_state}, "
                f"start {start_rank}: RMSE "
                f"{refinement_objective(start_record):.3f} -> "
                f"{refinement_objective(refined):.3f} m "
                f"({evaluations} evaluations)",
                flush=True,
            )

    all_records = original_records + binary_records + refined_records
    summaries = {
        "original_progressive_schedules": family_summary(
            original_records, model_input["compartment_order"]
        ),
        "exhaustive_binary_retention": family_summary(
            binary_records, model_input["compartment_order"]
        ),
        "continuous_coordinate_refinement": family_summary(
            refined_records, model_input["compartment_order"]
        ),
    }
    top_attitude = rank(all_records, "reference_height_rmse_m")[:20]
    top_pca = rank_strict_pca(all_records)[:20]
    selected_records = {}
    for name, records in {
        "closest_original_waterline": rank(
            original_records, "reference_height_rmse_m"
        ),
        "closest_binary_waterline": rank(binary_records, "reference_height_rmse_m"),
        "closest_refined_waterline": rank(refined_records, "reference_height_rmse_m"),
        "closest_refined_target_like_with_strict_size": sorted(
            [
                record
                for record in refined_records
                if record["pose"]["afloat"]
                and record["attitude"][
                    "within_25_percent_each_slope_component"
                ]
                and record["attitude"][
                    "root_above_and_tip_below_sea_level"
                ]
                and record.get("image_screen", {}).get("best_strict") is not None
            ],
            key=refinement_objective,
        ),
        "lowest_strict_pca_overall": rank_strict_pca(all_records),
    }.items():
        if not records:
            selected_records[name] = None
            continue
        record = records[0]
        template = templates[(record["draw_index"], record["engine_state"])]
        selected_records[name] = selected_mask_record(
            record,
            template,
            target,
            model_input,
        )

    elapsed = time.perf_counter() - started
    output = {
        "schema_version": 2,
        "status": "FIRST_ORDER_MODEL_CONDITIONAL_SENSITIVITY; NOT A BOEING TANK MODEL, FLOODING PROBABILITY, OR OBJECT IDENTITY RESULT",
        "source_hashes_sha256": {
            "sensitivity_input": sha256(input_path),
            "component_context": sha256(components_path),
            "targets": sha256(targets_path),
            "pca_selected_masks": sha256(pca_path),
            "runner_code": sha256(code_path),
            "hydrostatics_code": sha256(core_path),
        },
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "method": {
            "scope": "Complete left-wing geometry only, because that is the exact PHR_4 object-18 PCA-only random-pose source geometry.",
            "compartments": "Nine equal-index span/chord cells ordered root/midspan/tip by leading/middle/trailing. They are retained-air sensitivity cells, not documented Boeing tank bays.",
            "binary_enumeration": "All 2^9 fully retained/fully flooded patterns for three preserved mass-thickness draws and engine absent/attached mass cases.",
            "continuous_refinement": f"Deterministic coordinate search over retained-air fractions in [0,1], initialized at the {multistart_count} binary minima of reference-height RMSE for each mass/engine configuration. This is a local multistart sensitivity, not a proof of a continuous global optimum.",
            "attitude_target": "Exact waterline-relative root, tip, leading and trailing reference heights of random_pose__03122; this is a selected geometry sensitivity, not a measured wing attitude.",
            "descriptive_similarity_flag": "Same tip-down/trailing-down sense with each of those two vertical offsets within 25% of the selected target. The 25% flag is descriptive and is not an observation uncertainty or acceptance probability.",
            "image_screen": "Each equilibrium is rendered at 12 original sensor-surrogate views. PCA IoU is ranked only after the corrected two-sided object-18 area, oriented-length and oriented-width gate.",
            "hydrostatics": "Rigid quasi-static five-layer voxel displacement balance with coarse-to-fine minimum sampled potential; no waves, CFD, compressible trapped-air transport, slosh, flexure, breakup or time integration.",
        },
        "target": {
            "candidate_id": selected["candidate_id"],
            "pinned_pca_iou": selected["silhouette_iou_pca"],
            "pinned_pca_loss": selected["pca_loss_lower_is_better"],
            "pose": target_pose,
            "strict_intervals": target["strict_intervals"],
            "independent_renderer_check": {
                **target_render_score,
                "visible_area_m2": target_render["visible_area_m2"],
                "visible_length_m": target_render["visible_length_m"],
                "visible_width_m": target_render["visible_width_m"],
            },
        },
        "counts": {
            "original_states": len(original_records),
            "binary_states": len(binary_records),
            "refined_states": len(refined_records),
            "continuous_objective_evaluations": refinement_evaluations,
        },
        "summaries": summaries,
        "selected_records": selected_records,
        "top_20_reference_height_rmse": [compact_state(record) for record in top_attitude],
        "top_20_strict_pca": [compact_state(record) for record in top_pca],
        "runtime": {
            "wall_seconds": elapsed,
            "maximum_resident_set_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    }
    output_path = outputs / "phr4-18-wing-flooding-retention-sensitivity.json"
    output_path.write_text(
        json.dumps(json_value(output), indent=2) + "\n",
        encoding="utf-8",
    )
    write_state_csv(
        outputs / "phr4-18-wing-flooding-retention-states.csv",
        all_records,
        model_input["compartment_order"],
    )
    print(
        json.dumps(
            {
                "output": str(output_path),
                "wall_seconds": round(elapsed, 2),
                "summaries": {
                    key: {
                        "afloat": value["afloat_state_count"],
                        "within_25_percent": value[
                            "within_25_percent_each_slope_component_count"
                        ],
                        "strict_pca_states": value[
                            "states_with_any_strict_size_render"
                        ],
                    }
                    for key, value in summaries.items()
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
