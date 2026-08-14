#!/usr/bin/env python3
"""Build compact impact-PDF and search-footprint data for the MH370 overlay.

The two probability surfaces are the current fixed-beta=1 (no AES gain
precompensation) reconstruction at impact, before applying search
non-detections.  The imagery-conditioned branch uses the three public CSIRO
Pleiades/BRAN candidate origins as a broad likelihood.  Search polygons are
used here only for overlap diagnostics; uncertain Ocean Infinity outlines are
not treated as binary coverage masks.
"""

from __future__ import annotations

import base64
import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-mh370-search-overlay")

import numpy as np
import pandas as pd
from matplotlib.path import Path as MplPath
from PIL import Image
from scipy.ndimage import gaussian_filter, gaussian_filter1d

from run_integrated_0011_stage1 import (
    Case,
    bto_altitude_shift,
    family_loglikelihood,
    great_circle_nm,
    reconstruct_airborne_proposal,
    sample_control_families,
    systematic_resample,
    terminal_kernel,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "mh370_search_pdf_overlay"
OUT.mkdir(parents=True, exist_ok=True)

SOURCE_PDF_PLOT = ROOT / "downloads" / "MH370" / "mh370_integrated_0011_final_latitude_pdf.png"
SEARCH_GEOJSON = ROOT / "outputs" / "mh370_search_evidence" / "search_footprints.geojson"
ATSB_MASK = ROOT / "outputs" / "mh370_search_evidence" / "atsb_phase2_coverage_mask_z8.png"
ATSB_GEOREF = ROOT / "outputs" / "mh370_search_evidence" / "atsb_phase2_coverage_mask_georef.json"

SEED = 3701001
N_AIR = 850_000
N_TERMINAL = 1_250_000
BETA_REFERENCE = 0.6766419224079634
FIXED_BETA_CONTRAST = 1.0 / BETA_REFERENCE
EXTENT = (84.0, 98.0, -40.5, -32.0)
NX = 92
NY = 64


def normalize_logweights(logw: np.ndarray) -> np.ndarray:
    shifted = np.asarray(logw, dtype=float) - np.max(logw)
    w = np.exp(shifted)
    return w / w.sum()


def digitize_curve(image_rgb: np.ndarray, color: tuple[int, int, int], x_pixels: np.ndarray) -> np.ndarray:
    target = np.asarray(color, dtype=int)
    distance = np.max(np.abs(image_rgb.astype(int) - target), axis=2)
    y_curve = np.full(len(x_pixels), np.nan)
    for k, x in enumerate(x_pixels):
        lo = max(0, x - 1)
        hi = min(image_rgb.shape[1], x + 2)
        y = np.where(np.any(distance[:, lo:hi] < 12, axis=1))[0]
        y = y[(y >= 80) & (y <= 1175)]
        if len(y) == 0:
            continue
        clusters = np.split(y, np.where(np.diff(y) > 3)[0] + 1)
        cluster = max(clusters, key=lambda values: float(np.mean(values)))
        value = float(np.median(cluster))
        if x > 1000 and value < 250:
            continue
        y_curve[k] = value
    valid = np.isfinite(y_curve)
    y_curve = np.interp(x_pixels, x_pixels[valid], y_curve[valid])
    density = np.clip((1170.0 - y_curve) / 1755.0, 0.0, None)
    return gaussian_filter1d(density, 2.0)


def empirical_rf_log_bayes_factor() -> tuple[np.ndarray, np.ndarray]:
    image = np.asarray(Image.open(SOURCE_PDF_PLOT).convert("RGB"))
    x_pixels = np.arange(213, 1900)
    latitude = -40.0 + (x_pixels - 207.0) / 134.0
    bto_bfo = digitize_curve(image, (31, 119, 180), x_pixels)
    integrated = digitize_curve(image, (255, 127, 14), x_pixels)
    bto_bfo /= np.trapezoid(bto_bfo, latitude)
    integrated /= np.trapezoid(integrated, latitude)
    log_bf = gaussian_filter1d(
        np.log(np.clip(integrated, 1e-5, None)) - np.log(np.clip(bto_bfo, 1e-5, None)),
        10.0,
    )
    resolved = (latitude >= -38.4) & (latitude <= -31.2)
    log_bf = np.where(latitude < -38.4, log_bf[np.where(resolved)[0][0]], log_bf)
    log_bf = np.where(latitude > -31.2, log_bf[np.where(resolved)[0][-1]], log_bf)
    log_bf -= float(np.interp(-36.458390177, latitude, log_bf))
    return latitude, log_bf


def bran_candidate_likelihood(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    centers = [
        (-35.5, 92.8, 0.60, 35.0),
        (-34.7, 92.6, 0.20, 30.0),
        (-35.3, 91.8, 0.20, 30.0),
    ]
    value = np.zeros_like(lat, dtype=float)
    for clat, clon, weight, sigma_nm in centers:
        distance = great_circle_nm(lat, lon, clat, clon)
        value += weight * np.exp(-0.5 * (distance / sigma_nm) ** 2)
    return value


def weighted_quantile(values: np.ndarray, weights: np.ndarray, probs: list[float]) -> np.ndarray:
    order = np.argsort(values)
    cumulative = np.cumsum(weights[order])
    cumulative /= cumulative[-1]
    return np.interp(probs, cumulative, values[order])


def summary(label: str, lat: np.ndarray, lon: np.ndarray, weights: np.ndarray, density: np.ndarray) -> dict:
    weights = weights / weights.sum()
    iy, ix = np.unravel_index(np.argmax(density), density.shape)
    dx = (EXTENT[1] - EXTENT[0]) / NX
    dy = (EXTENT[3] - EXTENT[2]) / NY
    lat_q = weighted_quantile(lat, weights, [0.025, 0.5, 0.975])
    lon_q = weighted_quantile(lon, weights, [0.025, 0.5, 0.975])
    return {
        "estimate": label,
        "mode_lat_deg": EXTENT[2] + (iy + 0.5) * dy,
        "mode_lon_deg_E": EXTENT[0] + (ix + 0.5) * dx,
        "median_lat_deg": lat_q[1],
        "median_lon_deg_E": lon_q[1],
        "lat_95_low": lat_q[0],
        "lat_95_high": lat_q[2],
        "lon_95_low": lon_q[0],
        "lon_95_high": lon_q[2],
        "ESS": float(1.0 / np.sum(weights**2)),
    }


def density_grid(lat: np.ndarray, lon: np.ndarray, weights: np.ndarray) -> np.ndarray:
    hist, _, _ = np.histogram2d(
        lat,
        lon,
        bins=(NY, NX),
        range=((EXTENT[2], EXTENT[3]), (EXTENT[0], EXTENT[1])),
        weights=weights,
    )
    return gaussian_filter(hist.astype(float), sigma=1.15, mode="nearest")


def encode_density(density: np.ndarray) -> dict:
    normal = density / density.max()
    quantized = np.rint(255 * np.sqrt(np.clip(normal, 0, 1))).astype(np.uint8)
    flat = np.sort(density.ravel())[::-1]
    cumulative = np.cumsum(flat) / flat.sum()
    thresholds = {}
    for mass in (0.50, 0.90):
        idx = min(np.searchsorted(cumulative, mass), len(flat) - 1)
        thresholds[str(int(mass * 100))] = float(flat[idx] / density.max())
    return {
        "q8_b64": base64.b64encode(quantized.tobytes()).decode("ascii"),
        "hpd_threshold_relative": thresholds,
    }


def covered_by_atsb(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    mask = np.asarray(Image.open(ATSB_MASK).convert("L")) > 0
    georef = json.loads(ATSB_GEOREF.read_text())
    zoom = georef["web_mercator_zoom"]
    scale = (2**zoom) * 256
    gx = np.floor((lon + 180.0) / 360.0 * scale).astype(int)
    lat_rad = np.radians(lat)
    gy = np.floor((1.0 - np.arcsinh(np.tan(lat_rad)) / np.pi) / 2.0 * scale).astype(int)
    lx = gx - georef["tile_x_min"] * 256
    ly = gy - georef["tile_y_min"] * 256
    valid = (lx >= 0) & (lx < mask.shape[1]) & (ly >= 0) & (ly < mask.shape[0])
    answer = np.zeros(len(lat), dtype=bool)
    answer[valid] = mask[ly[valid], lx[valid]]
    return answer


def ring_contains(ring: list[list[float]], lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    return MplPath(np.asarray(ring, dtype=float)).contains_points(np.column_stack([lon, lat]))


def point_line_distance(point: np.ndarray, start: np.ndarray, end: np.ndarray) -> float:
    delta = end - start
    if np.allclose(delta, 0):
        return float(np.linalg.norm(point - start))
    t = float(np.clip(np.dot(point - start, delta) / np.dot(delta, delta), 0.0, 1.0))
    return float(np.linalg.norm(point - (start + t * delta)))


def rdp(points: list[list[float]], tolerance: float) -> list[list[float]]:
    array = np.asarray(points, dtype=float)
    if len(array) <= 2:
        return array.tolist()
    distances = np.array([point_line_distance(p, array[0], array[-1]) for p in array[1:-1]])
    if len(distances) and float(distances.max()) > tolerance:
        index = int(np.argmax(distances)) + 1
        left = rdp(array[: index + 1].tolist(), tolerance)
        right = rdp(array[index:].tolist(), tolerance)
        return left[:-1] + right
    return [array[0].tolist(), array[-1].tolist()]


def simplify_ring(ring: list[list[float]], tolerance: float) -> list[list[float]]:
    closed = np.allclose(ring[0], ring[-1])
    work = ring[:-1] if closed else ring
    if len(work) < 4:
        return ring
    # Rotate a closed ring so simplification does not use two identical endpoints.
    anchor = min(range(len(work)), key=lambda i: work[i][0])
    rotated = work[anchor:] + work[:anchor] + [work[anchor]]
    simplified = rdp(rotated, tolerance)
    if not np.allclose(simplified[0], simplified[-1]):
        simplified.append(simplified[0])
    return [[round(x, 4), round(y, 4)] for x, y in simplified]


def simplify_geometry(geometry: dict, tolerance: float) -> dict:
    kind = geometry["type"]
    coords = geometry["coordinates"]
    if kind == "LineString":
        return {"type": kind, "coordinates": rdp(coords, tolerance)}
    if kind == "Polygon":
        rings = [simplify_ring(ring, tolerance) for ring in coords]
        rings = [ring for ring in rings if len(ring) >= 4 and len({tuple(point) for point in ring[:-1]}) >= 3]
        return {"type": kind, "coordinates": rings}
    if kind == "MultiPolygon":
        polygons = []
        for polygon in coords:
            outer = polygon[0]
            lon = [p[0] for p in outer]
            lat = [p[1] for p in outer]
            if (max(lon) - min(lon)) * (max(lat) - min(lat)) < 0.003:
                continue
            rings = [simplify_ring(ring, tolerance) for ring in polygon]
            rings = [ring for ring in rings if len(ring) >= 4 and len({tuple(point) for point in ring[:-1]}) >= 3]
            if rings:
                polygons.append(rings)
        return {"type": kind, "coordinates": polygons}
    raise ValueError(kind)


def main() -> None:
    case = Case(
        name="Refined random BFO noise, no power precompensation",
        family_prior=(1 / 3, 1 / 3, 1 / 3),
        bfo_sigma_hz=0.9953793624482928,
        bfo_vertical_hz_per_fpm=0.009,
        drift_davey_weight=0.5,
        forward_glide_probability=0.70,
    )
    rng = np.random.default_rng(SEED)
    lat0, lon0, heading, mach, _component = reconstruct_airborne_proposal(rng, N_AIR)
    family, altitude, vspd, slow_minutes, slow_speed = sample_control_families(rng, N_AIR)
    air_lat, air_lon = bto_altitude_shift(lat0, lon0, altitude)
    logw, _ = family_loglikelihood(
        air_lat,
        air_lon,
        mach,
        family,
        altitude,
        vspd,
        slow_minutes,
        slow_speed,
        case,
    )
    rf_lat, rf_log_bf = empirical_rf_log_bayes_factor()
    empirical_rf = np.interp(air_lat, rf_lat, rf_log_bf)
    reference_w = normalize_logweights(logw)

    trng = np.random.default_rng(SEED + 711)
    ancestor = systematic_resample(trng, reference_w, N_TERMINAL)
    scenario = trng.integers(0, 3, N_TERMINAL)
    impact_lat, impact_lon, _ = terminal_kernel(
        trng,
        air_lat[ancestor],
        air_lon[ancestor],
        heading[ancestor],
        altitude[ancestor],
        vspd[ancestor],
        scenario,
        case.forward_glide_probability,
    )

    beta_ratio = np.exp((FIXED_BETA_CONTRAST - 1.0) * empirical_rf[ancestor])
    w_no = beta_ratio / beta_ratio.sum()
    image_like = bran_candidate_likelihood(impact_lat, impact_lon)
    w_yes = beta_ratio * image_like
    w_yes /= w_yes.sum()

    d_no = density_grid(impact_lat, impact_lon, w_no)
    d_yes = density_grid(impact_lat, impact_lon, w_yes)
    summaries = [
        summary("Pleiades excluded", impact_lat, impact_lon, w_no, d_no),
        summary("Pleiades objects assumed MH370", impact_lat, impact_lon, w_yes, d_yes),
    ]
    pd.DataFrame(summaries).to_csv(OUT / "impact_pdf_summary.csv", index=False)

    source = json.loads(SEARCH_GEOJSON.read_text())
    by_id = {f["properties"]["id"]: f for f in source["features"]}
    oi2018_ring = by_id["oi2018_total_outline_approx"]["geometry"]["coordinates"][0]
    outboard_ring = by_id["oi2024_proposed_outboard_southeast"]["geometry"]["coordinates"][0]
    inboard_ring = by_id["oi2024_proposed_inboard_northwest"]["geometry"]["coordinates"][0]
    masks = {
        "ATSB Phase-2 official footprint": covered_by_atsb(impact_lat, impact_lon),
        "OI 2018 reconstructed envelope": ring_contains(oi2018_ring, impact_lat, impact_lon),
        "Renewed outboard/southeast proposal band": ring_contains(outboard_ring, impact_lat, impact_lon),
        "Renewed inboard/northwest proposal band": ring_contains(inboard_ring, impact_lat, impact_lon),
    }
    masks["ATSB or OI2018 envelope"] = masks["ATSB Phase-2 official footprint"] | masks["OI 2018 reconstructed envelope"]
    masks["Historical plus both renewed proposal bands"] = (
        masks["ATSB or OI2018 envelope"]
        | masks["Renewed outboard/southeast proposal band"]
        | masks["Renewed inboard/northwest proposal band"]
    )
    overlap_rows = []
    for label, weights in [("Pleiades excluded", w_no), ("Pleiades objects assumed MH370", w_yes)]:
        for layer, mask in masks.items():
            overlap_rows.append(
                {
                    "impact_pdf": label,
                    "layer": layer,
                    "posterior_mass_inside_geometry": float(weights[mask].sum()),
                    "interpretation": "geometry overlap only; OI envelopes are not binary coverage and no detection probability is applied",
                }
            )
    pd.DataFrame(overlap_rows).to_csv(OUT / "search_geometry_overlap.csv", index=False)

    display_ids = [
        "atsb_phase2_2014_2017",
        "oi2018_total_outline_approx",
        "oi2024_proposed_outboard_southeast",
        "oi2024_proposed_inboard_northwest",
        "seventh_arc_fl400",
    ]
    features = []
    for key in display_ids:
        feature = by_id[key]
        tolerance = 0.025 if key == "atsb_phase2_2014_2017" else 0.012
        if key == "seventh_arc_fl400":
            tolerance = 0.01
        features.append(
            {
                "type": "Feature",
                "properties": {"id": key, "name": feature["properties"]["name"]},
                "geometry": simplify_geometry(feature["geometry"], tolerance),
            }
        )

    payload = {
        "extent": EXTENT,
        "nx": NX,
        "ny": NY,
        "pdfs": [
            {**summaries[0], **encode_density(d_no)},
            {**summaries[1], **encode_density(d_yes)},
        ],
        "search_features": {"type": "FeatureCollection", "features": features},
        "model_note": "Fixed beta=1 no-power-precompensation impact reconstruction; refined random BFO sigma 0.995 Hz; no 00:19 observation; broad published three-origin Pleiades/BRAN likelihood.",
    }
    (OUT / "overlay_data.json").write_text(json.dumps(payload, separators=(",", ":")), encoding="utf-8")
    (OUT / "run_manifest.json").write_text(
        json.dumps(
            {
                "seed": SEED,
                "n_air": N_AIR,
                "n_terminal": N_TERMINAL,
                "beta": 1.0,
                "reference_beta_mean": BETA_REFERENCE,
                "bfo_random_sigma_hz": case.bfo_sigma_hz,
                "uses_0019_observation": False,
                "search_non_detection_applied": False,
                "pleiades_likelihood": "public CSIRO three-origin broad mixture; conditional hypothesis",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(pd.DataFrame(summaries).to_string(index=False))
    print(pd.DataFrame(overlap_rows).to_string(index=False))
    print(f"overlay_data_bytes={len((OUT / 'overlay_data.json').read_bytes())}")


if __name__ == "__main__":
    main()
