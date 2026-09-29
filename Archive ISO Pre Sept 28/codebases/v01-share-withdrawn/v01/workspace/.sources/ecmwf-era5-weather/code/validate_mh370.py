#!/usr/bin/env python3
"""Independently validate, report, and optionally install the MH370 ERA5 grid."""

from __future__ import annotations

import argparse
import array
import hashlib
import html
import json
import math
import mmap
import os
import resource
import shutil
import struct
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


MAGIC = b"MHERA5V1"
EXPECTED_SHAPE = (9, 12, 221, 141)
EXPECTED_SOURCE_SHAPE = (9, 18, 221, 141)
EXPECTED_TIME_STRINGS = (
    "2014-03-07T17:00:00",
    "2014-03-07T18:00:00",
    "2014-03-07T19:00:00",
    "2014-03-07T20:00:00",
    "2014-03-07T21:00:00",
    "2014-03-07T22:00:00",
    "2014-03-07T23:00:00",
    "2014-03-08T00:00:00",
    "2014-03-08T01:00:00",
)
EXPECTED_TIMES = tuple(
    int(datetime.fromisoformat(value).replace(tzinfo=timezone.utc).timestamp())
    for value in EXPECTED_TIME_STRINGS
)
EXPECTED_ALTITUDES_FT = (
    500.0,
    5_000.0,
    10_000.0,
    15_000.0,
    20_000.0,
    25_000.0,
    28_000.0,
    31_000.0,
    34_000.0,
    37_000.0,
    40_000.0,
    43_000.0,
)
EXPECTED_LATITUDES = tuple(50.0 - 0.5 * index for index in range(221))
EXPECTED_LONGITUDES = tuple(55.0 + 0.5 * index for index in range(141))
EXPECTED_SOURCE_PRESSURES_HPA = (
    150,
    175,
    200,
    225,
    250,
    300,
    350,
    400,
    450,
    500,
    550,
    600,
    650,
    700,
    825,
    850,
    975,
    1000,
)
EXPECTED_VARIABLES = (
    "temperature_k",
    "wind_east_m_s",
    "wind_north_m_s",
)
EXPECTED_SPOTS = (
    ("2014-03-07T17:00:00", 500, 50.0, 55.0),
    ("2014-03-07T21:00:00", 20_000, -5.0, 90.0),
    ("2014-03-08T01:00:00", 43_000, -60.0, 125.0),
)
EXPECTED_SOURCE = (
    "gs://gcp-public-data-arco-era5/ar/full_37-1h-0p25deg-chunk-1.zarr-v3"
)
EXPECTED_ACCESS_REVISION = (
    "google-research/arco-era5@8fb5e9b982f489ba91af3ced9ce0b0a8ade8dd7d"
)
EXPECTED_METADATA_GENERATION = "1787799989791674"
EXPECTED_METADATA_SHA256 = (
    "b53631fb7e4767108275025f12d9c304da8d849d7862ac0e1439ab6634ab8fbd"
)
EXPECTED_CHUNK_IDENTITY_SHA256 = (
    "eed7079e6bbd5260d95f965071ed656d9667d43864f720207021fc1fb5bfb887"
)
EXPECTED_OUTPUT_SHA256 = (
    "261f4e1442ffac69df0201371f7dbf42da0ac0fa30065fc04e0e6293677a2a53"
)
EXPECTED_OUTPUT_BYTES = 40_386_248

SEA_LEVEL_PRESSURE_HPA = 1013.25
SEA_LEVEL_TEMPERATURE_K = 288.15
LAPSE_RATE_K_M = 0.0065
TROPOPAUSE_HEIGHT_M = 11_000.0
TROPOPAUSE_TEMPERATURE_K = 216.65
STANDARD_GRAVITY_M_S2 = 9.80665
DRY_AIR_GAS_CONSTANT_J_KG_K = 287.05287
METRES_PER_FOOT = 0.3048


class ValidationFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationFailure(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def float32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def isa_pressure_hpa(altitude_ft: float) -> float:
    altitude_m = altitude_ft * METRES_PER_FOOT
    if altitude_m <= TROPOPAUSE_HEIGHT_M:
        return SEA_LEVEL_PRESSURE_HPA * (
            1.0 - LAPSE_RATE_K_M * altitude_m / SEA_LEVEL_TEMPERATURE_K
        ) ** (
            STANDARD_GRAVITY_M_S2
            / (DRY_AIR_GAS_CONSTANT_J_KG_K * LAPSE_RATE_K_M)
        )
    pressure_11_hpa = SEA_LEVEL_PRESSURE_HPA * (
        TROPOPAUSE_TEMPERATURE_K / SEA_LEVEL_TEMPERATURE_K
    ) ** (
        STANDARD_GRAVITY_M_S2
        / (DRY_AIR_GAS_CONSTANT_J_KG_K * LAPSE_RATE_K_M)
    )
    return pressure_11_hpa * math.exp(
        -STANDARD_GRAVITY_M_S2 * (altitude_m - TROPOPAUSE_HEIGHT_M)
        / (DRY_AIR_GAS_CONSTANT_J_KG_K * TROPOPAUSE_TEMPERATURE_K)
    )


def pressure_bracket(altitude_ft: float) -> tuple[float, float, float, float]:
    target = isa_pressure_hpa(altitude_ft)
    candidates = [value for value in EXPECTED_SOURCE_PRESSURES_HPA if value > target]
    require(bool(candidates), f"no upper pressure bracket for {altitude_ft} ft")
    upper = float(min(candidates))
    lower_candidates = [
        value for value in EXPECTED_SOURCE_PRESSURES_HPA if value < target
    ]
    require(bool(lower_candidates), f"no lower pressure bracket for {altitude_ft} ft")
    lower = float(max(lower_candidates))
    weight = (math.log(target) - math.log(lower)) / (
        math.log(upper) - math.log(lower)
    )
    require(0.0 < weight < 1.0, f"non-interior bracket weight at {altitude_ft} ft")
    return target, lower, upper, weight


def unpack_axis(raw: mmap.mmap, cursor: int, count: int, code: str):
    byte_width = struct.calcsize(code)
    values = struct.unpack_from(f"<{count}{code}", raw, cursor)
    return values, cursor + count * byte_width


def parse_binary(raw: mmap.mmap) -> dict:
    require(raw[:8] == MAGIC, "binary magic is not MHERA5V1")
    shape = struct.unpack_from("<IIII", raw, 8)
    require(shape == EXPECTED_SHAPE, f"unexpected binary shape {shape}")
    nt, na, ny, nx = shape
    cursor = 24
    times, cursor = unpack_axis(raw, cursor, nt, "q")
    altitudes, cursor = unpack_axis(raw, cursor, na, "f")
    latitudes, cursor = unpack_axis(raw, cursor, ny, "f")
    longitudes, cursor = unpack_axis(raw, cursor, nx, "f")
    count = math.prod(shape)
    field_bytes = count * 4
    offsets = {
        name: cursor + index * field_bytes
        for index, name in enumerate(EXPECTED_VARIABLES)
    }
    expected_size = cursor + len(EXPECTED_VARIABLES) * field_bytes
    require(len(raw) == expected_size, f"unexpected byte count {len(raw)}")
    require(times == EXPECTED_TIMES, "UTC time axis differs from the pinned hours")
    require(
        altitudes == EXPECTED_ALTITUDES_FT,
        "pressure-altitude axis differs from the pinned targets",
    )
    require(
        latitudes == EXPECTED_LATITUDES,
        "latitude axis is not 50 to -60 degrees at descending 0.5-degree spacing",
    )
    require(
        longitudes == EXPECTED_LONGITUDES,
        "longitude axis is not 55 to 125 degrees east at 0.5-degree spacing",
    )
    return {
        "shape": shape,
        "times": times,
        "altitudes": altitudes,
        "latitudes": latitudes,
        "longitudes": longitudes,
        "count_per_field": count,
        "field_bytes": field_bytes,
        "field_offsets": offsets,
    }


def scan_fields(raw: mmap.mmap, parsed: dict) -> dict:
    result = {}
    for name, offset in parsed["field_offsets"].items():
        values = array.array("f")
        values.frombytes(raw[offset : offset + parsed["field_bytes"]])
        if sys.byteorder != "little":
            values.byteswap()
        require(
            len(values) == parsed["count_per_field"],
            f"wrong value count for {name}",
        )
        require(all(math.isfinite(value) for value in values), f"non-finite {name}")
        minimum = min(values)
        maximum = max(values)
        mean = math.fsum(values) / len(values)
        if name == "temperature_k":
            require(150.0 < minimum < maximum < 350.0, "implausible temperature range")
        else:
            require(-200.0 < minimum < maximum < 200.0, f"implausible {name} range")
        result[name] = {"minimum": minimum, "maximum": maximum, "mean": mean}
    return result


def flat_index(parsed: dict, t: int, a: int, y: int, x: int) -> int:
    _, na, ny, nx = parsed["shape"]
    return (((t * na + a) * ny + y) * nx) + x


def binary_value(raw: mmap.mmap, parsed: dict, name: str, index: int) -> float:
    return struct.unpack_from(
        "<f", raw, parsed["field_offsets"][name] + index * 4
    )[0]


def validate_manifest(manifest: dict, binary_path: Path, parsed: dict) -> dict:
    require(
        manifest["schema_version"] == "mh370-era5-runtime-grid-manifest-v2",
        "unexpected manifest schema",
    )
    require(
        manifest["status"]
        in {
            "validated_candidate_not_yet_installed_locally",
            "validated_expanded_grid",
        },
        "unexpected manifest status",
    )
    require(manifest["source"] == EXPECTED_SOURCE, "unexpected ARCO source")
    require(
        manifest["source_access_revision"] == EXPECTED_ACCESS_REVISION,
        "unexpected ARCO access revision",
    )
    require(
        manifest["source_consolidated_metadata"]["generation"]
        == EXPECTED_METADATA_GENERATION,
        "unexpected consolidated-metadata generation",
    )
    require(
        manifest["source_consolidated_metadata"]["sha256"]
        == EXPECTED_METADATA_SHA256,
        "unexpected consolidated-metadata SHA-256",
    )
    require(
        manifest["source_chunk_identity_sha256"]
        == EXPECTED_CHUNK_IDENTITY_SHA256,
        "unexpected source-chunk identity SHA-256",
    )
    chunk_objects = manifest["source_chunk_objects"]
    require(len(chunk_objects) == 27, "manifest must pin 27 source chunks")
    combinations = {
        (record["variable"], record["time_utc"]) for record in chunk_objects
    }
    expected_combinations = {
        (variable, time_utc)
        for variable in (
            "temperature",
            "u_component_of_wind",
            "v_component_of_wind",
        )
        for time_utc in EXPECTED_TIME_STRINGS
    }
    require(combinations == expected_combinations, "source chunk coverage is incomplete")
    require(
        all(
            record["source_chunks"] == [1, 37, 721, 1440]
            and record["source_dtype"] == "float32"
            and record["generation"].isdigit()
            and record["md5_base64"]
            for record in chunk_objects
        ),
        "source chunk metadata is incomplete",
    )
    canonical_chunks = json.dumps(
        chunk_objects, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    require(
        hashlib.sha256(canonical_chunks).hexdigest()
        == EXPECTED_CHUNK_IDENTITY_SHA256,
        "source chunk identity does not reproduce from the manifest records",
    )
    require(
        sum(record["size_bytes"] for record in chunk_objects)
        == manifest["source_chunk_compressed_bytes"],
        "source chunk compressed byte total does not reproduce",
    )

    require(tuple(manifest["times_utc"]) == EXPECTED_TIME_STRINGS, "wrong UTC hours")
    require(tuple(manifest["times_unix_s"]) == EXPECTED_TIMES, "wrong Unix times")
    require(
        tuple(manifest["source_pressure_levels_hpa"])
        == EXPECTED_SOURCE_PRESSURES_HPA,
        "wrong source pressure levels",
    )
    require(
        tuple(float(value) for value in manifest["pressure_altitudes_ft"])
        == EXPECTED_ALTITUDES_FT,
        "wrong target pressure altitudes",
    )
    require(
        tuple(manifest["source_array_shape_time_pressure_lat_lon"])
        == EXPECTED_SOURCE_SHAPE,
        "wrong selected source shape",
    )
    require(
        tuple(manifest["array_shape_time_pressure_altitude_lat_lon"])
        == EXPECTED_SHAPE,
        "wrong output shape in manifest",
    )
    require(
        tuple(manifest["variables_in_binary_order"]) == EXPECTED_VARIABLES,
        "binary fields are not exactly temperature and horizontal wind",
    )
    require(
        manifest["vertical_wind"] == "not retrieved, inferred, stored, or implied",
        "vertical-wind exclusion is not explicit",
    )
    require(
        manifest["latitude_axis"]
        == {
            "count": 221,
            "first_deg": 50.0,
            "last_deg": -60.0,
            "orientation": "north_to_south_descending",
            "step_deg": -0.5,
        },
        "latitude orientation metadata is wrong",
    )
    require(
        manifest["longitude_axis"]
        == {
            "count": 141,
            "first_deg": 55.0,
            "last_deg": 125.0,
            "orientation": "west_to_east_ascending; degrees_east",
            "step_deg": 0.5,
        },
        "longitude orientation metadata is wrong",
    )

    plan = manifest["pressure_altitude_interpolation"]
    require(len(plan) == len(EXPECTED_ALTITUDES_FT), "incomplete interpolation plan")
    for altitude_ft, record in zip(EXPECTED_ALTITUDES_FT, plan, strict=True):
        target, lower, upper, weight = pressure_bracket(altitude_ft)
        require(record["pressure_altitude_ft"] == altitude_ft, "plan altitude mismatch")
        require(
            math.isclose(record["target_pressure_hpa"], target, rel_tol=0, abs_tol=1e-12),
            "plan target pressure mismatch",
        )
        require(
            record["lower_source_hpa"] == lower
            and record["upper_source_hpa"] == upper,
            "plan source bracket mismatch",
        )
        require(
            math.isclose(
                record["log_pressure_weight_to_upper"],
                weight,
                rel_tol=0,
                abs_tol=1e-15,
            ),
            "plan log-pressure weight mismatch",
        )

    binary_hash = sha256(binary_path)
    require(binary_hash == EXPECTED_OUTPUT_SHA256, "candidate binary SHA-256 changed")
    require(manifest["output_sha256"] == binary_hash, "manifest output hash mismatch")
    require(binary_path.stat().st_size == EXPECTED_OUTPUT_BYTES, "wrong output byte count")
    require(manifest["output_bytes"] == EXPECTED_OUTPUT_BYTES, "wrong manifest byte count")

    extractor_path = Path(__file__).with_name("extract_mh370.py")
    require(extractor_path.is_file(), "extractor script is missing")
    require(
        manifest["extractor_sha256"] == sha256(extractor_path),
        "extractor changed after the publication runs",
    )

    deterministic = manifest["deterministic_regeneration"]
    runs = deterministic["runs"]
    require(
        deterministic["independent_remote_runs"] == 2
        and deterministic["byte_for_byte_equal"] is True
        and len(runs) == 2,
        "independent regeneration attestation is missing",
    )
    require(
        [run["run_id"] for run in runs] == ["independent-a", "independent-b"],
        "independent run identifiers are wrong",
    )
    require(
        all(
            run["output_sha256"] == binary_hash
            and run["output_bytes"] == EXPECTED_OUTPUT_BYTES
            and run["runtime"]["elapsed_seconds"] > 0.0
            and run["runtime"]["peak_process_rss_bytes"] > 0
            for run in runs
        ),
        "independent run hashes or metrics are invalid",
    )

    contract = manifest["density_derivation_contract"]
    require(contract["stored_in_binary"] is False, "density must not be stored")
    require(
        contract["dry_air_gas_constant_j_kg_k"] == DRY_AIR_GAS_CONSTANT_J_KG_K,
        "density gas constant mismatch",
    )
    require(contract["humidity"].startswith("not applied"), "density must be dry air")

    return {"binary_sha256": binary_hash, "source_chunk_count": len(chunk_objects)}


def validate_statistics(manifest: dict, actual: dict) -> None:
    for name in EXPECTED_VARIABLES:
        expected = manifest["field_statistics"][name]
        observed = actual[name]
        require(expected["minimum"] == observed["minimum"], f"{name} minimum mismatch")
        require(expected["maximum"] == observed["maximum"], f"{name} maximum mismatch")
        require(
            math.isclose(expected["mean"], observed["mean"], rel_tol=0, abs_tol=1e-12),
            f"{name} mean mismatch",
        )


def validate_spots(raw: mmap.mmap, parsed: dict, manifest: dict) -> list[dict]:
    spots = manifest["raw_source_spot_checks"]
    require(len(spots) == len(EXPECTED_SPOTS), "wrong raw spot-check count")
    results = []
    for expected_coordinates, spot in zip(EXPECTED_SPOTS, spots, strict=True):
        coordinates = (
            spot["time_utc"],
            spot["pressure_altitude_ft"],
            spot["latitude_deg"],
            spot["longitude_deg"],
        )
        require(coordinates == expected_coordinates, "raw spot coordinates changed")
        t = EXPECTED_TIME_STRINGS.index(spot["time_utc"])
        a = EXPECTED_ALTITUDES_FT.index(float(spot["pressure_altitude_ft"]))
        y = EXPECTED_LATITUDES.index(float(spot["latitude_deg"]))
        x = EXPECTED_LONGITUDES.index(float(spot["longitude_deg"]))
        index = flat_index(parsed, t, a, y, x)
        target, lower, upper, weight = pressure_bracket(spot["pressure_altitude_ft"])
        require(
            math.isclose(spot["target_pressure_hpa"], target, rel_tol=0, abs_tol=1e-12)
            and spot["lower_source_hpa"] == lower
            and spot["upper_source_hpa"] == upper,
            "spot pressure bracket mismatch",
        )
        field_results = {}
        for name in EXPECTED_VARIABLES:
            source = spot["fields"][name]
            raw_lower = source["raw_lower_source_value"]
            raw_upper = source["raw_upper_source_value"]
            require(
                math.isfinite(raw_lower) and math.isfinite(raw_upper),
                f"non-finite raw source spot for {name}",
            )
            independently_interpolated = float32(
                (1.0 - weight) * raw_lower + weight * raw_upper
            )
            stored = binary_value(raw, parsed, name, index)
            require(
                stored == independently_interpolated,
                f"{name} stored spot differs from independent log-pressure interpolation",
            )
            require(source["output_value"] == stored, f"{name} spot record mismatch")
            field_results[name] = {
                "raw_lower": raw_lower,
                "raw_upper": raw_upper,
                "independent_output": independently_interpolated,
                "stored_output": stored,
                "absolute_error": abs(stored - independently_interpolated),
            }
        density = target * 100.0 / (
            DRY_AIR_GAS_CONSTANT_J_KG_K * field_results["temperature_k"]["stored_output"]
        )
        require(
            math.isclose(
                density,
                spot["derived_dry_air_density_kg_m3"],
                rel_tol=0,
                abs_tol=1e-15,
            ),
            "spot dry-air density does not reproduce",
        )
        results.append(
            {
                "time_utc": spot["time_utc"],
                "pressure_altitude_ft": spot["pressure_altitude_ft"],
                "latitude_deg": spot["latitude_deg"],
                "longitude_deg": spot["longitude_deg"],
                "target_pressure_hpa": target,
                "lower_source_hpa": lower,
                "upper_source_hpa": upper,
                "fields": field_results,
                "derived_dry_air_density_kg_m3": density,
            }
        )
    return results


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", delete=False
    ) as stream:
        temporary = Path(stream.name)
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)


