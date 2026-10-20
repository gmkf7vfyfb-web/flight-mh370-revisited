#!/usr/bin/env python3
"""Build a source-graded MH370 searched-area evidence package.

The script deliberately keeps three concepts separate:
  1. a published search target or outline,
  2. spatial coverage actually acquired, and
  3. probability of detecting an aircraft debris field conditional on coverage.

It uses the public Geoscience Australia Phase-2 tile alpha channel as the
highest-fidelity open footprint for the 2014-2017 high-resolution sonar search.
Ocean Infinity AUV footprints have not been released publicly; those layers are
therefore marked as approximate and must not be treated as exact binary masks.
"""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
from collections import defaultdict
from pathlib import Path

import contourpy
import numpy as np
import pandas as pd
from PIL import Image
from lxml import etree


ROOT = Path(__file__).resolve().parent
SOURCE_ROOT = Path("/tmp/mh370-search-sources")
OUT = ROOT / "outputs" / "mh370_search_evidence"
OUT.mkdir(parents=True, exist_ok=True)

EARTH_RADIUS_KM = 6371.0088


def write_json(path: Path, obj: object, *, indent: int | None = 2) -> None:
    path.write_text(json.dumps(obj, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")


def close_ring(ring: list[list[float]]) -> list[list[float]]:
    if ring and ring[0] != ring[-1]:
        ring = ring + [ring[0]]
    return ring


def spherical_ring_area_km2(ring: list[list[float]]) -> float:
    """Signed Chamberlain-Duquette area for a lon/lat ring."""
    ring = close_ring(ring)
    acc = 0.0
    for (lon1, lat1), (lon2, lat2) in zip(ring, ring[1:]):
        dlon = math.radians(lon2 - lon1)
        if dlon > math.pi:
            dlon -= 2 * math.pi
        elif dlon < -math.pi:
            dlon += 2 * math.pi
        acc += dlon * (2 + math.sin(math.radians(lat1)) + math.sin(math.radians(lat2)))
    return -0.5 * EARTH_RADIUS_KM**2 * acc


def geometry_area_km2(geometry: dict) -> float:
    if geometry["type"] == "Polygon":
        return abs(sum(spherical_ring_area_km2(r) for r in geometry["coordinates"]))
    if geometry["type"] == "MultiPolygon":
        return sum(abs(sum(spherical_ring_area_km2(r) for r in poly)) for poly in geometry["coordinates"])
    return 0.0


def point_in_ring(x: float, y: float, ring: list[list[float]]) -> bool:
    inside = False
    xj, yj = ring[-1]
    for xi, yi in ring:
        if (yi > y) != (yj > y):
            x_at_y = (xj - xi) * (y - yi) / ((yj - yi) or 1e-300) + xi
            if x < x_at_y:
                inside = not inside
        xj, yj = xi, yi
    return inside


def points_in_ring(points: np.ndarray, ring: list[list[float]]) -> np.ndarray:
    x = points[:, 0]
    y = points[:, 1]
    inside = np.zeros(len(points), dtype=bool)
    xj, yj = ring[-1]
    for xi, yi in ring:
        crossing = ((yi > y) != (yj > y)) & (x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-300) + xi)
        inside ^= crossing
        xj, yj = xi, yi
    return inside


def copy_with_properties(feature: dict, extra: dict) -> dict:
    return {
        "type": "Feature",
        "properties": {**feature.get("properties", {}), **extra},
        "geometry": feature["geometry"],
    }


def rounded_geojson(obj: object, digits: int = 4) -> object:
    """Round coordinate-like floats for compact display copies, preserving source files."""
    if isinstance(obj, float):
        return round(obj, digits)
    if isinstance(obj, list):
        return [rounded_geojson(value, digits) for value in obj]
    if isinstance(obj, dict):
        return {key: rounded_geojson(value, digits) for key, value in obj.items()}
    return obj


def load_phase2_mask() -> tuple[np.ndarray, dict]:
    zoom = 8
    x0, x1 = 187, 201
    y0, y1 = 144, 160
    mask = np.zeros(((y1 - y0 + 1) * 256, (x1 - x0 + 1) * 256), dtype=np.uint8)
    valid_tiles = 0
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            path = SOURCE_ROOT / "phase2-z8" / f"{x}-{y}.png"
            try:
                alpha = np.asarray(Image.open(path).convert("RGBA"))[:, :, 3]
            except Exception:
                continue
            valid_tiles += 1
            r0, c0 = (y - y0) * 256, (x - x0) * 256
            mask[r0 : r0 + 256, c0 : c0 + 256] = alpha > 0

    n = 2**zoom
    area_km2 = 0.0
    for local_y in range(mask.shape[0]):
        global_y = y0 * 256 + local_y
        lat_top = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * global_y / (n * 256)))))
        lat_bottom = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (global_y + 1) / (n * 256)))))
        dlon = 2 * math.pi / (n * 256)
        pixel_area = EARTH_RADIUS_KM**2 * dlon * abs(
            math.sin(math.radians(lat_top)) - math.sin(math.radians(lat_bottom))
        )
        area_km2 += int(mask[local_y].sum()) * pixel_area

    georef = {
        "source": "Geoscience Australia public MH370 Phase-2 5 m web-tile alpha channel",
        "template_url": "https://mh370-tiles.ausseabed.gov.au/MH370_Phase2_5m_WGS84/L{level}R{row}C{col}.png",
        "web_mercator_zoom": zoom,
        "tile_x_min": x0,
        "tile_x_max": x1,
        "tile_y_min": y0,
        "tile_y_max": y1,
        "tile_size_pixels": 256,
        "mask_width_pixels": int(mask.shape[1]),
        "mask_height_pixels": int(mask.shape[0]),
        "valid_nonblank_tiles": valid_tiles,
        "coverage_area_km2_spherical_pixel_sum": area_km2,
        "query_formula": {
            "global_pixel_x": "floor((lon_deg + 180) / 360 * 2^zoom * 256)",
            "global_pixel_y": "floor((1 - asinh(tan(lat_rad))/pi) / 2 * 2^zoom * 256)",
            "local_x": f"global_pixel_x - {x0 * 256}",
            "local_y": f"global_pixel_y - {y0 * 256}",
            "covered": "mask[local_y, local_x] > 0",
        },
        "interpretation": "Published high-resolution Phase-2 data footprint, not a uniform probability-of-detection field.",
    }
    return mask, georef


