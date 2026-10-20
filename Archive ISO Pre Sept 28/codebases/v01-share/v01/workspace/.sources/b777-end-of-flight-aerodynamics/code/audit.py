#!/usr/bin/env python3
"""Reproducible, source-only audit of public B777 end-of-flight candidates.

This program deliberately implements no estimator model.  It verifies and inspects
upstream artifacts in an external cache, performs independent point-mass and
trajectory checks, and regenerates the audit outputs.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import math
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tarfile
from typing import Any, Iterable
import xml.etree.ElementTree as ET
import zipfile


PACKAGE_DIR = Path(__file__).resolve().parents[1]
PINS_PATH = PACKAGE_DIR / "data" / "source-pins.json"
OPENAP_RUNTIME_PATH = PACKAGE_DIR / "data" / "openap-runtime-observation.json"
CONTRACT_PATH = PACKAGE_DIR / "candidate-families.json"
OUTPUT_DIR = PACKAGE_DIR / "outputs"

G_M_S2 = 9.80665
G_FT_S2 = 32.174
R_AIR = 287.05287
GAMMA_AIR = 1.4
WING_AREA_M2 = 427.8
FL350_M = 35_000 * 0.3048


class AuditError(RuntimeError):
    """A reproducibility, format, or scientific invariant failed."""


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_by_id(pins: dict[str, Any], source_id: str) -> dict[str, Any]:
    matches = [source for source in pins["sources"] if source["id"] == source_id]
    if len(matches) != 1:
        raise AuditError(f"Expected exactly one source pin for {source_id!r}")
    return matches[0]


def ensure_external_cache(cache_dir: Path) -> Path:
    resolved = cache_dir.expanduser().resolve()
    package = PACKAGE_DIR.resolve()
    try:
        resolved.relative_to(package)
    except ValueError:
        pass
    else:
        raise AuditError(f"Cache must be outside the source package: {resolved}")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved


def fetch_sources(pins: dict[str, Any], cache_dir: Path, offline: bool) -> dict[str, Any]:
    verified: dict[str, Any] = {}
    for source in pins["sources"]:
        if not source.get("fetch"):
            continue
        destination = cache_dir / source["cache_filename"]
        if not destination.exists():
            if offline:
                raise AuditError(f"Offline source is missing: {destination}")
            temporary = destination.with_suffix(destination.suffix + ".partial")
            command = [
                "curl",
                "--http1.1",
                "--location",
                "--fail",
                "--silent",
                "--show-error",
                "--retry",
                "5",
                "--retry-all-errors",
                source["url"],
                "--output",
                os.fspath(temporary),
            ]
            completed = subprocess.run(command, check=False)
            if completed.returncode != 0:
                temporary.unlink(missing_ok=True)
                raise AuditError(f"Download failed for {source['id']} (curl {completed.returncode})")
            temporary.replace(destination)
        actual = sha256_file(destination)
        if actual != source["sha256"]:
            raise AuditError(
                f"Hash mismatch for {source['id']}: expected {source['sha256']}, got {actual}"
            )
        verified[source["id"]] = {
            "cache_file": destination.name,
            "bytes": destination.stat().st_size,
            "sha256": actual,
        }
    return verified


def tar_member_by_suffix(archive: Path, suffix: str) -> bytes:
    with tarfile.open(archive, "r:gz") as bundle:
        matches = [member for member in bundle.getmembers() if member.isfile() and member.name.endswith(suffix)]
        if len(matches) != 1:
            raise AuditError(f"Expected one *{suffix} in {archive.name}; found {len(matches)}")
        handle = bundle.extractfile(matches[0])
        if handle is None:
            raise AuditError(f"Could not read {matches[0].name}")
        return handle.read()


def verify_pinned_tar_members(archive: Path, pin: dict[str, Any]) -> None:
    for suffix, expected in pin.get("pinned_members", {}).items():
        actual = sha256_bytes(tar_member_by_suffix(archive, suffix))
        if actual != expected:
            raise AuditError(f"Pinned member mismatch for {suffix}: {actual}")


def finite_float(value: str | None) -> float | None:
    try:
        result = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def sample_stats(values: Iterable[float]) -> dict[str, float | int]:
    items = list(values)
    if not items:
        raise AuditError("Cannot summarize an empty sample")
    return {
        "count": len(items),
        "mean": statistics.fmean(items),
        "sample_stddev": statistics.stdev(items) if len(items) > 1 else 0.0,
        "min": min(items),
        "max": max(items),
    }


def correlation_matrix(rows: list[dict[str, str]], fields: list[str]) -> dict[str, dict[str, float]]:
    matrix: dict[str, dict[str, float]] = {}
    for first in fields:
        matrix[first] = {}
        for second in fields:
            pairs: list[tuple[float, float]] = []
            for row in rows:
                x = finite_float(row.get(first))
                y = finite_float(row.get(second))
                if x is not None and y is not None:
                    pairs.append((x, y))
            mean_x = statistics.fmean(x for x, _ in pairs)
            mean_y = statistics.fmean(y for _, y in pairs)
            covariance = sum((x - mean_x) * (y - mean_y) for x, y in pairs) / (len(pairs) - 1)
            std_x = math.sqrt(sum((x - mean_x) ** 2 for x, _ in pairs) / (len(pairs) - 1))
            std_y = math.sqrt(sum((y - mean_y) ** 2 for _, y in pairs) / (len(pairs) - 1))
            matrix[first][second] = covariance / (std_x * std_y)
    return matrix


def inspect_openap(pins: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    release_pin = source_by_id(pins, "openap_release")
    release = cache_dir / release_pin["cache_filename"]
    verify_pinned_tar_members(release, release_pin)

    aircraft_text = tar_member_by_suffix(release, "openap/data/aircraft/b772.yml").decode()
    polar_text = tar_member_by_suffix(release, "openap/data/dragpolar/b772.yml").decode()
    engines_text = tar_member_by_suffix(release, "openap/data/engine/engines.csv").decode()

    def yaml_number(text: str, key: str) -> float:
        match = re.search(rf"^\s*{re.escape(key)}:\s*([-+0-9.eE]+)\s*$", text, re.MULTILINE)
        if not match:
            raise AuditError(f"Could not locate YAML number {key}")
        return float(match.group(1))

    default_match = re.search(r"^\s*default:\s*(.+?)\s*$", aircraft_text, re.MULTILINE)
    options_match = re.search(r"^\s*options:\s*\n((?:\s+- .+\n)+)", aircraft_text, re.MULTILINE)
    if not default_match or not options_match:
        raise AuditError("Could not parse B772 engine choices")
    options = [line.strip()[2:] for line in options_match.group(1).splitlines()]

    engine_rows = list(csv.DictReader(io.StringIO(engines_text)))
    selected_engines: dict[str, Any] = {}
    for name in ["Trent 892", "Trent 895", "PW4090"]:
        matches = [row for row in engine_rows if row["name"] == name]
        if len(matches) != 1:
            raise AuditError(f"Expected one OpenAP engine row for {name}")
        row = matches[0]
        selected_engines[name] = {
            key: (float(row[key]) if row[key] else None)
            for key in [
                "bpr",
                "pr",
                "max_thrust",
                "ff_to",
                "ff_co",
                "ff_app",
                "ff_idl",
                "cruise_thrust",
                "cruise_mach",
                "cruise_alt",
            ]
        }

    dataset_pin = source_by_id(pins, "openap_drag_polar_dataset")
    dataset_path = cache_dir / dataset_pin["cache_filename"]
    member_name = "data/estimation_results/estimation_result_b772.csv"
    with zipfile.ZipFile(dataset_path) as bundle:
        member_bytes = bundle.read(member_name)
        expected_member = dataset_pin["pinned_members"][member_name]
        if sha256_bytes(member_bytes) != expected_member:
            raise AuditError("OpenAP B772 estimation member hash mismatch")
        estimation_rows = list(csv.DictReader(io.StringIO(member_bytes.decode("utf-8-sig"))))

        trajectory_names = sorted(
            name
            for name in bundle.namelist()
            if name.startswith("data/flight_trajectories/b772/") and name.endswith(".csv")
        )
        coverage_values: dict[str, list[float]] = {key: [] for key in ["alt", "tas", "mach", "roc"]}
        coverage_rows = 0
        for name in trajectory_names:
            reader = csv.DictReader(io.TextIOWrapper(bundle.open(name), encoding="utf-8-sig"))
            for row in reader:
                coverage_rows += 1
                for key in coverage_values:
                    value = finite_float(row.get(key))
                    if value is not None:
                        coverage_values[key].append(value)

    estimates: dict[str, Any] = {}
    for key in ["cd0", "k", "e", "m"]:
        values = [value for row in estimation_rows if (value := finite_float(row.get(key))) is not None]
        estimates[key] = sample_stats(values)

    return {
        "release": release_pin["version"],
        "commit": release_pin["commit"],
        "aircraft": "Boeing 777-200/200ER",
        "wing_area_m2": yaml_number(aircraft_text, "area"),
        "wing_span_m": yaml_number(aircraft_text, "span"),
        "mmo": yaml_number(aircraft_text, "mmo"),
        "cruise_mach": yaml_number(aircraft_text, "mach"),
        "current_clean_polar": {
            "cd0": yaml_number(polar_text, "cd0"),
            "k": yaml_number(polar_text, "k"),
            "oswald_e": yaml_number(polar_text, "e"),
        },
        "engine_default": default_match.group(1),
        "engine_options": options,
        "trent_892_is_listed_option": "Trent 892" in options,
        "engine_rows": selected_engines,
        "drag_estimation_dataset": {
            "estimation_rows": len(estimation_rows),
            "finite_estimates": estimates["cd0"]["count"],
            "statistics": estimates,
            "correlation": correlation_matrix(estimation_rows, ["cd0", "k", "e", "m"]),
            "trajectory_files": len(trajectory_names),
            "trajectory_rows": coverage_rows,
            "coverage": {key: sample_stats(values) for key, values in coverage_values.items()},
        },
        "interpretation": [
            "The source enforces an aircraft/engine option check; Trent 892 is not a B772 option.",
            "The empirical B772 source data are climb trajectories and contain no AoA, moments, controls, flameout, or windmilling state.",
            "The nearly singular cd0/k/e correlations are estimation structure, not independent parameter priors.",
        ],
    }


def inspect_flightgear(pins: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for label, source_id in [
        ("modern_gpl", "flightgear_777_modern_fdm"),
        ("historical_unlicensed", "flightgear_777_historical_fdm"),
    ]:
        pin = source_by_id(pins, source_id)
        data = (cache_dir / pin["cache_filename"]).read_bytes()
        root = ET.fromstring(data)
        cruise = root.find("cruise")
        wing = root.find("wing")
        if cruise is None or wing is None:
            raise AuditError(f"Missing YASim cruise or wing in {source_id}")
        stall = wing.find("stall")
        jets = root.findall("jet")
        controls = sorted({element.get("control", "") for element in root.iter("control-input")})
        output[label] = {
            "source_id": source_id,
            "commit": pin["commit"],
            "license_status": pin["license"]["status"] if "status" in pin["license"] else pin["license"]["spdx"],
            "cruise_target": {key: float(value) for key, value in cruise.attrib.items()},
            "wing": {
                "length_m": float(wing.attrib["length"]),
                "chord_m": float(wing.attrib["chord"]),
                "sweep_deg": float(wing.attrib["sweep"]),
                "mcrit": float(wing.attrib["mcrit"]) if "mcrit" in wing.attrib else None,
                "stall": {key: float(value) for key, value in (stall.attrib if stall is not None else {}).items()},
            },
            "active_jets": [
                {
                    key: float(jet.attrib[key])
                    for key in ["mass", "thrust", "spool-time", "tsfc"]
                }
                for jet in jets
            ],
            "comment_mentions": {
                "trent_895": "Trent 895" in data.decode(errors="replace"),
                "trent_892": "Trent 892" in data.decode(errors="replace"),
                "ge90_115b": "GE90-115B" in data.decode(errors="replace"),
            },
            "control_mappings": controls,
        }
    return output


def inspect_jsbsim(pins: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    pin = source_by_id(pins, "jsbsim_release")
    archive = cache_dir / pin["cache_filename"]
    verify_pinned_tar_members(archive, pin)
    with tarfile.open(archive, "r:gz") as bundle:
        names = [member.name for member in bundle.getmembers()]
    aircraft_directories: set[str] = set()
    for name in names:
        match = re.search(r"/aircraft/([^/]+)/", name)
        if match:
            aircraft_directories.add(match.group(1))
    token_hits = [name for name in names if re.search(r"(?:777|b772|trent.?892)", name, re.IGNORECASE)]
    return {
        "release": pin["version"],
        "commit": pin["commit"],
        "aircraft_directory_count": len(aircraft_directories),
        "aircraft_directories": sorted(aircraft_directories),
        "B777_path_hits": token_hits,
        "B777_model_present": bool(token_hits),
    }


def column_number(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference)
    if not letters:
        raise AuditError(f"Bad spreadsheet cell reference: {reference}")
    number = 0
    for char in letters.group(0):
        number = number * 26 + ord(char) - ord("A") + 1
    return number


def read_xlsx_sheet(path: Path, sheet_name: str) -> list[list[Any]]:
    main_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    package_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(path) as bundle:
        shared_root = ET.fromstring(bundle.read("xl/sharedStrings.xml"))
        shared = [
            "".join(node.text or "" for node in item.iter(f"{{{main_ns}}}t"))
            for item in shared_root.findall(f"{{{main_ns}}}si")
        ]
        workbook = ET.fromstring(bundle.read("xl/workbook.xml"))
        relationship_id = None
        for sheet in workbook.findall(f".//{{{main_ns}}}sheet"):
            if sheet.attrib.get("name") == sheet_name:
                relationship_id = sheet.attrib[f"{{{rel_ns}}}id"]
                break
        if relationship_id is None:
            raise AuditError(f"XLSX sheet not found: {sheet_name}")
        relationships = ET.fromstring(bundle.read("xl/_rels/workbook.xml.rels"))
        target = None
        for relationship in relationships.findall(f"{{{package_rel_ns}}}Relationship"):
            if relationship.attrib["Id"] == relationship_id:
                target = relationship.attrib["Target"]
                break
        if target is None:
            raise AuditError(f"XLSX relationship not found: {relationship_id}")
        sheet_path = "xl/" + target.lstrip("/")
        root = ET.fromstring(bundle.read(sheet_path))

    rows: list[list[Any]] = []
    for row in root.findall(f".//{{{main_ns}}}row"):
        values: dict[int, Any] = {}
        for cell in row.findall(f"{{{main_ns}}}c"):
            reference = cell.attrib["r"]
            value_node = cell.find(f"{{{main_ns}}}v")
            cell_type = cell.attrib.get("t")
            inline_text = "".join(
                node.text or "" for node in cell.iter(f"{{{main_ns}}}t")
            )
            if cell_type == "inlineStr":
                value = inline_text
            elif value_node is None or value_node.text is None:
                value: Any = None
            elif cell_type == "s":
                value = shared[int(value_node.text)]
            elif cell_type == "str":
                value = value_node.text
            else:
                numeric = float(value_node.text)
                value = int(numeric) if numeric.is_integer() else numeric
            values[column_number(reference)] = value
        if values:
            rows.append([values.get(index) for index in range(1, max(values) + 1)])
    return rows


def inspect_icao_engine(pins: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    pin = source_by_id(pins, "icao_engine_emissions_databank")
    rows = read_xlsx_sheet(cache_dir / pin["cache_filename"], "Gaseous Emissions and Smoke")
    headers = rows[0]
    records: list[dict[str, Any]] = []
    for row in rows[1:]:
        padded = row + [None] * (len(headers) - len(row))
        records.append(dict(zip(headers, padded)))
    matches = [row for row in records if row.get("Engine Identification") == "Trent 892"]
    if len(matches) != 1:
        raise AuditError(f"Expected one ICAO Trent 892 row; found {len(matches)}")
    row = matches[0]
    return {
        "version": pin["version"],
        "uid": row["UID No"],
        "engine": row["Engine Identification"],
        "manufacturer": row["Manufacturer"],
        "bypass_ratio": row["B/P Ratio"],
        "pressure_ratio": row["Pressure Ratio"],
        "rated_static_thrust_kN": row["Rated Thrust (kN)"],
        "current_engine_status": row["Current Engine Status"],
        "fuel_flow_kg_s": {
            "takeoff": row["Fuel Flow T/O (kg/sec)"],
            "climbout": row["Fuel Flow C/O (kg/sec)"],
            "approach": row["Fuel Flow App (kg/sec)"],
            "idle": row["Fuel Flow Idle (kg/sec)"],
        },
        "scope_warning": "Static LTO emissions certification data; not an altitude/Mach, spool-down, or windmilling model.",
    }


def read_iannello_cases(path: Path) -> dict[int, list[dict[str, float]]]:
    cases: dict[int, list[dict[str, float]]] = {}
    with zipfile.ZipFile(path) as bundle:
        for member in sorted(name for name in bundle.namelist() if name.lower().endswith(".csv")):
            match = re.fullmatch(r"Case (\d\d)\.csv", member)
            if not match:
                raise AuditError(f"Unexpected trajectory member: {member}")
            reader = csv.DictReader(io.TextIOWrapper(bundle.open(member), encoding="utf-8-sig"))
            rows = [
                {
                    "t_s": float(row["Time(sec)"]),
                    "x_nm": float(row["X(nm)"]),
                    "y_nm": float(row["Y(nm)"]),
                    "alt_ft": float(row["Alt(ft)"]),
                }
                for row in reader
            ]
            cases[int(match.group(1))] = rows
    if sorted(cases) != list(range(1, 11)):
        raise AuditError(f"Expected cases 1-10, found {sorted(cases)}")
    return cases


def trajectory_case_metrics(rows: list[dict[str, float]], stride: int = 1) -> dict[str, Any]:
    sampled = rows[::stride]
    vertical_rates: list[float] = []
    downward_accelerations: list[float] = []
    for index in range(1, len(sampled)):
        previous = sampled[index - 1]
        current = sampled[index]
        dt = current["t_s"] - previous["t_s"]
        vertical_rates.append((current["alt_ft"] - previous["alt_ft"]) / dt * 60.0)
    for index in range(1, len(vertical_rates)):
        dt = (sampled[index + 1]["t_s"] - sampled[index - 1]["t_s"]) / 2.0
        downward_accelerations.append(-(vertical_rates[index] - vertical_rates[index - 1]) / 60.0 / dt / G_FT_S2)

    first_high_index = None
    for index, rate in enumerate(vertical_rates, start=1):
        if rate <= -15_000:
            first_high_index = index
            break
    chord_to_last_nm = None
    if first_high_index is not None:
        crossing = sampled[first_high_index]
        final = sampled[-1]
        chord_to_last_nm = math.hypot(final["x_nm"] - crossing["x_nm"], final["y_nm"] - crossing["y_nm"])
    max_downward_g = max(downward_accelerations)
    min_vertical_rate = min(vertical_rates)
    return {
        "sample_interval_s": stride,
        "duration_s": sampled[-1]["t_s"] - sampled[0]["t_s"],
        "initial_altitude_ft": sampled[0]["alt_ft"],
        "last_altitude_ft": sampled[-1]["alt_ft"],
        "minimum_vertical_rate_fpm": min_vertical_rate,
        "maximum_downward_acceleration_g": max_downward_g,
        "exceeds_both_published_thresholds": min_vertical_rate <= -15_000 and max_downward_g >= 0.67,
        "first_15000_fpm_to_last_chord_nm": chord_to_last_nm,
    }


def inspect_iannello(pins: dict[str, Any], cache_dir: Path) -> dict[str, Any]:
    pin = source_by_id(pins, "iannello_boeing_eof_trajectories")
    path = cache_dir / pin["cache_filename"]
    cases = read_iannello_cases(path)
    case_metrics = {str(case): trajectory_case_metrics(rows) for case, rows in cases.items()}
    sensitivity: dict[str, Any] = {}
    for stride in [1, 2, 4, 8, 16, 32]:
        metrics = {case: trajectory_case_metrics(rows, stride) for case, rows in cases.items()}
        sensitivity[str(stride)] = {
            "high_rate_cases": [case for case, value in metrics.items() if value["exceeds_both_published_thresholds"]],
            "high_case_acceleration_range_g": [
                min(metrics[case]["maximum_downward_acceleration_g"] for case in [3, 4, 5, 6, 10]),
                max(metrics[case]["maximum_downward_acceleration_g"] for case in [3, 4, 5, 6, 10]),
            ],
        }
    high_cases = [int(case) for case, value in case_metrics.items() if value["exceeds_both_published_thresholds"]]
    distances = [
        case_metrics[str(case)]["first_15000_fpm_to_last_chord_nm"]
        for case in high_cases
    ]
    with zipfile.ZipFile(path) as bundle:
        member_hashes = {name: sha256_bytes(bundle.read(name)) for name in sorted(bundle.namelist())}
    return {
        "case_count": len(cases),
        "member_sha256": member_hashes,
        "one_second_case_metrics": case_metrics,
        "reproduced_high_rate_cases": high_cases,
        "published_high_rate_cases": [3, 4, 5, 6, 10],
        "high_case_chord_distance_range_nm": [min(distances), max(distances)],
        "time_sample_sensitivity": sensitivity,
        "interpretation": [
            "One-second backward differences independently reproduce cases 3, 4, 5, 6 and 10 and the published 4.7-7.9 NM distance range.",
            "The same five-case classification survives 2, 4 and 8 second sampling, but not 16 seconds; acceleration peaks are derivative-window dependent.",
            "The exports contain only X, Y and integer-foot altitude, and their last rows remain above sea level; they are validation comparators, not an implementable model."
        ],
    }


def isa_atmosphere(height_m: float) -> tuple[float, float, float]:
    if height_m < 0:
        height_m = 0.0
    temperature_0 = 288.15
    pressure_0 = 101_325.0
    lapse = -0.0065
    if height_m <= 11_000:
        temperature = temperature_0 + lapse * height_m
        pressure = pressure_0 * (temperature / temperature_0) ** (-G_M_S2 / (lapse * R_AIR))
    else:
        temperature = 216.65
        pressure_11 = pressure_0 * (temperature / temperature_0) ** (-G_M_S2 / (lapse * R_AIR))
        pressure = pressure_11 * math.exp(-G_M_S2 * (height_m - 11_000) / (R_AIR * temperature))
    density = pressure / (R_AIR * temperature)
    sound_speed = math.sqrt(GAMMA_AIR * R_AIR * temperature)
    return density, pressure, sound_speed


def polar_equilibrium(cd0: float, k: float, mass_kg: float, mach: float, height_m: float) -> dict[str, float]:
    density, _, sound_speed = isa_atmosphere(height_m)
    speed = mach * sound_speed
    dynamic_pressure = 0.5 * density * speed**2
    weight = mass_kg * G_M_S2
    cl = weight / (dynamic_pressure * WING_AREA_M2)
    cd = cd0 + k * cl**2
    drag = dynamic_pressure * WING_AREA_M2 * cd
    best_cl = math.sqrt(cd0 / k)
    best_ld = 1.0 / (2.0 * math.sqrt(cd0 * k))
    glide_angle = -math.atan(1.0 / best_ld)
    best_speed = math.sqrt(
        2.0 * weight * math.cos(glide_angle) / (density * WING_AREA_M2 * best_cl)
    )
    return {
        "height_m": height_m,
        "mach": mach,
        "mass_kg": mass_kg,
        "true_airspeed_m_s": speed,
        "dynamic_pressure_Pa": dynamic_pressure,
        "cl": cl,
        "cd": cd,
        "required_total_thrust_N": drag,
        "required_thrust_per_engine_N": drag / 2.0,
        "lift_to_drag": cl / cd,
        "best_cl": best_cl,
        "analytic_best_lift_to_drag": best_ld,
        "best_glide_angle_deg": math.degrees(glide_angle),
        "best_glide_true_airspeed_m_s": best_speed,
        "best_glide_mach": best_speed / sound_speed,
        "best_glide_descent_rate_fpm": best_speed * math.sin(glide_angle) / 0.00508,
        "vertical_force_residual_N": dynamic_pressure * WING_AREA_M2 * cl - weight,
        "longitudinal_force_residual_N_with_required_thrust": drag - drag,
    }


def point_mass_limit_checks(cd0: float, k: float, mass_kg: float) -> dict[str, Any]:
    weight = mass_kg * G_M_S2
    samples = []
    for q in [0.01, 1.0, 100.0, 10_000.0, 100_000.0]:
        cl = weight / (q * WING_AREA_M2)
        drag = q * WING_AREA_M2 * cd0 + k * weight**2 / (q * WING_AREA_M2)
        samples.append({"dynamic_pressure_Pa": q, "implied_cl": cl, "drag_N": drag})
    return {
        "cd_at_cl_zero": cd0,
        "drag_is_positive_for_positive_dynamic_pressure": all(sample["drag_N"] > 0 for sample in samples),
        "low_q_induced_drag_diverges": samples[0]["drag_N"] > samples[1]["drag_N"],
        "no_stall_or_cl_ceiling": True,
        "samples": samples,
        "warning": "These mathematical limits expose the point-mass polar's domain failure; they are not post-stall predictions."
    }


def glide_derivative(
    state: tuple[float, float, float, float], mass_kg: float, cd0: float, k: float
) -> tuple[tuple[float, float, float, float], float]:
    _, height, speed, flight_path_angle = state
    density, _, _ = isa_atmosphere(height)
    cl = math.sqrt(cd0 / k)
    cd = cd0 + k * cl**2
    dynamic_pressure = 0.5 * density * speed**2
    lift = dynamic_pressure * WING_AREA_M2 * cl
    drag = dynamic_pressure * WING_AREA_M2 * cd
    derivative = (
        speed * math.cos(flight_path_angle),
        speed * math.sin(flight_path_angle),
        -drag / mass_kg - G_M_S2 * math.sin(flight_path_angle),
        lift / (mass_kg * speed) - G_M_S2 * math.cos(flight_path_angle) / speed,
    )
    return derivative, drag * speed


def vector_add(
    left: tuple[float, float, float, float],
    right: tuple[float, float, float, float],
    scale: float,
) -> tuple[float, float, float, float]:
    return tuple(a + scale * b for a, b in zip(left, right))  # type: ignore[return-value]


def simulate_glide(cd0: float, k: float, mass_kg: float, step_s: float, duration_s: float = 600.0) -> dict[str, float]:
    density, _, _ = isa_atmosphere(FL350_M)
    cl = math.sqrt(cd0 / k)
    lift_to_drag = 1.0 / (2.0 * math.sqrt(cd0 * k))
    gamma = -math.atan(1.0 / lift_to_drag)
    speed = math.sqrt(
        2.0 * mass_kg * G_M_S2 * math.cos(gamma) / (density * WING_AREA_M2 * cl)
    )
    state = (0.0, FL350_M, speed, gamma)
    initial_energy = mass_kg * G_M_S2 * state[1] + 0.5 * mass_kg * state[2] ** 2
    drag_work = 0.0
    time = 0.0
    while time < duration_s - 1e-12:
        step = min(step_s, duration_s - time)
        k1, p1 = glide_derivative(state, mass_kg, cd0, k)
        k2, p2 = glide_derivative(vector_add(state, k1, step / 2), mass_kg, cd0, k)
        k3, p3 = glide_derivative(vector_add(state, k2, step / 2), mass_kg, cd0, k)
        k4, p4 = glide_derivative(vector_add(state, k3, step), mass_kg, cd0, k)
        state = tuple(
            value + step * (a + 2 * b + 2 * c + d) / 6
            for value, a, b, c, d in zip(state, k1, k2, k3, k4)
        )  # type: ignore[assignment]
        drag_work += step * (p1 + 2 * p2 + 2 * p3 + p4) / 6
        time += step
    final_energy = mass_kg * G_M_S2 * state[1] + 0.5 * mass_kg * state[2] ** 2
    energy_loss = initial_energy - final_energy
    return {
        "step_s": step_s,
        "duration_s": duration_s,
        "range_m": state[0],
        "final_height_m": state[1],
        "final_speed_m_s": state[2],
        "final_flight_path_angle_deg": math.degrees(state[3]),
        "initial_mechanical_energy_J": initial_energy,
        "mechanical_energy_loss_J": energy_loss,
        "integrated_drag_work_J": drag_work,
        "relative_energy_balance_error": abs(energy_loss - drag_work) / energy_loss,
    }


def run_numerical_checks(openap: dict[str, Any]) -> dict[str, Any]:
    mass_kg = float(openap["drag_estimation_dataset"]["statistics"]["m"]["mean"])
    polars = {
        "published_2020": {"cd0": 0.034, "k": 0.051, "oswald_e": 0.723},
        "current_v2_6_0": openap["current_clean_polar"],
    }
    results: dict[str, Any] = {
        "fixture": {
            "mass_kg": mass_kg,
            "mass_source": "Mean of 97 finite B772 estimates in pinned OpenAP Figshare dataset; a numerical fixture, not an MH370 prior.",
            "height": "FL350 ISA",
            "mach": 0.84,
            "wing_area_m2": WING_AREA_M2,
        },
        "ATSB_public_glide_ratio_comparator": 17.0,
        "polars": {},
    }
    for name, polar in polars.items():
        cd0 = float(polar["cd0"])
        k = float(polar["k"])
        equilibrium = polar_equilibrium(cd0, k, mass_kg, 0.84, FL350_M)
        limits = point_mass_limit_checks(cd0, k, mass_kg)
        step_runs = [simulate_glide(cd0, k, mass_kg, step) for step in [0.125, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0]]
        baseline = step_runs[0]
        for run in step_runs:
            run["range_difference_from_0_125s_m"] = run["range_m"] - baseline["range_m"]
            run["height_difference_from_0_125s_m"] = run["final_height_m"] - baseline["final_height_m"]
        results["polars"][name] = {
            "coefficients": polar,
            "equilibrium_cruise": equilibrium,
            "limiting_cases": limits,
            "unpowered_glide_energy_check": step_runs,
            "interpretation": "Equation consistency only. The polar supplies no AoA, stall, moments, controls, windmilling, or post-flameout aircraft validation."
        }
    return results


def validate_contract(contract: dict[str, Any]) -> None:
    admission = contract.get("admission", {})
    if admission.get("status") != "blocked":
        raise AuditError("Audit contract must retain the exact blocked admission")
    if admission.get("implementation_ready_conditional_aerodynamic_parameters") is not None:
        raise AuditError("Blocked audit must not publish implementation-ready parameters")
    family_ids = [candidate["id"] for candidate in contract["candidate_families"]]
    if len(family_ids) != len(set(family_ids)):
        raise AuditError("Duplicate candidate family id")


def load_openap_runtime_observation(pins: dict[str, Any]) -> dict[str, Any]:
    observation = read_json(OPENAP_RUNTIME_PATH)
    release = source_by_id(pins, "openap_release")
    if observation["source"]["commit"] != release["commit"]:
        raise AuditError("OpenAP runtime observation commit does not match the source pin")
    if observation["source"]["archive_sha256"] != release["sha256"]:
        raise AuditError("OpenAP runtime observation archive hash does not match the source pin")
    unforced_892 = [
        engine
        for engine in observation["probe"]["engines"]
        if engine["engine"] == "Trent 892" and not engine["force_engine"]
    ]
    if len(unforced_892) != 1 or unforced_892[0]["status"] != "rejected":
        raise AuditError("OpenAP runtime observation must preserve the Trent 892 mismatch rejection")
    return observation


def candidate_summary(candidate: dict[str, Any]) -> str:
    capability = candidate.get("capabilities", {})
    available = [key.replace("_", " ") for key, value in capability.items() if value not in {"absent", "not_claimed", "not_established"}]
    return ", ".join(available[:4]) if available else "No scoped capability"


def render_html(contract: dict[str, Any], results: dict[str, Any]) -> str:
    admission = contract["admission"]
    candidate_rows = []
    for candidate in contract["candidate_families"]:
        blockers = " ".join(candidate["blocking_findings"][:2])
        candidate_rows.append(
            f"<tr><td><strong>{html.escape(candidate['name'])}</strong><small>{html.escape(candidate['id'])}</small></td>"
            f"<td>{html.escape(candidate_summary(candidate))}</td>"
            f"<td>{html.escape(candidate['legal_status'].replace('_', ' '))}</td>"
            f"<td><span class='status'>{html.escape(candidate['admission_status'].replace('_', ' '))}</span><br>{html.escape(blockers)}</td></tr>"
        )

    polar_cards = []
    for name, polar in results["numerical_checks"]["polars"].items():
        eq = polar["equilibrium_cruise"]
        coeff = polar["coefficients"]
        polar_cards.append(
            f"<article><h3>{html.escape(name.replace('_', ' '))}</h3>"
            f"<div class='metric'>{eq['analytic_best_lift_to_drag']:.2f}<small>analytic max L/D</small></div>"
            f"<p>cd0 {coeff['cd0']:.3f} · k {coeff['k']:.3f} · FL350/M0.84 required thrust {eq['required_total_thrust_N']/1000:.1f} kN</p>"
            f"<p class='caution'>Equation check only — no stall, moments, controls, or windmilling.</p></article>"
        )

    case_rows = []
    iannello = results["candidate_execution"]["boeing_trajectory_exports"]
    for case in range(1, 11):
        metric = iannello["one_second_case_metrics"][str(case)]
        distance = metric["first_15000_fpm_to_last_chord_nm"]
        case_rows.append(
            f"<tr><td>{case:02d}</td><td>{metric['minimum_vertical_rate_fpm']:.0f}</td>"
            f"<td>{metric['maximum_downward_acceleration_g']:.3f}</td>"
            f"<td>{'yes' if metric['exceeds_both_published_thresholds'] else 'no'}</td>"
            f"<td>{'—' if distance is None else f'{distance:.3f}'}</td><td>{metric['last_altitude_ft']:.0f}</td></tr>"
        )

    sensitivity_rows = []
    for step, value in iannello["time_sample_sensitivity"].items():
        sensitivity_rows.append(
            f"<tr><td>{step}</td><td>{', '.join(str(case) for case in value['high_rate_cases']) or 'none'}</td>"
            f"<td>{value['high_case_acceleration_range_g'][0]:.3f}–{value['high_case_acceleration_range_g'][1]:.3f}</td></tr>"
        )

    source_rows = []
    for source_id, source in results["verified_sources"].items():
        source_rows.append(
            f"<tr><td>{html.escape(source_id)}</td><td>{source['bytes']:,}</td><td><code>{source['sha256']}</code></td></tr>"
        )

    embedded = html.escape(json.dumps(results, sort_keys=True))
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>B777 end-of-flight model audit</title>
<style>
:root {{ color-scheme: dark; --ink:#eef1f5; --muted:#aeb7c4; --panel:#151c25; --line:#303b49; --red:#ff7067; --amber:#ffc461; --green:#71d59f; }}
* {{ box-sizing:border-box }} body {{ margin:0; background:#0d1218; color:var(--ink); font:15px/1.55 system-ui,-apple-system,sans-serif; }}
main {{ max-width:1180px; margin:auto; padding:44px 24px 80px; }}
h1 {{ font-size:clamp(2rem,5vw,4.4rem); line-height:1; margin:.2em 0; letter-spacing:-.045em; }} h2 {{ margin-top:3rem; }} h3 {{ margin:.2rem 0 1rem; text-transform:capitalize; }}
.eyebrow, small {{ color:var(--muted); letter-spacing:.06em; text-transform:uppercase; }}
.verdict {{ border:1px solid #743d3a; background:linear-gradient(135deg,#301917,#171c24); border-radius:18px; padding:24px; margin:28px 0; }}
.verdict strong {{ color:var(--red); font-size:1.4rem; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(250px,1fr)); gap:14px; }}
article {{ background:var(--panel); border:1px solid var(--line); border-radius:14px; padding:18px; }}
.metric {{ font-size:2.6rem; font-weight:750; color:var(--amber); }} .metric small {{ display:block; font-size:.67rem; font-weight:500; }}
.caution {{ color:var(--amber); }} .status {{ color:var(--amber); font-weight:700; }}
.table-wrap {{ overflow:auto; border:1px solid var(--line); border-radius:14px; }}
table {{ width:100%; border-collapse:collapse; min-width:720px; background:var(--panel); }} th,td {{ padding:12px 14px; text-align:left; vertical-align:top; border-bottom:1px solid var(--line); }} th {{ color:var(--muted); font-size:.75rem; text-transform:uppercase; }} td small {{ display:block; text-transform:none; overflow-wrap:anywhere; }}
code {{ font:12px ui-monospace,monospace; color:#b8d7ff; overflow-wrap:anywhere; }}
.note {{ border-left:3px solid var(--amber); padding-left:14px; color:var(--muted); }}
details {{ margin-top:2rem; }} summary {{ cursor:pointer; color:#b8d7ff; }}
@media print {{ :root {{ color-scheme:light }} body {{ background:white;color:#111 }} article,table,.verdict {{ background:white;color:#111 }} }}
</style>
</head>
<body><main>
<p class="eyebrow">Source-only candidate-family audit · frozen 27 August 2026</p>
<h1>No admissible public<br>B777 end-of-flight model</h1>
<section class="verdict"><strong>{html.escape(admission['code'])}</strong><p>{html.escape(admission['plain_blocker'])}</p><p>The audit publishes no implementation-ready aerodynamic parameters.</p></section>

<h2>Candidate disposition</h2>
<div class="table-wrap"><table><thead><tr><th>Family</th><th>What it supplies</th><th>Legal intake</th><th>Admission</th></tr></thead><tbody>{''.join(candidate_rows)}</tbody></table></div>

<h2>Independent equation checks</h2>
<p class="note">Both public B772 polars are useful for exposing scope limits, not for admission. ATSB's public theoretical comparator is L/D ≈ 17; neither polar supplies AoA or post-stall behavior.</p>
<div class="grid">{''.join(polar_cards)}</div>

<h2>Public Boeing trajectory reproduction</h2>
<p>One-second finite differences reproduce the published high-rate cases 3, 4, 5, 6 and 10. The chord from first 15,000-fpm crossing to the last exported row spans {iannello['high_case_chord_distance_range_nm'][0]:.3f}–{iannello['high_case_chord_distance_range_nm'][1]:.3f} NM. Last rows are still above sea level.</p>
<div class="table-wrap"><table><thead><tr><th>Case</th><th>Minimum vertical rate<br>ft/min</th><th>Maximum downward<br>acceleration g</th><th>Both thresholds</th><th>Crossing to last row<br>NM</th><th>Last altitude<br>ft</th></tr></thead><tbody>{''.join(case_rows)}</tbody></table></div>

<h2>Derivative sampling sensitivity</h2>
<p class="note">The five-case classification survives through 8-second samples and changes at 16 seconds. Peak acceleration is not invariant to the derivative window.</p>
<div class="table-wrap"><table><thead><tr><th>Sample interval (s)</th><th>Cases above both thresholds</th><th>Acceleration range for published high cases (g)</th></tr></thead><tbody>{''.join(sensitivity_rows)}</tbody></table></div>

<h2>What would unblock admission</h2>
<p>{html.escape(admission['release_condition'])}</p>

<details><summary>Verified source bytes and SHA-256</summary><div class="table-wrap"><table><thead><tr><th>Source</th><th>Bytes</th><th>SHA-256</th></tr></thead><tbody>{''.join(source_rows)}</tbody></table></div></details>
<script type="application/json" id="audit-results">{embedded}</script>
</main></body></html>"""


