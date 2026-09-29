#!/usr/bin/env python3
"""Complete-grid two-station correlation baseline for prepared raw triads.

This is deliberately a conservative channel-incoherent energy detector. Each
channel is filtered and robustly standardised before channel energies are
combined, so kilometre-scale array delays do not cancel a signal. It does not
estimate a bearing. Bearing/coherent processing remains a separate extension
requiring verified array geometry, clock corrections and an injection study.

Significance is the maximum over every searched geometry lag under station time
slides; it is not a pointwise correlation p-value. Even a small p-value is a
diagnostic until blinded injections establish detection/localisation coverage.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.ndimage import uniform_filter1d
from scipy.signal import butter, correlate, correlation_lags, sosfiltfilt


EARTH_RADIUS_KM = 6371.0088


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_prepared(path: Path) -> tuple[dict, np.ndarray]:
    metadata_path = path / "metadata.json"
    pressure_path = path / "pressure-pa.npy"
    receipt_path = path / "receipt.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt["outputs"][pressure_path.name] != sha256(pressure_path):
        raise ValueError(f"prepared pressure hash mismatch in {path}")
    if receipt["outputs"][metadata_path.name] != sha256(metadata_path):
        raise ValueError(f"prepared metadata hash mismatch in {path}")
    pressure = np.load(pressure_path, allow_pickle=False)
    if pressure.shape != (3, int(metadata["sample_count"])):
        raise ValueError("prepared pressure array is not a three-channel triad")
    return metadata, np.asarray(pressure, dtype=float)


def energy_series(
    pressure: np.ndarray,
    sample_rate_hz: float,
    frequency_hz: tuple[float, float],
    energy_window_s: float,
) -> np.ndarray:
    low, high = frequency_hz
    nyquist = 0.5 * sample_rate_hz
    if not (0.0 < low < high < nyquist):
        raise ValueError("filter band must lie strictly below Nyquist")
    sos = butter(4, [low / nyquist, high / nyquist], btype="bandpass", output="sos")
    filtered = sosfiltfilt(sos, pressure, axis=1)
    median = np.median(filtered, axis=1, keepdims=True)
    mad = 1.4826 * np.median(np.abs(filtered - median), axis=1, keepdims=True)
    standardised = (filtered - median) / np.maximum(mad, 1.0e-12)
    width = max(2, int(round(energy_window_s * sample_rate_hz)))
    channel_energy = np.sqrt(
        np.maximum(uniform_filter1d(standardised**2, width, axis=1, mode="nearest"), 0.0)
    )
    combined = np.median(channel_energy, axis=0)
    return (combined - np.mean(combined)) / max(float(np.std(combined)), 1.0e-12)


def haversine_km(
    latitude: np.ndarray,
    longitude: np.ndarray,
    station_latitude: float,
    station_longitude: float,
) -> np.ndarray:
    lat_1 = np.radians(latitude)
    lat_2 = math.radians(station_latitude)
    delta_lat = lat_1 - lat_2
    delta_lon = np.radians(longitude - station_longitude)
    value = np.sin(delta_lat / 2.0) ** 2 + np.cos(lat_1) * math.cos(lat_2) * np.sin(delta_lon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(value, 0.0, 1.0)))


def load_grid(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("source grid is empty")
    return rows


def fft_response(
    first: np.ndarray,
    second: np.ndarray,
    first_start_s: float,
    second_start_s: float,
    sample_rate_hz: float,
) -> tuple[np.ndarray, np.ndarray]:
    first = np.asarray(first, dtype=float)
    second = np.asarray(second, dtype=float)
    ones_first = np.ones(first.size)
    ones_second = np.ones(second.size)

    def cross(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        return correlate(left, right, mode="full", method="fft")

    count = cross(ones_second, ones_first)
    sum_first = cross(ones_second, first)
    sum_second = cross(second, ones_first)
    sum_first2 = cross(ones_second, first * first)
    sum_second2 = cross(second * second, ones_first)
    sum_cross = cross(second, first)
    safe = np.maximum(count, 1.0)
    covariance = sum_cross - sum_first * sum_second / safe
    variance_first = sum_first2 - sum_first * sum_first / safe
    variance_second = sum_second2 - sum_second * sum_second / safe
    response = np.divide(
        covariance,
        np.sqrt(np.maximum(variance_first * variance_second, 1.0e-20)),
        out=np.full_like(covariance, np.nan),
        where=(count >= 100.0) & (variance_first > 0.0) & (variance_second > 0.0),
    )
    sample_lag = correlation_lags(second.size, first.size, mode="full")
    arrival_lag_s = second_start_s - first_start_s + sample_lag / sample_rate_hz
    arrival_steps = np.rint(arrival_lag_s * sample_rate_hz).astype(np.int64)
    return arrival_steps, response


def response_at_steps(all_steps: np.ndarray, response: np.ndarray, steps: np.ndarray) -> np.ndarray:
    indices = steps - int(all_steps[0])
    if np.any(indices < 0) or np.any(indices >= response.size):
        raise ValueError("raw triad time spans do not cover every requested geometry lag")
    return response[indices]


def run(
    first_path: Path,
    second_path: Path,
    grid_path: Path,
    output: Path,
    celerity_km_s: float,
    low_hz: float,
    high_hz: float,
    energy_window_s: float,
    null_replicates: int,
    seed: int,
) -> dict:
    first_meta, first_pressure = load_prepared(first_path)
    second_meta, second_pressure = load_prepared(second_path)
    rate = float(first_meta["sample_rate_hz"])
    if abs(rate - float(second_meta["sample_rate_hz"])) > 1.0e-12:
        raise ValueError("prepared triads must have the same sample rate")
    first = energy_series(first_pressure, rate, (low_hz, high_hz), energy_window_s)
    second = energy_series(second_pressure, rate, (low_hz, high_hz), energy_window_s)
    cells = load_grid(grid_path)
    latitude = np.asarray([float(row["latitude"]) for row in cells])
    longitude = np.asarray([float(row["longitude"]) for row in cells])
    first_position = first_meta["station_position_wgs84"]
    second_position = second_meta["station_position_wgs84"]
    first_distance = haversine_km(
        latitude, longitude, float(first_position["latitude_deg"]), float(first_position["longitude_deg_e"])
    )
    second_distance = haversine_km(
        latitude, longitude, float(second_position["latitude_deg"]), float(second_position["longitude_deg_e"])
    )
    lag_s = (second_distance - first_distance) / celerity_km_s
    requested_steps = np.rint(lag_s * rate).astype(np.int64)
    unique_steps = np.unique(requested_steps)
    all_steps, all_response = fft_response(
        first,
        second,
        float(first_meta["start_time_utc_unix_s"]),
        float(second_meta["start_time_utc_unix_s"]),
        rate,
    )
    unique_response = response_at_steps(all_steps, all_response, unique_steps)
    cell_response = unique_response[np.searchsorted(unique_steps, requested_steps)]
    observed_maximum = float(np.nanmax(unique_response))

    rng = np.random.default_rng(seed)
    minimum_shift = min(second.size // 4, max(1, int(round(60.0 * rate))))
    valid_shifts = np.arange(minimum_shift, second.size - minimum_shift, dtype=int)
    if valid_shifts.size < null_replicates:
        raise ValueError("raw record is too short for the requested time-slide controls")
    selected_shifts = rng.choice(valid_shifts, size=null_replicates, replace=False)
    null_maxima = np.empty(null_replicates)
    for index, shift in enumerate(selected_shifts):
        shifted = np.roll(second, int(shift))
        null_steps, null_response = fft_response(
            first,
            shifted,
            float(first_meta["start_time_utc_unix_s"]),
            float(second_meta["start_time_utc_unix_s"]),
            rate,
        )
        null_maxima[index] = float(
            np.nanmax(response_at_steps(null_steps, null_response, unique_steps))
        )
    p_scan = float((1 + np.count_nonzero(null_maxima >= observed_maximum)) / (null_replicates + 1))

    order = np.argsort(np.nan_to_num(cell_response, nan=-np.inf))[::-1]
    top = []
    seen_steps: set[int] = set()
    for cell_index in order:
        step = int(requested_steps[cell_index])
        if step in seen_steps:
            continue
        seen_steps.add(step)
        row = cells[int(cell_index)]
        top.append(
            {
                "rank": len(top) + 1,
                "representative_cell_id": row["id"],
                "along_nm": float(row["alongNm"]),
                "cross_nm": float(row["crossNm"]),
                "latitude_deg": float(row["latitude"]),
                "longitude_deg_e": float(row["longitude"]),
                "interstation_lag_s": step / rate,
                "energy_correlation_r": float(cell_response[cell_index]),
            }
        )
        if len(top) == 10:
            break

    output.mkdir(parents=True, exist_ok=True)
    top_path = output / "raw-triad-complete-grid-top10.csv"
    with top_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(top[0]))
        writer.writeheader()
        writer.writerows(top)
    null_path = output / "raw-triad-time-slide-null-maxima.csv"
    with null_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["replicate", "circular_shift_samples", "complete_grid_maximum_r"])
        writer.writeheader()
        for index, (shift, maximum) in enumerate(zip(selected_shifts, null_maxima), start=1):
            writer.writerow({"replicate": index, "circular_shift_samples": int(shift), "complete_grid_maximum_r": float(maximum)})
    summary = {
        "schema_id": "mh370-raw-triad-complete-grid-diagnostic",
        "schema_version": 1,
        "status": "DIAGNOSTIC_ZERO_WEIGHT_REQUIRES_BLINDED_INJECTION_VALIDATION",
        "stations": [first_meta["station_id"], second_meta["station_id"]],
        "source_cell_count": len(cells),
        "unique_geometry_lag_count": int(unique_steps.size),
        "observed_complete_grid_maximum_r": observed_maximum,
        "time_slide_replicates": null_replicates,
        "scan_adjusted_time_slide_p": p_scan,
        "detector": "2-40 Hz channel-incoherent robust rolling energy; two-station correlation",
        "likelihood_evaluated": False,
        "log_weight_increment": 0.0,
        "limits": [
            "no coherent triad beamforming or bearing estimate",
            "time-slide null preserves each station series but is not a calibrated receiver operating characteristic",
            "candidate selection and every source-cell lag are included in the maximum statistic",
            "a future likelihood requires blinded injections into contemporaneous raw noise",
        ],
    }
    summary_path = output / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    manifest = {
        "schema_id": "mh370-raw-triad-search-manifest",
        "schema_version": 1,
        "inputs": {
            "first_receipt": sha256(first_path / "receipt.json"),
            "second_receipt": sha256(second_path / "receipt.json"),
            "source_grid": sha256(grid_path),
        },
        "configuration": {
            "celerity_km_s": celerity_km_s,
            "frequency_hz": [low_hz, high_hz],
            "energy_window_s": energy_window_s,
            "null_replicates": null_replicates,
            "seed": seed,
        },
        "outputs": {
            top_path.name: sha256(top_path),
            null_path.name: sha256(null_path),
            summary_path.name: sha256(summary_path),
        },
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("first_prepared", type=Path)
    parser.add_argument("second_prepared", type=Path)
    parser.add_argument("source_grid", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--celerity-km-s", type=float, default=1.5)
    parser.add_argument("--low-hz", type=float, default=2.0)
    parser.add_argument("--high-hz", type=float, default=40.0)
    parser.add_argument("--energy-window-s", type=float, default=1.0)
    parser.add_argument("--null-replicates", type=int, default=250)
    parser.add_argument("--seed", type=int, default=3700111)
    args = parser.parse_args()
    summary = run(
        args.first_prepared.resolve(),
        args.second_prepared.resolve(),
        args.source_grid.resolve(),
        args.output.resolve(),
        args.celerity_km_s,
        args.low_hz,
        args.high_hz,
        args.energy_window_s,
        args.null_replicates,
        args.seed,
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
