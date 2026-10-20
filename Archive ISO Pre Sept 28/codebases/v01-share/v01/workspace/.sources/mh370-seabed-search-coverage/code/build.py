#!/usr/bin/env python3
"""Acquire, build, and validate the MH370 searched-area evidence package.

Network downloads are staged under /tmp; package files are replaced only after
all requested source hashes match. Publication rendering uses Matplotlib from
the repository's pinned Python environment; acquisition and validation remain
standard-library code.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import html
import io
import json
import math
import re
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "provenance" / "sources.lock.json"
USER_AGENT = "mh370-seabed-search-coverage/1.0 (source verification)"
EXPECTED_GEOMETRY = {
    "phase2-deep-tow-l0": {
        "parts": 6758,
        "points": 242890,
        "bbox": [85.11591396, -40.08278133, 95.74649375, -32.83007115],
    },
    "phase2-dhj-l0": {
        "parts": 4,
        "points": 52,
        "bbox": [88.6800112, -37.89959829, 95.37573454, -33.03721718],
    },
    "phase2-gophoenix-l0": {
        "parts": 1,
        "points": 5,
        "bbox": [92.71456679, -35.28258753, 95.85067497, -32.71210312],
    },
}
DISPLAY_TOLERANCE_DEGREES = 0.006
DISPLAY_MIN_SPAN_DEGREES = 0.01
ATLAS_BBOX = [82.0, -42.0, 106.5, -19.0]
TILE_SIZE_KM = 25.0
PLANNING_BUDGET_KM2 = 7500.0
KDE_BANDWIDTH_KM = 35.0
KDE_RADIUS_SIGMA = 4.0
EARTH_RADIUS_KM = 6371.0088


class PackageError(RuntimeError):
    pass


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def pretty_json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def deterministic_gzip(data: bytes) -> bytes:
    output = io.BytesIO()
    with gzip.GzipFile(filename="", mode="wb", fileobj=output, compresslevel=9, mtime=0) as gz:
        gz.write(data)
    return output.getvalue()


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=180) as response, destination.open("wb") as out:
        shutil.copyfileobj(response, out, length=1024 * 1024)


def lock_sources() -> list[dict[str, Any]]:
    return read_json(LOCK_PATH)["sources"]


def source_content(record: dict[str, Any], downloaded: bytes) -> bytes:
    transformation = record.get("transformation", "none")
    if "canonical JSON" in transformation:
        value = json.loads(downloaded)
        if "remove volatile" in transformation:
            value.pop("timeStamp", None)
        return canonical_json_bytes(value)
    return downloaded


def verify_expected(record: dict[str, Any], content: bytes) -> None:
    actual_hash = sha256(content)
    actual_size = len(content)
    if actual_hash != record["content_sha256"] or actual_size != record["content_bytes"]:
        raise PackageError(
            f"source mismatch for {record['id']}: expected "
            f"{record['content_sha256']} / {record['content_bytes']} bytes, got "
            f"{actual_hash} / {actual_size} bytes"
        )


def acquire() -> None:
    bundled = [
        source
        for source in lock_sources()
        if source.get("bundled") and source.get("acquire_supported", True)
    ]
    staged: list[tuple[Path, Path]] = []
    with tempfile.TemporaryDirectory(prefix="mh370-coverage-", dir="/tmp") as scratch_name:
        scratch = Path(scratch_name)
        for source in bundled:
            raw_path = scratch / f"{source['id']}.download"
            print(f"fetch {source['id']}")
            download(source["url"], raw_path)
            content = source_content(source, raw_path.read_bytes())
            verify_expected(source, content)
            package_bytes = deterministic_gzip(content) if source["stored_path"].endswith(".gz") else content
            staged_path = scratch / f"{source['id']}.staged"
            staged_path.write_bytes(package_bytes)
            staged.append((staged_path, ROOT / source["stored_path"]))

        for staged_path, destination in staged:
            destination.parent.mkdir(parents=True, exist_ok=True)
            temporary_destination = destination.with_suffix(destination.suffix + ".new")
            shutil.copyfile(staged_path, temporary_destination)
            temporary_destination.replace(destination)
            print(f"pinned {destination.relative_to(ROOT)}")


def verify_references() -> None:
    stable = [
        source
        for source in lock_sources()
        if not source.get("bundled")
        and (source.get("retrieval_url") or source["id"] == "mot-malaysia-2026-update")
    ]
    with tempfile.TemporaryDirectory(prefix="mh370-reference-", dir="/tmp") as scratch_name:
        scratch = Path(scratch_name)
        for source in stable:
            destination = scratch / source["id"]
            print(f"fetch {source['id']}")
            retrieval_url = source["retrieval_url"] if "retrieval_url" in source else source["url"]
            download(retrieval_url, destination)
            content = destination.read_bytes()
            verify_expected(source, content)
            print(f"verified {source['content_sha256']}  {len(content)} bytes")


def read_stored_content(record: dict[str, Any]) -> bytes:
    path = ROOT / record["stored_path"]
    if not path.exists():
        raise PackageError(f"missing pinned source: {path.relative_to(ROOT)}")
    return gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()


def iter_rings(geometry: dict[str, Any]) -> Iterable[list[list[float]]]:
    if geometry["type"] == "Polygon":
        yield from geometry["coordinates"]
    elif geometry["type"] == "MultiPolygon":
        for polygon in geometry["coordinates"]:
            yield from polygon
    else:
        raise PackageError(f"unsupported geometry type: {geometry['type']}")


def geometry_metrics(geometry: dict[str, Any]) -> dict[str, Any]:
    points = 0
    parts = 0
    bounds = [math.inf, math.inf, -math.inf, -math.inf]
    coordinates = geometry["coordinates"]
    polygons = [coordinates] if geometry["type"] == "Polygon" else coordinates
    for polygon in polygons:
        parts += 1
        for ring in polygon:
            if len(ring) < 4 or ring[0] != ring[-1]:
                raise PackageError("polygon ring is not closed or has fewer than four points")
            for point in ring:
                if len(point) < 2:
                    raise PackageError("coordinate has fewer than two ordinates")
                lon, lat = point[:2]
                if not (-180 <= lon <= 180 and -90 <= lat <= 90):
                    raise PackageError(f"coordinate outside longitude/latitude bounds: {point}")
                bounds[0] = min(bounds[0], lon)
                bounds[1] = min(bounds[1], lat)
                bounds[2] = max(bounds[2], lon)
                bounds[3] = max(bounds[3], lat)
                points += 1
    return {"parts": parts, "points": points, "bbox": bounds}


def close_ring(ring: list[list[float]]) -> list[list[float]]:
    return ring if ring and ring[0] == ring[-1] else ring + [ring[0]]


def spherical_ring_area_km2(ring: list[list[float]]) -> float:
    """Signed Chamberlain-Duquette area on a spherical Earth."""
    closed = close_ring(ring)
    accumulator = 0.0
    for (longitude_1, latitude_1), (longitude_2, latitude_2) in zip(
        closed, closed[1:]
    ):
        delta_longitude = math.radians(longitude_2 - longitude_1)
        if delta_longitude > math.pi:
            delta_longitude -= 2 * math.pi
        elif delta_longitude < -math.pi:
            delta_longitude += 2 * math.pi
        accumulator += delta_longitude * (
            2
            + math.sin(math.radians(latitude_1))
            + math.sin(math.radians(latitude_2))
        )
    return -0.5 * EARTH_RADIUS_KM**2 * accumulator


def geometry_area_km2(geometry: dict[str, Any]) -> float:
    polygons = (
        [geometry["coordinates"]]
        if geometry["type"] == "Polygon"
        else geometry["coordinates"]
    )
    return sum(
        abs(sum(spherical_ring_area_km2(ring) for ring in polygon))
        for polygon in polygons
    )


def point_in_ring(longitude: float, latitude: float, ring: list[list[float]]) -> bool:
    inside = False
    previous_longitude, previous_latitude = ring[-1][:2]
    for current in ring:
        current_longitude, current_latitude = current[:2]
        if (current_latitude > latitude) != (previous_latitude > latitude):
            longitude_at_latitude = (
                (previous_longitude - current_longitude)
                * (latitude - current_latitude)
                / (previous_latitude - current_latitude)
                + current_longitude
            )
            if longitude < longitude_at_latitude:
                inside = not inside
        previous_longitude, previous_latitude = current_longitude, current_latitude
    return inside


def point_in_geometry(longitude: float, latitude: float, geometry: dict[str, Any]) -> bool:
    polygons = (
        [geometry["coordinates"]]
        if geometry["type"] == "Polygon"
        else geometry["coordinates"]
    )
    for polygon in polygons:
        if point_in_ring(longitude, latitude, polygon[0]) and not any(
            point_in_ring(longitude, latitude, hole) for hole in polygon[1:]
        ):
            return True
    return False


def haversine_km(
    latitude_1: float, longitude_1: float, latitude_2: float, longitude_2: float
) -> float:
    latitude_1_radians = math.radians(latitude_1)
    latitude_2_radians = math.radians(latitude_2)
    delta_latitude = latitude_2_radians - latitude_1_radians
    delta_longitude = math.radians(longitude_2 - longitude_1)
    haversine = (
        math.sin(delta_latitude / 2) ** 2
        + math.cos(latitude_1_radians)
        * math.cos(latitude_2_radians)
        * math.sin(delta_longitude / 2) ** 2
    )
    return 2 * EARTH_RADIUS_KM * math.asin(min(1.0, math.sqrt(haversine)))


def iter_line_strings(geometry: dict[str, Any]) -> Iterable[list[list[float]]]:
    if geometry["type"] == "LineString":
        yield geometry["coordinates"]
    elif geometry["type"] == "MultiLineString":
        yield from geometry["coordinates"]
    elif geometry["type"] in ("Polygon", "MultiPolygon"):
        yield from iter_rings(geometry)
    else:
        raise PackageError(f"unsupported display geometry: {geometry['type']}")


def point_segment_distance_squared(point: list[float], start: list[float], end: list[float]) -> float:
    x, y = start[:2]
    dx = end[0] - x
    dy = end[1] - y
    if dx or dy:
        t = ((point[0] - x) * dx + (point[1] - y) * dy) / (dx * dx + dy * dy)
        if t > 1:
            x, y = end[:2]
        elif t > 0:
            x += dx * t
            y += dy * t
    dx = point[0] - x
    dy = point[1] - y
    return dx * dx + dy * dy


def douglas_peucker(points: list[list[float]], tolerance: float) -> list[list[float]]:
    if len(points) <= 2:
        return points
    threshold = tolerance * tolerance
    maximum = threshold
    index = 0
    for candidate in range(1, len(points) - 1):
        distance = point_segment_distance_squared(points[candidate], points[0], points[-1])
        if distance > maximum:
            maximum = distance
            index = candidate
    if index:
        left = douglas_peucker(points[: index + 1], tolerance)
        right = douglas_peucker(points[index:], tolerance)
        return left[:-1] + right
    return [points[0], points[-1]]


def simplify_ring(ring: list[list[float]], tolerance: float) -> list[list[float]]:
    points = ring[:-1]
    if len(points) <= 3:
        simplified = points
    else:
        anchor_index = min(range(len(points)), key=lambda index: (points[index][0], points[index][1]))
        rotated = points[anchor_index:] + points[:anchor_index]
        farthest_index = max(
            range(1, len(rotated)),
            key=lambda index: (
                (rotated[index][0] - rotated[0][0]) ** 2
                + (rotated[index][1] - rotated[0][1]) ** 2
            ),
        )
        first = douglas_peucker(rotated[: farthest_index + 1], tolerance)
        second = douglas_peucker(rotated[farthest_index:] + [rotated[0]], tolerance)
        simplified = first[:-1] + second[:-1]
        if len(simplified) < 3:
            simplified = points
    rounded = [[round(point[0], 5), round(point[1], 5)] for point in simplified]
    rounded.append(rounded[0])
    return rounded


def ring_span(ring: list[list[float]]) -> float:
    longitudes = [point[0] for point in ring]
    latitudes = [point[1] for point in ring]
    return max(max(longitudes) - min(longitudes), max(latitudes) - min(latitudes))


def cartographic_geometry(
    geometry: dict[str, Any], tolerance: float, minimum_span: float
) -> tuple[dict[str, Any], dict[str, int]]:
    if geometry["type"] not in ("Polygon", "MultiPolygon"):
        raise PackageError(f"unsupported geometry type: {geometry['type']}")
    source_polygons = [geometry["coordinates"]] if geometry["type"] == "Polygon" else geometry["coordinates"]
    kept_polygons: list[list[list[list[float]]]] = []
    omitted_polygons = 0
    omitted_holes = 0
    for polygon in source_polygons:
        if geometry["type"] == "MultiPolygon" and ring_span(polygon[0]) < minimum_span:
            omitted_polygons += 1
            omitted_holes += max(0, len(polygon) - 1)
            continue
        kept_rings = [polygon[0]]
        for hole in polygon[1:]:
            if ring_span(hole) >= minimum_span:
                kept_rings.append(hole)
            else:
                omitted_holes += 1
        kept_polygons.append(kept_rings)
    simplified = [
        [simplify_ring(ring, tolerance) for ring in polygon] for polygon in kept_polygons
    ]
    coordinates: Any = simplified[0] if geometry["type"] == "Polygon" else simplified
    return (
        {"type": geometry["type"], "coordinates": coordinates},
        {
            "source_polygons": len(source_polygons),
            "display_polygons": len(kept_polygons),
            "omitted_subpixel_polygons": omitted_polygons,
            "source_holes": sum(max(0, len(polygon) - 1) for polygon in source_polygons),
            "display_holes": sum(max(0, len(polygon) - 1) for polygon in kept_polygons),
            "omitted_subpixel_holes": omitted_holes,
        },
    )


def source_by_id(identifier: str) -> dict[str, Any]:
    for source in lock_sources():
        if source["id"] == identifier:
            return source
    raise PackageError(f"source not in lock: {identifier}")


def load_source_geojson(identifier: str) -> dict[str, Any]:
    source = source_by_id(identifier)
    content = read_stored_content(source)
    verify_expected(source, content)
    return json.loads(content)


def build_display_geometry() -> dict[str, Any]:
    register = read_json(ROOT / "data" / "evidence-register.json")
    register_by_id = {record["id"]: record for record in register["records"]}
    layers = [
        ("phase2-deep-tow-l0", "atsb-phase2-deep-tow-l0", "Deep Tow — detailed L0 data footprint"),
        ("phase2-dhj-l0", "atsb-phase2-dong-hai-jiu-101-l0", "Dong Hai Jiu — coarse L0 catalog footprint"),
        ("phase2-gophoenix-l0", "atsb-phase2-go-phoenix-l0", "GO Phoenix — catalog bounding rectangle"),
    ]
    features: list[dict[str, Any]] = []
    source_bounds = [math.inf, math.inf, -math.inf, -math.inf]
    source_metrics: dict[str, Any] = {}
    display_reduction: dict[str, Any] = {}
    display_points = 0
    for source_id, evidence_id, label in layers:
        collection = load_source_geojson(source_id)
        if len(collection.get("features", [])) != 1:
            raise PackageError(f"expected one feature in {source_id}")
        source_geometry = collection["features"][0]["geometry"]
        metrics = geometry_metrics(source_geometry)
        source_metrics[source_id] = metrics
        for index, value in enumerate(metrics["bbox"]):
            if index < 2:
                source_bounds[index] = min(source_bounds[index], value)
            else:
                source_bounds[index] = max(source_bounds[index], value)
        display_geometry, reduction = cartographic_geometry(
            source_geometry, DISPLAY_TOLERANCE_DEGREES, DISPLAY_MIN_SPAN_DEGREES
        )
        display_reduction[source_id] = reduction
        display_points += geometry_metrics(display_geometry)["points"]
        evidence = register_by_id[evidence_id]
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": source_id,
                    "label": label,
                    "geometry_class": evidence["geometry_class"],
                    "source_path": evidence["geometry"],
                    "source_content_sha256": source_by_id(source_id)["content_sha256"],
                    "source_catalog_area_km2": evidence["source_catalog_area_km2"],
                    "display_only": True,
                    "negative_search_eligible": False,
                },
                "geometry": display_geometry,
            }
        )
    result = {
        "type": "FeatureCollection",
        "metadata": {
            "purpose": "browser display only",
            "analysis_eligible": False,
            "source_geometry_modified": True,
            "operation": "omit subpixel polygon parts/holes by bounding-box span, then topology-unaware Douglas-Peucker simplification and coordinate rounding",
            "tolerance_degrees": DISPLAY_TOLERANCE_DEGREES,
            "minimum_retained_bbox_span_degrees": DISPLAY_MIN_SPAN_DEGREES,
            "coordinate_precision_degrees": 0.00001,
            "crs": "OGC:CRS84 longitude/latitude display convention",
            "source_bbox": source_bounds,
            "source_metrics": source_metrics,
            "display_reduction": display_reduction,
            "display_point_count": display_points,
            "warning": "Never use this derivative for area, overlap, elimination, or likelihood calculations.",
        },
        "features": features,
    }
    destination = ROOT / "data" / "map" / "phase2-display.geojson"
    destination.write_bytes(canonical_json_bytes(result))
    return result


def feature_collection(identifier: str) -> dict[str, Any]:
    collection = load_source_geojson(identifier)
    if collection.get("type") != "FeatureCollection":
        raise PackageError(f"source is not a FeatureCollection: {identifier}")
    return collection


def build_atlas_data(phase2_display: dict[str, Any]) -> dict[str, Any]:
    features: list[dict[str, Any]] = []
    phase2_layers = {
        "phase2-deep-tow-l0": "phase2_deep",
        "phase2-dhj-l0": "phase2_coarse",
        "phase2-gophoenix-l0": "phase2_extent",
    }
    for feature in phase2_display["features"]:
        copied = json.loads(json.dumps(feature))
        copied["properties"]["atlas_layer"] = phase2_layers[
            copied["properties"]["id"]
        ]
        features.append(copied)

    for index, feature in enumerate(
        feature_collection("bluefin-21-area-searched-2014")["features"], 1
    ):
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "id": f"bluefin-21-display-{index}",
                    "label": "Bluefin-21 official display footprint",
                    "atlas_layer": "bluefin",
                    "source_grade": "A",
                    "negative_search_eligible": False,
                },
                "geometry": feature["geometry"],
            }
        )

    outline_collection = read_json(
        ROOT / "data" / "context" / "approximate-ocean-infinity-outlines.geojson"
    )
    outline_layers = {
        "oi2018_total_outline_approx": "oi2018_proxy",
        "oi2024_proposed_outboard_southeast": "oi2024_outboard_proxy",
        "oi2024_proposed_inboard_northwest": "oi2024_inboard_proxy",
    }
    for feature in outline_collection["features"]:
        copied = json.loads(json.dumps(feature))
        for inherited_field in (
            "inference",
            "model_role",
            "nominal_uniform_coverage_fraction",
            "remaining_likelihood",
            "status",
        ):
            copied["properties"].pop(inherited_field, None)
        copied["properties"]["atlas_layer"] = outline_layers[
            copied["properties"]["id"]
        ]
        copied["properties"]["atlas_role"] = (
            "grade-C planning context only; no likelihood or binary exclusion"
        )
        copied["properties"]["negative_search_eligible"] = False
        features.append(copied)

    for identifier, layer, label in (
        ("seventh-arc-fl400", "seventh_arc", "Official seventh arc at FL400"),
        (
            "initial-100nm-wide-area",
            "wide_area_context",
            "Official historical ±100 NM planning envelope",
        ),
    ):
        for feature in feature_collection(identifier)["features"]:
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "id": identifier,
                        "label": label,
                        "atlas_layer": layer,
                        "source_grade": "A",
                        "negative_search_eligible": False,
                    },
                    "geometry": feature["geometry"],
                }
            )

    tracks = read_json(ROOT / "data" / "context" / "oi-vessel-track-proxies.geojson")
    for index, feature in enumerate(tracks["features"], 1):
        copied = json.loads(json.dumps(feature))
        copied["properties"]["id"] = f"oi-vessel-track-proxy-{index}"
        copied["properties"]["atlas_layer"] = "ais_proxy"
        copied["properties"]["negative_search_eligible"] = False
        features.append(copied)

    atlas = {
        "type": "FeatureCollection",
        "metadata": {
            "schema_version": 1,
            "purpose": "publication atlas and planning context",
            "analysis_eligible": False,
            "negative_search_eligible": False,
            "bbox": ATLAS_BBOX,
            "warning": "Official display footprints, approximate outlines, and AIS tracks have different semantics. None is a calibrated negative-search likelihood.",
        },
        "features": features,
    }
    (ROOT / "data" / "map" / "search-evidence-atlas.geojson").write_bytes(
        canonical_json_bytes(atlas)
    )
    return atlas


def build_area_inventory() -> dict[str, Any]:
    evidence = read_json(ROOT / "data" / "evidence-register.json")
    records = {record["id"]: record for record in evidence["records"]}
    bluefin = feature_collection("bluefin-21-area-searched-2014")
    bluefin_display_area = sum(
        geometry_area_km2(feature["geometry"]) for feature in bluefin["features"]
    )
    outlines = read_json(
        ROOT / "data" / "context" / "approximate-ocean-infinity-outlines.geojson"
    )
    outline_areas = {
        feature["properties"]["id"]: geometry_area_km2(feature["geometry"])
        for feature in outlines["features"]
    }
    inventory = {
        "schema_version": 1,
        "snapshot_date": "2026-08-31",
        "area_rule": "Reported totals, source catalog attributes, and context-outline areas are different quantities and must not be summed.",
        "rows": [
            {
                "id": "phase2-deep-tow",
                "plotted_geometry": "official detailed L0 data footprint",
                "plotted_area_semantics": "source catalog attribute",
                "plotted_or_catalog_area_km2": records["atsb-phase2-deep-tow-l0"][
                    "source_catalog_area_km2"
                ],
                "reported_but_unplotted_km2": None,
                "source_grade": "A",
            },
            {
                "id": "phase2-dong-hai-jiu",
                "plotted_geometry": "official coarse L0 catalog footprint",
                "plotted_area_semantics": "source catalog attribute",
                "plotted_or_catalog_area_km2": records[
                    "atsb-phase2-dong-hai-jiu-101-l0"
                ]["source_catalog_area_km2"],
                "reported_but_unplotted_km2": None,
                "source_grade": "A",
            },
            {
                "id": "phase2-go-phoenix",
                "plotted_geometry": "official catalog bounding rectangle",
                "plotted_area_semantics": "source catalog attribute",
                "plotted_or_catalog_area_km2": records["atsb-phase2-go-phoenix-l0"][
                    "source_catalog_area_km2"
                ],
                "reported_but_unplotted_km2": None,
                "source_grade": "A",
            },
            {
                "id": "bluefin-artemis-2014",
                "plotted_geometry": "two official application display polygons",
                "plotted_area_semantics": "spherical area of display polygons",
                "plotted_or_catalog_area_km2": round(bluefin_display_area, 6),
                "reported_area_km2": 860,
                "reported_minus_display_km2": round(860 - bluefin_display_area, 6),
                "reported_but_unplotted_km2": round(860 - bluefin_display_area, 6),
                "source_grade": "A for display polygons and total; swaths unresolved",
            },
            {
                "id": "ocean-infinity-2018",
                "plotted_geometry": "approximate context outline only",
                "plotted_area_semantics": "outline support, not covered area",
                "plotted_or_catalog_area_km2": round(
                    outline_areas["oi2018_total_outline_approx"], 1
                ),
                "reported_area_km2": {"lower_bound": 112000, "later_context": 120000},
                "reported_but_unplotted_km2": {
                    "operator_lower_bound": 112000,
                    "later_dataset_context": 120000,
                },
                "unplotted_semantics": "No exact AUV swath geometry obtained; the two totals are contextual alternatives, not quantities to sum.",
                "source_grade": "A for totals; C for outline",
            },
            {
                "id": "ocean-infinity-2025-2026",
                "plotted_geometry": "two approximate proposal outlines plus AIS vessel tracks",
                "plotted_area_semantics": "proposal/context support, not surveyed area",
                "plotted_or_catalog_area_km2": round(
                    outline_areas["oi2024_proposed_outboard_southeast"]
                    + outline_areas["oi2024_proposed_inboard_northwest"],
                    1,
                ),
                "estimated_contract_area_km2": 15000,
                "reported_surveyed_area_km2": 7571,
                "derived_rounded_remainder_km2": 7429,
                "reported_but_unplotted_km2": 7571,
                "source_grade": "A for totals; C for outlines/tracks",
            },
        ],
        "rounding": {
            "expression": "15,000 - 7,571 = 7,429 km2",
            "warning": "15,000 is estimated and 7,571 is approximate; 7,429 is derived planning arithmetic, not an exact remainder polygon.",
        },
    }
    (ROOT / "data" / "area-inventory.json").write_bytes(pretty_json_bytes(inventory))
    return inventory


def plotting_modules() -> tuple[Any, Any, Any, Any, Any]:
    try:
        import matplotlib as mpl
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
        from matplotlib.patches import Patch, PathPatch
        from matplotlib.path import Path as PlotPath
    except ImportError as error:
        raise PackageError(
            "publication rendering requires Matplotlib; run with the repository "
            ".venv/bin/python or install the pinned development environment"
        ) from error
    mpl.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 8.5,
            "axes.titlesize": 11,
            "axes.labelsize": 9,
            "svg.hashsalt": "mh370-seabed-search-coverage-v0.1",
            "pdf.compression": 9,
            "savefig.facecolor": "white",
        }
    )
    return plt, Line2D, Patch, PathPatch, PlotPath


def polygon_plot_path(geometry: dict[str, Any], plot_path: Any) -> Any:
    paths = []
    polygons = (
        [geometry["coordinates"]]
        if geometry["type"] == "Polygon"
        else geometry["coordinates"]
    )
    for polygon in polygons:
        vertices: list[tuple[float, float]] = []
        codes: list[int] = []
        for ring in polygon:
            closed = close_ring(ring)
            vertices.extend((point[0], point[1]) for point in closed)
            codes.extend(
                [plot_path.MOVETO]
                + [plot_path.LINETO] * (len(closed) - 2)
                + [plot_path.CLOSEPOLY]
            )
        paths.append(plot_path(vertices, codes))
    return plot_path.make_compound_path(*paths)


def draw_polygon(
    axis: Any,
    geometry: dict[str, Any],
    path_patch: Any,
    plot_path: Any,
    *,
    facecolor: str,
    edgecolor: str,
    linewidth: float,
    alpha: float,
    linestyle: str = "-",
    zorder: int = 1,
) -> None:
    patch = path_patch(
        polygon_plot_path(geometry, plot_path),
        facecolor=facecolor,
        edgecolor=edgecolor,
        linewidth=linewidth,
        alpha=alpha,
        linestyle=linestyle,
        zorder=zorder,
    )
    axis.add_patch(patch)


def draw_lines(
    axis: Any,
    geometry: dict[str, Any],
    *,
    color: str,
    linewidth: float,
    alpha: float = 1.0,
    linestyle: str = "-",
    zorder: int = 5,
) -> None:
    for line in iter_line_strings(geometry):
        axis.plot(
            [point[0] for point in line],
            [point[1] for point in line],
            color=color,
            linewidth=linewidth,
            alpha=alpha,
            linestyle=linestyle,
            zorder=zorder,
        )


def configure_map_axis(axis: Any) -> None:
    minimum_longitude, minimum_latitude, maximum_longitude, maximum_latitude = ATLAS_BBOX
    axis.set_xlim(minimum_longitude, maximum_longitude)
    axis.set_ylim(minimum_latitude, maximum_latitude)
    axis.set_aspect(1 / math.cos(math.radians(-31.5)))
    axis.set_xlabel("Longitude (°E)")
    axis.set_ylabel("Latitude (°)")
    axis.set_xticks(range(84, 107, 2))
    axis.set_yticks(range(-42, -18, 2))
    axis.grid(color="#cbd5e1", linewidth=0.45, alpha=0.65, zorder=0)
    for spine in axis.spines.values():
        spine.set_color("#64748b")
        spine.set_linewidth(0.7)


def draw_atlas_layers(axis: Any, atlas: dict[str, Any]) -> None:
    _, _, _, path_patch, plot_path = plotting_modules()
    polygon_styles = {
        "wide_area_context": ("none", "#94a3b8", 0.8, 0.8, "--", 1),
        "oi2018_proxy": ("#cbd5e1", "#64748b", 0.9, 0.24, "--", 2),
        "oi2024_outboard_proxy": ("#93c5fd", "#2563eb", 1.0, 0.34, "--", 3),
        "oi2024_inboard_proxy": ("#fde68a", "#d97706", 1.0, 0.40, "--", 3),
        "phase2_deep": ("#99f6e4", "#0f766e", 0.55, 0.42, "-", 4),
        "phase2_coarse": ("#a7f3d0", "#047857", 0.85, 0.30, "-", 4),
        "phase2_extent": ("#d1fae5", "#065f46", 0.85, 0.24, "-", 4),
        "bluefin": ("#c4b5fd", "#6d28d9", 1.0, 0.62, "-", 5),
    }
    line_styles = {
        "seventh_arc": ("#111827", 1.35, 1.0, "-", 7),
        "ais_proxy": ("#dc2626", 0.65, 0.62, ":", 6),
    }
    for feature in atlas["features"]:
        layer = feature["properties"]["atlas_layer"]
        geometry = feature["geometry"]
        if layer in polygon_styles:
            face, edge, width, alpha, linestyle, zorder = polygon_styles[layer]
            draw_polygon(
                axis,
                geometry,
                path_patch,
                plot_path,
                facecolor=face,
                edgecolor=edge,
                linewidth=width,
                alpha=alpha,
                linestyle=linestyle,
                zorder=zorder,
            )
        elif layer in line_styles:
            color, width, alpha, linestyle, zorder = line_styles[layer]
            draw_lines(
                axis,
                geometry,
                color=color,
                linewidth=width,
                alpha=alpha,
                linestyle=linestyle,
                zorder=zorder,
            )


def publication_metadata(format_name: str) -> dict[str, Any]:
    fixed_time = dt.datetime(2026, 8, 31, tzinfo=dt.timezone.utc)
    if format_name == "pdf":
        return {
            "Title": "MH370 seabed-search evidence atlas",
            "Author": "MH370 Bayesian estimator project",
            "Subject": "Evidence-graded searched-area context",
            "Keywords": "MH370, seabed search, evidence atlas",
            "Creator": "mh370-seabed-search-coverage/code/build.py",
            "CreationDate": fixed_time,
            "ModDate": fixed_time,
        }
    if format_name == "svg":
        return {"Title": "MH370 seabed-search evidence atlas", "Date": "2026-08-31"}
    return {"Software": "mh370-seabed-search-coverage/code/build.py"}


def save_figure_set(figure: Any, stem: Path) -> None:
    stem.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(
        stem.with_suffix(".svg"),
        format="svg",
        bbox_inches=None,
        metadata=publication_metadata("svg"),
    )
    figure.savefig(
        stem.with_suffix(".pdf"),
        format="pdf",
        bbox_inches=None,
        metadata=publication_metadata("pdf"),
    )
    figure.savefig(
        stem.with_suffix(".png"),
        format="png",
        dpi=240,
        bbox_inches=None,
        metadata=publication_metadata("png"),
    )


def embedded_svg(path: Path) -> str:
    svg = path.read_text(encoding="utf-8")
    start = svg.find("<svg")
    if start < 0:
        raise PackageError(f"generated SVG is invalid: {path.relative_to(ROOT)}")
    return svg[start:]


def display_inventory_value(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:,.3f}".rstrip("0").rstrip(".")
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, dict) and {
        "operator_lower_bound",
        "later_dataset_context",
    }.issubset(value):
        return (
            f">{value['operator_lower_bound']:,}; "
            f"{value['later_dataset_context']:,} later context"
        )
    return str(value)


def build_evidence_atlas(atlas: dict[str, Any], inventory: dict[str, Any]) -> None:
    plt, line_2d, patch, _, _ = plotting_modules()
    figure = plt.figure(figsize=(14.2, 8.6), constrained_layout=False)
    grid = figure.add_gridspec(
        1, 2, width_ratios=[2.28, 1], left=0.055, right=0.975, top=0.86, bottom=0.115, wspace=0.12
    )
    axis = figure.add_subplot(grid[0, 0])
    side = figure.add_subplot(grid[0, 1])
    side.axis("off")
    configure_map_axis(axis)
    draw_atlas_layers(axis, atlas)
    axis.set_title("Spatial evidence classes", loc="left", fontweight="bold", pad=8)

    scale_latitude = -40.8
    scale_start = 83.4
    scale_degrees = 500 / (111.32 * math.cos(math.radians(scale_latitude)))
    axis.plot(
        [scale_start, scale_start + scale_degrees],
        [scale_latitude, scale_latitude],
        color="#111827",
        linewidth=2.0,
        zorder=10,
    )
    axis.text(
        scale_start + scale_degrees / 2,
        scale_latitude + 0.28,
        "500 km",
        ha="center",
        va="bottom",
        fontsize=7.5,
        color="#111827",
    )
    axis.annotate(
        "N",
        xy=(105.5, -20.0),
        xytext=(105.5, -22.1),
        ha="center",
        va="center",
        fontsize=8,
        fontweight="bold",
        arrowprops={"arrowstyle": "-|>", "color": "#111827", "lw": 0.9},
    )
    axis.text(103.9, -21.55, "Bluefin\ndisplay polygons", fontsize=7, color="#5b21b6", ha="center")
    axis.text(96.0, -26.4, "OI 2018 approximate\ncontext outline", fontsize=7, color="#475569", ha="center")
    axis.text(91.8, -34.0, "March-2024 proposal\ncontext", fontsize=7, color="#1e40af", ha="center")

    legend = [
        patch(facecolor="#99f6e4", edgecolor="#0f766e", alpha=0.55, label="Official Phase-2 source geometry"),
        patch(facecolor="#c4b5fd", edgecolor="#6d28d9", alpha=0.70, label="Official Bluefin display polygons"),
        patch(facecolor="#cbd5e1", edgecolor="#64748b", alpha=0.40, label="Approx. OI2018 context (grade C)"),
        patch(facecolor="#93c5fd", edgecolor="#2563eb", alpha=0.45, label="Approx. renewed outboard band (C)"),
        patch(facecolor="#fde68a", edgecolor="#d97706", alpha=0.50, label="Approx. renewed inboard band (C)"),
        line_2d([0], [0], color="#111827", lw=1.4, label="Official seventh arc at FL400"),
        line_2d([0], [0], color="#dc2626", lw=0.8, ls=":", label="AIS surface-vessel proxy (C)"),
        line_2d([0], [0], color="#94a3b8", lw=0.9, ls="--", label="Official ±100 NM context"),
    ]
    axis.legend(
        handles=legend,
        loc="lower left",
        bbox_to_anchor=(0.005, 0.012),
        frameon=True,
        facecolor="white",
        edgecolor="#cbd5e1",
        framealpha=0.96,
        fontsize=7.1,
        ncol=2,
    )

    side.text(0, 0.98, "Area evidence", fontsize=13, fontweight="bold", va="top", color="#0f172a")
    side.text(
        0,
        0.925,
        "Mapped geometry and reported totals are shown\nseparately; overlapping catalog areas are not summed.",
        fontsize=8.2,
        va="top",
        color="#475569",
        linespacing=1.35,
    )
    blocks = [
        ("PHASE 2 · OFFICIAL", "Deep Tow 130,961 km² catalog\nDong Hai Jiu 46,884 km² catalog\nGO Phoenix 82,606 km² catalog\n(overlap and geometry semantics differ)"),
        ("BLUEFIN · OFFICIAL DISPLAY", "771.410 km² plotted polygons\n860 km² reported total\n88.590 km² not represented by display-area arithmetic\n(exact mission swaths unresolved)"),
        ("OCEAN INFINITY 2018", ">112,000 km² reported by contract end\n120,000 km² later dataset context\n148,993 km² approximate outline support\n(exact AUV swaths unplotted)"),
        ("OCEAN INFINITY 2025–2026", "15,000 km² estimated contract area\n7,571 km² approximately surveyed\n7,429 km² arithmetic remainder\n(exact surveyed and remainder polygons unplotted)"),
    ]
    y = 0.82
    for heading, body in blocks:
        side.text(0, y, heading, fontsize=8.2, fontweight="bold", va="top", color="#0f766e")
        side.text(0, y - 0.035, body, fontsize=7.7, va="top", color="#1f2937", linespacing=1.42)
        y -= 0.20
    side.text(
        0,
        0.035,
        "Interpretation: context supports planning sensitivity only.\n"
        "No searched/not-searched mask; no calibrated PoD.",
        fontsize=7.1,
        va="bottom",
        color="#991b1b",
        fontweight="bold",
        linespacing=1.35,
    )
    figure.suptitle(
        "MH370 seabed-search evidence atlas",
        x=0.055,
        y=0.965,
        ha="left",
        fontsize=19,
        fontweight="bold",
        color="#0f172a",
    )
    figure.text(
        0.055,
        0.91,
        "Official source geometry, reported-but-unplotted totals, and explicitly graded contextual reconstructions · snapshot 31 August 2026",
        fontsize=9.2,
        color="#475569",
    )
    figure.text(
        0.055,
        0.035,
        "No polygon in this atlas is used as binary negative evidence. Detailed sonar quality, holidays, overlap, exact OI AUV swaths, and calibrated target-specific probability of detection remain unresolved.",
        fontsize=7.4,
        color="#475569",
    )
    stem = ROOT / "outputs" / "evidence-atlas"
    save_figure_set(figure, stem)
    plt.close(figure)

    rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['id'])}</td>"
        f"<td>{html.escape(str(row['plotted_geometry']))}</td>"
        f"<td>{html.escape(display_inventory_value(row.get('plotted_or_catalog_area_km2')))}</td>"
        f"<td>{html.escape(display_inventory_value(row.get('reported_but_unplotted_km2')))}</td>"
        f"<td>{html.escape(str(row['source_grade']))}</td>"
        "</tr>"
        for row in inventory["rows"]
    )
    atlas_html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MH370 seabed-search evidence atlas</title><style>
body{{margin:0;background:#eef3f2;color:#17211f;font:15px/1.5 system-ui,sans-serif}}main{{max-width:1500px;margin:auto;padding:28px}}h1{{margin:0 0 5px;font-size:30px}}.note{{color:#526762}}.frame{{background:white;border:1px solid #c8d6d2;border-radius:10px;padding:10px;box-shadow:0 8px 25px #17322b18}}svg{{width:100%;height:auto}}table{{width:100%;border-collapse:collapse;background:white;margin-top:22px}}th,td{{padding:10px;border-bottom:1px solid #dbe5e2;text-align:left;vertical-align:top}}th{{font-size:11px;text-transform:uppercase;color:#526762}}.boundary{{margin-top:20px;padding:14px;border-left:4px solid #b45309;background:#fff7ed}}a{{color:#0f766e}}</style></head><body><main>
<h1>MH370 seabed-search evidence atlas</h1><p class="note">Self-contained publication view · exact artifact alternatives: <a href="evidence-atlas.svg">SVG</a> · <a href="evidence-atlas.pdf">PDF</a> · <a href="evidence-atlas.png">PNG</a></p>
<div class="frame">{embedded_svg(stem.with_suffix('.svg'))}</div>
<table><thead><tr><th>Evidence</th><th>Plotted geometry</th><th>Plotted/catalog km²</th><th>Reported but unplotted</th><th>Grade</th></tr></thead><tbody>{rows}</tbody></table>
<div class="boundary"><strong>Scientific boundary.</strong> Approximate OI outlines and AIS vessel tracks inform only a separately labelled planning sensitivity. They never downweight the impact posterior and are not binary evidence of target absence.</div>
</main></body></html>"""
    stem.with_suffix(".html").write_text(atlas_html, encoding="utf-8", newline="\n")


