"""First-order rigid-wing hydrostatics and Pléiades mask rendering.

This is a deterministic sensitivity model.  Its 3 x 3 retained-air cells are
surrogates for unknown post-fracture vent paths; they are not Boeing tank bays.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from scipy import ndimage

from morphology import (
    best_iou,
    oriented_dimensions,
    shape_transforms,
)


ANGLE_LIMIT_DEGREES = 86.0
LEGACY_RENDER_SIZE = 112


@dataclass(frozen=True)
class WingTemplate:
    """Geometry, mass and per-cell volumes that do not depend on flooding."""

    component_id: str
    draw_index: int
    engine_state: str
    parameters: dict
    plan_step_m: float
    plan_xy: np.ndarray
    thickness_m: np.ndarray
    span_fraction: np.ndarray
    chord_fraction: np.ndarray
    compartment_index: np.ndarray
    sample_xyz: np.ndarray
    sample_vertical_size_m: np.ndarray
    sample_solid_volume_m3: np.ndarray
    sample_air_volume_m3: np.ndarray
    sample_compartment_index: np.ndarray
    mass_kg: float
    centre_of_mass: np.ndarray
    references: dict[str, np.ndarray]
    outer_volume_m3: float


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


def _average_polygon(polygon: Iterable[dict]) -> np.ndarray:
    values = np.asarray([[point["x"], point["y"]] for point in polygon], dtype=float)
    return values.mean(axis=0)


def build_wing_template(
    component: dict,
    parameters: dict,
    model_input: dict,
    engine_state: str,
) -> WingTemplate:
    """Build the preserved 1 m / five-layer complete-wing surrogate."""
    if engine_state not in {"absent", "attached"}:
        raise ValueError(f"Unknown engine state: {engine_state}")
    outline = np.asarray(
        [[point["x"], point["y"]] for point in component["polygon"]],
        dtype=float,
    )
    negatives = [
        np.asarray([[point["x"], point["y"]] for point in polygon], dtype=float)
        for polygon in component.get("negative_polygons", [])
    ]
    minimum = outline.min(axis=0)
    maximum = outline.max(axis=0)
    centre = (minimum + maximum) / 2.0
    root_absolute_y = float(np.min(np.abs(outline[:, 1])))
    tip_absolute_y = float(np.max(np.abs(outline[:, 1])))
    step = float(model_input["plan_sampling_m"])

    plan_xy = []
    thickness = []
    span_fraction = []
    chord_fraction = []
    mass_weight = []
    compartment_index = []
    for y in np.arange(minimum[1] + step / 2.0, maximum[1], step):
        intersections = _line_intersections_at_y(outline, float(y))
        if len(intersections) < 2:
            continue
        leading_x, trailing_x = intersections[0], intersections[-1]
        for x in np.arange(minimum[0] + step / 2.0, maximum[0], step):
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
            mass_weight.append(
                (1.0 + parameters["root_mass_bias"] * (1.0 - span) ** 2)
                * (1.0 + parameters["trailing_mass_bias"] * chord**2)
            )
            span_index = min(2, int(np.floor(min(span, 0.999999) * 3.0)))
            chord_index = min(2, int(np.floor(min(chord, 0.999999) * 3.0)))
            compartment_index.append(span_index * 3 + chord_index)

    plan_xy_array = np.asarray(plan_xy, dtype=float)
    thickness_array = np.asarray(thickness, dtype=float)
    span_array = np.asarray(span_fraction, dtype=float)
    chord_array = np.asarray(chord_fraction, dtype=float)
    mass_weight_array = np.asarray(mass_weight, dtype=float)
    compartment_array = np.asarray(compartment_index, dtype=np.int8)
    if len(plan_xy_array) < 30:
        raise ValueError("Too few plan cells for wing hydrostatic model")

    dry_mass_kg = float(parameters["dry_mass_kg"])
    solid_volume_m3 = dry_mass_kg / float(model_input["material_density_kg_m3"])
    cell_outer_volume = step**2 * thickness_array
    cell_solid_volume = (
        solid_volume_m3 * mass_weight_array / mass_weight_array.sum()
    )
    cell_air_volume = np.maximum(0.0, cell_outer_volume - cell_solid_volume)
    layers = int(model_input["vertical_layers"])
    layer_fraction = (np.arange(layers, dtype=float) + 0.5) / layers - 0.5
    sample_xy = np.repeat(plan_xy_array, layers, axis=0)
    sample_z = (thickness_array[:, None] * layer_fraction[None, :]).ravel()
    sample_xyz = np.column_stack((sample_xy, sample_z))
    sample_vertical_size = np.maximum(
        0.12,
        np.repeat(thickness_array / layers, layers),
    )
    sample_solid_volume = np.repeat(cell_solid_volume / layers, layers)
    sample_air_volume = np.repeat(cell_air_volume / layers, layers)
    sample_compartment = np.repeat(compartment_array, layers)

    dry_mass_points = np.column_stack(
        (plan_xy_array, -0.08 * thickness_array)
    )
    dry_point_mass = dry_mass_kg * mass_weight_array / mass_weight_array.sum()
    if engine_state == "attached":
        engine_point = np.asarray(
            [
                model_input["engine_mass_point_local_m"]["x"],
                model_input["engine_mass_point_local_m"]["y"],
                model_input["engine_mass_point_local_m"]["z"],
            ],
            dtype=float,
        )
        dry_mass_points = np.vstack((dry_mass_points, engine_point))
        dry_point_mass = np.concatenate(
            (dry_point_mass, [float(model_input["engine_mass_kg"])])
        )
    mass_kg = float(dry_point_mass.sum())
    centre_of_mass = (
        dry_mass_points * dry_point_mass[:, None]
    ).sum(axis=0) / mass_kg

    references = {}
    for name, mask in {
        "root": span_array < 0.12,
        "tip": span_array > 0.88,
        "leading": chord_array < 0.12,
        "trailing": chord_array > 0.88,
    }.items():
        references[name] = np.asarray(
            [plan_xy_array[mask, 0].mean(), plan_xy_array[mask, 1].mean(), 0.0]
        )

    return WingTemplate(
        component_id=component["id"],
        draw_index=int(parameters["draw_index"]),
        engine_state=engine_state,
        parameters=dict(parameters),
        plan_step_m=step,
        plan_xy=plan_xy_array,
        thickness_m=thickness_array,
        span_fraction=span_array,
        chord_fraction=chord_array,
        compartment_index=compartment_array,
        sample_xyz=sample_xyz,
        sample_vertical_size_m=sample_vertical_size,
        sample_solid_volume_m3=sample_solid_volume,
        sample_air_volume_m3=sample_air_volume,
        sample_compartment_index=sample_compartment,
        mass_kg=mass_kg,
        centre_of_mass=centre_of_mass,
        references=references,
        outer_volume_m3=float(cell_outer_volume.sum()),
    )


def rotation_matrix(roll_degrees: float, pitch_degrees: float) -> np.ndarray:
    roll = math.radians(roll_degrees)
    pitch = math.radians(pitch_degrees)
    cosine_roll, sine_roll = math.cos(roll), math.sin(roll)
    cosine_pitch, sine_pitch = math.cos(pitch), math.sin(pitch)
    return np.asarray(
        [
            [
                cosine_pitch,
                sine_pitch * sine_roll,
                sine_pitch * cosine_roll,
            ],
            [0.0, cosine_roll, -sine_roll],
            [
                -sine_pitch,
                cosine_pitch * sine_roll,
                cosine_pitch * cosine_roll,
            ],
        ]
    )


def transform_points(
    points: np.ndarray,
    matrix: np.ndarray,
    heave_m: float = 0.0,
) -> np.ndarray:
    output = np.asarray(points, dtype=float) @ np.asarray(matrix, dtype=float).T
    output[:, 2] += heave_m
    return output


def retained_buoyancy_volumes(
    template: WingTemplate,
    retained_air_fraction: np.ndarray,
) -> np.ndarray:
    retained = np.asarray(retained_air_fraction, dtype=float)
    if retained.shape != (9,) or np.any(retained < 0.0) or np.any(retained > 1.0):
        raise ValueError("retained-air fractions must be a length-nine vector in [0,1]")
    return template.sample_solid_volume_m3 + template.sample_air_volume_m3 * retained[
        template.sample_compartment_index
    ]


def _submerged_fraction(z: np.ndarray, characteristic_height: np.ndarray) -> np.ndarray:
    half_band = np.maximum(0.08, characteristic_height / 2.0)
    return np.clip((half_band - z) / (2.0 * half_band), 0.0, 1.0)


def _evaluate_orientation(
    template: WingTemplate,
    buoyancy_volume: np.ndarray,
    water_density: float,
    roll_degrees: float,
    pitch_degrees: float,
) -> dict:
    matrix = rotation_matrix(roll_degrees, pitch_degrees)
    rotated = template.sample_xyz @ matrix.T
    characteristic_height = np.maximum(
        0.12,
        abs(matrix[2, 0]) * template.plan_step_m
        + abs(matrix[2, 1]) * template.plan_step_m
        + abs(matrix[2, 2]) * template.sample_vertical_size_m,
    )
    target_volume = template.mass_kg / water_density
    lower, upper = -40.0, 40.0
    for _ in range(14):
        middle = (lower + upper) / 2.0
        displaced = float(
            np.sum(
                buoyancy_volume
                * _submerged_fraction(rotated[:, 2] + middle, characteristic_height)
            )
        )
        if displaced > target_volume:
            lower = middle
        else:
            upper = middle
    heave_m = (lower + upper) / 2.0
    z = rotated[:, 2] + heave_m
    fraction = _submerged_fraction(z, characteristic_height)
    displaced_by_sample = buoyancy_volume * fraction
    displaced_volume = float(displaced_by_sample.sum())
    submerged_centroid_z = z - characteristic_height * (1.0 - fraction) / 2.0
    centre_of_buoyancy = np.asarray(
        [
            np.sum(rotated[:, 0] * displaced_by_sample),
            np.sum(rotated[:, 1] * displaced_by_sample),
            np.sum(submerged_centroid_z * displaced_by_sample),
        ]
    ) / displaced_volume
    centre_of_mass_world = transform_points(
        template.centre_of_mass[None, :], matrix, heave_m
    )[0]
    residual = float(
        np.hypot(
            centre_of_buoyancy[0] - centre_of_mass_world[0],
            centre_of_buoyancy[1] - centre_of_mass_world[1],
        )
    )
    potential_per_kg = float(
        centre_of_mass_world[2]
        - water_density / template.mass_kg
        * np.sum(submerged_centroid_z * displaced_by_sample)
    )
    return {
        "roll_degrees": float(roll_degrees),
        "pitch_degrees": float(pitch_degrees),
        "heave_m": heave_m,
        "matrix": matrix,
        "centre_of_buoyancy": centre_of_buoyancy,
        "centre_of_mass_world": centre_of_mass_world,
        "horizontal_force_line_residual_m": residual,
        "objective": potential_per_kg,
        "displaced_volume_m3": displaced_volume,
    }


def _angle_grid(centre: float, radius: float, step: float) -> list[float]:
    values = []
    value = centre - radius
    while value <= centre + radius + 1e-9:
        clipped = min(ANGLE_LIMIT_DEGREES, max(-ANGLE_LIMIT_DEGREES, value))
        if clipped not in values:
            values.append(clipped)
        value += step
    return values


def _evaluate_grid(
    template: WingTemplate,
    buoyancy_volume: np.ndarray,
    water_density: float,
    rolls: Iterable[float],
    pitches: Iterable[float],
) -> list[dict]:
    results = [
        _evaluate_orientation(
            template,
            buoyancy_volume,
            water_density,
            roll,
            pitch,
        )
        for roll in rolls
        for pitch in pitches
    ]
    return sorted(results, key=lambda record: record["objective"])


def reference_heights(template: WingTemplate, pose: dict) -> dict[str, float]:
    matrix = np.asarray(pose["matrix"], dtype=float)
    heave_m = float(pose["heave_m"])
    return {
        name: float(transform_points(point[None, :], matrix, heave_m)[0, 2])
        for name, point in template.references.items()
    }


def solve_hydrostatic_pose(
    template: WingTemplate,
    retained_air_fraction: np.ndarray,
    water_density: float,
) -> dict:
    """Solve the preserved coarse-to-fine minimum-potential attitude."""
    retained = np.asarray(retained_air_fraction, dtype=float)
    buoyancy_volume = retained_buoyancy_volumes(template, retained)
    reserve_kg = float(buoyancy_volume.sum() * water_density - template.mass_kg)
    if reserve_kg < 0.0:
        return {
            "afloat": False,
            "reserve_buoyancy_kg": reserve_kg,
            "reason": "effective retained buoyancy is less than required displacement",
        }
    coarse_angles = (-75.0, -50.0, -25.0, 0.0, 25.0, 50.0, 75.0)
    ranked = _evaluate_grid(
        template,
        buoyancy_volume,
        water_density,
        coarse_angles,
        coarse_angles,
    )
    refined = []
    for seed in ranked[:2]:
        refined.extend(
            _evaluate_grid(
                template,
                buoyancy_volume,
                water_density,
                _angle_grid(seed["roll_degrees"], 20.0, 10.0),
                _angle_grid(seed["pitch_degrees"], 20.0, 10.0),
            )
        )
    ranked = sorted(ranked + refined, key=lambda record: record["objective"])
    seed = ranked[0]
    final = _evaluate_grid(
        template,
        buoyancy_volume,
        water_density,
        _angle_grid(seed["roll_degrees"], 8.0, 4.0),
        _angle_grid(seed["pitch_degrees"], 8.0, 4.0),
    )
    best = min(ranked + final, key=lambda record: record["objective"])
    perturbations = (
        _evaluate_orientation(
            template,
            buoyancy_volume,
            water_density,
            best["roll_degrees"] + 4.0,
            best["pitch_degrees"],
        ),
        _evaluate_orientation(
            template,
            buoyancy_volume,
            water_density,
            best["roll_degrees"] - 4.0,
            best["pitch_degrees"],
        ),
        _evaluate_orientation(
            template,
            buoyancy_volume,
            water_density,
            best["roll_degrees"],
            best["pitch_degrees"] + 4.0,
        ),
        _evaluate_orientation(
            template,
            buoyancy_volume,
            water_density,
            best["roll_degrees"],
            best["pitch_degrees"] - 4.0,
        ),
    )
    locally_stable = all(
        pose["objective"] >= best["objective"] - 0.01 for pose in perturbations
    )
    heights = reference_heights(template, best)
    root_to_tip = heights["tip"] - heights["root"]
    leading_to_trailing = heights["trailing"] - heights["leading"]
    equivalent_tilt = math.degrees(
        math.acos(min(1.0, max(-1.0, abs(float(best["matrix"][2, 2])))))
    )
    return {
        "afloat": True,
        "reserve_buoyancy_kg": reserve_kg,
        "roll_degrees": best["roll_degrees"],
        "pitch_degrees": best["pitch_degrees"],
        "heave_m": best["heave_m"],
        "equivalent_tilt_from_face_on_degrees": equivalent_tilt,
        "root_to_tip_height_difference_m": root_to_tip,
        "leading_to_trailing_height_difference_m": leading_to_trailing,
        "reference_heights_m": heights,
        "centre_of_buoyancy": best["centre_of_buoyancy"],
        "centre_of_mass_world": best["centre_of_mass_world"],
        "horizontal_force_line_residual_m": best[
            "horizontal_force_line_residual_m"
        ],
        "locally_stable_grid_check": locally_stable,
        "matrix": best["matrix"],
    }


def retention_from_start_progress(
    start_progress: np.ndarray,
    flood_progress: float,
) -> np.ndarray:
    start = np.asarray(start_progress, dtype=float).reshape(9)
    retained = np.ones(9, dtype=float)
    active = flood_progress > start
    finite = active & (start < 1.0)
    retained[finite] = np.clip(
        (1.0 - flood_progress) / (1.0 - start[finite]),
        0.0,
        1.0,
    )
    return retained


def binary_retention(pattern_index: int) -> np.ndarray:
    if not 0 <= pattern_index < 512:
        raise ValueError("binary pattern index must be in [0,511]")
    return np.asarray(
        [(pattern_index >> index) & 1 for index in range(9)],
        dtype=float,
    )


def retention_code(retained_air_fraction: np.ndarray) -> str:
    return "".join(f"{value:.5f}".rstrip("0").rstrip(".") for value in retained_air_fraction)


def attitude_metrics(pose: dict, target_pose: dict) -> dict:
    if not pose["afloat"]:
        return {}
    target_heights = target_pose["reference_heights_m"]
    heights = pose["reference_heights_m"]
    span_error = (
        pose["root_to_tip_height_difference_m"]
        - target_pose["root_to_tip_height_difference_m"]
    )
    chord_error = (
        pose["leading_to_trailing_height_difference_m"]
        - target_pose["leading_to_trailing_height_difference_m"]
    )
    reference_errors = np.asarray(
        [heights[name] - target_heights[name] for name in target_heights]
    )
    relative_span = span_error / abs(target_pose["root_to_tip_height_difference_m"])
    relative_chord = chord_error / abs(
        target_pose["leading_to_trailing_height_difference_m"]
    )
    return {
        "span_height_error_m": span_error,
        "chord_height_error_m": chord_error,
        "slope_vector_distance_m": float(math.hypot(span_error, chord_error)),
        "relative_slope_rmse": float(
            math.sqrt((relative_span**2 + relative_chord**2) / 2.0)
        ),
        "reference_height_rmse_m": float(
            math.sqrt(np.mean(reference_errors**2))
        ),
        "tilt_error_degrees": (
            pose["equivalent_tilt_from_face_on_degrees"]
            - target_pose["equivalent_tilt_from_face_on_degrees"]
        ),
        "same_span_and_chord_sense": (
            pose["root_to_tip_height_difference_m"] < 0.0
            and pose["leading_to_trailing_height_difference_m"] < 0.0
        ),
        "root_above_and_tip_below_sea_level": (
            heights["root"] > 0.0 and heights["tip"] < 0.0
        ),
        "within_25_percent_each_slope_component": (
            abs(relative_span) <= 0.25 and abs(relative_chord) <= 0.25
        ),
    }


def render_projected_mask(
    template: WingTemplate,
    pose: dict,
    off_nadir_degrees: float,
    azimuth_degrees: float,
    shallow_underwater_visibility_m: float,
    pixel_size_m: float = 0.5,
    size: int = LEGACY_RENDER_SIZE,
) -> dict | None:
    """Render the preserved point-sampled orthographic visible silhouette."""
    if not pose["afloat"]:
        return None
    world = transform_points(
        template.sample_xyz,
        np.asarray(pose["matrix"], dtype=float),
        float(pose["heave_m"]),
    )
    world = world[world[:, 2] >= -shallow_underwater_visibility_m]
    if len(world) < 2:
        return None
    theta = math.radians(off_nadir_degrees)
    azimuth = math.radians(azimuth_degrees)
    right = np.asarray((-math.sin(azimuth), math.cos(azimuth), 0.0))
    up = np.asarray(
        (
            -math.cos(theta) * math.cos(azimuth),
            -math.cos(theta) * math.sin(azimuth),
            math.sin(theta),
        )
    )
    u = world @ right
    v = world @ up
    x = np.floor(size / 2.0 + (u - u.mean()) / pixel_size_m + 0.5).astype(int)
    y = np.floor(size / 2.0 + (v - v.mean()) / pixel_size_m + 0.5).astype(int)
    valid = (x >= 1) & (y >= 1) & (x < size - 1) & (y < size - 1)
    raw = np.zeros((size, size), dtype=bool)
    raw[y[valid], x[valid]] = True
    structure = np.ones((3, 3), dtype=bool)
    closed = ndimage.binary_erosion(
        ndimage.binary_dilation(raw, structure=structure),
        structure=structure,
    )
    expanded = ndimage.binary_dilation(closed, structure=structure)
    labels, count = ndimage.label(expanded, structure=structure)
    candidates = []
    for label in range(1, count + 1):
        component = labels == label
        ys, xs = np.nonzero(component)
        if len(xs) < 2:
            continue
        touches = (
            xs.min() == 0
            or ys.min() == 0
            or xs.max() == size - 1
            or ys.max() == size - 1
        )
        if not touches:
            candidates.append(component)
    if not candidates:
        return None
    mask = max(candidates, key=np.count_nonzero)
    dimensions = oriented_dimensions(mask)
    return {
        "mask": mask,
        "visible_area_m2": dimensions["visible_area_m2"],
        "visible_length_m": dimensions["visible_length_m"],
        "visible_width_m": dimensions["visible_width_m"],
        "shape_transforms": shape_transforms(dimensions["normalized"]),
        "off_nadir_degrees": float(off_nadir_degrees),
        "view_azimuth_degrees": float(azimuth_degrees),
    }


def score_pca_mask(rendered: dict, target: dict) -> dict:
    intervals = target["strict_intervals"]
    strict = all(
        intervals[key]["p10"] <= rendered[key] <= intervals[key]["p90"]
        for key in ("visible_area_m2", "visible_length_m", "visible_width_m")
    )
    iou = best_iou(
        int(target["views"]["pca"]["normalized_mask_integer"]),
        rendered["shape_transforms"],
    )
    return {
        "strict_size_eligible": strict,
        "silhouette_iou_pca": iou,
        "pca_loss_lower_is_better": 1.0 - iou,
    }
