"""Shared deterministic geometry and binary-mask operations for the fuselage screen."""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
from scipy.spatial import ConvexHull


PIXEL_SIZE_M = 0.5
GRID_SIZE = 144
NORMALIZED_SIZE = 40
FIELD_METRES = 24.0
CROP_HYPOTHESES = {
    "standard": (0.06, 0.18, 0.58, 0.90),
    "wide": (0.02, 0.12, 0.64, 0.94),
    "inset": (0.10, 0.23, 0.54, 0.86),
}
SEGMENTATION_QUANTILES = (0.96, 0.975, 0.985)
BASELINE_CROP = "standard"
BASELINE_QUANTILE = 0.975


def _component_features(mask: np.ndarray, scores: np.ndarray) -> dict:
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        raise ValueError("Cannot describe an empty component")
    area = len(xs)
    centroid_x = float(xs.mean())
    centroid_y = float(ys.mean())
    dx = xs - centroid_x
    dy = ys - centroid_y
    covariance_xx = float(np.mean(dx * dx))
    covariance_yy = float(np.mean(dy * dy))
    covariance_xy = float(np.mean(dx * dy))
    trace = covariance_xx + covariance_yy
    determinant = covariance_xx * covariance_yy - covariance_xy**2
    discriminant = math.sqrt(max(0.0, trace**2 / 4.0 - determinant))
    lambda1 = max(0.0, trace / 2.0 + discriminant)
    lambda2 = max(1e-9, trace / 2.0 - discriminant)
    orientation = 0.5 * math.atan2(
        2.0 * covariance_xy, covariance_xx - covariance_yy
    )
    min_x, max_x = int(xs.min()), int(xs.max())
    min_y, max_y = int(ys.min()), int(ys.max())
    bounding_width = max_x - min_x + 1
    bounding_height = max_y - min_y + 1
    padded = np.pad(mask, 1, constant_values=False)
    perimeter = 0
    core = padded[1:-1, 1:-1]
    for shifted in (
        padded[:-2, 1:-1],
        padded[1:-1, 2:],
        padded[2:, 1:-1],
        padded[1:-1, :-2],
    ):
        perimeter += int(np.count_nonzero(core & ~shifted))
    return {
        "area": area,
        "centroid_x": centroid_x,
        "centroid_y": centroid_y,
        "bbox": {
            "x": min_x,
            "y": min_y,
            "width": bounding_width,
            "height": bounding_height,
        },
        "mean_anomaly_score": float(scores[mask].mean()),
        "aspect_ratio": math.sqrt(lambda1 / lambda2),
        "orientation_degrees": math.degrees(orientation),
        "perimeter": perimeter,
        "compactness": 4.0 * math.pi * area / perimeter**2 if perimeter else 0.0,
        "fill_ratio": area / (bounding_width * bounding_height),
        "touches_boundary": (
            min_x == 0
            or min_y == 0
            or max_x == mask.shape[1] - 1
            or max_y == mask.shape[0] - 1
        ),
        "mask": mask,
    }


def _components(mask: np.ndarray, scores: np.ndarray) -> list[dict]:
    labels, count = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.uint8))
    return [_component_features(labels == label, scores) for label in range(1, count + 1)]