def read_weighted_particles(
    path: Path, weight_column: str, weight_mode: str
) -> list[dict[str, float | str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames or []
        required = {"latitude_deg", "longitude_deg", weight_column}
        if not required.issubset(fields):
            raise PackageError(
                f"particle CSV is missing {sorted(required - set(fields))}; fields={fields}"
            )
        particles: list[dict[str, float | str]] = []
        for row_number, row in enumerate(reader, 2):
            try:
                latitude = float(row["latitude_deg"])
                longitude = float(row["longitude_deg"])
                supplied_weight = float(row[weight_column])
            except (TypeError, ValueError) as error:
                raise PackageError(f"invalid numeric particle row {row_number}") from error
            if not all(math.isfinite(value) for value in (latitude, longitude)):
                raise PackageError(f"non-finite coordinate in particle row {row_number}")
            if weight_mode == "linear" and not math.isfinite(supplied_weight):
                raise PackageError(f"non-finite linear weight in particle row {row_number}")
            if weight_mode == "log" and (
                math.isnan(supplied_weight) or supplied_weight == math.inf
            ):
                raise PackageError(f"invalid log weight in particle row {row_number}")
            if not -90 <= latitude <= 90 or not -180 <= longitude < 180:
                raise PackageError(f"non-canonical coordinate in particle row {row_number}")
            if weight_mode == "linear" and supplied_weight < 0:
                raise PackageError(f"negative linear weight in particle row {row_number}")
            particles.append(
                {
                    "id": row.get("particle_id") or row.get("source_run_id") or str(row_number - 1),
                    "latitude_deg": latitude,
                    "longitude_deg": longitude,
                    "supplied_weight": supplied_weight,
                }
            )
    if not particles:
        raise PackageError("particle CSV contains no data rows")
    if weight_mode == "log":
        maximum = max(float(particle["supplied_weight"]) for particle in particles)
        if maximum == -math.inf:
            raise PackageError("log weights have no positive finite support")
        linear = [
            math.exp(float(particle["supplied_weight"]) - maximum)
            for particle in particles
        ]
    else:
        linear = [float(particle["supplied_weight"]) for particle in particles]
    total = math.fsum(linear)
    if not math.isfinite(total) or total <= 0:
        raise PackageError("particle weights have no positive finite total")
    for particle, weight in zip(particles, linear):
        particle["weight"] = weight / total
    return particles


def local_projection(
    particles: list[dict[str, float | str]],
) -> tuple[float, float, list[dict[str, float | str]]]:
    latitude_origin = math.fsum(
        float(particle["latitude_deg"]) * float(particle["weight"])
        for particle in particles
    )
    longitude_values = [float(particle["longitude_deg"]) for particle in particles]
    if max(longitude_values) - min(longitude_values) >= 180:
        raise PackageError("planner does not support a particle set spanning the antimeridian")
    longitude_origin = math.fsum(
        float(particle["longitude_deg"]) * float(particle["weight"])
        for particle in particles
    )
    cosine = math.cos(math.radians(latitude_origin))
    if cosine <= 0:
        raise PackageError("local projection is undefined at a pole")
    projected = []
    for particle in particles:
        copied = dict(particle)
        copied["x_km"] = (
            EARTH_RADIUS_KM
            * cosine
            * math.radians(float(particle["longitude_deg"]) - longitude_origin)
        )
        copied["y_km"] = EARTH_RADIUS_KM * math.radians(
            float(particle["latitude_deg"]) - latitude_origin
        )
        projected.append(copied)
    return latitude_origin, longitude_origin, projected


def inverse_local(
    x_km: float, y_km: float, latitude_origin: float, longitude_origin: float
) -> tuple[float, float]:
    latitude = latitude_origin + math.degrees(y_km / EARTH_RADIUS_KM)
    longitude = longitude_origin + math.degrees(
        x_km / (EARTH_RADIUS_KM * math.cos(math.radians(latitude_origin)))
    )
    return latitude, longitude


def prepared_polygons(geometry: dict[str, Any]) -> list[tuple[list[float], list[list[list[float]]]]]:
    polygons = (
        [geometry["coordinates"]]
        if geometry["type"] == "Polygon"
        else geometry["coordinates"]
    )
    result = []
    for polygon in polygons:
        longitudes = [point[0] for ring in polygon for point in ring]
        latitudes = [point[1] for ring in polygon for point in ring]
        result.append(
            ([min(longitudes), min(latitudes), max(longitudes), max(latitudes)], polygon)
        )
    return result


def point_in_prepared(
    longitude: float,
    latitude: float,
    prepared: list[tuple[list[float], list[list[list[float]]]]],
) -> bool:
    for bounds, polygon in prepared:
        if not (
            bounds[0] <= longitude <= bounds[2]
            and bounds[1] <= latitude <= bounds[3]
        ):
            continue
        if point_in_ring(longitude, latitude, polygon[0]) and not any(
            point_in_ring(longitude, latitude, hole) for hole in polygon[1:]
        ):
            return True
    return False


def point_to_track_distance_km(
    latitude: float, longitude: float, track_points: list[tuple[float, float]]
) -> float:
    return min(
        haversine_km(latitude, longitude, track_latitude, track_longitude)
        for track_longitude, track_latitude in track_points
    )


def planning_context() -> dict[str, Any]:
    phase2 = feature_collection("phase2-deep-tow-l0")["features"][0]["geometry"]
    bluefin = feature_collection("bluefin-21-area-searched-2014")
    outlines = read_json(
        ROOT / "data" / "context" / "approximate-ocean-infinity-outlines.geojson"
    )
    outline_by_id = {
        feature["properties"]["id"]: feature["geometry"]
        for feature in outlines["features"]
    }
    tracks = read_json(ROOT / "data" / "context" / "oi-vessel-track-proxies.geojson")
    track_points = [
        (point[0], point[1])
        for feature in tracks["features"]
        for point in feature["geometry"]["coordinates"]
    ]
    return {
        "phase2": prepared_polygons(phase2),
        "bluefin": [
            prepared
            for feature in bluefin["features"]
            for prepared in prepared_polygons(feature["geometry"])
        ],
        "oi2018": prepared_polygons(outline_by_id["oi2018_total_outline_approx"]),
        "oi2024_outboard": prepared_polygons(
            outline_by_id["oi2024_proposed_outboard_southeast"]
        ),
        "oi2024_inboard": prepared_polygons(
            outline_by_id["oi2024_proposed_inboard_northwest"]
        ),
        "track_points": track_points,
    }


def context_for_tile(
    latitude: float, longitude: float, context: dict[str, Any]
) -> dict[str, Any]:
    flags = {
        "inside_official_phase2_source_footprint": point_in_prepared(
            longitude, latitude, context["phase2"]
        ),
        "inside_official_bluefin_display_support": point_in_prepared(
            longitude, latitude, context["bluefin"]
        ),
        "inside_approximate_oi2018_outline": point_in_prepared(
            longitude, latitude, context["oi2018"]
        ),
        "inside_approximate_oi2024_outboard": point_in_prepared(
            longitude, latitude, context["oi2024_outboard"]
        ),
        "inside_approximate_oi2024_inboard": point_in_prepared(
            longitude, latitude, context["oi2024_inboard"]
        ),
    }
    nearest_track = point_to_track_distance_km(
        latitude, longitude, context["track_points"]
    )
    multiplier = 1.0
    if flags["inside_official_phase2_source_footprint"]:
        multiplier *= 0.72
    if flags["inside_official_bluefin_display_support"]:
        multiplier *= 0.75
    if flags["inside_approximate_oi2018_outline"]:
        multiplier *= 0.82
    if flags["inside_approximate_oi2024_outboard"]:
        multiplier *= 0.88
    if flags["inside_approximate_oi2024_inboard"]:
        multiplier *= 1.05
    if nearest_track <= TILE_SIZE_KM:
        multiplier *= 0.95
    multiplier = min(1.10, max(0.50, multiplier))
    return {
        **flags,
        "nearest_ais_surface_vessel_track_km": nearest_track,
        "declared_opportunity_multiplier": multiplier,
    }


def tile_grid(
    particles: list[dict[str, float | str]],
    latitude_origin: float,
    longitude_origin: float,
) -> list[dict[str, Any]]:
    margin = KDE_BANDWIDTH_KM * KDE_RADIUS_SIGMA
    minimum_x = math.floor(
        (min(float(particle["x_km"]) for particle in particles) - margin)
        / TILE_SIZE_KM
    ) * TILE_SIZE_KM
    maximum_x = math.ceil(
        (max(float(particle["x_km"]) for particle in particles) + margin)
        / TILE_SIZE_KM
    ) * TILE_SIZE_KM
    minimum_y = math.floor(
        (min(float(particle["y_km"]) for particle in particles) - margin)
        / TILE_SIZE_KM
    ) * TILE_SIZE_KM
    maximum_y = math.ceil(
        (max(float(particle["y_km"]) for particle in particles) + margin)
        / TILE_SIZE_KM
    ) * TILE_SIZE_KM
    count_x = int(round((maximum_x - minimum_x) / TILE_SIZE_KM))
    count_y = int(round((maximum_y - minimum_y) / TILE_SIZE_KM))
    if count_x <= 0 or count_y <= 0 or count_x * count_y > 50000:
        raise PackageError(
            f"planning grid is unreasonable: {count_x} by {count_y} tiles"
        )

    particle_bins: dict[tuple[int, int], list[dict[str, float | str]]] = {}
    for particle in particles:
        index_x = int(
            math.floor((float(particle["x_km"]) - minimum_x) / TILE_SIZE_KM)
        )
        index_y = int(
            math.floor((float(particle["y_km"]) - minimum_y) / TILE_SIZE_KM)
        )
        particle_bins.setdefault((index_x, index_y), []).append(particle)

    neighbor_radius = math.ceil(KDE_RADIUS_SIGMA * KDE_BANDWIDTH_KM / TILE_SIZE_KM)
    maximum_distance_squared = (KDE_RADIUS_SIGMA * KDE_BANDWIDTH_KM) ** 2
    context = planning_context()
    tiles = []
    raw_total = 0.0
    for index_y in range(count_y):
        center_y = minimum_y + (index_y + 0.5) * TILE_SIZE_KM
        for index_x in range(count_x):
            center_x = minimum_x + (index_x + 0.5) * TILE_SIZE_KM
            raw_density = 0.0
            for neighbor_y in range(
                max(0, index_y - neighbor_radius),
                min(count_y, index_y + neighbor_radius + 1),
            ):
                for neighbor_x in range(
                    max(0, index_x - neighbor_radius),
                    min(count_x, index_x + neighbor_radius + 1),
                ):
                    for particle in particle_bins.get((neighbor_x, neighbor_y), []):
                        delta_x = center_x - float(particle["x_km"])
                        delta_y = center_y - float(particle["y_km"])
                        squared_distance = delta_x * delta_x + delta_y * delta_y
                        if squared_distance <= maximum_distance_squared:
                            raw_density += float(particle["weight"]) * math.exp(
                                -0.5 * squared_distance / KDE_BANDWIDTH_KM**2
                            )
            latitude, longitude = inverse_local(
                center_x, center_y, latitude_origin, longitude_origin
            )
            corners = [
                inverse_local(x, y, latitude_origin, longitude_origin)[::-1]
                for x, y in (
                    (center_x - TILE_SIZE_KM / 2, center_y - TILE_SIZE_KM / 2),
                    (center_x + TILE_SIZE_KM / 2, center_y - TILE_SIZE_KM / 2),
                    (center_x + TILE_SIZE_KM / 2, center_y + TILE_SIZE_KM / 2),
                    (center_x - TILE_SIZE_KM / 2, center_y + TILE_SIZE_KM / 2),
                    (center_x - TILE_SIZE_KM / 2, center_y - TILE_SIZE_KM / 2),
                )
            ]
            context_fields = context_for_tile(latitude, longitude, context)
            tile = {
                "tile_id": f"tile-x{index_x:03d}-y{index_y:03d}",
                "index_x": index_x,
                "index_y": index_y,
                "center_x_km": center_x,
                "center_y_km": center_y,
                "center_latitude_deg": latitude,
                "center_longitude_deg": longitude,
                "corners_lon_lat": corners,
                "area_km2": TILE_SIZE_KM**2,
                "raw_kde_mass": raw_density * TILE_SIZE_KM**2,
                **context_fields,
            }
            tiles.append(tile)
            raw_total += tile["raw_kde_mass"]
    if not math.isfinite(raw_total) or raw_total <= 0:
        raise PackageError("KDE grid has no positive finite mass")
    for tile in tiles:
        tile["posterior_mass"] = tile["raw_kde_mass"] / raw_total
        tile["posterior_mass_per_km2"] = tile["posterior_mass"] / tile["area_km2"]
        tile["proxy_logistics_priority"] = (
            tile["posterior_mass_per_km2"] * tile["declared_opportunity_multiplier"]
        )
    return tiles


def rank_tiles(
    tiles: list[dict[str, Any]], key: str, budget_km2: float
) -> list[dict[str, Any]]:
    ordered = sorted(tiles, key=lambda tile: (-float(tile[key]), tile["tile_id"]))
    cumulative_area = 0.0
    cumulative_mass = 0.0
    for rank, tile in enumerate(ordered, 1):
        cumulative_area += float(tile["area_km2"])
        cumulative_mass += float(tile["posterior_mass"])
        tile[f"{key}_rank"] = rank
        tile[f"{key}_cumulative_area_km2"] = cumulative_area
        tile[f"{key}_cumulative_posterior_mass"] = cumulative_mass
        tile[f"{key}_within_budget"] = cumulative_area <= budget_km2 + 1e-9
    return ordered


def logistics_sequence(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not selected:
        return []
    remaining = list(selected)
    current = max(
        remaining,
        key=lambda tile: (float(tile["proxy_logistics_priority"]), tile["tile_id"]),
    )
    ordered = [current]
    remaining.remove(current)
    while remaining:
        def operational_score(tile: dict[str, Any]) -> tuple[float, str]:
            transit = haversine_km(
                float(current["center_latitude_deg"]),
                float(current["center_longitude_deg"]),
                float(tile["center_latitude_deg"]),
                float(tile["center_longitude_deg"]),
            )
            utility = float(tile["proxy_logistics_priority"]) / (1 + transit / 100.0)
            return utility, tile["tile_id"]

        current = max(remaining, key=operational_score)
        ordered.append(current)
        remaining.remove(current)
    for sequence, tile in enumerate(ordered, 1):
        tile["proxy_logistics_operational_sequence"] = sequence
    return ordered


def write_tile_csv(
    path: Path, ordered: list[dict[str, Any]], rank_key: str
) -> None:
    fields = [
        "tile_id",
        f"{rank_key}_rank",
        "proxy_logistics_operational_sequence",
        "center_latitude_deg",
        "center_longitude_deg",
        "area_km2",
        "posterior_mass",
        "posterior_mass_per_km2",
        "declared_opportunity_multiplier",
        "proxy_logistics_priority",
        f"{rank_key}_cumulative_area_km2",
        f"{rank_key}_cumulative_posterior_mass",
        f"{rank_key}_within_budget",
        "inside_official_phase2_source_footprint",
        "inside_official_bluefin_display_support",
        "inside_approximate_oi2018_outline",
        "inside_approximate_oi2024_outboard",
        "inside_approximate_oi2024_inboard",
        "nearest_ais_surface_vessel_track_km",
        "corners_lon_lat_json",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for tile in ordered:
            row = {
                field: tile.get(field, "")
                for field in fields
                if field != "corners_lon_lat_json"
            }
            row["corners_lon_lat_json"] = json.dumps(
                tile["corners_lon_lat"], separators=(",", ":")
            )
            writer.writerow(row)


def selected_tiles_geojson(
    posterior_selected: list[dict[str, Any]],
    proxy_selected: list[dict[str, Any]],
) -> dict[str, Any]:
    features = []
    for family, selected in (
        ("posterior_only", posterior_selected),
        ("proxy_logistics_sensitivity", proxy_selected),
    ):
        for tile in selected:
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "tile_id": tile["tile_id"],
                        "plan_family": family,
                        "posterior_mass": tile["posterior_mass"],
                        "opportunity_multiplier": tile[
                            "declared_opportunity_multiplier"
                        ],
                        "negative_search_likelihood_applied": False,
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [tile["corners_lon_lat"]],
                    },
                }
            )
    return {
        "type": "FeatureCollection",
        "metadata": {
            "schema_version": 1,
            "tile_area_km2": TILE_SIZE_KM**2,
            "budget_km2": PLANNING_BUDGET_KM2,
            "negative_search_likelihood_applied": False,
        },
        "features": features,
    }


def logical_input_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(ROOT.parent.parent).as_posix()
    except ValueError:
        return f"external-input/{path.name}"


def configure_planning_axis(axis: Any, tiles: list[dict[str, Any]]) -> None:
    configure_map_axis(axis)
    cumulative = 0.0
    support = []
    for tile in sorted(
        tiles, key=lambda candidate: -float(candidate["posterior_mass"])
    ):
        support.append(tile)
        cumulative += float(tile["posterior_mass"])
        if cumulative >= 0.995:
            break
    longitudes = [
        point[0] for tile in support for point in tile["corners_lon_lat"]
    ]
    latitudes = [
        point[1] for tile in support for point in tile["corners_lon_lat"]
    ]
    minimum_longitude = max(ATLAS_BBOX[0], min(longitudes) - 0.8)
    maximum_longitude = min(ATLAS_BBOX[2], max(longitudes) + 0.8)
    minimum_latitude = max(ATLAS_BBOX[1], min(latitudes) - 0.65)
    maximum_latitude = min(ATLAS_BBOX[3], max(latitudes) + 0.65)
    if maximum_longitude - minimum_longitude < 4:
        midpoint = (minimum_longitude + maximum_longitude) / 2
        minimum_longitude = max(ATLAS_BBOX[0], midpoint - 2)
        maximum_longitude = min(ATLAS_BBOX[2], midpoint + 2)
    if maximum_latitude - minimum_latitude < 4:
        midpoint = (minimum_latitude + maximum_latitude) / 2
        minimum_latitude = max(ATLAS_BBOX[1], midpoint - 2)
        maximum_latitude = min(ATLAS_BBOX[3], midpoint + 2)
    axis.set_xlim(minimum_longitude, maximum_longitude)
    axis.set_ylim(minimum_latitude, maximum_latitude)
    longitude_step = 1 if maximum_longitude - minimum_longitude <= 10 else 2
    latitude_step = 1 if maximum_latitude - minimum_latitude <= 10 else 2
    axis.set_xticks(
        range(
            math.ceil(minimum_longitude),
            math.floor(maximum_longitude) + 1,
            longitude_step,
        )
    )
    axis.set_yticks(
        range(
            math.ceil(minimum_latitude),
            math.floor(maximum_latitude) + 1,
            latitude_step,
        )
    )


def draw_plan_panel(
    axis: Any,
    atlas: dict[str, Any],
    tiles: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    *,
    title: str,
    route: list[dict[str, Any]] | None = None,
) -> None:
    import numpy as np
    from matplotlib.collections import PatchCollection
    from matplotlib.patches import Polygon as PlotPolygon

    configure_planning_axis(axis, tiles)
    positive = [tile for tile in tiles if float(tile["posterior_mass"]) > 0]
    maximum_density = max(
        float(tile["posterior_mass_per_km2"]) for tile in positive
    )
    density_patches = [
        PlotPolygon(tile["corners_lon_lat"], closed=True) for tile in positive
    ]
    relative_density = np.asarray(
        [
            math.sqrt(
                float(tile["posterior_mass_per_km2"]) / maximum_density
            )
            for tile in positive
        ]
    )
    density_collection = PatchCollection(
        density_patches,
        cmap="Blues",
        edgecolor="none",
        linewidth=0,
        alpha=0.62,
        zorder=1,
    )
    density_collection.set_array(relative_density)
    density_collection.set_clim(0, 1)
    axis.add_collection(density_collection)
    draw_atlas_layers(axis, atlas)

    for sequence, tile in enumerate(selected, 1):
        polygon = PlotPolygon(
            tile["corners_lon_lat"],
            closed=True,
            facecolor="none",
            edgecolor="#be123c",
            linewidth=1.25,
            zorder=12,
        )
        axis.add_patch(polygon)
        label = (
            tile.get("proxy_logistics_operational_sequence", sequence)
            if route is not None
            else sequence
        )
        axis.text(
            float(tile["center_longitude_deg"]),
            float(tile["center_latitude_deg"]),
            str(label),
            ha="center",
            va="center",
            fontsize=6.4,
            fontweight="bold",
            color="#881337",
            zorder=13,
            bbox={"boxstyle": "circle,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.78},
        )
    if route:
        axis.plot(
            [float(tile["center_longitude_deg"]) for tile in route],
            [float(tile["center_latitude_deg"]) for tile in route],
            color="#be123c",
            linewidth=0.8,
            alpha=0.75,
            zorder=11,
        )
    axis.set_title(title, loc="left", fontweight="bold", pad=8)
    axis.text(
        0.012,
        0.012,
        "Light blue: KDE density · red: selected 25 km tiles",
        transform=axis.transAxes,
        fontsize=6.6,
        color="#334155",
        bbox={"fc": "white", "ec": "#cbd5e1", "alpha": 0.94, "pad": 3},
        zorder=20,
    )


def build_search_plan_figure(
    atlas: dict[str, Any],
    tiles: list[dict[str, Any]],
    posterior_selected: list[dict[str, Any]],
    proxy_selected: list[dict[str, Any]],
    proxy_route: list[dict[str, Any]],
    summary: dict[str, Any],
    output_directory: Path,
) -> None:
    plt, _, _, _, _ = plotting_modules()
    figure = plt.figure(figsize=(15.2, 8.4), constrained_layout=False)
    grid = figure.add_gridspec(
        2,
        2,
        height_ratios=[1, 0.16],
        left=0.055,
        right=0.975,
        top=0.84,
        bottom=0.095,
        wspace=0.12,
        hspace=0.13,
    )
    posterior_axis = figure.add_subplot(grid[0, 0])
    proxy_axis = figure.add_subplot(grid[0, 1])
    draw_plan_panel(
        posterior_axis,
        atlas,
        tiles,
        posterior_selected,
        title="A · Posterior mass per area",
    )
    draw_plan_panel(
        proxy_axis,
        atlas,
        tiles,
        proxy_selected,
        title="B · Proxy-aware logistics sensitivity",
        route=proxy_route,
    )
    note = figure.add_subplot(grid[1, :])
    note.axis("off")
    posterior_mass = summary["plans"]["posterior_only"][
        "selected_posterior_mass"
    ]
    proxy_mass = summary["plans"]["proxy_logistics_sensitivity"][
        "selected_posterior_mass"
    ]
    overlap = summary["plans"]["selected_tile_overlap_count"]
    note.text(
        0,
        0.88,
        f"12 × 625 km² = 7,500 km² · posterior-only mass {posterior_mass:.3%} · "
        f"proxy-sensitivity mass {proxy_mass:.3%} · {overlap}/12 selected tiles overlap",
        fontsize=9.2,
        fontweight="bold",
        color="#0f172a",
        va="top",
    )
    note.text(
        0,
        0.50,
        "Panel B applies declared soft opportunity multipliers and a greedy transit sequence. "
        "These are scenario assumptions—not probability of detection, negative-search evidence, or posterior weights.",
        fontsize=7.8,
        color="#475569",
        va="top",
    )
    note.text(
        0,
        0.14,
        "Exact OI AUV swaths, complete quality/holiday masks and calibrated PoD remain unavailable; "
        "official and reconstructed context layers retain distinct symbology.",
        fontsize=7.4,
        color="#991b1b",
        va="top",
        fontweight="bold",
    )
    role = summary["input"]["role"]
    prefix = "SYNTHETIC FIXTURE · " if role == "synthetic_fixture" else ""
    figure.suptitle(
        f"{prefix}MH370 7,500 km² search-planning sensitivity",
        x=0.055,
        y=0.96,
        ha="left",
        fontsize=18.5,
        fontweight="bold",
        color="#0f172a",
    )
    figure.text(
        0.055,
        0.895,
        f"Impact-particle input: {summary['input']['logical_path']} · "
        f"{summary['input']['particle_count']} weighted particles · deterministic 35 km Gaussian KDE · "
        f"{summary['branch_status'].replace('_', ' ')}",
        fontsize=8.8,
        color="#475569",
    )
    save_figure_set(figure, output_directory / "search-plan")
    plt.close(figure)


def build_plan_html(output_directory: Path, summary: dict[str, Any]) -> None:
    rows = []
    for family, plan in (
        ("Posterior only", summary["plans"]["posterior_only"]),
        (
            "Proxy/logistics sensitivity",
            summary["plans"]["proxy_logistics_sensitivity"],
        ),
    ):
        rows.append(
            "<tr>"
            f"<td>{family}</td>"
            f"<td>{plan['selected_area_km2']:,.0f}</td>"
            f"<td>{plan['selected_posterior_mass']:.4%}</td>"
            f"<td>{html.escape(', '.join(plan['selected_tile_ids']))}</td>"
            "</tr>"
        )
    role_note = (
        "This is a synthetic interface fixture, not an MH370 result."
        if summary["input"]["role"] == "synthetic_fixture"
        else "This plan is conditional on the supplied impact-particle weights."
    )
    if summary["status_note"]:
        role_note += f" {summary['status_note']}"
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MH370 7,500 km² planning sensitivity</title><style>
body{{margin:0;background:#eef3f2;color:#17211f;font:15px/1.5 system-ui,sans-serif}}main{{max-width:1500px;margin:auto;padding:28px}}h1{{margin:0 0 5px;font-size:30px}}.note{{color:#526762}}.frame{{background:white;border:1px solid #c8d6d2;border-radius:10px;padding:10px;box-shadow:0 8px 25px #17322b18}}svg{{width:100%;height:auto}}table{{width:100%;border-collapse:collapse;background:white;margin-top:22px}}th,td{{padding:10px;border-bottom:1px solid #dbe5e2;text-align:left;vertical-align:top}}th{{font-size:11px;text-transform:uppercase;color:#526762}}.boundary{{margin-top:20px;padding:14px;border-left:4px solid #b45309;background:#fff7ed}}code{{font-size:12px}}a{{color:#0f766e}}</style></head><body><main>
<h1>MH370 7,500 km² search-planning sensitivity</h1><p class="note">{html.escape(role_note)} · <a href="search-plan.svg">SVG</a> · <a href="search-plan.pdf">PDF</a> · <a href="search-plan.png">PNG</a></p>
<div class="frame">{embedded_svg(output_directory / 'search-plan.svg')}</div>
<table><thead><tr><th>Plan</th><th>Area km²</th><th>Input posterior mass</th><th>Selected tile IDs in rank order</th></tr></thead><tbody>{''.join(rows)}</tbody></table>
<div class="boundary"><strong>Scientific boundary.</strong> No searched-area layer was applied as a likelihood or binary exclusion. The proxy/logistics plan uses declared subjective opportunity multipliers solely to expose sensitivity. Exact OI AUV swaths, complete search quality and calibrated PoD remain unresolved.</div>
<p>Machine outputs: <a href="plan-summary.json">summary</a> · <a href="ordered-tiles-posterior-only.csv">posterior ranking</a> · <a href="ordered-tiles-proxy-logistics.csv">proxy/logistics ranking</a> · <a href="selected-tiles.geojson">selected tiles</a> · <a href="run-manifest.json">manifest</a>.</p>
</main></body></html>"""
    (output_directory / "index.html").write_text(
        document, encoding="utf-8", newline="\n"
    )


def plan(
    particles_path: Path,
    weight_column: str,
    weight_mode: str,
    label: str,
    atlas: dict[str, Any] | None = None,
    branch_status: str = "sensitivity_not_operational",
    status_note: str = "",
) -> dict[str, Any]:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", label):
        raise PackageError("plan label must contain lowercase letters, digits, or hyphens")
    if weight_mode not in ("linear", "log"):
        raise PackageError("weight mode must be linear or log")
    if branch_status not in (
        "sensitivity_not_operational",
        "diagnostic_only",
        "numerically_unresolved_non_operational",
    ):
        raise PackageError("branch status is not supported")
    if not particles_path.is_file():
        raise PackageError(f"particle CSV does not exist: {particles_path}")
    if atlas is None:
        atlas_path = ROOT / "data" / "map" / "search-evidence-atlas.geojson"
        if not atlas_path.is_file():
            raise PackageError("build the evidence package before running the planner")
        atlas = read_json(atlas_path)

    particles = read_weighted_particles(particles_path, weight_column, weight_mode)
    latitude_origin, longitude_origin, projected = local_projection(particles)
    tiles = tile_grid(projected, latitude_origin, longitude_origin)
    posterior_ordered = rank_tiles(
        tiles, "posterior_mass_per_km2", PLANNING_BUDGET_KM2
    )
    proxy_ordered = rank_tiles(
        tiles, "proxy_logistics_priority", PLANNING_BUDGET_KM2
    )
    posterior_selected = [
        tile
        for tile in posterior_ordered
        if tile["posterior_mass_per_km2_within_budget"]
    ]
    proxy_selected = [
        tile
        for tile in proxy_ordered
        if tile["proxy_logistics_priority_within_budget"]
    ]
    expected_count = int(PLANNING_BUDGET_KM2 / TILE_SIZE_KM**2)
    if len(posterior_selected) != expected_count or len(proxy_selected) != expected_count:
        raise PackageError("planning grid cannot fill the declared area budget exactly")
    proxy_route = logistics_sequence(proxy_selected)
    posterior_ids = {tile["tile_id"] for tile in posterior_selected}
    proxy_ids = {tile["tile_id"] for tile in proxy_selected}

    output_directory = ROOT / "outputs" / f"planning-{label}"
    output_directory.mkdir(parents=True, exist_ok=True)
    source_logical_path = logical_input_path(particles_path)
    input_role = "synthetic_fixture" if label == "fixture" else "release_input"
    summary = {
        "schema_version": 1,
        "snapshot_date": "2026-08-31",
        "label": label,
        "branch_status": branch_status,
        "status_note": status_note,
        "input": {
            "logical_path": source_logical_path,
            "sha256": sha256_file(particles_path),
            "bytes": particles_path.stat().st_size,
            "role": input_role,
            "particle_count": len(particles),
            "weight_column": weight_column,
            "weight_mode": weight_mode,
            "weights_normalized_by_planner": True,
        },
        "method": {
            "projection": "local equirectangular coordinates about weighted particle centroid",
            "centroid_latitude_deg": latitude_origin,
            "centroid_longitude_deg": longitude_origin,
            "tile_size_km": TILE_SIZE_KM,
            "tile_area_km2": TILE_SIZE_KM**2,
            "budget_km2": PLANNING_BUDGET_KM2,
            "selected_tile_count": expected_count,
            "kde": "isotropic Gaussian evaluated at tile centers",
            "kde_bandwidth_km": KDE_BANDWIDTH_KM,
            "kde_truncation_sigma": KDE_RADIUS_SIGMA,
            "kde_grid_mass_renormalized": True,
            "ranking_extension": "all rows after the first 12 in each ordered CSV are the deterministic extension order under that family's assumptions",
        },
        "plans": {
            "posterior_only": {
                "ranking": "posterior KDE mass per square kilometre",
                "selected_area_km2": math.fsum(
                    float(tile["area_km2"]) for tile in posterior_selected
                ),
                "selected_posterior_mass": math.fsum(
                    float(tile["posterior_mass"]) for tile in posterior_selected
                ),
                "selected_tile_ids": [tile["tile_id"] for tile in posterior_selected],
            },
            "proxy_logistics_sensitivity": {
                "ranking": "posterior KDE mass per square kilometre times declared opportunity multiplier",
                "operational_sequence": "greedy next-tile score divided by 1 + great-circle transit_km/100 within the selected set",
                "selected_area_km2": math.fsum(
                    float(tile["area_km2"]) for tile in proxy_selected
                ),
                "selected_posterior_mass": math.fsum(
                    float(tile["posterior_mass"]) for tile in proxy_selected
                ),
                "selected_tile_ids": [tile["tile_id"] for tile in proxy_selected],
                "operational_tile_ids": [tile["tile_id"] for tile in proxy_route],
            },
            "selected_tile_overlap_count": len(posterior_ids & proxy_ids),
        },
        "declared_proxy_opportunity_multipliers": {
            "official_phase2_source_footprint": 0.72,
            "official_bluefin_display_footprint": 0.75,
            "approximate_oi2018_outline": 0.82,
            "approximate_march2024_outboard_outline": 0.88,
            "approximate_march2024_inboard_outline": 1.05,
            "within_25_km_of_ais_surface_vessel_track": 0.95,
            "combined_clamp": [0.50, 1.10],
            "interpretation": "subjective planning sensitivity only; not PoD, a likelihood, or evidence of target absence",
        },
        "scientific_boundary": {
            "negative_search_likelihood_applied": False,
            "binary_exclusion_applied": False,
            "approximate_outlines_update_posterior": False,
            "ais_tracks_update_posterior": False,
            "calibrated_search_optimization_ready": False,
        },
    }
    (output_directory / "plan-summary.json").write_bytes(pretty_json_bytes(summary))
    write_tile_csv(
        output_directory / "ordered-tiles-posterior-only.csv",
        posterior_ordered,
        "posterior_mass_per_km2",
    )
    write_tile_csv(
        output_directory / "ordered-tiles-proxy-logistics.csv",
        proxy_ordered,
        "proxy_logistics_priority",
    )
    (output_directory / "selected-tiles.geojson").write_bytes(
        canonical_json_bytes(
            selected_tiles_geojson(posterior_selected, proxy_selected)
        )
    )
    build_search_plan_figure(
        atlas,
        tiles,
        posterior_selected,
        proxy_selected,
        proxy_route,
        summary,
        output_directory,
    )
    build_plan_html(output_directory, summary)
    output_names = [
        "index.html",
        "ordered-tiles-posterior-only.csv",
        "ordered-tiles-proxy-logistics.csv",
        "plan-summary.json",
        "search-plan.pdf",
        "search-plan.png",
        "search-plan.svg",
        "selected-tiles.geojson",
    ]
    manifest = {
        "schema_version": 1,
        "snapshot_date": "2026-08-31",
        "generator": "code/build.py",
        "generator_sha256": sha256_file(Path(__file__)),
        "deterministic": True,
        "input": summary["input"],
        "outputs": [
            {
                "path": f"outputs/planning-{label}/{name}",
                "sha256": sha256_file(output_directory / name),
                "bytes": (output_directory / name).stat().st_size,
            }
            for name in output_names
        ],
    }
    (output_directory / "run-manifest.json").write_bytes(
        pretty_json_bytes(manifest)
    )
    print(
        f"planned {PLANNING_BUDGET_KM2:,.0f} km2 from {len(particles):,} particles "
        f"to {output_directory.relative_to(ROOT)}"
    )
    return summary


def format_area(record: dict[str, Any]) -> str:
    if "source_catalog_area_km2" in record:
        return f"{record['source_catalog_area_km2']:,.3f}".rstrip("0").rstrip(".") + " catalog"
    if "reported_area_km2" in record:
        area = record["reported_area_km2"]
        if isinstance(area, dict):
            return f"{area['comparator']}{area['value']:,.0f} reported"
        if area is not None:
            return f"{area:,.0f} reported"
    if "reported_surveyed_area_km2" in record:
        return f"≈{record['reported_surveyed_area_km2']:,.0f} reported"
    return "not stated"


def link(url: str, label: str) -> str:
    return (
        f'<a href="{html.escape(url, quote=True)}" target="_blank" '
        f'rel="noreferrer">{html.escape(label)}</a>'
    )


def build_report(display: dict[str, Any]) -> None:
    evidence = read_json(ROOT / "data" / "evidence-register.json")
    readiness = read_json(ROOT / "data" / "readiness.json")
    citations = read_json(ROOT / "provenance" / "citations.json")
    lock = read_json(LOCK_PATH)

    evidence_rows = []
    for record in evidence["records"]:
        geometry = record["geometry"] or "none obtained"
        evidence_rows.append(
            "<tr>"
            f"<td><strong>{html.escape(record['id'])}</strong><small>{html.escape(record['campaign'])}</small></td>"
            f"<td><span class=\"class-tag\">{html.escape(record['geometry_class'])}</span><small>{html.escape(geometry)}</small></td>"
            f"<td>{html.escape(format_area(record))} km²</td>"
            "<td><span class=\"unknown\">quality unresolved</span> · "
            "<span class=\"unknown\">holidays unresolved</span> · "
            "<span class=\"unknown\">PoD unresolved</span></td>"
            "<td><span class=\"no\">NO</span></td>"
            "</tr>"
        )

    citation_rows = []
    for claim in citations["claims"]:
        excerpt = claim.get("located_passage")
        support = f'<q>{html.escape(excerpt)}</q>' if excerpt else html.escape(claim.get("scope_note", "No supporting passage located."))
        citation_rows.append(
            "<tr>"
            f"<td><span class=\"status {claim['status'].lower().replace('_', '-')}\">{html.escape(claim['status'])}</span></td>"
            f"<td>{html.escape(claim['claim'])}</td>"
            f"<td>{link(claim['url'], claim['source'])}<small>{html.escape(claim['locator'])}</small></td>"
            f"<td>{support}</td>"
            "</tr>"
        )

    source_rows = []
    for source in lock["sources"]:
        source_url = source.get("canonical_url", source.get("url"))
        decision = "bundled" if source["bundled"] else "hash/link only"
        source_rows.append(
            "<tr>"
            f"<td>{link(source_url, source['id'])}<small>{html.escape(source['publisher'])}</small></td>"
            f"<td><code>{source['content_sha256']}</code><small>{source['content_bytes']:,} bytes</small></td>"
            f"<td>{decision}</td>"
            "</tr>"
        )

    requirements = "".join(
        f'<li><span class="req-state">{html.escape(item["state"])}</span>{html.escape(item["input"])}</li>'
        for item in readiness["negative_search_likelihood"]["required_inputs"]
    )
    blockers = "".join(
        f"<li>{html.escape(item)}</li>"
        for item in readiness["planning_approximately_7500_km2"]["spatial_blockers"]
    )
    map_json = canonical_json_bytes(display).decode("utf-8").strip().replace("</", "<\\/")

    template = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="dark">
<title>MH370 seabed-search coverage evidence</title>
<style>
:root{--ink:#eef6f4;--muted:#9fb4b1;--panel:#102925;--panel2:#13332e;--line:#31514b;--sea:#071b1d;--mint:#68d7bd;--cyan:#60b7d5;--amber:#f4bd63;--red:#ff8678;--cream:#f7f0dd}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:radial-gradient(circle at 12% -10%,#16473d 0,transparent 34rem),var(--sea);color:var(--ink);font:15px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}a{color:#8dd9ed}a:hover{color:#c7f2ff}.wrap{width:min(1200px,calc(100% - 32px));margin:auto}header{padding:72px 0 40px;border-bottom:1px solid var(--line)}.kicker{color:var(--mint);font:700 12px/1.2 ui-monospace,monospace;letter-spacing:.14em;text-transform:uppercase}h1{max-width:900px;margin:.35em 0 .3em;font:600 clamp(38px,7vw,76px)/.95 Georgia,serif;letter-spacing:-.045em}header p{max-width:790px;color:#c2d2cf;font-size:18px}.stamp{display:flex;gap:10px;flex-wrap:wrap;margin-top:25px}.pill,.status{display:inline-flex;padding:4px 9px;border:1px solid var(--line);border-radius:999px;background:#0b2320;font:700 11px/1.4 ui-monospace,monospace;letter-spacing:.04em}.danger{border-color:#97544c;color:#ffd4cd;background:#3b211f}.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:28px auto 0}.metric{padding:20px;border:1px solid var(--line);border-radius:14px;background:linear-gradient(145deg,#12322c,#0d2623)}.metric strong{display:block;font:600 30px/1 Georgia,serif;color:var(--cream)}.metric span{display:block;margin-top:8px;color:var(--muted);font-size:12px}main section{padding:52px 0;border-bottom:1px solid #213d38}h2{margin:0 0 10px;font:600 34px/1.05 Georgia,serif;letter-spacing:-.02em}h3{font-size:17px;margin:0 0 8px}.lead{max-width:790px;color:#b7c9c5}.callout{padding:20px 22px;margin:22px 0;border-left:4px solid var(--amber);background:#30291c;border-radius:0 12px 12px 0;color:#f6e6be}.map-shell{margin-top:24px;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#07191b}.map-tools{display:flex;align-items:center;gap:16px;flex-wrap:wrap;padding:12px 16px;border-bottom:1px solid var(--line);background:#0d2623}.map-tools label{display:flex;align-items:center;gap:7px;color:#c8d8d5;font-size:13px}.map-tools input{accent-color:var(--mint)}button{margin-left:auto;padding:7px 12px;border:1px solid var(--line);border-radius:8px;background:#173b35;color:var(--ink);cursor:pointer}#map{display:block;width:100%;height:auto;min-height:420px;touch-action:none;background:linear-gradient(#0b2427,#07191b)}.grid{stroke:#325052;stroke-width:.7;stroke-dasharray:3 6;vector-effect:non-scaling-stroke}.grid-label{fill:#78989a;font:12px ui-monospace,monospace}.coverage{vector-effect:non-scaling-stroke;stroke-linejoin:round;fill-rule:evenodd;transition:opacity .15s}.deep{fill:#68d7bd55;stroke:#8ce7d1;stroke-width:1}.dhj{fill:#60b7d533;stroke:#71cbe8;stroke-width:1.4}.gophoenix{fill:#f4bd6318;stroke:#f4bd63;stroke-width:2;stroke-dasharray:6 5}.map-caption{padding:13px 16px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}#tooltip{position:fixed;z-index:9;display:none;max-width:300px;padding:9px 11px;border:1px solid var(--line);border-radius:8px;background:#061715ee;color:#e6f4f0;font-size:12px;pointer-events:none}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-top:25px}.card{padding:22px;border:1px solid var(--line);border-radius:14px;background:var(--panel)}.card p{color:#b8cac6}.card ul,.checklist{padding-left:18px;color:#c7d6d3}.card li{margin:.45em 0}.bar{display:flex;height:54px;margin:19px 0 8px;border:1px solid #4a625b;border-radius:9px;overflow:hidden}.bar div{display:flex;align-items:center;justify-content:center;color:#061716;font-weight:800}.surveyed{width:50.4733%;background:var(--mint)}.remainder{width:49.5267%;background:var(--amber)}.equation{font:600 23px ui-monospace,monospace;color:var(--cream)}.req-list{list-style:none;padding:0}.req-list li{display:flex;gap:10px;align-items:flex-start;margin:8px 0}.req-state{min-width:110px;color:var(--amber);font:700 10px/1.5 ui-monospace,monospace;text-transform:uppercase}table{width:100%;margin-top:22px;border-collapse:collapse;font-size:13px}th{text-align:left;color:#91aaa5;font:700 10px ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase}th,td{padding:12px 10px;border-bottom:1px solid #29453f;vertical-align:top}td small{display:block;color:var(--muted);margin-top:4px}td code{font-size:10px;word-break:break-all;color:#b9d7d1}.table-scroll{overflow:auto}.class-tag,.unknown{color:var(--amber);font:700 10px ui-monospace,monospace}.no{display:inline-block;color:#ffd0ca;background:#4a2421;border:1px solid #8f4b43;border-radius:5px;padding:2px 6px;font:800 10px ui-monospace,monospace}.found{color:var(--mint)}.not-found,.blocked{color:var(--amber)}q{color:#d9e7e4}.method{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:24px}.method div{padding:18px;border:1px solid var(--line);border-radius:12px;background:var(--panel)}.method b{display:block;color:var(--mint);font:700 11px ui-monospace,monospace}.method p{margin:7px 0 0;color:var(--muted)}footer{padding:38px 0 70px;color:#8da6a1;font-size:12px}@media(max-width:850px){.summary{grid-template-columns:1fr 1fr}.grid2,.method{grid-template-columns:1fr}table{min-width:860px}}@media(max-width:520px){.summary{grid-template-columns:1fr}.wrap{width:min(100% - 20px,1200px)}header{padding-top:45px}h1{font-size:43px}.map-tools button{margin-left:0}}
</style>
</head>
<body>
<header><div class="wrap"><div class="kicker">Primary-source coverage audit · snapshot 2026-08-31</div><h1>What was mapped is not automatically what was searched.</h1><p>A conservative evidence package for MH370 seabed coverage. Official geometry is preserved at source resolution; missing swaths, quality, holidays, and probability of detection remain explicit unknowns.</p><p><a href="evidence-atlas.html">Open the publication evidence atlas</a> · <a href="planning-fixture/index.html">Open the synthetic planning-interface fixture</a></p><div class="stamp"><span class="pill">EPSG:4326 source coordinates</span><span class="pill">deterministic build</span><span class="pill danger">no binary elimination mask</span></div><div class="summary"><div class="metric"><strong>3</strong><span>official Phase 2 WFS coverage records</span></div><div class="metric"><strong>0</strong><span>exact public OI AUV swath sets obtained</span></div><div class="metric"><strong>0</strong><span>calibrated numeric PoD fields obtained</span></div><div class="metric"><strong>7,429</strong><span>km² approximate arithmetic remainder—not a polygon</span></div></div></div></header>
<main>
<section><div class="wrap"><div class="kicker">01 · Spatial evidence</div><h2>Phase 2 source geometries</h2><p class="lead">The map contains a display simplification of three unmodified, hash-pinned GA/AusSeabed level-0 source records. Their visual detail and scientific meaning differ. Area attributes overlap and must not be summed.</p><div class="callout"><strong>Interpretation boundary:</strong> Deep Tow is a detailed data footprint. Dong Hai Jiu is coarse. GO Phoenix is a bounding rectangle. None carries complete per-cell QA, holidays, or target-specific PoD.</div><div class="map-shell"><div class="map-tools"><label><input type="checkbox" data-layer="deep" checked> Deep Tow detailed</label><label><input type="checkbox" data-layer="dhj" checked> Dong Hai Jiu coarse</label><label><input type="checkbox" data-layer="gophoenix" checked> GO Phoenix rectangle</label><button id="reset" type="button">Reset view</button></div><svg id="map" viewBox="0 0 1000 640" role="img" aria-label="Official Phase 2 coverage source geometries"></svg><div class="map-caption">Pan by dragging; zoom with the wheel. Cartographic derivative: parts/holes below 0.01° bounding-box span are omitted as subpixel at this map scale, retained lines use 0.006° simplification, and coordinates are rounded to 0.00001°. Exact full geometry is retained separately. No basemap, bathymetry, OI outline, AIS proxy, or inferred swath is shown.</div></div></div></section>
<section><div class="wrap"><div class="kicker">02 · Evidence classes</div><h2>Every area keeps its uncertainty</h2><p class="lead">An explicit false value in the last column prevents accidental use as negative-search elimination.</p><div class="table-scroll"><table><thead><tr><th>Evidence record</th><th>Geometry class / file</th><th>Published area</th><th>Unresolved observation inputs</th><th>Elimination eligible</th></tr></thead><tbody>__EVIDENCE_ROWS__</tbody></table></div></div></section>
<section><div class="wrap"><div class="kicker">03 · Readiness</div><h2>Likelihood blocked; explicit planning sensitivity available</h2><div class="grid2"><article class="card"><h3>Negative-search likelihood · NOT READY</h3><p>A footprint is only the spatial support of possible observations. A defensible miss probability still needs:</p><ul class="req-list">__REQUIREMENTS__</ul></article><article class="card"><h3>~7,500 km² planning · SENSITIVITY READY</h3><p class="equation">15,000 − 7,571 = 7,429 km²</p><div class="bar" aria-label="Approximate reported area accounting"><div class="surveyed">7,571 surveyed</div><div class="remainder">7,429 remainder</div></div><p>The official figures are estimated/approximate. A supplied impact posterior can now be ranked into 25 km tiles, both posterior-only and under a separately labelled proxy/logistics sensitivity. Neither is calibrated search optimization.</p><ul>__BLOCKERS__</ul></article></div><div class="method"><div><b>APPROXIMATE OUTLINES</b><p>Context only. Never subtract them from a prior or contract polygon.</p></div><div><b>AIS TRACKS</b><p>Surface-vessel motion cannot establish AUV position, valid sonar width, or detection.</p></div><div><b>BATHYMETRY</b><p>Seafloor mapping assists operations; it is not aircraft-target search evidence.</p></div></div></div></section>
<section><div class="wrap"><div class="kicker">04 · Blockers stated plainly</div><h2>No swaths were invented</h2><div class="grid2"><article class="card"><h3>Ocean Shield AUV / Bluefin evidence, 2014</h3><p>ATSB names the Phoenix International Artemis AUV and reports 30 missions and 860 km². The official GA application supplies two display polygons with 771.410 km² spherical display area; these are not mission swaths or a valid-data mask, and the 88.590 km² difference remains unplotted.</p></article><article class="card"><h3>Ocean Infinity 2018 and 2025–2026</h3><p>Operator/government area statements were found. Exact public AUV swaths, an authoritative 15,000 km² boundary, spatial QA, holiday/resurvey masks, and calibrated PoD were not. Approximate outlines and AIS tracks are shown only as grade-C planning context.</p></article></div></div></section>
<section><div class="wrap"><div class="kicker">05 · Citation audit</div><h2>Claims are tied to located primary evidence</h2><p class="lead"><code>NOT_FOUND</code> is scoped to the searches recorded here. <code>BLOCKED</code> means the required artifact was not publicly obtained—not that it cannot exist.</p><div class="table-scroll"><table><thead><tr><th>Status</th><th>Claim tested</th><th>Primary source / locator</th><th>Located support or blocker</th></tr></thead><tbody>__CITATION_ROWS__</tbody></table></div></div></section>
<section><div class="wrap"><div class="kicker">06 · Provenance</div><h2>Exact bytes or an explicit non-bundling decision</h2><p class="lead">Bundled WFS records are redistributable and necessary for regeneration. Large or rights-ambiguous references are linked and hash-pinned without being copied into the package.</p><div class="table-scroll"><table><thead><tr><th>Source</th><th>SHA-256 / uncompressed bytes</th><th>Retention</th></tr></thead><tbody>__SOURCE_ROWS__</tbody></table></div></div></section>
</main>
<footer><div class="wrap">Built from pinned source records with <code>.venv/bin/python .sources/mh370-seabed-search-coverage/code/build.py build</code>. Self-contained HTML; no external assets or network requests. Scientific status: evidence inventory and planning sensitivity, not a negative-search likelihood.</div></footer><div id="tooltip"></div>
<script>
const data=__MAP_JSON__;
const svg=document.getElementById('map'),tooltip=document.getElementById('tooltip');
const initial={x:0,y:0,w:1000,h:640};let view={...initial},drag=null;
const bbox=data.metadata.source_bbox,pad=.45,minLon=bbox[0]-pad,maxLon=bbox[2]+pad,minLat=bbox[1]-pad,maxLat=bbox[3]+pad;
const project=([lon,lat])=>[(lon-minLon)/(maxLon-minLon)*1000,(maxLat-lat)/(maxLat-minLat)*640];
const pathGeometry=g=>{const polygons=g.type==='Polygon'?[g.coordinates]:g.coordinates;let d='';for(const polygon of polygons)for(const ring of polygon){ring.forEach((p,i)=>{const [x,y]=project(p);d+=(i?'L':'M')+x.toFixed(2)+','+y.toFixed(2)});d+='Z'}return d};
const ns='http://www.w3.org/2000/svg';
const add=(name,attrs,parent=svg)=>{const el=document.createElementNS(ns,name);Object.entries(attrs).forEach(([k,v])=>el.setAttribute(k,v));parent.appendChild(el);return el};
for(let lon=Math.ceil(minLon/2)*2;lon<=maxLon;lon+=2){const [x]=project([lon,0]);add('line',{x1:x,y1:0,x2:x,y2:640,class:'grid'});const t=add('text',{x:x+5,y:22,class:'grid-label'});t.textContent=lon+'°E'}
for(let lat=Math.ceil(minLat/2)*2;lat<=maxLat;lat+=2){const [,y]=project([0,lat]);add('line',{x1:0,y1:y,x2:1000,y2:y,class:'grid'});const t=add('text',{x:8,y:y-6,class:'grid-label'});t.textContent=Math.abs(lat)+'°S'}
const classFor=id=>id.includes('deep')?'deep':id.includes('dhj')?'dhj':'gophoenix';
for(const feature of data.features){const cls=classFor(feature.properties.id),path=add('path',{d:pathGeometry(feature.geometry),class:'coverage '+cls,'data-layer':cls,tabindex:'0'});const show=e=>{tooltip.style.display='block';tooltip.style.left=(e.clientX+12)+'px';tooltip.style.top=(e.clientY+12)+'px';tooltip.innerHTML='<strong>'+feature.properties.label+'</strong><br>'+feature.properties.geometry_class+'<br>'+Number(feature.properties.source_catalog_area_km2).toLocaleString()+' km² catalog attribute<br><em>not elimination eligible</em>'};path.addEventListener('pointermove',show);path.addEventListener('pointerleave',()=>tooltip.style.display='none')}
const apply=()=>svg.setAttribute('viewBox',`${view.x} ${view.y} ${view.w} ${view.h}`);apply();
svg.addEventListener('wheel',e=>{e.preventDefault();const rect=svg.getBoundingClientRect(),px=view.x+(e.clientX-rect.left)/rect.width*view.w,py=view.y+(e.clientY-rect.top)/rect.height*view.h,f=e.deltaY>0?1.16:.86,nw=Math.min(1600,Math.max(80,view.w*f)),nh=nw*.64;view={x:px-(px-view.x)*nw/view.w,y:py-(py-view.y)*nh/view.h,w:nw,h:nh};apply()},{passive:false});
svg.addEventListener('pointerdown',e=>{drag={x:e.clientX,y:e.clientY,v:{...view}};svg.setPointerCapture(e.pointerId)});svg.addEventListener('pointermove',e=>{if(!drag)return;const rect=svg.getBoundingClientRect();view.x=drag.v.x-(e.clientX-drag.x)/rect.width*view.w;view.y=drag.v.y-(e.clientY-drag.y)/rect.height*view.h;apply()});svg.addEventListener('pointerup',()=>drag=null);
document.getElementById('reset').addEventListener('click',()=>{view={...initial};apply()});
document.querySelectorAll('[data-layer]').forEach(input=>{if(input.tagName==='INPUT')input.addEventListener('change',()=>document.querySelectorAll('path[data-layer="'+input.dataset.layer+'"]').forEach(path=>path.style.display=input.checked?'':'none'))});
</script>
</body></html>
'''
    report = (
        template.replace("__EVIDENCE_ROWS__", "".join(evidence_rows))
        .replace("__REQUIREMENTS__", requirements)
        .replace("__BLOCKERS__", blockers)
        .replace("__CITATION_ROWS__", "".join(citation_rows))
        .replace("__SOURCE_ROWS__", "".join(source_rows))
        .replace("__MAP_JSON__", map_json)
    )
    (ROOT / "outputs" / "report.html").write_text(report, encoding="utf-8", newline="\n")


def build_manifest() -> None:
    input_paths = [
        "data/evidence-register.json",
        "data/planning/fixture-impact-particles.csv",
        "data/planning/weighted-particle-csv-schema.json",
        "data/readiness.json",
        "provenance/citations.json",
        "provenance/sources.lock.json",
    ] + [source["stored_path"] for source in lock_sources() if source.get("bundled")]
    output_paths = [
        "data/area-inventory.json",
        "data/map/phase2-display.geojson",
        "data/map/search-evidence-atlas.geojson",
        "outputs/evidence-atlas.html",
        "outputs/evidence-atlas.pdf",
        "outputs/evidence-atlas.png",
        "outputs/evidence-atlas.svg",
        "outputs/planning-fixture/index.html",
        "outputs/planning-fixture/ordered-tiles-posterior-only.csv",
        "outputs/planning-fixture/ordered-tiles-proxy-logistics.csv",
        "outputs/planning-fixture/plan-summary.json",
        "outputs/planning-fixture/run-manifest.json",
        "outputs/planning-fixture/search-plan.pdf",
        "outputs/planning-fixture/search-plan.png",
        "outputs/planning-fixture/search-plan.svg",
        "outputs/planning-fixture/selected-tiles.geojson",
        "outputs/report.html",
    ]
    manifest = {
        "schema_version": 1,
        "snapshot_date": "2026-08-31",
        "generator": "code/build.py",
        "generator_sha256": sha256_file(Path(__file__)),
        "deterministic": True,
        "inputs": [
            {
                "path": path,
                "sha256": sha256_file(ROOT / path),
                "bytes": (ROOT / path).stat().st_size,
            }
            for path in input_paths
        ],
        "outputs": [
            {
                "path": path,
                "sha256": sha256_file(ROOT / path),
                "bytes": (ROOT / path).stat().st_size,
            }
            for path in output_paths
        ],
    }
    (ROOT / "provenance" / "build-manifest.json").write_bytes(pretty_json_bytes(manifest))


def build() -> None:
    display = build_display_geometry()
    atlas = build_atlas_data(display)
    inventory = build_area_inventory()
    build_evidence_atlas(atlas, inventory)
    build_report(display)
    plan(
        ROOT / "data" / "planning" / "fixture-impact-particles.csv",
        "weight",
        "linear",
        "fixture",
        atlas,
    )
    build_manifest()
    print(
        "built data/map/phase2-display.geojson "
        f"({display['metadata']['display_point_count']:,} display points)"
    )
    print(
        f"built outputs/report.html "
        f"({(ROOT / 'outputs' / 'report.html').stat().st_size:,} bytes)"
    )


def compare_metrics(actual: dict[str, Any], expected: dict[str, Any], identifier: str) -> None:
    if actual["parts"] != expected["parts"] or actual["points"] != expected["points"]:
        raise PackageError(f"geometry structure mismatch for {identifier}: {actual} != {expected}")
    for actual_value, expected_value in zip(actual["bbox"], expected["bbox"]):
        if not math.isclose(actual_value, expected_value, abs_tol=1e-10):
            raise PackageError(f"geometry bounds mismatch for {identifier}: {actual['bbox']} != {expected['bbox']}")


def check_figure_set(stem: Path) -> None:
    svg = stem.with_suffix(".svg").read_text(encoding="utf-8")
    if "<svg" not in svg or "http://www.w3.org/2000/svg" not in svg:
        raise PackageError(f"invalid SVG: {stem.with_suffix('.svg').relative_to(ROOT)}")
    pdf = stem.with_suffix(".pdf").read_bytes()
    if not pdf.startswith(b"%PDF-") or len(pdf) < 10_000:
        raise PackageError(f"invalid PDF: {stem.with_suffix('.pdf').relative_to(ROOT)}")
    png = stem.with_suffix(".png").read_bytes()
    if not png.startswith(b"\x89PNG\r\n\x1a\n") or len(png) < 24:
        raise PackageError(f"invalid PNG: {stem.with_suffix('.png').relative_to(ROOT)}")
    width = int.from_bytes(png[16:20], "big")
    height = int.from_bytes(png[20:24], "big")
    if width < 2_000 or height < 1_000:
        raise PackageError(f"publication PNG is undersized: {width} by {height}")


def check_plan_run(label: str) -> None:
    directory = ROOT / "outputs" / f"planning-{label}"
    summary = read_json(directory / "plan-summary.json")
    if summary["scientific_boundary"] != {
        "ais_tracks_update_posterior": False,
        "approximate_outlines_update_posterior": False,
        "binary_exclusion_applied": False,
        "calibrated_search_optimization_ready": False,
        "negative_search_likelihood_applied": False,
    }:
        raise PackageError("planner scientific boundary changed")
    if summary["branch_status"] not in (
        "sensitivity_not_operational",
        "diagnostic_only",
        "numerically_unresolved_non_operational",
    ):
        raise PackageError("planner branch status is missing")
    if summary["method"]["selected_tile_count"] != 12:
        raise PackageError("planner did not select 12 tiles")
    for plan_name in ("posterior_only", "proxy_logistics_sensitivity"):
        plan_summary = summary["plans"][plan_name]
        if not math.isclose(plan_summary["selected_area_km2"], 7500.0):
            raise PackageError(f"incorrect planning area: {plan_name}")
        if not 0 < plan_summary["selected_posterior_mass"] <= 1:
            raise PackageError(f"invalid selected posterior mass: {plan_name}")

    for name, rank_key in (
        ("ordered-tiles-posterior-only.csv", "posterior_mass_per_km2"),
        ("ordered-tiles-proxy-logistics.csv", "proxy_logistics_priority"),
    ):
        with (directory / name).open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        if len(rows) <= 12:
            raise PackageError(f"planning ranking has no extension rows: {name}")
        if not math.isclose(
            math.fsum(float(row["posterior_mass"]) for row in rows),
            1.0,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise PackageError(f"planning grid mass is not normalized: {name}")
        for index, row in enumerate(rows, 1):
            if int(row[f"{rank_key}_rank"]) != index:
                raise PackageError(f"planning ranks are not contiguous: {name}")
            expected = "True" if index <= 12 else "False"
            if row[f"{rank_key}_within_budget"] != expected:
                raise PackageError(f"planning budget flag is wrong: {name} row {index}")

    selected = read_json(directory / "selected-tiles.geojson")
    if len(selected["features"]) != 24:
        raise PackageError("selected tile GeoJSON must contain both 12-tile plans")
    if any(
        feature["properties"]["negative_search_likelihood_applied"] is not False
        for feature in selected["features"]
    ):
        raise PackageError("selected tiles claim a negative-search likelihood")

    check_figure_set(directory / "search-plan")
    index = (directory / "index.html").read_text(encoding="utf-8")
    if any(
        token in index
        for token in ('<script src=', '<link rel="stylesheet"', '<img src="http')
    ):
        raise PackageError("planning report contains an external asset request")
    for phrase in ("Scientific boundary", "not an MH370 result", "7,500"):
        if label == "fixture" and phrase not in index:
            raise PackageError(f"planning report is missing required statement: {phrase}")

    manifest_path = directory / "run-manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    if b"/jackbox/" in manifest_bytes or b"/tmp/" in manifest_bytes:
        raise PackageError("planning manifest contains a host-specific path")
    manifest = json.loads(manifest_bytes)
    if manifest["generator_sha256"] != sha256_file(Path(__file__)):
        raise PackageError("planning manifest generator hash is stale")
    for artifact in manifest["outputs"]:
        path = ROOT / artifact["path"]
        if (
            sha256_file(path) != artifact["sha256"]
            or path.stat().st_size != artifact["bytes"]
        ):
            raise PackageError(f"planning manifest mismatch: {artifact['path']}")


def check() -> None:
    for path in ROOT.rglob("*"):
        if path.name in (".tmp", "__pycache__") or path.suffix == ".pyc":
            raise PackageError(
                f"temporary/cache path must not remain: {path.relative_to(ROOT)}"
            )

    for source in lock_sources():
        if not source.get("bundled"):
            continue
        path = ROOT / source["stored_path"]
        content = read_stored_content(source)
        verify_expected(source, content)
        if path.suffix == ".gz":
            header = path.read_bytes()[:10]
            if (
                len(header) != 10
                or header[4:8] != b"\x00\x00\x00\x00"
                or header[3] & 0x08
            ):
                raise PackageError(
                    f"gzip is not deterministic: {path.relative_to(ROOT)}"
                )

    for identifier, expected in EXPECTED_GEOMETRY.items():
        collection = load_source_geojson(identifier)
        if (
            collection.get("type") != "FeatureCollection"
            or len(collection.get("features", [])) != 1
        ):
            raise PackageError(f"invalid feature collection: {identifier}")
        compare_metrics(
            geometry_metrics(collection["features"][0]["geometry"]),
            expected,
            identifier,
        )

    bluefin = feature_collection("bluefin-21-area-searched-2014")
    if len(bluefin["features"]) != 2:
        raise PackageError("official Bluefin display source must contain two polygons")
    bluefin_area = math.fsum(
        geometry_area_km2(feature["geometry"]) for feature in bluefin["features"]
    )
    if not math.isclose(bluefin_area, 771.410285920366, abs_tol=1e-9):
        raise PackageError("official Bluefin display area changed")
    if len(feature_collection("seventh-arc-fl400")["features"]) != 1:
        raise PackageError("official seventh-arc reference changed")
    if len(feature_collection("initial-100nm-wide-area")["features"]) != 1:
        raise PackageError("official ±100 NM reference changed")

    capabilities = read_stored_content(
        source_by_id("ausseabed-wfs-capabilities")
    ).decode("utf-8")
    required_names = (
        "MH370_Phase_2_Sonar_Imagery_Backscatter_Inverse_Deep_Tow__SSS__5m_2018_L0_Coverage",
        "MH370_Phase_2_Sonar_Imagery_Backscatter_Wide_DHJ__SAS__5m_2018_L0_Coverage",
        "MH370_Phase_2_Sonar_Imagery_Backscatter_Wide_GoPhoenix__SAS__5m_2018_L0_Coverage",
    )
    if any(name not in capabilities for name in required_names):
        raise PackageError(
            "pinned WFS capability record is missing an expected Phase 2 feature"
        )
    if "Autonomous_Underwater_Vehicle__SSS__5m_2018_L0_Coverage" in capabilities:
        raise PackageError(
            "AUV L0 availability assertion must be reviewed: feature now appears in pin"
        )

    evidence = read_json(ROOT / "data" / "evidence-register.json")
    for record in evidence["records"]:
        if record.get("negative_search_eligible") is not False:
            raise PackageError(f"record is not explicitly ineligible: {record['id']}")
        if record.get("probability_of_detection") is not None:
            raise PackageError(
                f"numeric/non-null PoD was introduced without evidence: {record['id']}"
            )
    bluefin_record = next(
        record for record in evidence["records"] if record["id"] == "bluefin-artemis-2014"
    )
    if (
        bluefin_record["geometry"]
        != "official/bluefin-21-area-searched-2014.geojson"
        or bluefin_record["geometry_class"]
        != "official_display_footprint_not_mission_swaths"
    ):
        raise PackageError("Bluefin display geometry semantics changed")
    for identifier in ("ocean-infinity-2018", "ocean-infinity-2025-2026"):
        record = next(item for item in evidence["records"] if item["id"] == identifier)
        if record["geometry"] is not None:
            raise PackageError(f"unavailable exact geometry must remain null: {identifier}")
    if any(rule["negative_search_eligible"] for rule in evidence["proxy_rules"]):
        raise PackageError("a context proxy was marked elimination eligible")

    readiness = read_json(ROOT / "data" / "readiness.json")
    negative = readiness["negative_search_likelihood"]
    planning = readiness["planning_approximately_7500_km2"]
    if negative["status"] != "not_ready":
        raise PackageError("negative-search readiness is overstated")
    if (
        planning["spatial_planning_status"]
        != "ready_for_explicit_sensitivity_only"
        or planning["calibrated_search_optimization_status"] != "not_ready"
    ):
        raise PackageError("planning readiness boundary changed")
    if (
        planning["official_estimated_contract_area_km2"]
        - planning["official_approximate_surveyed_area_km2"]
        != planning["derived_arithmetic_remainder_km2"]
    ):
        raise PackageError("planning arithmetic is inconsistent")

    display = read_json(ROOT / "data" / "map" / "phase2-display.geojson")
    atlas = read_json(ROOT / "data" / "map" / "search-evidence-atlas.geojson")
    for derivative, name in ((display, "display"), (atlas, "atlas")):
        if derivative["metadata"].get("analysis_eligible") is not False:
            raise PackageError(f"{name} derivative is not analysis-ineligible")
        if any(
            feature["properties"].get("negative_search_eligible") is not False
            for feature in derivative["features"]
        ):
            raise PackageError(f"{name} feature is elimination-eligible")
    layers = {feature["properties"]["atlas_layer"] for feature in atlas["features"]}
    required_layers = {
        "phase2_deep",
        "phase2_coarse",
        "phase2_extent",
        "bluefin",
        "oi2018_proxy",
        "oi2024_outboard_proxy",
        "oi2024_inboard_proxy",
        "seventh_arc",
        "wide_area_context",
        "ais_proxy",
    }
    if not required_layers.issubset(layers):
        raise PackageError("evidence atlas is missing a required layer")

    inventory = read_json(ROOT / "data" / "area-inventory.json")
    bluefin_inventory = next(
        row for row in inventory["rows"] if row["id"] == "bluefin-artemis-2014"
    )
    if not math.isclose(
        bluefin_inventory["reported_minus_display_km2"],
        88.589714,
        abs_tol=1e-6,
    ):
        raise PackageError("Bluefin plotted/unplotted accounting changed")
    if inventory["rounding"]["expression"] != "15,000 - 7,571 = 7,429 km2":
        raise PackageError("contract-area rounding statement changed")

    report_path = ROOT / "outputs" / "report.html"
    report = report_path.read_text(encoding="utf-8")
    if any(
        token in report
        for token in ('<script src=', '<link rel="stylesheet"', '<img src="http')
    ):
        raise PackageError("report contains an external asset request")
    for phrase in (
        "no binary elimination mask",
        "No swaths were invented",
        "7,429",
        "SENSITIVITY READY",
    ):
        if phrase not in report:
            raise PackageError(f"report is missing required statement: {phrase}")
    if report_path.stat().st_size > 5 * 1024 * 1024:
        raise PackageError("self-contained report exceeds 5 MiB")

    atlas_html = (ROOT / "outputs" / "evidence-atlas.html").read_text(
        encoding="utf-8"
    )
    if any(
        token in atlas_html
        for token in ('<script src=', '<link rel="stylesheet"', '<img src="http')
    ):
        raise PackageError("atlas report contains an external asset request")
    for phrase in ("Scientific boundary", "771.410", "7,429"):
        if phrase not in atlas_html:
            raise PackageError(f"atlas is missing required statement: {phrase}")
    check_figure_set(ROOT / "outputs" / "evidence-atlas")
    check_plan_run("fixture")

    manifest = read_json(ROOT / "provenance" / "build-manifest.json")
    if manifest["generator_sha256"] != sha256_file(Path(__file__)):
        raise PackageError("build manifest generator hash is stale")
    for group in ("inputs", "outputs"):
        for artifact in manifest[group]:
            path = ROOT / artifact["path"]
            if (
                sha256_file(path) != artifact["sha256"]
                or path.stat().st_size != artifact["bytes"]
            ):
                raise PackageError(f"build manifest mismatch: {artifact['path']}")

    print("check ok")
    for identifier in EXPECTED_GEOMETRY:
        metrics = geometry_metrics(
            load_source_geojson(identifier)["features"][0]["geometry"]
        )
        print(
            f"  {identifier}: {metrics['parts']:,} parts, "
            f"{metrics['points']:,} points"
        )
    print("  Bluefin: 2 official display polygons; exact mission swaths unresolved")
    print("  exact OI AUV swaths: unresolved; grade-C context only")
    print("  quality / holidays / PoD: unresolved")
    print("  negative-search likelihood: not ready")
    print("  7,500 km2 planner: deterministic sensitivity interface ready")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=(
            "acquire",
            "build",
            "check",
            "all",
            "plan",
            "verify-references",
        ),
        help="operation to perform",
    )
    parser.add_argument(
        "--particles",
        type=Path,
        help="weighted impact-particle CSV for the plan command",
    )
    parser.add_argument(
        "--weight-column",
        default="weight",
        help="linear or log-weight column in the particle CSV",
    )
    parser.add_argument(
        "--weight-mode",
        choices=("linear", "log"),
        default="linear",
    )
    parser.add_argument(
        "--label",
        default="release-impact",
        help="lowercase output label used under outputs/planning-<label>",
    )
    parser.add_argument(
        "--branch-status",
        choices=(
            "sensitivity-not-operational",
            "diagnostic-only",
            "numerically-unresolved-non-operational",
        ),
        default="sensitivity-not-operational",
        help="explicit scientific status attached to this conditional plan",
    )
    parser.add_argument(
        "--status-note",
        default="",
        help="short branch-specific ESS/support or interpretation warning",
    )
    args = parser.parse_args()
    try:
        if args.command in ("acquire", "all"):
            acquire()
        if args.command in ("build", "all"):
            build()
        if args.command in ("check", "all"):
            check()
        if args.command == "verify-references":
            verify_references()
        if args.command == "plan":
            if args.particles is None:
                raise PackageError("plan requires --particles")
            plan(
                args.particles,
                args.weight_column,
                args.weight_mode,
                args.label,
                branch_status=args.branch_status.replace("-", "_"),
                status_note=args.status_note,
            )
            check_plan_run(args.label)
    except (PackageError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
