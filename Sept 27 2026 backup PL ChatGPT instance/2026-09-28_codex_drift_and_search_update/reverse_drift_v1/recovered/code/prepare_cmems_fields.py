#!/usr/bin/env python3
"""Convert pinned March 2014 CMEMS NetCDF subsets to the runner grid format."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import netCDF4
import numpy as np


BUNDLE = Path(__file__).resolve().parents[1]
DEFAULT_DATA = BUNDLE / "data"
DEFAULT_OCEAN_BUNDLE = BUNDLE.parent / "ocean-drift-input-preparation"
UTC = timezone.utc


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def iso_utc(value: object) -> str:
    return datetime(
        int(value.year), int(value.month), int(value.day),
        int(value.hour), int(value.minute), int(value.second), tzinfo=UTC,
    ).isoformat().replace("+00:00", "Z")


def select_indices(values: np.ndarray, minimum: float, maximum: float) -> np.ndarray:
    indices = np.flatnonzero((values >= minimum - 1e-6) & (values <= maximum + 1e-6))
    if indices.size < 2 or not np.array_equal(indices, np.arange(indices[0], indices[-1] + 1)):
        raise ValueError(f"coordinate selection {minimum}..{maximum} is not contiguous")
    return indices


def source_receipt(
    retrieval_manifest: Path,
    source: Path,
    target: Path,
) -> tuple[dict, str]:
    raw = retrieval_manifest.read_bytes()
    manifest = json.loads(raw)
    source_hash = sha256_file(source)
    matches = [
        entry for entry in manifest.get("files", [])
        if Path(entry.get("path", "")).name == source.name
    ]
    if len(matches) != 1:
        raise ValueError(f"expected one retrieval receipt for {source.name}")
    if matches[0].get("sha256") != source_hash:
        raise ValueError(f"source SHA-256 mismatch for {source}")
    receipt = {
        "schema_version": 1,
        "dataset_id": manifest.get("dataset_id"),
        "dataset_version": manifest.get("dataset_version"),
        "dataset_part": manifest.get("dataset_part"),
        "component_units": manifest.get("component_units"),
        "source_retrieval_manifest_sha256": hashlib.sha256(raw).hexdigest(),
        "source_file": matches[0],
        "limitations": manifest.get("limitations", []),
    }
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt, source_hash


def convert(
    *,
    source: Path,
    source_hash: str,
    receipt_relative: str,
    output_dir: Path,
    stem: str,
    components: tuple[str, str],
    source_family: str,
    role: str,
    start_utc: datetime,
    end_utc: datetime,
    latitude_bounds: tuple[float, float],
    longitude_bounds: tuple[float, float],
    depth_index: int | None,
    extra: dict,
) -> dict:
    with netCDF4.Dataset(source) as dataset:
        latitudes_all = np.asarray(dataset.variables["latitude"][:], dtype=np.float64)
        longitudes_all = np.asarray(dataset.variables["longitude"][:], dtype=np.float64)
        time_variable = dataset.variables["time"]
        dates = netCDF4.num2date(
            time_variable[:], time_variable.units,
            calendar=getattr(time_variable, "calendar", "standard"),
            only_use_cftime_datetimes=True,
        )
        epoch_seconds = np.asarray([
            datetime(
                int(value.year), int(value.month), int(value.day),
                int(value.hour), int(value.minute), int(value.second), tzinfo=UTC,
            ).timestamp()
            for value in dates
        ])
        time_indices = select_indices(
            epoch_seconds, start_utc.timestamp(), end_utc.timestamp(),
        )
        latitude_indices = select_indices(latitudes_all, *latitude_bounds)
        longitude_indices = select_indices(longitudes_all, *longitude_bounds)
        if not np.all(np.diff(latitudes_all[latitude_indices]) > 0):
            raise ValueError("latitude coordinate is not strictly ascending")
        if not np.all(np.diff(longitudes_all[longitude_indices]) > 0):
            raise ValueError("longitude coordinate is not strictly ascending")

        slices = (
            slice(time_indices[0], time_indices[-1] + 1),
            slice(latitude_indices[0], latitude_indices[-1] + 1),
            slice(longitude_indices[0], longitude_indices[-1] + 1),
        )
        vectors: list[np.ndarray] = []
        for name in components:
            variable = dataset.variables[name]
            if depth_index is None:
                values = variable[slices]
            else:
                values = variable[slices[0], depth_index, slices[1], slices[2]]
            vectors.append(np.asarray(np.ma.filled(values, np.nan), dtype=np.float32))

    interleaved = np.stack(vectors, axis=-1).astype("<f4", copy=False)
    output_dir.mkdir(parents=True, exist_ok=True)
    binary_name = f"{stem}.f32le"
    binary_path = output_dir / binary_name
    binary_path.write_bytes(interleaved.tobytes(order="C"))
    selected_times = epoch_seconds[time_indices]
    steps = np.diff(selected_times)
    if steps.size == 0 or not np.allclose(steps, steps[0], atol=1e-6, rtol=0):
        raise ValueError("time coordinate is not regular")
    missing = int(np.count_nonzero(~np.isfinite(interleaved).all(axis=-1)))
    manifest = {
        "schema_version": 1,
        "name": stem,
        "binary_file": binary_name,
        "byte_order": "little_endian",
        "scalar_type": "float32",
        "value_count": int(interleaved.size),
        "sha256": sha256_file(binary_path),
        "status": "retrieved",
        "source_family": source_family,
        "field_role": role,
        "source_file_name": source.name,
        "source_file_sha256": source_hash,
        "source_retrieval_receipt": receipt_relative,
        "variable_order": ["u_east_m_s", "v_north_m_s"],
        "source_variable_order": list(components),
        "dimension_order": ["time", "latitude", "longitude", "component"],
        "shape": list(interleaved.shape),
        "time": {
            "start_center_utc": iso_utc(dates[time_indices[0]]),
            "step_days": float(steps[0] / 86400.0),
            "count": int(time_indices.size),
            "end_center_utc": iso_utc(dates[time_indices[-1]]),
        },
        "latitude": {
            "values_deg": [float(value) for value in latitudes_all[latitude_indices]],
            "ascending": True,
        },
        "longitude": {
            "values_deg": [float(value) for value in longitudes_all[longitude_indices]],
            "ascending": True,
        },
        "units": "m s-1",
        "missing_vector_count": missing,
        "processing": "Exact contiguous coordinate subset; no spatial or temporal resampling; masked values retained as IEEE NaN.",
        **extra,
    }
    (output_dir / f"{stem}.manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8",
    )
    return manifest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--glorys-netcdf", type=Path,
        default=Path("/jackbox/home/.cache/mh370-cmems-glorys12/cmems-glorys12-surface-2014-03.nc"),
    )
    parser.add_argument(
        "--waverys-netcdf", type=Path,
        default=Path("/jackbox/home/.cache/mh370-cmems-waverys/cmems-waverys-stokes-2014-03.nc"),
    )
    parser.add_argument(
        "--glorys-retrieval-manifest", type=Path,
        default=DEFAULT_OCEAN_BUNDLE / "outputs/cmems-glorys12-retrieval-manifest.json",
    )
    parser.add_argument(
        "--waverys-retrieval-manifest", type=Path,
        default=DEFAULT_OCEAN_BUNDLE / "outputs/cmems-waverys-retrieval-manifest.json",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_DATA)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metadata_dir = args.output_dir / "source-metadata"
    glorys_receipt_path = metadata_dir / "cmems-glorys12-2014-03-source-receipt.json"
    waverys_receipt_path = metadata_dir / "cmems-waverys-2014-03-source-receipt.json"
    _, glorys_hash = source_receipt(
        args.glorys_retrieval_manifest, args.glorys_netcdf, glorys_receipt_path,
    )
    _, waverys_hash = source_receipt(
        args.waverys_retrieval_manifest, args.waverys_netcdf, waverys_receipt_path,
    )

    glorys = convert(
        source=args.glorys_netcdf,
        source_hash=glorys_hash,
        receipt_relative="data/source-metadata/" + glorys_receipt_path.name,
        output_dir=args.output_dir,
        stem="cmems-glorys12-surface-currents-20140308-24",
        components=("uo", "vo"),
        source_family="CMEMS GLORYS12V1",
        role="Eulerian ocean current",
        start_utc=datetime(2014, 3, 8, tzinfo=UTC),
        end_utc=datetime(2014, 3, 24, tzinfo=UTC),
        latitude_bounds=(-45.0, -25.0),
        longitude_bounds=(80.0, 105.0),
        depth_index=0,
        extra={
            "dataset_id": "cmems_mod_glo_phy_my_0.083deg_P1D-m",
            "product_id": "GLOBAL_MULTIYEAR_PHY_001_030",
            "surface_depth_m": 0.49402499198913574,
            "native_nominal_resolution_deg": 1 / 12,
        },
    )
    waverys = convert(
        source=args.waverys_netcdf,
        source_hash=waverys_hash,
        receipt_relative="data/source-metadata/" + waverys_receipt_path.name,
        output_dir=args.output_dir,
        stem="cmems-waverys-surface-stokes-20140308-23",
        components=("VSDX", "VSDY"),
        source_family="CMEMS WAVERYS",
        role="surface Stokes drift",
        start_utc=datetime(2014, 3, 8, tzinfo=UTC),
        end_utc=datetime(2014, 3, 23, 6, tzinfo=UTC),
        latitude_bounds=(-45.0, -25.0),
        longitude_bounds=(80.0, 105.0),
        depth_index=None,
        extra={
            "dataset_id": "cmems_mod_glo_wav_my_0.2deg_PT3H-i",
            "product_id": "GLOBAL_REANALYSIS_WAV_001_032",
            "dataset_version": "202411",
            "native_nominal_resolution_deg": 0.2,
            "wave_model": "Meteo-France MFWAM with ECMWF forcing and GLORYS12 currents",
        },
    )
    print(json.dumps({
        "glorys": {"shape": glorys["shape"], "sha256": glorys["sha256"]},
        "waverys": {"shape": waverys["shape"], "sha256": waverys["sha256"]},
    }, indent=2))


if __name__ == "__main__":
    main()