def pixel_to_lonlat(x: float, y: float, georef: dict) -> list[float]:
    zoom = georef["web_mercator_zoom"]
    npx = 2**zoom * 256
    gx = georef["tile_x_min"] * 256 + x + 0.5
    gy = georef["tile_y_min"] * 256 + y + 0.5
    lon = gx / npx * 360.0 - 180.0
    lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * gy / npx))))
    return [round(lon, 6), round(lat, 6)]


def mask_to_multipolygon(mask: np.ndarray, georef: dict) -> dict:
    generator = contourpy.contour_generator(z=mask.astype(float), line_type="Separate")
    contours = generator.lines(0.5)
    positive: list[tuple[float, list[list[float]]]] = []
    negative: list[tuple[float, list[list[float]]]] = []
    for contour in contours:
        if len(contour) < 4:
            continue
        signed_pixel_area = 0.5 * float(
            np.sum(contour[:-1, 0] * contour[1:, 1] - contour[1:, 0] * contour[:-1, 1])
        )
        ring = close_ring([pixel_to_lonlat(float(x), float(y), georef) for x, y in contour])
        # Pixel y increases southward, so reversing restores GeoJSON right-hand orientation.
        ring = list(reversed(ring))
        if signed_pixel_area > 0:
            positive.append((abs(signed_pixel_area), ring))
        else:
            negative.append((abs(signed_pixel_area), ring))

    positive.sort(reverse=True, key=lambda item: item[0])
    polygons = [[ring] for _, ring in positive]
    for _, hole in negative:
        cx = sum(p[0] for p in hole[:-1]) / max(1, len(hole) - 1)
        cy = sum(p[1] for p in hole[:-1]) / max(1, len(hole) - 1)
        containers = [
            (idx, outer_area)
            for idx, (outer_area, outer_ring) in enumerate(positive)
            if point_in_ring(cx, cy, outer_ring)
        ]
        if containers:
            idx = min(containers, key=lambda item: item[1])[0]
            polygons[idx].append(hole)

    return {"type": "MultiPolygon", "coordinates": polygons}


def kml_named_lines(path: Path, wanted: set[str]) -> dict[str, list[list[list[float]]]]:
    tree = etree.parse(str(path))
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    found: dict[str, list[list[list[float]]]] = defaultdict(list)
    for placemark in tree.xpath("//k:Placemark", namespaces=ns):
        name = " ".join(placemark.xpath("./k:name/text()", namespaces=ns)).strip()
        if name not in wanted:
            continue
        for raw in placemark.xpath(".//k:coordinates/text()", namespaces=ns):
            line = []
            for token in raw.split():
                lon, lat, *_ = map(float, token.split(","))
                line.append([round(lon, 6), round(lat, 6)])
            found[name].append(line)
    return found


def extract_station_track(path: Path, *, label: str, date_start: str, date_end: str) -> dict:
    tree = etree.parse(str(path))
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    points = []
    for placemark in tree.xpath("//k:Placemark[position()>1]", namespaces=ns):
        name = " ".join(placemark.xpath("./k:name/text()", namespaces=ns)).strip()
        raw = placemark.xpath(".//k:Point/k:coordinates/text()", namespaces=ns)
        speed_match = re.search(r"([0-9.]+)kts", name)
        if not raw or not speed_match or not (date_start <= name[:10] <= date_end):
            continue
        lon, lat, *_ = map(float, raw[0].strip().split(","))
        speed = float(speed_match.group(1))
        if -37 <= lat <= -32 and 90 <= lon <= 97 and speed <= 6:
            points.append([round(lon, 5), round(lat, 5)])
    return {
        "type": "Feature",
        "properties": {
            "id": label,
            "name": label,
            "evidence_type": "surface-vessel AIS track proxy",
            "source_grade": "C",
            "warning": "Launch/recovery vessel positions are not AUV sonar swaths and cannot be used as a binary search mask.",
        },
        "geometry": {"type": "LineString", "coordinates": points},
    }


