#!/usr/bin/env python3
"""Build reproducible GeoJSON areas of interest for historical AIS retrieval.

The user-facing upload files are conventional GeoJSON FeatureCollections.
Separate ``*-geometry.json`` files contain bare Polygon objects whose ``type``
and ``coordinates`` members can be copied directly into Spire/Kpler API
queries. The large seventh-arc corridor is also split into a FeatureCollection
of sub-50,000 km2 tiles for the Historical Vessel Points/Tracks service.

Longitude precedes latitude throughout, as required by GeoJSON.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = DATA / "spire-aois"
ARC_PATH = DATA / "seventh_arc_fl400.geojson"

EARTH_RADIUS_KM = 6371.0088
KM_PER_NM = 1.852
CORRIDOR_HALF_WIDTH_NM = 100.0
NORTHERN_LIMIT_DEG = -20.0
MAXIMUM_CENTRELINE_LATITUDE_DEG = -45.0
MAXIMUM_DENSIFIED_STEP_KM = 15.0
TILE_LENGTH_KM = 100.0
SPIRE_MAXIMUM_REQUEST_AREA_KM2 = 50_000.0

HUZZAS_OPERATIONAL_RING = [
    [114.8138754, -20.58733899],
    [115.0753119, -20.85470804],
    [115.0295099, -20.89421945],
    [115.08704, -20.95310347],
    [115.0391446, -20.99439869],
    [115.1305689, -21.08788911],
    [114.7285102, -21.4809714],
    [114.5768772, -21.54177143],
    [114.4532048, -21.41589336],
    [114.4252723, -21.43994645],
    [114.3653754, -21.37886497],
    [114.3031422, -21.44036465],
    [114.2763645, -21.41301544],
    [114.1654904, -21.52135929],
    [114.0156687, -21.36807367],
]


def wrap_longitude(longitude_deg: float) -> float:
    return (longitude_deg + 180.0) % 360.0 - 180.0


def inverse_sphere(first: list[float], second: list[float]) -> tuple[float, float]:
    """Return great-circle distance kilometres and initial bearing degrees."""
    lon_1, lat_1 = map(math.radians, first)
    lon_2, lat_2 = map(math.radians, second)
    delta_lon = math.radians(wrap_longitude(math.degrees(lon_2 - lon_1)))
    delta_lat = lat_2 - lat_1
    haversine = (
        math.sin(delta_lat / 2.0) ** 2
        + math.cos(lat_1) * math.cos(lat_2) * math.sin(delta_lon / 2.0) ** 2
    )
    angular = 2.0 * math.asin(min(1.0, math.sqrt(haversine)))
    bearing = math.atan2(
        math.sin(delta_lon) * math.cos(lat_2),
        math.cos(lat_1) * math.sin(lat_2)
        - math.sin(lat_1) * math.cos(lat_2) * math.cos(delta_lon),
    )
    return EARTH_RADIUS_KM * angular, math.degrees(bearing) % 360.0


def direct_sphere(point: list[float], bearing_deg: float, distance_km: float) -> list[float]:
    """Project a point over a spherical Earth and return [longitude, latitude]."""
    longitude, latitude = map(math.radians, point)
    bearing = math.radians(bearing_deg)
    angular = distance_km / EARTH_RADIUS_KM
    result_latitude = math.asin(
        math.sin(latitude) * math.cos(angular)
        + math.cos(latitude) * math.sin(angular) * math.cos(bearing)
    )
    result_longitude = longitude + math.atan2(
        math.sin(bearing) * math.sin(angular) * math.cos(latitude),
        math.cos(angular) - math.sin(latitude) * math.sin(result_latitude),
    )
    return [
        wrap_longitude(math.degrees(result_longitude)),
        math.degrees(result_latitude),
    ]


def point_between(first: list[float], second: list[float], fraction: float) -> list[float]:
    distance_km, bearing_deg = inverse_sphere(first, second)
    return direct_sphere(first, bearing_deg, fraction * distance_km)


def crossing_at_latitude(
    first: list[float], second: list[float], target_latitude_deg: float
) -> list[float]:
    """Bisect a monotonic short great-circle segment at the requested latitude."""
    low, high = 0.0, 1.0
    increasing = second[1] > first[1]
    for _ in range(60):
        middle = (low + high) / 2.0
        point = point_between(first, second, middle)
        before_target = point[1] < target_latitude_deg
        if before_target == increasing:
            low = middle
        else:
            high = middle
    point = point_between(first, second, (low + high) / 2.0)
    point[1] = target_latitude_deg
    return point


def load_southern_arc() -> list[list[float]]:
    document = json.loads(ARC_PATH.read_text(encoding="utf-8"))
    coordinates = document["features"][0]["geometry"]["coordinates"]
    start_index = next(
        index
        for index in range(1, len(coordinates))
        if coordinates[index - 1][1] > NORTHERN_LIMIT_DEG
        and coordinates[index][1] <= NORTHERN_LIMIT_DEG
    )
    start = crossing_at_latitude(
        coordinates[start_index - 1], coordinates[start_index], NORTHERN_LIMIT_DEG
    )
    selected = [start, *coordinates[start_index:]]
    # The official FL400 reference ends near 43.91 S. This guard would clip a
    # future replacement source if it extends south of the requested 45 S.
    for index in range(1, len(selected)):
        if selected[index][1] < MAXIMUM_CENTRELINE_LATITUDE_DEG:
            return [
                *selected[:index],
                crossing_at_latitude(
                    selected[index - 1],
                    selected[index],
                    MAXIMUM_CENTRELINE_LATITUDE_DEG,
                ),
            ]
    return selected


def densify(line: list[list[float]]) -> list[list[float]]:
    result = [line[0]]
    for first, second in zip(line, line[1:]):
        distance_km, bearing_deg = inverse_sphere(first, second)
        steps = max(1, math.ceil(distance_km / MAXIMUM_DENSIFIED_STEP_KM))
        result.extend(
            direct_sphere(first, bearing_deg, distance_km * step / steps)
            for step in range(1, steps + 1)
        )
    return result


def cumulative_distances(line: list[list[float]]) -> list[float]:
    result = [0.0]
    for first, second in zip(line, line[1:]):
        result.append(result[-1] + inverse_sphere(first, second)[0])
    return result


def offset_edges(line: list[list[float]]) -> tuple[list[list[float]], list[list[float]]]:
    half_width_km = CORRIDOR_HALF_WIDTH_NM * KM_PER_NM
    left, right = [], []
    for index, point in enumerate(line):
        if index == 0:
            tangent = inverse_sphere(point, line[index + 1])[1]
        elif index == len(line) - 1:
            tangent = (inverse_sphere(point, line[index - 1])[1] + 180.0) % 360.0
        else:
            tangent = inverse_sphere(line[index - 1], line[index + 1])[1]
        left.append(direct_sphere(point, tangent - 90.0, half_width_km))
        right.append(direct_sphere(point, tangent + 90.0, half_width_km))
    return left, right


def ring_from_edges(
    left: list[list[float]], right: list[list[float]]
) -> list[list[float]]:
    ring = [*left, *reversed(right), left[0]]
    return counter_clockwise(
        [[round(value, 8) for value in point] for point in ring]
    )


def counter_clockwise(ring: list[list[float]]) -> list[list[float]]:
    """Return a closed exterior ring in RFC 7946's recommended winding order."""
    signed_area = sum(
        longitude_1 * latitude_2 - longitude_2 * latitude_1
        for (longitude_1, latitude_1), (longitude_2, latitude_2)
        in zip(ring, ring[1:])
    ) / 2.0
    return list(reversed(ring)) if signed_area < 0.0 else ring