def segment_candidate(
    image_path: str,
    crop_bounds: tuple[float, float, float, float] = CROP_HYPOTHESES[BASELINE_CROP],
    threshold_quantile: float = BASELINE_QUANTILE,
) -> dict:
    """Segment one report-panel crop and anomaly-threshold hypothesis."""
    rgba = np.asarray(Image.open(image_path).convert("RGBA"), dtype=np.float64)
    height, width = rgba.shape[:2]
    fraction_x0, fraction_y0, fraction_x1, fraction_y1 = crop_bounds
    x0 = max(0, math.floor(width * fraction_x0))
    y0 = max(0, math.floor(height * fraction_y0))
    x1 = min(width, math.ceil(width * fraction_x1))
    y1 = min(height, math.ceil(height * fraction_y1))
    crop = rgba[y0:y1, x0:x1, :3]
    red, green, blue = crop[..., 0], crop[..., 1], crop[..., 2]
    valid = ~((red > 70) & (red > green * 1.35) & (red > blue * 1.25))
    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    values = luminance[valid]
    background = float(np.median(values))
    mad = max(1.0, float(np.median(np.abs(values - background))))
    scores = np.zeros_like(luminance, dtype=np.float64)
    scores[valid] = np.abs(luminance[valid] - background) / (1.4826 * mad)
    threshold = float(
        np.quantile(scores[valid], threshold_quantile, method="linear")
    )
    anomalous = valid & (scores >= threshold)
    maximum_area = anomalous.size * 0.12
    candidates = []
    for component in _components(anomalous, scores):
        bbox = component["bbox"]
        if (
            component["area"] >= 3
            and component["area"] <= maximum_area
            and bbox["width"] < anomalous.shape[1] * 0.75
            and bbox["height"] < anomalous.shape[0] * 0.75
            and not component["touches_boundary"]
        ):
            distance = math.hypot(
                (component["centroid_x"] - anomalous.shape[1] * 0.48)
                / anomalous.shape[1],
                (component["centroid_y"] - anomalous.shape[0] * 0.52)
                / anomalous.shape[0],
            )
            component["selection_score"] = (
                component["mean_anomaly_score"]
                * math.sqrt(component["area"])
                / (1.0 + 10.0 * distance**2)
            )
            candidates.append(component)
    if not candidates:
        raise ValueError(
            f"No candidate component in {image_path} for "
            f"crop={crop_bounds}, q={threshold_quantile}"
        )
    candidates.sort(key=lambda item: item["selection_score"], reverse=True)
    best = candidates[0]
    radius = max(8.0, min(anomalous.shape) * 0.10)
    merged = np.zeros_like(anomalous, dtype=bool)
    for component in candidates:
        distance = math.hypot(
            component["centroid_x"] - best["centroid_x"],
            component["centroid_y"] - best["centroid_y"],
        )
        if component is best or (component["area"] >= 2 and distance <= radius):
            merged |= component["mask"]
    result = _component_features(merged, scores)
    result.update(
        {
            "source_width": width,
            "source_height": height,
            "source_x": x0,
            "source_y": y0,
            "centroid_source_x": x0 + result["centroid_x"],
            "centroid_source_y": y0 + result["centroid_y"],
            "threshold_quantile": threshold_quantile,
            "threshold": threshold,
            "background": background,
            "mad": mad,
        }
    )
    return result


def component_source_mask(component: dict) -> np.ndarray:
    """Place a crop-local component mask in its complete report-panel field."""
    output = np.zeros(
        (component["source_height"], component["source_width"]),
        dtype=bool,
    )
    source_y = int(component["source_y"])
    source_x = int(component["source_x"])
    height, width = component["mask"].shape
    output[source_y : source_y + height, source_x : source_x + width] = component[
        "mask"
    ]
    return output


def mask_iou(first: np.ndarray, second: np.ndarray) -> float:
    intersection = int(np.count_nonzero(first & second))
    union = int(np.count_nonzero(first | second))
    return intersection / union if union else 0.0