mask, georef = load_phase2_mask()
Image.fromarray(mask * 255, mode="L").save(OUT / "atsb_phase2_coverage_mask_z8.png", optimize=True)
write_json(OUT / "atsb_phase2_coverage_mask_georef.json", georef)
atsb_geometry = mask_to_multipolygon(mask, georef)

arcgis_dir = SOURCE_ROOT / "arcgis"
arc = json.loads((arcgis_dir / "arc.geojson").read_text())
bluefin = json.loads((arcgis_dir / "bluefin.geojson").read_text())
wide = json.loads((arcgis_dir / "wide.geojson").read_text())
surface = json.loads((arcgis_dir / "surface.geojson").read_text())
land = json.loads((arcgis_dir / "context-land.geojson").read_text())

third_party_kml = SOURCE_ROOT / "search-areas-kml" / "doc.kml"
kml = kml_named_lines(
    third_party_kml,
    {"Ocean Infinity 2018 search", "Ocean Infinity proposed 2024 area"},
)
oi2018_ring = close_ring(kml["Ocean Infinity 2018 search"][0])
oi2024_rings = [close_ring(line) for line in kml["Ocean Infinity proposed 2024 area"]]
oi2018_outline_area = abs(spherical_ring_area_km2(oi2018_ring))
oi2024_areas = [abs(spherical_ring_area_km2(ring)) for ring in oi2024_rings]

features = []
features.append(
    {
        "type": "Feature",
        "properties": {
            "id": "atsb_phase2_2014_2017",
            "name": "ATSB-led high-resolution sonar search (2014–2017)",
            "status": "searched",
            "geometry_quality": "A: official published data footprint",
            "source_grade": "A",
            "published_area_km2": 120000,
            "derived_geometry_area_km2": round(georef["coverage_area_km2_spherical_pixel_sum"], 1),
            "model_role": "seabed non-detection likelihood",
            "detection_note": "ATSB stated >95% overall debris-field detection confidence; explicit LPD and holiday cells require lower values.",
        },
        "geometry": atsb_geometry,
    }
)
for idx, feature in enumerate(bluefin["features"], 1):
    features.append(
        copy_with_properties(
            feature,
            {
                "id": f"bluefin21_2014_{idx}",
                "name": "Bluefin-21 seafloor sonar search (2014)",
                "status": "searched",
                "geometry_quality": "A: official ArcGIS story-map geometry",
                "source_grade": "A",
                "model_role": "seabed non-detection likelihood",
            },
        )
    )

features.append(
    {
        "type": "Feature",
        "properties": {
            "id": "oi2018_total_outline_approx",
            "name": "Ocean Infinity 2018 total-search outline (approximate)",
            "status": "searched, including post-contract extension",
            "geometry_quality": "C: reconstructed outline, checked against official weekly maps and totals",
            "source_grade": "C",
            "published_mapped_area_km2": 120000,
            "outline_area_km2": round(oi2018_outline_area, 1),
            "nominal_uniform_coverage_fraction": round(120000 / oi2018_outline_area, 4),
            "model_role": "uncertain-coverage seabed non-detection likelihood",
            "warning": "Do not treat the outline as a fully covered binary polygon; exact AUV swaths are not public.",
        },
        "geometry": {"type": "Polygon", "coordinates": [oi2018_ring]},
    }
)

oi2024_meta = [
    {
        "id": "oi2024_proposed_outboard_southeast",
        "name": "Renewed-search proposed outboard/southeast band",
        "status": "likely substantially searched by Jan 2026, including pre-contract work",
        "remaining_likelihood": "low-to-moderate",
        "inference": "Community vessel tracking indicates the outboard band was traversed; exact AUV coverage remains unpublished.",
    },
    {
        "id": "oi2024_proposed_inboard_northwest",
        "name": "Renewed-search proposed inboard/northwest band",
        "status": "most likely concentration of the official remaining area",
        "remaining_likelihood": "high",
        "inference": "The official residual is 7,428.54 km²; this uncompleted-looking band is about 6,100 km² in the approximate reconstruction, with the balance plausibly in infill/gaps or boundary differences.",
    },
]
for ring, area, props in zip(oi2024_rings, oi2024_areas, oi2024_meta):
    features.append(
        {
            "type": "Feature",
            "properties": {
                **props,
                "geometry_quality": "C: traced from Ocean Infinity's March 2024 presentation by community analysts",
                "source_grade": "C",
                "approx_outline_area_km2": round(area, 1),
                "model_role": "uncertain current-search status; marginalize footprint",
                "warning": "Not an official contract polygon and not an AUV swath polygon.",
            },
            "geometry": {"type": "Polygon", "coordinates": [ring]},
        }
    )