def spherical_area_km2(ring: list[list[float]]) -> float:
    """Approximate polygon area using the Chamberlain-Duquette spherical form."""
    total = 0.0
    for first, second in zip(ring, ring[1:]):
        lon_1, lat_1 = map(math.radians, first)
        lon_2, lat_2 = map(math.radians, second)
        delta_lon = math.radians(wrap_longitude(math.degrees(lon_2 - lon_1)))
        total += delta_lon * (2.0 + math.sin(lat_1) + math.sin(lat_2))
    return abs(total) * EARTH_RADIUS_KM**2 / 2.0


def bounds(ring: list[list[float]]) -> list[float]:
    longitudes = [point[0] for point in ring]
    latitudes = [point[1] for point in ring]
    return [min(longitudes), min(latitudes), max(longitudes), max(latitudes)]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def write_json(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def feature_collection(name: str, geometry: dict, properties: dict) -> dict:
    """Wrap a geometry in the conservative file-upload form used by GIS tools."""
    return {
        "type": "FeatureCollection",
        "name": name,
        "features": [
            {
                "type": "Feature",
                "properties": {"name": name, **properties},
                "geometry": geometry,
            }
        ],
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    huzzas_ring = counter_clockwise(
        [*HUZZAS_OPERATIONAL_RING, HUZZAS_OPERATIONAL_RING[0]]
    )
    huzzas_geometry = {"type": "Polygon", "coordinates": [huzzas_ring]}
    huzzas_path = OUTPUT / "huzzas-geo-caspian-operational-area.geojson"
    huzzas_geometry_path = OUTPUT / "huzzas-geo-caspian-operational-area-geometry.json"
    write_json(
        huzzas_path,
        feature_collection(
            "Huzzas Geo Caspian operational area",
            huzzas_geometry,
            {
                "source": "NOPSEMA Huzzas environmental-plan operational polygon",
                "purpose": "Historical AIS retrieval for Geo Caspian and support vessels",
            },
        ),
    )
    write_json(huzzas_geometry_path, huzzas_geometry)

    centreline = densify(load_southern_arc())
    chainages = cumulative_distances(centreline)
    left_edge, right_edge = offset_edges(centreline)
    full_ring = ring_from_edges(left_edge, right_edge)
    full_geometry = {"type": "Polygon", "coordinates": [full_ring]}
    full_path = OUTPUT / "seventh-arc-100nm-corridor.geojson"
    full_geometry_path = OUTPUT / "seventh-arc-100nm-corridor-geometry.json"
    write_json(
        full_path,
        feature_collection(
            "MH370 seventh arc corridor plus or minus 100 NM",
            full_geometry,
            {
                "source": "ATSB official reference seventh arc at FL400",
                "centreline_northern_limit_deg": NORTHERN_LIMIT_DEG,
                "centreline_southern_endpoint_deg": round(centreline[-1][1], 8),
                "corridor_half_width_nm": CORRIDOR_HALF_WIDTH_NM,
            },
        ),
    )
    write_json(full_geometry_path, full_geometry)

    total_length_km = chainages[-1]
    # Boundary indices are points on the already constructed full edges. This
    # makes adjacent tiles share exactly the same cross-section and therefore
    # prevents slivers, gaps or overlaps when their query results are merged.
    tile_boundary_indices = [0]
    for index, chainage in enumerate(chainages[1:], start=1):
        if chainage - chainages[tile_boundary_indices[-1]] >= TILE_LENGTH_KM:
            tile_boundary_indices.append(index)
    if tile_boundary_indices[-1] != len(centreline) - 1:
        tile_boundary_indices.append(len(centreline) - 1)
    features = []
    for index, (start_index, end_index) in enumerate(
        zip(tile_boundary_indices, tile_boundary_indices[1:]), start=1
    ):
        start_km = chainages[start_index]
        end_km = chainages[end_index]
        ring = ring_from_edges(
            left_edge[start_index : end_index + 1],
            right_edge[start_index : end_index + 1],
        )
        area_km2 = spherical_area_km2(ring)
        if area_km2 >= SPIRE_MAXIMUM_REQUEST_AREA_KM2:
            raise RuntimeError(
                f"tile {index:03d} area {area_km2:.1f} km2 exceeds Spire limit"
            )
        features.append(
            {
                "type": "Feature",
                "properties": {
                    "tile_id": f"seventh-arc-{index:03d}",
                    "centreline_start_km": round(start_km, 3),
                    "centreline_end_km": round(end_km, 3),
                    "centreline_length_km": round(end_km - start_km, 3),
                    "corridor_half_width_nm": CORRIDOR_HALF_WIDTH_NM,
                    "approximate_area_km2": round(area_km2, 1),
                },
                "geometry": {"type": "Polygon", "coordinates": [ring]},
            }
        )
    tiles_path = OUTPUT / "seventh-arc-100nm-corridor-query-tiles.geojson"
    write_json(tiles_path, {"type": "FeatureCollection", "features": features})

    huzzas_area = spherical_area_km2(huzzas_ring)
    full_area = spherical_area_km2(full_ring)
    manifest_path = OUTPUT / "manifest.json"
    manifest = {
        "coordinate_reference_system": "OGC:CRS84 / WGS84 longitude-latitude degrees",
        "geojson_coordinate_order": "longitude, latitude",
        "generated_by": "code/build_spire_aois.py",
        "source_arc": str(ARC_PATH.relative_to(HERE)),
        "source_arc_sha256": sha256(ARC_PATH),
        "recommended_query_windows_utc": {
            "seventh_arc_primary_impact_window": [
                "2014-03-08T00:19:37Z",
                "2014-03-08T00:49:37Z",
            ],
            "seventh_arc_padded_retrieval_window": [
                "2014-03-08T00:00:00Z",
                "2014-03-08T01:00:00Z",
            ],
            "huzzas_track_context": [
                "2014-03-07T22:00:00Z",
                "2014-03-08T03:00:00Z",
            ],
        },
        "areas": {
            "huzzas_geo_caspian_operational_area": {
                "file": huzzas_path.name,
                "api_geometry_file": huzzas_geometry_path.name,
                "approximate_area_km2": round(huzzas_area, 1),
                "bounds": bounds(huzzas_ring),
                "source": "NOPSEMA Huzzas environmental-plan operational polygon",
            },
            "seventh_arc_100nm_corridor": {
                "file": full_path.name,
                "api_geometry_file": full_geometry_path.name,
                "centreline_northern_latitude_deg": centreline[0][1],
                "centreline_southern_latitude_deg": centreline[-1][1],
                "centreline_length_km": round(total_length_km, 1),
                "corridor_half_width_nm": CORRIDOR_HALF_WIDTH_NM,
                "approximate_area_km2": round(full_area, 1),
                "bounds": bounds(full_ring),
                "query_limit_note": "Too large for one HVP/HVT spatiotemporal request; use tiles.",
            },
            "seventh_arc_query_tiles": {
                "file": tiles_path.name,
                "feature_count": len(features),
                "maximum_tile_area_km2": max(
                    feature["properties"]["approximate_area_km2"]
                    for feature in features
                ),
                "documented_spire_request_limit_km2": SPIRE_MAXIMUM_REQUEST_AREA_KM2,
            },
        },
    }
    write_json(manifest_path, manifest)

    for path in (
        huzzas_path,
        huzzas_geometry_path,
        full_path,
        full_geometry_path,
        tiles_path,
    ):
        json.loads(path.read_text(encoding="utf-8"))
    if not 5_000.0 < huzzas_area < 7_000.0:
        raise RuntimeError(f"unexpected Huzzas polygon area: {huzzas_area:.1f} km2")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