def normalize_mask(
    mask: np.ndarray,
    orientation_degrees: float,
    centroid_x: float,
    centroid_y: float,
    size: int = NORMALIZED_SIZE,
) -> np.ndarray:
    ys, xs = np.nonzero(mask)
    angle = math.radians(orientation_degrees)
    cosine, sine = math.cos(angle), math.sin(angle)
    dx = xs - centroid_x
    dy = ys - centroid_y
    u = dx * cosine + dy * sine
    v = -dx * sine + dy * cosine
    minimum_u, maximum_u = float(u.min()) - 0.5, float(u.max()) + 0.5
    minimum_v, maximum_v = float(v.min()) - 0.5, float(v.max()) + 0.5
    centre_u = (minimum_u + maximum_u) / 2.0
    centre_v = (minimum_v + maximum_v) / 2.0
    scale = (size - 6) / max(maximum_u - minimum_u, maximum_v - minimum_v)
    out_y, out_x = np.indices((size, size), dtype=np.float64)
    sample_u = (out_x + 0.5 - size / 2.0) / scale + centre_u
    sample_v = (out_y + 0.5 - size / 2.0) / scale + centre_v
    source_dx = sample_u * cosine - sample_v * sine
    source_dy = sample_u * sine + sample_v * cosine
    source_x = np.floor(centroid_x + source_dx + 0.5).astype(int)
    source_y = np.floor(centroid_y + source_dy + 0.5).astype(int)
    valid = (
        (source_x >= 0)
        & (source_x < mask.shape[1])
        & (source_y >= 0)
        & (source_y < mask.shape[0])
    )
    normalized = np.zeros((size, size), dtype=bool)
    normalized[valid] = mask[source_y[valid], source_x[valid]]
    return normalized


def mask_integer(mask: np.ndarray) -> int:
    value = 0
    for index in np.flatnonzero(mask.ravel()):
        value |= 1 << int(index)
    return value


def shape_transforms(mask: np.ndarray) -> tuple[int, int, int, int]:
    return (
        mask_integer(mask),
        mask_integer(np.fliplr(mask)),
        mask_integer(np.flipud(mask)),
        mask_integer(np.flipud(np.fliplr(mask))),
    )


def best_iou(target: int, candidates: Iterable[int]) -> float:
    best = 0.0
    for candidate in candidates:
        union = (target | candidate).bit_count()
        if union:
            best = max(best, (target & candidate).bit_count() / union)
    return best


def oriented_dimensions(mask: np.ndarray) -> dict:
    scores = mask.astype(np.float64)
    component = _component_features(mask, scores)
    ys, xs = np.nonzero(mask)
    angle = math.radians(component["orientation_degrees"])
    cosine, sine = math.cos(angle), math.sin(angle)
    dx = xs - component["centroid_x"]
    dy = ys - component["centroid_y"]
    first = dx * cosine + dy * sine
    second = -dx * sine + dy * cosine
    first_extent = float(first.max() - first.min() + 1.0)
    second_extent = float(second.max() - second.min() + 1.0)
    normalized = normalize_mask(
        mask,
        component["orientation_degrees"],
        component["centroid_x"],
        component["centroid_y"],
    )
    return {
        "visible_area_m2": component["area"] * PIXEL_SIZE_M**2,
        "visible_length_m": max(first_extent, second_extent) * PIXEL_SIZE_M,
        "visible_width_m": min(first_extent, second_extent) * PIXEL_SIZE_M,
        "orientation_degrees": component["orientation_degrees"],
        "normalized": normalized,
    }


@dataclass(frozen=True)
class RadiusProfile:
    x: np.ndarray
    radius: np.ndarray

    @property
    def minimum_x(self) -> float:
        return float(self.x[0])

    @property
    def maximum_x(self) -> float:
        return float(self.x[-1])

    def at(self, values: np.ndarray) -> np.ndarray:
        return np.interp(values, self.x, self.radius)


def radius_profile_from_polygon(points: list[dict], samples: int = 320) -> RadiusProfile:
    polygon = np.array([[point["x"], point["y"]] for point in points], dtype=float)
    minimum_x, maximum_x = float(polygon[:, 0].min()), float(polygon[:, 0].max())
    sample_x = np.linspace(minimum_x, maximum_x, samples)
    radius = np.zeros(samples, dtype=float)
    for sample_index, x_value in enumerate(sample_x):
        intersections: list[float] = []
        for index in range(len(polygon)):
            first = polygon[index]
            second = polygon[(index + 1) % len(polygon)]
            low, high = sorted((first[0], second[0]))
            if x_value < low - 1e-9 or x_value > high + 1e-9:
                continue
            if abs(second[0] - first[0]) < 1e-12:
                if abs(x_value - first[0]) < (maximum_x - minimum_x) / samples:
                    intersections.extend((float(first[1]), float(second[1])))
                continue
            fraction = (x_value - first[0]) / (second[0] - first[0])
            if -1e-9 <= fraction <= 1.0 + 1e-9:
                intersections.append(float(first[1] + fraction * (second[1] - first[1])))
        if len(intersections) >= 2:
            radius[sample_index] = (max(intersections) - min(intersections)) / 2.0
    valid = radius > 1e-4
    if valid.sum() < samples // 2:
        raise ValueError("Could not derive a usable fuselage radius profile")
    radius = np.interp(sample_x, sample_x[valid], radius[valid])
    radius[0] = min(radius[0], 0.05)
    radius[-1] = min(radius[-1], 0.05)
    return RadiusProfile(sample_x, radius)