for feature in arc["features"]:
    features.append(
        copy_with_properties(
            feature,
            {
                "id": "seventh_arc_fl400",
                "name": "Official reference 7th arc at FL400",
                "status": "reference only",
                "source_grade": "A",
                "model_role": "geometric reference, not a search footprint",
            },
        )
    )
for feature in wide["features"]:
    features.append(
        copy_with_properties(
            feature,
            {
                "id": "initial_100nm_wide_area_context",
                "name": "Initial ±100 NM wide-area/glide context",
                "status": "context only; not fully searched",
                "source_grade": "A",
                "model_role": "support/context only",
                "warning": "This official planning envelope must not be interpreted as searched seafloor.",
            },
        )
    )

footprints = {"type": "FeatureCollection", "features": features}
write_json(OUT / "search_footprints.geojson", footprints, indent=None)

for feature in surface["features"]:
    feature["properties"].update(
        {
            "evidence_type": "daily surface/aerial search box",
            "source_grade": "A",
            "model_role": "drift-conditioned surface-debris observation only",
        }
    )
write_json(OUT / "surface_search_2014_official.geojson", surface, indent=None)
write_json(OUT / "context_land.geojson", land, indent=None)

tracks = {
    "type": "FeatureCollection",
    "features": [
        extract_station_track(
            SOURCE_ROOT / "phase1" / "kml" / "doc.kml",
            label="OI pre-contract vessel proxy: 23–28 Feb 2025",
            date_start="2025-02-23",
            date_end="2025-02-28",
        ),
        extract_station_track(
            SOURCE_ROOT / "phase2" / "ARMADA 78 06 - Phase 2 -2025-03-06-to-2025-04-08-MH370-CAPTION.net.kml",
            label="OI pre-contract vessel proxy: 11–24 Mar 2025",
            date_start="2025-03-11",
            date_end="2025-03-24",
        ),
        extract_station_track(
            SOURCE_ROOT / "phase2" / "ARMADA 78 06 - Phase 2 -2025-03-06-to-2025-04-08-MH370-CAPTION.net.kml",
            label="OI contracted vessel proxy: 25–28 Mar 2025",
            date_start="2025-03-25",
            date_end="2025-03-28",
        ),
        extract_station_track(
            SOURCE_ROOT / "phase3" / "ARMADA 86 05 - Phase 3 - 2025-12-30-to-2026-01-23-MH370-CAPTION.net.kml",
            label="OI contracted vessel proxy: 31 Dec 2025–23 Jan 2026",
            date_start="2025-12-31",
            date_end="2026-01-23",
        ),
    ],
}
write_json(OUT / "oi_2025_2026_vessel_track_proxies.geojson", tracks, indent=None)