def package_checksums() -> str:
    files = [
        CONTRACT_PATH,
        PACKAGE_DIR / "README.md",
        PACKAGE_DIR / "CITATIONS.md",
        PINS_PATH,
        OPENAP_RUNTIME_PATH,
        PACKAGE_DIR / "code" / "audit.py",
        PACKAGE_DIR / "code" / "openap_runtime_probe.py",
        PACKAGE_DIR / "code" / "test_audit.py",
        OUTPUT_DIR / "results.json",
        OUTPUT_DIR / "comparison.html",
    ]
    lines = []
    for path in files:
        if path.exists():
            lines.append(f"{sha256_file(path)}  {path.relative_to(PACKAGE_DIR).as_posix()}")
    return "\n".join(lines) + "\n"


def execute(cache_dir: Path, offline: bool = False, write_outputs: bool = True) -> dict[str, Any]:
    pins = read_json(PINS_PATH)
    contract = read_json(CONTRACT_PATH)
    validate_contract(contract)
    cache = ensure_external_cache(cache_dir)
    verified = fetch_sources(pins, cache, offline)
    openap = inspect_openap(pins, cache)
    candidate_execution = {
        "openap": openap,
        "openap_runtime_probe": load_openap_runtime_observation(pins),
        "flightgear_yasim": inspect_flightgear(pins, cache),
        "official_jsbsim": inspect_jsbsim(pins, cache),
        "trent892_certification": inspect_icao_engine(pins, cache),
        "boeing_trajectory_exports": inspect_iannello(pins, cache),
    }
    results = {
        "schema_version": "1.0.0",
        "audit_date_utc": "2026-08-27",
        "admission": contract["admission"],
        "verified_sources": verified,
        "candidate_execution": candidate_execution,
        "numerical_checks": run_numerical_checks(openap),
        "scientific_boundary": {
            "measured_or_published_inputs": [
                "Pinned source bytes and their extracted values",
                "Public Boeing trajectory coordinates",
                "ATSB's approximately 17:1 theoretical glide comparator",
                "ICAO static Trent 892 certification fields"
            ],
            "audit_calculations": [
                "Parabolic-polar equilibrium and mathematical limiting cases",
                "Unpowered two-dimensional point-mass energy integration",
                "Finite-difference trajectory rates and sampling sensitivity"
            ],
            "not_inferred": [
                "MH370 end-of-flight prior",
                "00:19 BFO-conditioned parameter",
                "Impact position",
                "Cross-family surrogate uncertainty"
            ]
        }
    }
    if write_outputs:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        write_json(OUTPUT_DIR / "results.json", results)
        (OUTPUT_DIR / "comparison.html").write_text(render_html(contract, results), encoding="utf-8")
        (PACKAGE_DIR / "SHA256SUMS").write_text(package_checksums(), encoding="utf-8")
    return results


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cache-dir",
        type=Path,
        required=True,
        help="External download/tool cache (use /tmp; paths inside this source package are rejected).",
    )
    parser.add_argument("--offline", action="store_true", help="Require all pinned sources to exist in the cache.")
    parser.add_argument("--no-write", action="store_true", help="Run all checks without regenerating outputs.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        results = execute(args.cache_dir, offline=args.offline, write_outputs=not args.no_write)
    except (AuditError, OSError, ValueError, zipfile.BadZipFile, tarfile.TarError, ET.ParseError) as error:
        print(f"audit failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps({
        "status": results["admission"]["status"],
        "code": results["admission"]["code"],
        "verified_sources": len(results["verified_sources"]),
        "outputs_written": not args.no_write,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