def project_segment_polygon(
    profile: RadiusProfile,
    x0: float,
    x1: float,
    view_axis_cosine: float,
    axial_samples: int = 56,
    radial_samples: int = 20,
) -> np.ndarray:
    x_values = np.linspace(x0, x1, axial_samples)
    radii = profile.at(x_values)
    phi = np.linspace(0.0, 2.0 * math.pi, radial_samples, endpoint=False)
    mu = min(1.0, max(0.0, view_axis_cosine))
    axial_projection = math.sqrt(max(0.0, 1.0 - mu**2))
    centred_x = x_values - (x0 + x1) / 2.0
    u = centred_x[:, None] * axial_projection + radii[:, None] * mu * np.cos(phi)
    v = np.broadcast_to(radii[:, None] * np.sin(phi), u.shape)
    points = np.column_stack((u.ravel(), v.ravel()))
    hull = ConvexHull(points)
    return points[hull.vertices]


def rasterize_polygon(polygon_m: np.ndarray, supersample: int = 2) -> np.ndarray:
    side = GRID_SIZE * supersample
    centre = side / 2.0
    coordinates = [
        (
            centre + float(point[0]) / PIXEL_SIZE_M * supersample,
            centre + float(point[1]) / PIXEL_SIZE_M * supersample,
        )
        for point in polygon_m
    ]
    canvas = Image.new("L", (side, side), 0)
    ImageDraw.Draw(canvas).polygon(coordinates, fill=255)
    high = np.asarray(canvas, dtype=np.float32) / 255.0
    coverage = high.reshape(GRID_SIZE, supersample, GRID_SIZE, supersample).mean(axis=(1, 3))
    return coverage >= 0.25


def clip_waterline(mask: np.ndarray, fraction: float, angle: float) -> np.ndarray:
    if fraction >= 0.999:
        return mask.copy()
    ys, xs = np.nonzero(mask)
    if len(xs) == 0:
        return mask.copy()
    coordinate = (
        (xs - GRID_SIZE / 2.0) * math.cos(angle)
        + (ys - GRID_SIZE / 2.0) * math.sin(angle)
    )
    order = np.argsort(-coordinate, kind="stable")
    keep = max(1, min(len(order), int(round(len(order) * fraction))))
    output = np.zeros_like(mask, dtype=bool)
    output[ys[order[:keep]], xs[order[:keep]]] = True
    return output


def render_candidate_mask(
    profile: RadiusProfile,
    x0: float,
    x1: float,
    view_axis_cosine: float,
    visible_fraction: float,
    waterline_angle: float,
) -> np.ndarray:
    polygon = project_segment_polygon(profile, x0, x1, view_axis_cosine)
    mask = rasterize_polygon(polygon)
    return clip_waterline(mask, visible_fraction, waterline_angle)


def pack_mask(mask: np.ndarray) -> str:
    return np.packbits(mask.ravel().astype(np.uint8)).tobytes().hex()


def unpack_mask(value: str, shape: tuple[int, int] = (GRID_SIZE, GRID_SIZE)) -> np.ndarray:
    packed = np.frombuffer(bytes.fromhex(value), dtype=np.uint8)
    return np.unpackbits(packed, count=shape[0] * shape[1]).reshape(shape).astype(bool)