inventory_rows = [
    {
        "campaign_id": "surface_sio_2014",
        "dates": "2014-03-18 to 2014-04-28",
        "operator": "AMSA-led multinational force",
        "modality": "aircraft and vessel visual/radar surface search",
        "published_or_reported_area_km2": "about 4,500,000",
        "geometry_status": "Official daily search-box geometry (387 polygons) included separately",
        "actual_status": "searched; no associated debris found",
        "aircraft_debris_field_detection_use": "No direct seabed exclusion",
        "recommended_model_treatment": "Condition a time-resolved drift-and-surface-detection model; do not raster-mask impact points and do not double count if already assimilated by the drift likelihood.",
        "source_grade": "A",
    },
    {
        "campaign_id": "bluefin21_2014",
        "dates": "2014-04-14 to 2014-05-28",
        "operator": "JACC/ATSB, ADV Ocean Shield and Bluefin-21",
        "modality": "AUV seafloor side-scan sonar near false acoustic detections",
        "published_or_reported_area_km2": "over 850 (official contemporaneous statement); official GIS geometry is about 771",
        "geometry_status": "Official ArcGIS polygon included",
        "actual_status": "searched and discounted; geographically remote from current main posterior",
        "aircraft_debris_field_detection_use": "Yes, but only inside footprint and within depth/quality limits",
        "recommended_model_treatment": "Separate campaign likelihood with uncertain detection probability; negligible for the present 33–40°S posterior.",
        "source_grade": "A",
    },
    {
        "campaign_id": "phase1_bathymetry_2014_2017",
        "dates": "2014-06 to 2017-01",
        "operator": "ATSB/Geoscience Australia and partners",
        "modality": "shipborne multibeam bathymetry for terrain/navigation",
        "published_or_reported_area_km2": "710,000",
        "geometry_status": "Official raster service available",
        "actual_status": "mapped, but generally >30 m resolution",
        "aircraft_debris_field_detection_use": "No",
        "recommended_model_treatment": "Set aircraft debris-field detection probability to zero; retain only as environmental/terrain support.",
        "source_grade": "A",
    },
    {
        "campaign_id": "atsb_phase2_2014_2017",
        "dates": "2014-10 to 2017-01",
        "operator": "ATSB-led Australia/Malaysia/China search",
        "modality": "deep-tow/AUV side-scan, SAS and multibeam high-resolution sonar",
        "published_or_reported_area_km2": f">120,000; open tile mask sums to {georef['coverage_area_km2_spherical_pixel_sum']:.0f}",
        "geometry_status": "Official data-footprint mask and vector contour included",
        "actual_status": "searched; 97% deep-tow coverage; high-priority coverage about 99.9%; overall debris-field detection confidence stated >95%",
        "aircraft_debris_field_detection_use": "Strong but non-binary",
        "recommended_model_treatment": "Normal cells: hierarchical q around 0.97 with 0.95–0.99 sensitivity; LPD cells: q=0.50–0.90; holidays: q≈0. Marginalize footprint and q uncertainty.",
        "source_grade": "A",
    },
    {
        "campaign_id": "oi2018_contract_to_29may",
        "dates": "2018-01-22 to 2018-05-29",
        "operator": "Ocean Infinity under Malaysian no-find/no-fee agreement",
        "modality": "fleet of eight AUVs with high-resolution sonar",
        "published_or_reported_area_km2": "over 112,000 by 29 May 2018",
        "geometry_status": "Official weekly maps exist; exact AUV swaths are not public",
        "actual_status": "searched from about 35°S northward through Sites 1–4",
        "aircraft_debris_field_detection_use": "Strong but footprint-uncertain",
        "recommended_model_treatment": "Use an uncertain coverage field inside the reconstructed outline, not a hard polygon; include terrain/quality random effects.",
        "source_grade": "A for area; C for reconstructed geometry",
    },
    {
        "campaign_id": "oi2018_post_contract_extension",
        "dates": "2018-05-30 to about 2018-06-08",
        "operator": "Ocean Infinity, outside the expired Malaysian agreement",
        "modality": "AUV high-resolution sonar",
        "published_or_reported_area_km2": "not separately published; final campaign data total was 120,000, versus >112,000 at contract end",
        "geometry_status": "Approximate northern extension toward/around 25.98°S, 101.46°E; exact swaths not public",
        "actual_status": "uncontracted additional work; no find",
        "aircraft_debris_field_detection_use": "Potentially strong locally, but geometry uncertain",
        "recommended_model_treatment": "Represent as an uncertain northern extension; do not equate the ~8,000 km² difference in rounded totals with exact unique coverage.",
        "source_grade": "B",
    },
    {
        "campaign_id": "oi2025_precontract",
        "dates": "about 2025-02-23 to 2025-03-24",
        "operator": "Ocean Infinity before contract signature",
        "modality": "AUV sonar with Armada 78 06 as launch/recovery vessel",
        "published_or_reported_area_km2": "not separately published",
        "geometry_status": "Malaysia confirms wider pre-contract activity; community AIS tracks supplied only as a proxy",
        "actual_status": "searched at Ocean Infinity's commercial risk before 25 March signature; includes infill/holiday work and new outboard seabed",
        "aircraft_debris_field_detection_use": "Use only after marginalizing unknown AUV footprint",
        "recommended_model_treatment": "Latent footprint conditioned on vessel tracks and reported objectives; never buffer the ship track and call it searched seabed.",
        "source_grade": "A for occurrence; B/C for location detail",
    },
    {
        "campaign_id": "oi2025_2026_contracted_completed",
        "dates": "2025-03-25 to 2025-03-28 and 2025-12-31 to 2026-01-23",
        "operator": "Ocean Infinity under Malaysian no-find/no-fee agreement",
        "modality": "AUV high-resolution seabed search",
        "published_or_reported_area_km2": "about 7,571",
        "geometry_status": "Official area total; exact polygon/AUV swaths not public",
        "actual_status": "28 contracted operating days; no confirmed wreckage",
        "aircraft_debris_field_detection_use": "Strong but footprint-uncertain",
        "recommended_model_treatment": "Constrain latent completed footprint to 7,571 km² inside the 15,000 km² target and marginalize over plausible AUV coverage realizations.",
        "source_grade": "A for area and dates; C for reconstructed geometry",
    },
    {
        "campaign_id": "oi2026_2027_remaining",
        "dates": "planned between 2026-11 and 2027-04; agreement ends 2027-06-30",
        "operator": "Ocean Infinity under extended Malaysian agreement",
        "modality": "planned AUV seabed search",
        "published_or_reported_area_km2": "7,428.54 remaining from 15,000 target",
        "geometry_status": "No official remaining polygon published",
        "actual_status": "not yet searched as of 2026-08-11",
        "aircraft_debris_field_detection_use": "None until actually searched",
        "recommended_model_treatment": "Do not downweight now. For planning maps, place most probability on the reconstructed inboard/northwest band plus infill/gap uncertainty.",
        "source_grade": "A for quantity/schedule; C for likely geometry",
    },
]