def staged_copy(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "wb", dir=destination.parent, prefix=f".{destination.name}.", delete=False
    ) as stream:
        temporary = Path(stream.name)
        with source.open("rb") as input_stream:
            shutil.copyfileobj(input_stream, stream, 1024 * 1024)
        stream.flush()
        os.fsync(stream.fileno())
    return temporary


def install_pair(binary: Path, manifest_path: Path, directory: Path) -> dict:
    binary_destination = directory / "mh370-era5-grid.bin"
    manifest_destination = directory / "mh370-era5-grid.manifest.json"
    previous = {}
    for name, path in (
        ("binary", binary_destination),
        ("manifest", manifest_destination),
    ):
        if path.exists():
            previous[name] = {
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
    staged_binary = staged_copy(binary, binary_destination)
    staged_manifest = staged_copy(manifest_path, manifest_destination)
    require(sha256(staged_binary) == sha256(binary), "staged binary hash mismatch")
    require(
        sha256(staged_manifest) == sha256(manifest_path),
        "staged manifest hash mismatch",
    )
    os.replace(staged_binary, binary_destination)
    os.replace(staged_manifest, manifest_destination)
    require(
        sha256(binary_destination) == EXPECTED_OUTPUT_SHA256,
        "installed binary hash mismatch",
    )
    require(
        sha256(manifest_destination) == sha256(manifest_path),
        "installed manifest hash mismatch",
    )
    return {
        "installed": True,
        "directory": str(directory),
        "previous_artifacts": previous,
        "installed_binary_sha256": sha256(binary_destination),
        "installed_manifest_sha256": sha256(manifest_destination),
    }


def fmt_bytes(value: int) -> str:
    if value >= 1024**3:
        return f"{value / 1024**3:.2f} GiB"
    if value >= 1024**2:
        return f"{value / 1024**2:.2f} MiB"
    return f"{value:,} bytes"


def render_report(manifest: dict, validation: dict) -> str:
    esc = lambda value: html.escape(str(value))
    level_cells = "".join(
        f'<span class="level">{int(level):,}<small> ft</small></span>'
        for level in EXPECTED_ALTITUDES_FT
    )
    time_cells = "".join(
        f'<span class="time">{esc(value[5:10])}<b>{esc(value[11:16])}</b></span>'
        for value in EXPECTED_TIME_STRINGS
    )
    interpolation_rows = "".join(
        "<tr>"
        f"<td>{record['pressure_altitude_ft']:,}</td>"
        f"<td>{record['target_pressure_hpa']:.6f}</td>"
        f"<td>{record['lower_source_hpa']:.0f} / {record['upper_source_hpa']:.0f}</td>"
        f"<td>{record['log_pressure_weight_to_upper']:.9f}</td>"
        "</tr>"
        for record in manifest["pressure_altitude_interpolation"]
    )
    stats_rows = "".join(
        "<tr>"
        f"<td>{esc(name)}</td><td>{values['minimum']:.6f}</td>"
        f"<td>{values['mean']:.6f}</td><td>{values['maximum']:.6f}</td>"
        "</tr>"
        for name, values in validation["field_statistics"].items()
    )
    run_rows = "".join(
        "<tr>"
        f"<td>{esc(run['run_id'])}</td>"
        f"<td>{run['runtime']['elapsed_seconds']:.3f} s</td>"
        f"<td>{fmt_bytes(run['runtime']['peak_process_rss_bytes'])}</td>"
        f"<td><code>{esc(run['output_sha256'][:16])}&hellip;</code></td>"
        "</tr>"
        for run in manifest["deterministic_regeneration"]["runs"]
    )
    spot_rows = "".join(
        "<tr>"
        f"<td>{esc(spot['time_utc'].replace('T', ' '))}</td>"
        f"<td>{spot['pressure_altitude_ft']:,} ft<br><small>{spot['latitude_deg']:.1f}°, {spot['longitude_deg']:.1f}°E</small></td>"
        f"<td>{spot['lower_source_hpa']:.0f} / {spot['upper_source_hpa']:.0f} hPa</td>"
        f"<td>{spot['fields']['temperature_k']['stored_output']:.5f} K</td>"
        f"<td>{spot['fields']['wind_east_m_s']['stored_output']:.5f} / {spot['fields']['wind_north_m_s']['stored_output']:.5f} m/s</td>"
        f"<td>{spot['derived_dry_air_density_kg_m3']:.6f}</td>"
        f"<td>{max(field['absolute_error'] for field in spot['fields'].values()):.1e}</td>"
        "</tr>"
        for spot in validation["independent_spot_checks"]
    )
    source_meta = manifest["source_consolidated_metadata"]
    installed = validation.get("installation", {}).get("installed", False)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>MH370 ERA5 expanded-grid validation</title>
<style>
:root{{--ink:#12202b;--muted:#5b6b76;--line:#d8e1e6;--paper:#fbfcfd;--blue:#0b6b9a;--green:#13795b;--soft:#eaf6f1;--amber:#9a6410}}
*{{box-sizing:border-box}}body{{margin:0;background:#edf2f4;color:var(--ink);font:15px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}}
main{{max-width:1120px;margin:28px auto;padding:0 20px 48px}}header,.card{{background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:0 8px 22px #1b35400d}}
header{{padding:26px 30px;margin-bottom:16px}}h1{{font-size:28px;margin:0 0 5px}}h2{{font-size:18px;margin:0 0 14px}}p{{margin:.5em 0}}.sub{{color:var(--muted)}}.badge{{display:inline-block;color:var(--green);background:var(--soft);border:1px solid #b9dfd0;border-radius:999px;padding:5px 10px;font-weight:750;font-size:12px;letter-spacing:.05em}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0}}.card{{padding:18px}}.metric b{{display:block;font-size:21px;color:var(--blue)}}.metric small{{color:var(--muted)}}
.wide{{margin:16px 0;padding:22px}}.axis{{display:grid;gap:6px}}.times{{grid-template-columns:repeat(9,1fr)}}.levels{{grid-template-columns:repeat(6,1fr)}}.time,.level{{background:#eef5f8;border-radius:7px;padding:8px;text-align:center;font-size:12px}}.time b,.level small{{display:block;color:var(--blue)}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}table{{border-collapse:collapse;width:100%;font-variant-numeric:tabular-nums}}th,td{{padding:8px 9px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}}th{{font-size:12px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}}th:first-child,td:first-child{{text-align:left}}code{{font-size:12px;overflow-wrap:anywhere}}.note{{border-left:4px solid var(--amber);padding:10px 14px;background:#fff8e9}}footer{{color:var(--muted);margin-top:18px;font-size:12px}}
@media(max-width:800px){{.cards,.grid2{{grid-template-columns:1fr 1fr}}.levels{{grid-template-columns:repeat(3,1fr)}}.times{{grid-template-columns:repeat(3,1fr)}}}}@media(max-width:520px){{.cards,.grid2{{grid-template-columns:1fr}}}}
</style></head><body><main>
<header><span class="badge">VALIDATION PASSED</span><h1>MH370 ERA5 expanded atmosphere</h1>
<p class="sub">Public ARCO ERA5 pressure-level temperature and horizontal wind, prepared for 7–8 March 2014. Installed locally: <b>{str(installed).lower()}</b>.</p></header>
<section class="cards">
<div class="card metric"><small>Output shape</small><b>9 × 12 × 221 × 141</b><small>time · altitude · latitude · longitude</small></div>
<div class="card metric"><small>Coverage</small><b>17:00–01:00 UTC</b><small>9 hourly analysis validity times</small></div>
<div class="card metric"><small>Horizontal domain</small><b>55–125° E</b><small>50° N to 60° S at 0.5°</small></div>
<div class="card metric"><small>Binary</small><b>{fmt_bytes(manifest['output_bytes'])}</b><small><code>{esc(manifest['output_sha256'][:20])}&hellip;</code></small></div>
</section>
<section class="card wide"><h2>Coverage axes</h2><div class="axis times">{time_cells}</div><p></p><div class="axis levels">{level_cells}</div></section>
<section class="grid2">
<div class="card wide"><h2>Independent regeneration</h2><table><thead><tr><th>Run</th><th>Wall</th><th>Peak RSS</th><th>SHA-256</th></tr></thead><tbody>{run_rows}</tbody></table>
<p class="sub">Two public-bucket reads with filesystem instance caching disabled produced byte-identical outputs.</p></div>
<div class="card wide"><h2>Field scan</h2><table><thead><tr><th>Field</th><th>Min</th><th>Mean</th><th>Max</th></tr></thead><tbody>{stats_rows}</tbody></table>
<p class="sub">Every one of {math.prod(EXPECTED_SHAPE):,} values per field was finite. Units: K and m s<sup>−1</sup>.</p></div>
</section>
<section class="card wide"><h2>Pressure-height interpolation</h2><table><thead><tr><th>Pressure altitude (ft)</th><th>ISA pressure (hPa)</th><th>ERA5 bracket (hPa)</th><th>log-p weight to upper</th></tr></thead><tbody>{interpolation_rows}</tbody></table>
<p class="note"><b>Near sea level:</b> 500 ft is the lowest target strictly bracketed by public pressure levels (975/1000 hPa). Exact ISA 0 ft is 1013.25 hPa and would require extrapolation, so it is not invented.</p></section>
<section class="card wide"><h2>Raw-source spot checks</h2><table><thead><tr><th>UTC</th><th>Target</th><th>Raw bracket</th><th>Temperature</th><th>East / north wind</th><th>Dry density kg/m³</th><th>|error|</th></tr></thead><tbody>{spot_rows}</tbody></table>
<p class="sub">Stored float32 values were recomputed locally from the two raw ARCO bracket values using natural-log-pressure weights. Density is not stored: ρ = p/(287.05287·T), using the target ISA pressure and local interpolated temperature.</p></section>
<section class="card wide"><h2>Source identity and exclusions</h2>
<p><b>Store:</b> <code>{esc(manifest['source'])}</code><br><b>Consolidated metadata:</b> generation {esc(source_meta['generation'])}, SHA-256 <code>{esc(source_meta['sha256'])}</code><br><b>Historical chunks:</b> {len(manifest['source_chunk_objects'])} objects, {fmt_bytes(manifest['source_chunk_compressed_bytes'])} compressed; identity SHA-256 <code>{esc(manifest['source_chunk_identity_sha256'])}</code>.</p>
<p><b>Variables:</b> temperature K, east-positive U wind m/s, north-positive V wind m/s. Vertical wind was not retrieved, inferred, stored, or implied.</p></section>
<footer>Generated from the candidate binary and manifest by validate_mh370.py at {esc(validation['validated_utc'])}. Local validation: {validation['runtime']['elapsed_seconds']:.3f} s, peak RSS {fmt_bytes(validation['runtime']['peak_process_rss_bytes'])}.</footer>
</main></body></html>"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--install-directory", type=Path)
    args = parser.parse_args()

    started = time.perf_counter()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    with args.binary.open("rb") as stream:
        with mmap.mmap(stream.fileno(), 0, access=mmap.ACCESS_READ) as raw:
            parsed = parse_binary(raw)
            manifest_result = validate_manifest(manifest, args.binary, parsed)
            statistics = scan_fields(raw, parsed)
            validate_statistics(manifest, statistics)
            spots = validate_spots(raw, parsed, manifest)

    validation = {
        "schema_version": "mh370-era5-independent-validation-v1",
        "status": "passed",
        "validated_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "binary_path": str(args.binary),
        "binary_sha256": manifest_result["binary_sha256"],
        "binary_bytes": args.binary.stat().st_size,
        "manifest_path": str(args.manifest),
        "manifest_sha256": sha256(args.manifest),
        "extractor_sha256": sha256(Path(__file__).with_name("extract_mh370.py")),
        "validator_sha256": sha256(Path(__file__)),
        "checks": {
            "binary_header_axes_and_exact_size": "passed",
            "all_field_values_finite_and_plausible": "passed",
            "manifest_and_source_object_identity": "passed",
            "two_byte_identical_remote_regenerations": "passed",
            "raw_bracket_spot_interpolation": "passed_bit_exact_float32",
            "dry_air_density_contract": "passed",
            "vertical_wind_absent": "passed",
        },
        "shape_time_pressure_altitude_lat_lon": list(parsed["shape"]),
        "values_scanned_per_field": parsed["count_per_field"],
        "source_chunk_count": manifest_result["source_chunk_count"],
        "field_statistics": statistics,
        "independent_spot_checks": spots,
    }
    if args.install_directory is not None:
        validation["installation"] = install_pair(
            args.binary, args.manifest, args.install_directory
        )
    else:
        validation["installation"] = {"installed": False}

    validation["runtime"] = {
        "elapsed_seconds": time.perf_counter() - started,
        "peak_process_rss_bytes": int(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        )
        * 1024,
        "peak_process_rss_basis": "Linux getrusage(RUSAGE_SELF).ru_maxrss",
    }
    report = render_report(manifest, validation)
    atomic_write_text(args.report, report)
    validation["report_path"] = str(args.report)
    validation["report_sha256"] = sha256(args.report)
    atomic_write_text(
        args.record,
        json.dumps(validation, indent=2, sort_keys=True) + "\n",
    )
    print(json.dumps(validation, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