with (OUT / "search_campaign_inventory.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=list(inventory_rows[0]))
    writer.writeheader()
    writer.writerows(inventory_rows)


source_rows = [
    ("ATSB search overview", "https://www.atsb.gov.au/mh370-search-overview", "A", "ATSB >120,000 km²; total after 2018 close to 200,000 km²"),
    ("ATSB investigation/final-report summary", "https://www.atsb.gov.au/investigations/ae-2014-054", "A", "710,000 km² bathymetry versus >120,000 km² high-resolution sonar; contacts and QA"),
    ("Geoscience Australia data release", "https://www.ga.gov.au/about/projects/marine/mh370-data-release", "A", "Phase 1 bathymetry versus Phase 2 aircraft-search sonar"),
    ("GA Phase-2 raw-data metadata", "https://ecat.ga.gov.au/geonetwork/srv/api/records/11759ecd-b6ea-4e98-95fd-b966cd5735b3?language=eng", "A", ">121,000 km² public high-resolution sonar data"),
    ("ATSB First Principles Review", "https://www.atsb.gov.au/sites/default/files/investigation-reports/ae2014054_final-first-principles-report.pdf", "A", "97% coverage; LPD/gap statistics; >95% overall detection confidence; search widths"),
    ("GA 2022 data review", "https://www.atsb.gov.au/sites/default/files/2024-02/mh370-data-review-2022-final-report-v2.pdf", "A", "4,900 km² re-reviewed; 72.79 km² holidays/LPD; OI data unavailable to GA"),
    ("Ocean Infinity conclusion, 29 May 2018", "https://oceaninfinity.com/news/conclusion-of-current-search-for-malaysian-airlines-flight-mh370/", "A", ">112,000 km² high-quality data by contract conclusion"),
    ("Ocean Infinity 2018 data donation", "https://oceaninfinity.com/news/ocean-infinity-donates-120000-square-kilometres-of-data-for-missing-malaysian-airliner-to-gebco-seabed-2030-project/", "A", "120,000 km² final campaign data total"),
    ("Government of Malaysia weekly update #1 (archived)", "https://web.archive.org/web/20180208174245/https://oceaninfinity.com/wp-content/uploads/MH370-Search-Weekly-Report-1.pdf", "A", "Initial planned Sites 1–3 geometry and 33,012 km² Site 1 target"),
    ("Government of Malaysia weekly update #14 (archived)", "https://web.archive.org/web/20180514064904/https://oceaninfinity.com/wp-content/uploads/MH370-Search-Weekly-Report-14.pdf", "A", "Site 1/2 completion and 73,000 km² through Site 3"),
    ("ABC report on post-contract 2018 extension", "https://www.abc.net.au/news/2018-06-01/unofficial-search-for-mh370-continues/9825700", "B", "Search continued beyond contract near Haixun area"),
    ("Malaysia MOT update, 8 Mar 2026", "https://www.mot.gov.my/my/Kenyataan%20Media/Tahun%202026/SIARAN%20MEDIA%20OPERASI%20PENCARIAN%20MH370%20%2820252026%29%20KEMAS%20KINI%20TERKINI.pdf", "A", "15,000 target; 7,571 completed; pre-contract wider-area work acknowledged"),
    ("Malaysia MOT extension, 29 Jun 2026", "https://www.mot.gov.my/my/Kenyataan%20Media/Tahun%202026/29%20JUN%2026_KENYATAAN%20MEDIA%20MENTERI%20PENGANGKUTAN%20PERLANJUTAN%20PERJANJIAN%20ANTARA%20KERAJAAN%20MALAYSIA%20%26%20OCEAN%20INFINITY%20BAGI%20MENGESAN%20BANGKAI%20PESAWAT%20MH370.pdf", "A", "7,428.54 km² remaining; extension through 30 Jun 2027; Nov-Apr window"),
    ("Ocean Infinity conclusion, 8 Mar 2026", "https://oceaninfinity.com/news/conclusion-of-the-search-for-malaysian-airlines-flight-mh370/", "A", "151 days since 2018 and >140,000 km² mapped cumulatively"),
    ("Radiant Physics 2025 reconstruction", "https://mh370.radiantphysics.com/2025/03/31/update-on-the-search-for-mh370/", "B", "Pre-contract phases, infill intent and new outboard search"),
    ("Radiant Physics 2018/2026 extent review", "https://mh370.radiantphysics.com/2026/01/01/the-search-for-mh370-continues-into-2026/", "B", "OI2018 approximate 24.7–36°S and ±25/32 NM widths"),
    ("CAPTION Armada tracking", "https://www.mh370-caption.net/index.php/armada-tracking/", "C", "Community AIS tracking and inferred completion of outboard 2024 band"),
    ("Official ArcGIS story map", "https://geoscience-au.maps.arcgis.com/apps/MapSeries/index.html?appid=038a72439bfa4d28b3dde81cc6ff3214", "A", "Official 7th arc, Bluefin, surface-search and Phase-2 data layers"),
]
with (OUT / "source_register.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.writer(handle)
    writer.writerow(["source", "url", "grade", "claim_used"])
    writer.writerows(source_rows)


# Illustrative overlap with the existing stage-1 impact sample. This is a diagnostic,
# not a final posterior update and is deliberately kept separate from the evidence files.
sample_path = ROOT / "outputs" / "mh370_stage1_0011" / "impact_posterior_sample.csv"
diagnostic_rows = []
posterior_bins = []
if sample_path.exists():
    sample = pd.read_csv(sample_path)
    points = sample[["lon_deg_E", "lat_deg"]].to_numpy()
    zoom = georef["web_mercator_zoom"]
    n = 2**zoom
    gx = np.floor((points[:, 0] + 180) / 360 * n * 256).astype(int)
    gy = np.floor((1 - np.arcsinh(np.tan(np.radians(points[:, 1]))) / math.pi) / 2 * n * 256).astype(int)
    ix = gx - georef["tile_x_min"] * 256
    iy = gy - georef["tile_y_min"] * 256
    valid = (ix >= 0) & (iy >= 0) & (ix < mask.shape[1]) & (iy < mask.shape[0])
    in_atsb = np.zeros(len(sample), dtype=bool)
    in_atsb[valid] = mask[iy[valid], ix[valid]] > 0
    in_oi2018 = points_in_ring(points, oi2018_ring)
    in_oi24 = [points_in_ring(points, ring) for ring in oi2024_rings]
    masks = {
        "ATSB official Phase-2 footprint": in_atsb,
        "OI2018 approximate outline": in_oi2018,
        "ATSB or OI2018 approximate": in_atsb | in_oi2018,
        "OI2024 proposed outboard band": in_oi24[0],
        "OI2024 proposed inboard band": in_oi24[1],
        "historical union plus both OI2024 bands": in_atsb | in_oi2018 | in_oi24[0] | in_oi24[1],
    }
    for name, values in masks.items():
        diagnostic_rows.append(
            {
                "layer": name,
                "unweighted_stage1_sample_fraction_inside": float(values.mean()),
                "interpretation": "Geometry-overlap diagnostic only; not detection-probability adjusted and not a final posterior update.",
            }
        )

    bins = sample.assign(
        lon_bin=np.floor(sample["lon_deg_E"] * 4) / 4,
        lat_bin=np.floor(sample["lat_deg"] * 4) / 4,
    ).groupby(["lon_bin", "lat_bin"]).size().reset_index(name="count")
    bins["relative_density"] = bins["count"] / bins["count"].max()
    posterior_bins = [
        {
            "lon": round(float(row.lon_bin), 2),
            "lat": round(float(row.lat_bin), 2),
            "density": round(float(row.relative_density), 4),
        }
        for row in bins.itertuples()
        if row.relative_density >= 0.02
    ]

with (OUT / "stage1_search_overlap_diagnostic.csv").open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(
        handle,
        fieldnames=["layer", "unweighted_stage1_sample_fraction_inside", "interpretation"],
    )
    writer.writeheader()
    writer.writerows(diagnostic_rows)


map_data = {
    "footprints": footprints,
    "tracks": tracks,
    "land": rounded_geojson(land, 3),
    "posterior_bins": posterior_bins,
    "metadata": {
        "as_of": "2026-08-11",
        "official_remaining_area_km2": 7428.54,
        "official_contract_target_km2": 15000,
        "official_contracted_completed_km2": 7571,
        "atsb_tile_mask_area_km2": round(georef["coverage_area_km2_spherical_pixel_sum"], 1),
    },
}
write_json(OUT / "map_data.json", map_data, indent=None)


report = f"""# MH370 searched-area evidence audit

As of 11 August 2026

## Bottom line

The model should not use a single binary `searched = 1` mask. The open record supports a high-fidelity binary *coverage* mask only for the 2014–2017 ATSB-led Phase-2 data footprint, and even there detection probability varies with terrain, sonar quality, and known holidays. Ocean Infinity has not published its AUV swath polygons for either 2018 or 2025–2026, so those footprints must be marginalized.

The official current position is unambiguous on area but not geometry: the renewed contract targets 15,000 km²; about 7,571 km² was completed after signature; 7,428.54 km² remains; the agreement runs to 30 June 2027, with redeployment expected in the November 2026–April 2027 calm-season window. The best public reconstruction places most of that residual in the proposed inboard/northwest band, with some allowance for infill, data holidays, and contract-boundary differences. No official remaining polygon has been released.

## Cross-checks that matter

- **Bathymetry is not aircraft-search evidence.** The 710,000 km² Phase-1 bathymetric survey was collected primarily to map terrain and navigate near-bottom systems. The 2022 Geoscience Australia review states that the >30 m shipborne data cannot identify an aircraft debris field. Its aircraft-detection probability should be zero.
- **ATSB high-resolution footprint.** The official public Phase-2 tile alpha mask sums to **{georef['coverage_area_km2_spherical_pixel_sum']:.0f} km²**, agreeing with the official “over 120,000 km²” statement. The First Principles Review reported about 97% deep-tow coverage, about 99.9% coverage in the high-priority portion after AUV completion, and >95% overall debris-field detection confidence. It separately identified 606.7 km² of lower-probability-detection terrain and 119.29 km² of shadow/avoidance/equipment gaps in the 36–39.3°S indicative area.
- **The 2022 re-review does not validate OI2018 data.** Within the 17,000 km² review circle around 33.177°S, 95.3°E, GA reviewed 4,900 km² of ATSB high-resolution data. It found 72.79 km² of holidays/LPD (1.5% of reviewed area) and explicitly said it did not have Ocean Infinity's 2018 data.
- **OI2018 area totals are stage-dependent.** Ocean Infinity reported >112,000 km² of high-quality data at the 29 May contract conclusion. It continued for several days beyond the expired agreement in the northern/Haixun area. Its later data-donation release used 120,000 km² for the final campaign. That roughly 8,000 km² difference is not an exact unique-area estimate because both numbers are rounded and may differ in definitions.
- **OI2025 pre-contract work is real but not quantified.** Malaysia's 8 March 2026 release explicitly acknowledges additional survey activity in a broader area before the 25 March 2025 agreement. Community vessel tracks place activity on 23–28 February and 11–24 March, but the ship is only an AUV launch/recovery platform; its track is not the sonar footprint.
- **The cumulative OI number cannot be subtracted mechanically.** OI reported >140,000 km² mapped and 151 sea days cumulatively since 2018. Subtracting its 2018 120,000 km² figure suggests >20,000 km² of later mapping, greater than the 7,571 km² officially credited inside the signed contract. The difference can contain pre-contract work, infill, repeat passes, overlap, and different accounting definitions.

## Likely geography of the remaining OI area

The approximate March-2024 proposal reconstruction consists of two long bands around the 7th arc from roughly 33–36°S. Its outboard/southeast band is about {oi2024_areas[0]:.0f} km² in the traced outline; its inboard/northwest band is about {oi2024_areas[1]:.0f} km². Community tracking indicates that the 2025–2026 campaigns substantially traversed the outboard band, including pre-contract activity. The official residual of 7,428.54 km² is therefore most plausibly concentrated in the inboard/northwest band plus infill and boundary differences. This is an inference, not a published Ocean Infinity polygon.

This matters for the controlled-glide hypothesis: historical ATSB and OI2018 searches are predominantly close to the 7th arc, and the renewed proposal reaches only on the order of 45 NM from it. A controlled terminal displacement of 100 NM or more leaves large cross-arc regions with no high-resolution sonar exclusion. The official ±100 NM planning envelope is included as context and must not be mistaken for searched seabed.

## Recommended likelihood in the integrated estimator

For an impact state `x`, campaign `k`, coverage probability `c_k(x)`, and conditional detection probability `q_k(x)`, use

`P(no detection | x) = product_k [1 - c_k(x) q_k(x)]`.

For genuinely independent repeat passes, combine them as `1 - product_j(1 - q_kj)`. Do not subtract overlapping polygon areas. Recommended implementation:

1. Read the ATSB mask directly. Assign normal-quality cells a hierarchical `q` centred near 0.97 with at least 0.95–0.99 sensitivity; use the report's 0.50–0.90 range in LPD cells and approximately zero in true holidays.
2. Treat OI2018 and OI2025–2026 footprints as latent random fields. Constrain their total unique covered areas by official totals, and constrain their spatial support by official maps plus track-derived envelopes. Draw multiple plausible footprint realizations and marginalize them.
3. Give bathymetry-only cells `q=0` for aircraft-debris detection.
4. Assimilate the March–April 2014 surface search through the drift/debris observation model, not by applying the aircraft's impact coordinate to the daily surface polygons. If the drift likelihood already uses the absence of observed debris, do not add it again.
5. Do not apply the 7,428.54 km² future residual as negative evidence until it has actually been searched.

## Package contents

- `search_campaign_inventory.csv`: source-graded campaign ledger and model treatment.
- `source_register.csv`: primary and reconstruction sources with the claim each supports.
- `search_footprints.geojson`: official ATSB/Bluefin geometry, official arc/context, and clearly labelled approximate OI outlines.
- `atsb_phase2_coverage_mask_z8.png` and georeferencing JSON: model-ready official open footprint.
- `surface_search_2014_official.geojson`: official daily surface-search polygons, kept separate to prevent accidental seabed use.
- `oi_2025_2026_vessel_track_proxies.geojson`: community AIS evidence, expressly not AUV swaths.
- `stage1_search_overlap_diagnostic.csv`: geometry-only overlap with the existing Stage-1 impact sample; not a posterior update.

## Limitations

Exact Ocean Infinity 2018 and 2025–2026 AUV mission polygons, per-cell sonar quality, data holidays and audited probabilities of detection are not public. The 2024 proposal outlines and present remaining-area geography are therefore source-grade C. The evidence package preserves those uncertainties so the integrated estimator can marginalize them instead of turning inference into false precision.
"""
(OUT / "MH370_searched_area_evidence_audit.md").write_text(report, encoding="utf-8")

print(json.dumps({
    "output_directory": str(OUT),
    "atsb_mask_area_km2": georef["coverage_area_km2_spherical_pixel_sum"],
    "oi2018_outline_area_km2": oi2018_outline_area,
    "oi2024_band_areas_km2": oi2024_areas,
    "files": sorted(path.name for path in OUT.iterdir()),
}, indent=2))
