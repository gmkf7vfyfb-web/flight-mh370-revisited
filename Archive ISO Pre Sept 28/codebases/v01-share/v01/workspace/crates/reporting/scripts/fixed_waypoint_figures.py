#!/usr/bin/env python3
"""Generate the fixed-waypoint conditional comparison from run artifacts only.

The three structural families remain separate. Equal weighting is used only for
the declared numerical seeds within one family. Candidate selection was
geometry-prompted, so conditional integrated-fit differences are not model
probabilities and do not establish waypoint intent.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import sys
import tomllib
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1394237459")

import matplotlib as mpl

mpl.use("Agg")
mpl.rcParams.update(
    {
        "axes.facecolor": "#fbfcfd",
        "axes.grid": True,
        "font.family": "DejaVu Sans",
        "font.size": 9.2,
        "grid.color": "#dfe4e9",
        "grid.linewidth": 0.65,
        "pdf.fonttype": 42,
        "savefig.dpi": 300,
        "svg.fonttype": "none",
        "svg.hashsalt": "mh370-fixed-waypoint-conditionals",
    }
)
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from scipy.ndimage import gaussian_filter


SEEDS = (370023, 370024, 370025)
PARTICLES_PER_SEED = 30_000
BANDWIDTH_NM = 7.5
SOURCE_EPOCH_UTC = "2014-03-08T00:10:59Z"
M1941_TIME_S = 5953.0
M0011_TIME_S = 22150.0
R600_TIME_S = 22660.0
SELECTED_INTEGRATION_STEP_S = 30.0
R600_MAX_LOG_PREDICTIVE_RANGE_NATS = 0.8
R600_MAX_CONDITIONED_CENTROID_SEPARATION_NM = 30.0
FAMILIES = (
    (
        "constant-true-track-reference",
        "Constant true track",
        "#0072B2",
        "o",
        "constant_true_track",
    ),
    (
        "direct-to-davis-plateau-sla",
        "Direct to Davis Plateau",
        "#D55E00",
        "s",
        "lateral_navigation",
    ),
    (
        "direct-to-fossil-bluff",
        "Direct to Fossil Bluff",
        "#009E73",
        "D",
        "lateral_navigation",
    ),
)
ROOT = Path(__file__).resolve().parents[3]
DEFAULT_STEP_CONTROL = ROOT / "runs/mh370/fixed-waypoint-integration-step-control"
DEFAULT_R600_CONFIG = ROOT / "configs/mh370-r600-bto-predictive-control.toml"
CITATION_LEDGER = ROOT / ".sources/antarctic-waypoint-navigation/README.md"
SELECTION_LEDGER = ROOT / ".sources/antarctic-waypoint-navigation/SELECTION-LEDGER.md"
SCOPE = (
    "Three separate one-turn structural conditionals fitted to the same BTO/BFO observations "
    "through 00:11; ERA5 active, IGRF inactive; equal seed weighting occurs only within a family."
)
SELECTION_WARNING = (
    "POST-HOC, NON-EXHAUSTIVE GEOMETRY SCREEN; R600 NOT SELECTION-BLIND — sensitivity "
    "controls, not intent/model/impact probabilities."
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def require_file(path: Path, description: str) -> Path:
    if not path.is_file():
        raise ValueError(f"missing {description}: {path}")
    return path


def finite_number(value: object, description: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite {description}: {value!r}")
    return number


def latlon(value: dict, description: str) -> tuple[float, float]:
    return (
        finite_number(value["latitude"], f"{description} latitude"),
        finite_number(value["longitude"], f"{description} longitude"),
    )


def position(value: dict, description: str) -> tuple[float, float]:
    return (
        finite_number(value["latitude_deg"], f"{description} latitude"),
        finite_number(value["longitude_deg"], f"{description} longitude"),
    )


def angular_summary(value: dict, description: str) -> tuple[float, tuple[float, float]]:
    if not isinstance(value, dict):
        raise ValueError(f"missing {description}")
    mean = finite_number(value["circular_mean_deg"], f"{description} circular mean")
    interval = value.get("central_90_deg")
    if not isinstance(interval, list) or len(interval) != 2:
        raise ValueError(f"invalid {description} central interval")
    low = finite_number(interval[0], f"{description} central-90 low")
    high = finite_number(interval[1], f"{description} central-90 high")
    if not 0.0 <= mean < 360.0 or low > high or not low - 1e-9 <= mean <= high + 1e-9:
        raise ValueError(f"invalid {description} angular summary")
    return mean, (low, high)


def checkpoint_summary(
    value: dict | None,
    epoch_id: str,
    time_s: float,
    description: str,
) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"missing {description}")
    if value.get("epoch_id") != epoch_id or not math.isclose(
        finite_number(value.get("time_s"), f"{description} time"),
        time_s,
        rel_tol=0,
        abs_tol=1e-9,
    ):
        raise ValueError(f"{description} is bound to the wrong epoch")
    position(value["mean"], f"{description} mean")
    for field in ("latitude_90_deg", "longitude_90_deg"):
        interval = value.get(field)
        if not isinstance(interval, list) or len(interval) != 2:
            raise ValueError(f"invalid {description} {field}")
        low = finite_number(interval[0], f"{description} {field} low")
        high = finite_number(interval[1], f"{description} {field} high")
        if low > high:
            raise ValueError(f"reversed {description} {field}")
    angular_summary(value["track_true"], f"{description} true track")
    return value


def resolve_config_input(config_path: Path, raw: str) -> Path:
    candidate = Path(raw)
    return candidate if candidate.is_absolute() else config_path.parent / candidate


def manifest_artifact(run: Path, manifest: dict, relative: str) -> Path:
    expected = manifest.get("outputs", {}).get(relative)
    if not expected:
        raise ValueError(f"run manifest does not identify loaded artifact: {relative}")
    path = require_file(run / relative, "run artifact")
    actual = digest(path)
    if actual != expected:
        raise ValueError(f"run artifact hash mismatch: {relative}")
    return path


def resolve_config_path(raw: str) -> Path:
    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate
    root_candidate = ROOT / candidate
    return root_candidate if root_candidate.exists() else candidate.resolve()


def fixed_waypoint(metadata: dict | None) -> dict | None:
    if metadata is None:
        return None
    latitude, longitude = latlon(metadata["position"], "fixed waypoint")
    return {
        "target_name": str(metadata["target_name"]),
        "latitude_deg": latitude,
        "longitude_deg": longitude,
        "arrival_radius_nm": finite_number(metadata["arrival_radius"], "arrival radius"),
        "coordinate_source_title": str(metadata["coordinate_source_title"]),
        "coordinate_source_uri": str(metadata["coordinate_source_uri"]),
        "coordinate_frame_assumption": str(metadata["coordinate_frame_assumption"]),
        "coordinate_source_date": metadata.get("coordinate_source_date"),
        "coordinate_note": str(metadata["coordinate_note"]),
    }


def configured_waypoint(family: dict) -> dict | None:
    metadata = family.get("fixed_waypoint")
    if metadata is None:
        return None
    return {
        "target_name": str(metadata["target_name"]),
        "latitude_deg": finite_number(metadata["latitude_deg"], "configured waypoint latitude"),
        "longitude_deg": finite_number(
            metadata["longitude_deg"], "configured waypoint longitude"
        ),
        "arrival_radius_nm": finite_number(
            metadata["arrival_radius_nm"], "configured arrival radius"
        ),
        "coordinate_source_title": str(metadata["coordinate_source_title"]),
        "coordinate_source_uri": str(metadata["coordinate_source_uri"]),
        "coordinate_frame_assumption": str(metadata["coordinate_frame_assumption"]),
        "coordinate_source_date": metadata.get("coordinate_source_date"),
        "coordinate_note": str(metadata["coordinate_note"]),
    }


def same_waypoint(first: dict | None, second: dict | None) -> bool:
    if first is None or second is None:
        return first is second
    numeric = ("latitude_deg", "longitude_deg", "arrival_radius_nm")
    text = tuple(key for key in first if key not in numeric)
    return set(first) == set(second) and all(first[key] == second[key] for key in text) and all(
        math.isclose(float(first[key]), float(second[key]), rel_tol=0, abs_tol=1e-10)
        for key in numeric
    )


def logmeanexp(values: np.ndarray) -> float:
    maximum = float(np.max(values))
    return maximum + math.log(float(np.exp(values - maximum).mean()))


def route_identity(value: object, description: str) -> str:
    if value in (None, ""):
        return ""
    identity = str(value)
    if len(identity) != 64 or any(character not in "0123456789abcdef" for character in identity):
        raise ValueError(f"invalid {description}: {identity!r}")
    return identity


def load_run(run: Path) -> tuple[dict, list[dict], list[Path], dict]:
    suite_path = require_file(run / "suite-summary.json", "suite summary")
    manifest_path = require_file(run / "run-manifest.json", "run manifest")
    suite = json.loads(suite_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if suite.get("schema_version") != 2 or manifest.get("schema_version") != 2:
        raise ValueError("reporter requires independent schema-v2 source artifacts")
    for artifact, name in ((suite, "suite summary"), (manifest, "run manifest")):
        if artifact.get("config_schema_version") != 2:
            raise ValueError(f"{name} does not identify config schema v2")
        if artifact.get("handoff_schema_version") != 2:
            raise ValueError(f"{name} does not identify handoff schema v2")
    if suite.get("status") not in {"complete_converged", "complete_nonconverged"}:
        raise ValueError(f"source run is incomplete or unassessed: {suite.get('status')!r}")
    if manifest.get("command") != "estimate":
        raise ValueError("source manifest is not an estimate run")
    if manifest.get("outputs", {}).get("suite-summary.json") != digest(suite_path):
        raise ValueError("suite-summary hash mismatch")
    config_path = require_file(
        resolve_config_path(str(manifest["config_path"])), "hashed suite configuration"
    )
    if digest(config_path) != manifest.get("config_sha256"):
        raise ValueError("suite configuration hash mismatch")
    configuration = tomllib.loads(config_path.read_text(encoding="utf-8"))
    if configuration.get("schema_version") != 2:
        raise ValueError("hashed source configuration is not schema v2")
    if tuple(configuration.get("seeds", [])) != SEEDS:
        raise ValueError("hashed source configuration has the wrong numerical seeds")
    if not math.isclose(
        finite_number(
            configuration.get("environment", {}).get("integration_step_s"),
            "source integration step",
        ),
        SELECTED_INTEGRATION_STEP_S,
        rel_tol=0,
        abs_tol=1e-12,
    ):
        raise ValueError("hashed source configuration does not select the audited 30 s step")
    convergence = configuration.get("convergence", {})
    for field, expected_value in (
        ("maximum_log_evidence_range", R600_MAX_LOG_PREDICTIVE_RANGE_NATS),
        (
            "maximum_seed_mean_separation_nm",
            R600_MAX_CONDITIONED_CENTROID_SEPARATION_NM,
        ),
    ):
        if not math.isclose(
            finite_number(convergence.get(field), f"source convergence {field}"),
            expected_value,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError(
                f"hashed source configuration does not bind the frozen R600 descriptive limit {field}"
            )

    expected = {family[0]: family for family in FAMILIES}
    configured_by_name = {
        item["name"]: item for item in configuration.get("families", [])
    }
    if set(configured_by_name) != set(expected):
        raise ValueError("hashed source configuration has the wrong structural-family set")
    by_name = {item["name"]: item for item in suite.get("families", [])}
    if set(by_name) != set(expected):
        raise ValueError(f"wrong source family set: {sorted(by_name)}")
    structural_by_name = {
        item["name"]: item for item in manifest.get("structural_families", [])
    }
    if set(structural_by_name) != set(expected):
        raise ValueError("run manifest does not enumerate the exact structural-family set")

    inputs = [suite_path, manifest_path, config_path]
    families: list[dict] = []
    numeric_columns = ["weight", "last_contact_latitude_deg", "last_contact_longitude_deg"]
    identity_columns = [
        "artifact_schema_version",
        "config_schema_version",
        "handoff_schema_version",
        "model_family",
        "run_identity_sha256",
        "lateral_mode",
        "fixed_waypoint_identity_sha256",
        "fixed_waypoint_latitude_deg",
        "fixed_waypoint_longitude_deg",
        "fixed_waypoint_arrival_radius_nm",
    ]
    columns = identity_columns + numeric_columns
    for key, label, color, marker, mode in FAMILIES:
        aggregate = by_name[key]
        structural = structural_by_name[key]
        configured = configured_by_name[key]
        if configured.get("lateral_mode") != mode:
            raise ValueError(f"configured lateral mode mismatch for {key}")
        if aggregate.get("lateral_mode") != mode:
            raise ValueError(f"wrong lateral mode for {key}")
        if structural.get("lateral_mode") != mode:
            raise ValueError(f"manifest lateral-mode mismatch for {key}")
        if aggregate.get("use_bfo") is not True:
            raise ValueError(f"BFO must be enabled for {key}")
        if not math.isclose(float(aggregate.get("bfo_sd_override_hz")), 4.0):
            raise ValueError(f"wrong BFO uncertainty for {key}")
        if aggregate.get("antenna_gain_applied") is not False:
            raise ValueError(f"antenna gain must be disabled for {key}")
        if aggregate.get("environment_applied") is not True:
            raise ValueError(f"navigation environment must be enabled for {key}")
        if aggregate.get("weather_applied") is not True:
            raise ValueError(f"ERA5 weather must be active for {key}")
        if aggregate.get("magnetic_declination_applied") is not False:
            raise ValueError(f"IGRF declination must be inactive for true-reference family {key}")
        if structural.get("era5_temperature_wind_active") is not True:
            raise ValueError(f"manifest does not declare ERA5 active for {key}")
        if structural.get("igrf_declination_active") is not False:
            raise ValueError(f"manifest does not declare IGRF inactive for {key}")
        if aggregate.get("pooled_particles") != PARTICLES_PER_SEED * len(SEEDS):
            raise ValueError(f"wrong pooled particle count for {key}")
        waypoint = fixed_waypoint(aggregate.get("fixed_waypoint"))
        if not same_waypoint(configured_waypoint(configured), waypoint):
            raise ValueError(f"configured fixed-waypoint metadata mismatch for {key}")
        if (mode == "lateral_navigation") != (waypoint is not None):
            raise ValueError(f"fixed-waypoint metadata mismatch for {key}")
        if not same_waypoint(fixed_waypoint(structural.get("fixed_waypoint")), waypoint):
            raise ValueError(f"manifest fixed-waypoint metadata mismatch for {key}")
        expected_route_identity = route_identity(
            structural.get("fixed_waypoint_identity_sha256"),
            f"manifest fixed-waypoint identity for {key}",
        )
        if (waypoint is not None) != bool(expected_route_identity):
            raise ValueError(f"manifest route-identity presence mismatch for {key}")

        seed_results = {int(item["seed"]): item for item in aggregate.get("seeds", [])}
        if set(seed_results) != set(SEEDS):
            raise ValueError(f"wrong seed set for {key}")
        pieces: list[pd.DataFrame] = []
        seeds: list[dict] = []
        for seed in SEEDS:
            seed_result = seed_results[seed]
            folder = f"{key}/{seed_result['output']}"
            summary_relative = f"{folder}/summary.json"
            posterior_relative = f"{folder}/posterior.csv"
            checkpoints_relative = f"{folder}/checkpoints.json"
            handoff_relative = f"{key}/{seed_result['posterior_handoff']}"
            summary_path = manifest_artifact(run, manifest, summary_relative)
            posterior_path = manifest_artifact(run, manifest, posterior_relative)
            checkpoints_path = manifest_artifact(run, manifest, checkpoints_relative)
            handoff_path = manifest_artifact(run, manifest, handoff_relative)
            inputs.extend([summary_path, posterior_path, checkpoints_path, handoff_path])

            seed_artifact = json.loads(summary_path.read_text(encoding="utf-8"))
            handoff = json.loads(handoff_path.read_text(encoding="utf-8"))
            if seed_artifact.get("schema_version") != 2:
                raise ValueError(f"seed summary is not schema v2: {summary_path}")
            if seed_artifact.get("config_schema_version") != 2:
                raise ValueError(f"seed summary config schema mismatch: {summary_path}")
            if seed_artifact.get("handoff_schema_version") != 2:
                raise ValueError(f"seed summary handoff schema mismatch: {summary_path}")
            wrapped_run = seed_artifact.get("run", {})
            summary = seed_artifact.get("summary", {})
            if summary.get("seed") != seed or summary.get("particles") != PARTICLES_PER_SEED:
                raise ValueError(f"seed summary identity mismatch: {summary_path}")
            if summary.get("lateral_mode") != mode:
                raise ValueError(f"seed lateral-mode mismatch: {summary_path}")
            if seed_result.get("summary") != summary:
                raise ValueError(f"suite embedded seed summary differs from wrapped artifact: {summary_path}")
            if wrapped_run.get("model_family") != key or wrapped_run.get("seed") != seed:
                raise ValueError(f"wrapped seed run identity mismatch: {summary_path}")
            if wrapped_run.get("lateral_mode") != mode:
                raise ValueError(f"wrapped seed lateral-mode mismatch: {summary_path}")
            if wrapped_run.get("config_sha256") != manifest["config_sha256"]:
                raise ValueError(f"wrapped seed config mismatch: {summary_path}")
            if not same_waypoint(fixed_waypoint(wrapped_run.get("fixed_waypoint")), waypoint):
                raise ValueError(f"wrapped seed waypoint mismatch: {summary_path}")
            if route_identity(
                seed_artifact.get("fixed_waypoint_identity_sha256"),
                f"wrapped route identity for {key}",
            ) != expected_route_identity:
                raise ValueError(f"wrapped seed route identity mismatch: {summary_path}")
            if handoff.get("schema_version") != 2:
                raise ValueError(f"handoff is not schema v2: {handoff_path}")
            handoff_run = handoff.get("run", {})
            if handoff_run != wrapped_run:
                raise ValueError(f"wrapped seed metadata differs from handoff: {handoff_path}")
            if handoff_run.get("model_family") != key:
                raise ValueError(f"handoff family mismatch: {handoff_path}")
            if handoff_run.get("seed") != seed:
                raise ValueError(f"handoff seed mismatch: {handoff_path}")
            if handoff_run.get("lateral_mode") != mode:
                raise ValueError(f"handoff lateral-mode mismatch: {handoff_path}")
            if handoff_run.get("config_sha256") != manifest["config_sha256"]:
                raise ValueError(f"handoff config mismatch: {handoff_path}")
            if not same_waypoint(fixed_waypoint(handoff_run.get("fixed_waypoint")), waypoint):
                raise ValueError(f"handoff waypoint mismatch: {handoff_path}")

            frame = pd.read_csv(
                posterior_path,
                usecols=columns,
                dtype={column: "string" for column in identity_columns},
                keep_default_na=False,
            )
            if len(frame) != PARTICLES_PER_SEED:
                raise ValueError(f"wrong particle count: {posterior_path}")
            for column, expected_value in (
                ("artifact_schema_version", "2"),
                ("config_schema_version", "2"),
                ("handoff_schema_version", "2"),
                ("model_family", key),
                ("run_identity_sha256", wrapped_run["run_identity_sha256"]),
                ("lateral_mode", mode),
                ("fixed_waypoint_identity_sha256", expected_route_identity),
            ):
                observed = set(frame[column].astype(str))
                if observed != {expected_value}:
                    raise ValueError(f"posterior identity column {column} mismatch: {posterior_path}")
            if waypoint:
                expected_route_values = {
                    "fixed_waypoint_latitude_deg": waypoint["latitude_deg"],
                    "fixed_waypoint_longitude_deg": waypoint["longitude_deg"],
                    "fixed_waypoint_arrival_radius_nm": waypoint["arrival_radius_nm"],
                }
                for column, expected_value in expected_route_values.items():
                    observed = pd.to_numeric(frame[column], errors="raise").to_numpy()
                    if not np.allclose(observed, expected_value, rtol=0, atol=1e-10):
                        raise ValueError(f"posterior route column {column} mismatch: {posterior_path}")
            elif any((frame[column] != "").any() for column in (
                "fixed_waypoint_latitude_deg",
                "fixed_waypoint_longitude_deg",
                "fixed_waypoint_arrival_radius_nm",
            )):
                raise ValueError(f"scalar-family posterior unexpectedly carries a route: {posterior_path}")
            values = frame[numeric_columns].to_numpy(dtype=float)
            if not np.isfinite(values).all() or (frame["weight"] < 0).any():
                raise ValueError(f"invalid posterior values: {posterior_path}")
            if not np.isclose(float(frame["weight"].sum()), 1.0, atol=2e-9):
                raise ValueError(f"posterior weights are not normalized: {posterior_path}")
            frame = frame[numeric_columns].copy()
            frame["weight"] /= len(SEEDS)
            pieces.append(frame)
            seed_lat, seed_lon = latlon(summary["last_contact_mean"], "seed last-contact mean")
            seeds.append(
                {
                    "seed": seed,
                    "latitude_deg": seed_lat,
                    "longitude_deg": seed_lon,
                    "log_evidence": finite_number(summary["log_evidence"], "seed log evidence"),
                    "minimum_mutation_acceptance": finite_number(
                        summary["minimum_mutation_acceptance"], "mutation acceptance"
                    ),
                }
            )

        frame = pd.concat(pieces, ignore_index=True)
        mean_lat, mean_lon = latlon(aggregate["pooled_mean"], "pooled mean")
        log_values = np.array([item["log_evidence"] for item in seeds], dtype=float)
        families.append(
            {
                "key": key,
                "label": label,
                "color": color,
                "marker": marker,
                "mode": mode,
                "waypoint": waypoint,
                "route_identity_sha256": expected_route_identity,
                "summary": aggregate,
                "seeds": seeds,
                "frame": frame,
                "mean_latitude_deg": mean_lat,
                "mean_longitude_deg": mean_lon,
                "equal_seed_logmean_evidence": logmeanexp(log_values),
            }
        )
    return suite, families, inputs, {
        "manifest": manifest,
        "configuration": configuration,
        "config_path": config_path,
        "suite_path": suite_path,
        "manifest_path": manifest_path,
    }


def load_step_control(
    folder: Path,
    suite: dict,
    families: list[dict],
    source_context: dict,
) -> tuple[dict, list[Path]]:
    result_path = require_file(
        folder / "fixed_waypoint_integration_step_control.json", "integration-step control"
    )
    csv_path = require_file(
        folder / "fixed_waypoint_integration_step_control.csv", "integration-step control table"
    )
    manifest_path = require_file(
        folder / "fixed_waypoint_integration_step_control_manifest.json",
        "integration-step control manifest",
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if result.get("schema_version") != 1 or manifest.get("schema_version") != 1:
        raise ValueError("reporter requires schema-v1 integration-step control artifacts")
    if manifest.get("result_schema_version") != 1 or result.get("status") != "complete":
        raise ValueError("integration-step control is incomplete or has the wrong result schema")
    if result.get("suite_name") != suite.get("name"):
        raise ValueError("integration-step control suite identity mismatch")
    if result.get("suite_config_schema_version") != 2:
        raise ValueError("integration-step control did not use a schema-v2 suite")
    if result.get("input_set_sha256") != manifest.get("input_set_sha256"):
        raise ValueError("integration-step control input-set identity mismatch")
    if result.get("input_sha256") != manifest.get("input_sha256"):
        raise ValueError("integration-step control input hashes disagree with its manifest")
    for path in (result_path, csv_path):
        if manifest.get("output_sha256", {}).get(path.name) != digest(path):
            raise ValueError(f"integration-step control output hash mismatch: {path}")

    generator_path = require_file(
        resolve_config_path(str(manifest.get("generator"))),
        "integration-step control generator",
    )
    if digest(generator_path) != manifest.get("generator_source_sha256"):
        raise ValueError("integration-step control generator hash mismatch; regenerate the control")
    route_identity(manifest.get("executable_sha256"), "integration-step executable SHA-256")

    configuration = source_context["configuration"]
    config_path = source_context["config_path"]
    source_manifest = source_context["manifest"]
    expected_config_sha256 = source_manifest["config_sha256"]
    if result["input_sha256"].get("suite_config") != expected_config_sha256:
        raise ValueError("integration-step control did not use the selected production config")
    if manifest["input_sha256"].get("suite_config") != digest(config_path):
        raise ValueError("integration-step control suite-config hash mismatch")

    raw_inputs = {
        "observations": configuration["inputs"]["observations"],
        "satellite_ephemeris": configuration["inputs"]["satellite_ephemeris"],
        "era5": configuration["environment"]["era5"],
        "igrf": configuration["environment"]["igrf"],
    }
    loaded_inputs = []
    source_hashes = set(source_manifest.get("input_sha256", {}).values())
    for label, raw in raw_inputs.items():
        path = require_file(resolve_config_input(config_path, str(raw)), f"step-control {label}")
        observed = digest(path)
        if result["input_sha256"].get(label) != observed:
            raise ValueError(f"integration-step control {label} hash mismatch")
        if observed not in source_hashes:
            raise ValueError(f"integration-step control {label} is not a source-run input")
        loaded_inputs.append(path)

    if not math.isclose(
        finite_number(result.get("reference_step_s"), "integration-step reference"),
        SELECTED_INTEGRATION_STEP_S,
        rel_tol=0,
        abs_tol=1e-12,
    ):
        raise ValueError("integration-step control does not select 30 s as its reference")
    for field in ("chosen_production_step_s", "configured_production_step_s"):
        if not math.isclose(
            finite_number(result.get(field), f"integration-step {field}"),
            SELECTED_INTEGRATION_STEP_S,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError(f"integration-step control has the wrong {field}")
    if result.get("configured_step_matches_chosen") is not True:
        raise ValueError("configured production step does not match the chosen step")
    if result.get("decision_rule") != (
        "largest tested step passing every threshold for both routes; 30 s is the reference"
    ):
        raise ValueError("integration-step control decision rule changed")
    expected_thresholds = {
        "maximum_bto_difference_us": 1.0,
        "maximum_bfo_difference_hz": 0.1,
        "maximum_endpoint_separation_nm": 0.5,
        "maximum_posterior_relevant_log_likelihood_difference": 0.05,
        "maximum_partition_endpoint_separation_nm": 1e-6,
        "maximum_partition_track_difference_deg": 1e-9,
    }
    observed_thresholds = result.get("thresholds", {})
    if set(observed_thresholds) != set(expected_thresholds) or any(
        not math.isclose(
            finite_number(observed_thresholds[key], f"integration-step threshold {key}"),
            expected,
            rel_tol=0,
            abs_tol=max(1e-15, abs(expected) * 1e-12),
        )
        for key, expected in expected_thresholds.items()
    ):
        raise ValueError("integration-step control thresholds changed")
    if tuple(result.get("tested_steps_s", [])) != (600.0, 300.0, 60.0, 30.0):
        raise ValueError("integration-step control tested-step set changed")
    if tuple(result.get("fitted_epoch_ids", [])) != (
        "m1825",
        "m1828a",
        "m1828b",
        "m1839",
        "m1941",
        "m2041",
        "m2141",
        "m2241",
        "m2315",
        "m0011",
    ):
        raise ValueError("integration-step control fitted-epoch identity changed")
    if tuple(float(value) for value in result.get("fitted_epoch_times_s", [])) != (
        1425.0,
        1576.0,
        1585.0,
        2286.0,
        5953.0,
        9555.0,
        13177.0,
        16772.0,
        18793.0,
        22150.0,
    ):
        raise ValueError("integration-step control fitted-epoch times changed")

    waypoint_by_family = {
        family["key"]: family["waypoint"] for family in families if family["waypoint"] is not None
    }
    comparisons = result.get("comparisons", [])
    expected_rows = {
        (family, step) for family in waypoint_by_family for step in (600.0, 300.0, 60.0, 30.0)
    }
    observed_rows = {
        (str(item.get("route_family")), finite_number(item.get("step_s"), "control step"))
        for item in comparisons
    }
    if observed_rows != expected_rows or len(comparisons) != len(expected_rows):
        raise ValueError("integration-step control route/step matrix changed")
    for item in comparisons:
        family = str(item["route_family"])
        step = finite_number(item["step_s"], "control step")
        if not same_waypoint(fixed_waypoint(item.get("route")), waypoint_by_family[family]):
            raise ValueError(f"integration-step control route identity mismatch for {family}")
        if not math.isclose(
            finite_number(item.get("reference_step_s"), "comparison reference step"),
            SELECTED_INTEGRATION_STEP_S,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError("integration-step comparison has the wrong reference")
        if step == SELECTED_INTEGRATION_STEP_S and item.get("passes") is not True:
            raise ValueError(f"selected 30 s control row does not pass for {family}")
    for step in (600.0, 300.0, 60.0):
        if all(
            item.get("passes") is True
            for item in comparisons
            if finite_number(item["step_s"], "control step") == step
        ):
            raise ValueError(f"coarser {step:g} s step unexpectedly passes both routes")

    return result, [result_path, csv_path, manifest_path, generator_path, *loaded_inputs]


def load_r600(
    run: Path,
    suite: dict,
    families: list[dict],
    source_context: dict,
) -> tuple[dict, dict, list[Path]]:
    folder = run / "r600-predictive-control"
    result_path = require_file(folder / "r600_predictive_compatibility.json", "R600 result")
    csv_path = require_file(folder / "r600_predictive_compatibility.csv", "R600 table")
    manifest_path = require_file(
        folder / "r600_predictive_compatibility_manifest.json", "R600 manifest"
    )
    result = json.loads(result_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if result.get("schema_version") != 2 or manifest.get("schema_version") != 2:
        raise ValueError("reporter requires independent schema-v2 R600 artifacts")
    for artifact, name in ((result, "R600 result"), (manifest, "R600 manifest")):
        source_fields = {
            "source_suite_artifact_schema_version": 2,
            "source_config_schema_version": 2,
            "source_handoff_schema_version": 2,
        }
        for field, expected in source_fields.items():
            if artifact.get(field) != expected:
                raise ValueError(f"{name} has wrong {field}")
    if manifest.get("result_schema_version") != 2:
        raise ValueError("R600 manifest does not identify result schema v2")
    if result.get("status") not in (
        "complete_control",
        "complete_control_provisional_numerical_stability",
    ):
        raise ValueError("R600 control is incomplete")
    if result.get("source_run_status") != suite.get("status"):
        raise ValueError("R600 source-run status mismatch")
    if result.get("source_epoch_id") != "m0011":
        raise ValueError("R600 control starts at the wrong epoch")
    if result.get("structural_pooling") != "none":
        raise ValueError("R600 control pooled structural families")
    if result.get("seed_pooling") != (
        "equal weight within each family only; R600-conditioned particle weights are "
        "normalized separately within each seed before equal-seed averaging"
    ):
        raise ValueError("R600 control seed-pooling contract changed")
    for path in (result_path, csv_path):
        if manifest.get("output_sha256", {}).get(path.name) != digest(path):
            raise ValueError(f"R600 output hash mismatch: {path}")
    if result.get("input_set_sha256") != manifest.get("input_set_sha256"):
        raise ValueError("R600 input-set identity mismatch")
    if result.get("input_sha256") != manifest.get("input_sha256"):
        raise ValueError("R600 result and manifest input hashes disagree")
    generator_path = require_file(
        resolve_config_path(str(manifest.get("generator"))), "R600 generator"
    )
    if digest(generator_path) != manifest.get("generator_source_sha256"):
        raise ValueError("R600 generator hash mismatch; regenerate the control")
    route_identity(manifest.get("executable_sha256"), "R600 executable SHA-256")
    if manifest.get("scientific_scope") != result.get("limitations"):
        raise ValueError("R600 manifest scientific scope differs from result limitations")
    r600_inputs = result.get("input_sha256", {})
    source_manifest = source_context["manifest"]
    if r600_inputs.get("suite_config") != source_manifest.get("config_sha256"):
        raise ValueError("R600 control did not use the selected source suite configuration")
    if r600_inputs.get("source_suite_summary") != digest(source_context["suite_path"]):
        raise ValueError("R600 control did not bind the selected source suite summary")
    if r600_inputs.get("source_suite_manifest") != digest(source_context["manifest_path"]):
        raise ValueError("R600 control did not bind the selected source run manifest")
    continuation_path = require_file(DEFAULT_R600_CONFIG, "neutral R600 continuation config")
    if r600_inputs.get("continuation_config") != digest(continuation_path):
        raise ValueError("R600 control did not bind the canonical neutral continuation config")
    continuation = tomllib.loads(continuation_path.read_text(encoding="utf-8"))
    if continuation.get("schema_version") != 2 or continuation.get("selection", {}).get("kind") != "bto":
        raise ValueError("neutral R600 continuation config contract changed")
    control_input_paths = [continuation_path]
    for label, field in (
        ("control_observations", "observations"),
        ("control_satellite_ephemeris", "satellite_ephemeris"),
    ):
        path = require_file(
            resolve_config_input(continuation_path, str(continuation["inputs"][field])),
            f"R600 {field}",
        )
        if r600_inputs.get(label) != digest(path):
            raise ValueError(f"R600 control input hash mismatch: {label}")
        control_input_paths.append(path)

    propagation = result.get("propagation", {})
    for field in ("source_fit_integration_step_s", "r600_propagation_integration_step_s"):
        if not math.isclose(
            finite_number(propagation.get(field), f"R600 {field}"),
            SELECTED_INTEGRATION_STEP_S,
            rel_tol=0,
            abs_tol=1e-12,
        ):
            raise ValueError("R600 control did not use the selected 30 s full-path replay")
    if not math.isclose(
        finite_number(propagation.get("source_time_s"), "R600 source time"),
        M0011_TIME_S,
        rel_tol=0,
        abs_tol=1e-9,
    ) or not math.isclose(
        finite_number(propagation.get("target_time_s"), "R600 target time"),
        R600_TIME_S,
        rel_tol=0,
        abs_tol=1e-9,
    ):
        raise ValueError("R600 propagation is bound to the wrong source or target time")
    selection = result.get("selection", {})
    if (
        selection.get("epoch_id") != "m0019a"
        or selection.get("channel") != "R600"
        or selection.get("time_utc") != "2014-03-08T00:19:29.000Z"
        or not math.isclose(
            finite_number(selection.get("observed_bto_us"), "R600 observed BTO"),
            18400.0,
            rel_tol=0,
            abs_tol=1e-12,
        )
        or not math.isclose(
            finite_number(selection.get("standard_deviation_us"), "R600 BTO uncertainty"),
            63.0,
            rel_tol=0,
            abs_tol=1e-12,
        )
    ):
        raise ValueError("R600 selection identity is not the corrected m0019a/R600 observation")

    table = pd.read_csv(csv_path, dtype="string", keep_default_na=False)
    if len(table) != len(families) or set(table["family"]) != {item["key"] for item in families}:
        raise ValueError("R600 route-identity table has the wrong family set")
    for column, expected in (
        ("result_schema_version", "2"),
        ("source_suite_artifact_schema_version", "2"),
        ("source_config_schema_version", "2"),
        ("source_handoff_schema_version", "2"),
        ("input_set_sha256", str(result["input_set_sha256"])),
    ):
        if set(table[column]) != {expected}:
            raise ValueError(f"R600 table identity column {column} mismatch")

    by_name = {item["family"]: item for item in result.get("families", [])}
    if set(by_name) != {item["key"] for item in families}:
        raise ValueError("R600 family set mismatch")
    for family in families:
        item = by_name[family["key"]]
        row = table.loc[table["family"] == family["key"]].iloc[0]
        if item.get("lateral_mode") != family["mode"]:
            raise ValueError(f"R600 lateral-mode mismatch for {family['key']}")
        if row["lateral_mode"] != family["mode"]:
            raise ValueError(f"R600 table lateral-mode mismatch for {family['key']}")
        if not same_waypoint(fixed_waypoint(item.get("fixed_waypoint")), family["waypoint"]):
            raise ValueError(f"R600 fixed-waypoint mismatch for {family['key']}")
        if route_identity(
            row["fixed_waypoint_identity_sha256"],
            f"R600 table fixed-waypoint identity for {family['key']}",
        ) != family["route_identity_sha256"]:
            raise ValueError(f"R600 table route-identity mismatch for {family['key']}")
        if family["waypoint"]:
            for column, expected_value in (
                ("fixed_waypoint_latitude_deg", family["waypoint"]["latitude_deg"]),
                ("fixed_waypoint_longitude_deg", family["waypoint"]["longitude_deg"]),
                ("fixed_waypoint_arrival_radius_nm", family["waypoint"]["arrival_radius_nm"]),
            ):
                if not math.isclose(float(row[column]), expected_value, rel_tol=0, abs_tol=1e-10):
                    raise ValueError(f"R600 table route coordinate mismatch: {column}")
        elif any(
            row[column] != ""
            for column in (
                "fixed_waypoint_latitude_deg",
                "fixed_waypoint_longitude_deg",
                "fixed_waypoint_arrival_radius_nm",
            )
        ):
            raise ValueError("R600 CTT row unexpectedly carries a fixed route")
        if item.get("particles") != PARTICLES_PER_SEED * len(SEEDS):
            raise ValueError(f"R600 particle-count mismatch for {family['key']}")
        source_lat, source_lon = position(item["source_mean_at_0011"], "R600 source mean")
        if not np.allclose(
            [source_lat, source_lon],
            [family["mean_latitude_deg"], family["mean_longitude_deg"]],
            atol=1e-9,
        ):
            raise ValueError(f"R600 source mean mismatch for {family['key']}")
        initial_mean, initial_interval = angular_summary(
            item.get("initial_post_turn_track_true"),
            f"{family['key']} initial post-turn true track",
        )
        m1941 = checkpoint_summary(
            item.get("m1941_through_m0011_smoothing_posterior"),
            "m1941",
            M1941_TIME_S,
            f"{family['key']} through-m0011 smoothing checkpoint at m1941",
        )
        m0011 = checkpoint_summary(
            item.get("m0011_source_posterior"),
            "m0011",
            M0011_TIME_S,
            f"{family['key']} m0011 source checkpoint",
        )
        m0011_lat, m0011_lon = position(m0011["mean"], "m0011 checkpoint mean")
        if not np.allclose([m0011_lat, m0011_lon], [source_lat, source_lon], atol=1e-9):
            raise ValueError(f"m0011 checkpoint and source mean disagree for {family['key']}")
        prior_track_mean, prior_track_interval = angular_summary(
            item["propagated_prior_at_0019"].get("track_true"),
            f"{family['key']} R600 predictive true track",
        )
        conditioned_track_mean, conditioned_track_interval = angular_summary(
            item["r600_conditioned_at_0019"].get("track_true"),
            f"{family['key']} R600-conditioned true track",
        )
        if not math.isclose(
            conditioned_track_mean,
            finite_number(
                item.get("mean_track_true_deg_after_conditioning"),
                "legacy conditioned mean true track",
            ),
            rel_tol=0,
            abs_tol=1e-10,
        ):
            raise ValueError(f"conditioned true-track summaries disagree for {family['key']}")
        item["_report_course"] = {
            "initial": (initial_mean, initial_interval),
            "m1941": angular_summary(
                m1941["track_true"], f"{family['key']} m1941 true track"
            ),
            "m0011": angular_summary(
                m0011["track_true"], f"{family['key']} m0011 true track"
            ),
            "r600_predictive": (prior_track_mean, prior_track_interval),
            "r600_conditioned": (conditioned_track_mean, conditioned_track_interval),
        }

        csv_course_fields = {
            "initial_post_turn_track_true_mean_deg": initial_mean,
            "initial_post_turn_track_true_p05_deg": initial_interval[0],
            "initial_post_turn_track_true_p95_deg": initial_interval[1],
            "m1941_through_m0011_smoothing_track_true_mean_deg": item["_report_course"]["m1941"][0],
            "m1941_through_m0011_smoothing_track_true_p05_deg": item["_report_course"]["m1941"][1][0],
            "m1941_through_m0011_smoothing_track_true_p95_deg": item["_report_course"]["m1941"][1][1],
            "m0011_source_track_true_mean_deg": item["_report_course"]["m0011"][0],
            "m0011_source_track_true_p05_deg": item["_report_course"]["m0011"][1][0],
            "m0011_source_track_true_p95_deg": item["_report_course"]["m0011"][1][1],
            "prior_track_true_mean_deg": prior_track_mean,
            "prior_track_true_p05_deg": prior_track_interval[0],
            "prior_track_true_p95_deg": prior_track_interval[1],
            "conditioned_track_true_mean_deg": conditioned_track_mean,
            "conditioned_track_true_p05_deg": conditioned_track_interval[0],
            "conditioned_track_true_p95_deg": conditioned_track_interval[1],
        }
        for column, expected_value in csv_course_fields.items():
            if column not in row or not math.isclose(
                finite_number(row[column], f"R600 CSV {column}"),
                expected_value,
                rel_tol=0,
                abs_tol=5e-10,
            ):
                raise ValueError(f"R600 JSON/CSV course mismatch: {column}")
        log_predictive = finite_number(
            item["equal_seed_log_predictive_density"], "R600 log predictive density"
        )
        item["_report_log_predictive_density"] = log_predictive
        raw_seed_logs = item.get("seed_log_predictive_density")
        raw_seed_ess = item.get("seed_posterior_effective_sample_size")
        if not isinstance(raw_seed_logs, dict) or not isinstance(raw_seed_ess, dict):
            raise ValueError(f"missing R600 per-seed diagnostics for {family['key']}")
        seed_log_values = {
            str(seed): finite_number(value, f"{family['key']} seed log predictive density")
            for seed, value in raw_seed_logs.items()
        }
        seed_ess_values = {
            str(seed): finite_number(value, f"{family['key']} conditioned seed ESS")
            for seed, value in raw_seed_ess.items()
        }
        expected_seeds = {str(seed) for seed in SEEDS}
        if set(seed_log_values) != expected_seeds or set(seed_ess_values) != expected_seeds:
            raise ValueError(f"R600 seed diagnostics have the wrong seed set for {family['key']}")
        predictive_range = finite_number(
            item.get("seed_log_predictive_density_range"),
            f"{family['key']} seed log predictive density range",
        )
        conditioned_separation = finite_number(
            item.get("maximum_seed_conditioned_mean_separation_nm"),
            f"{family['key']} conditioned centroid separation",
        )
        if predictive_range < 0 or conditioned_separation < 0:
            raise ValueError(f"negative R600 cross-seed diagnostic for {family['key']}")
        derived_range = max(seed_log_values.values()) - min(seed_log_values.values())
        if not math.isclose(predictive_range, derived_range, rel_tol=0, abs_tol=2e-12):
            raise ValueError(f"R600 predictive range disagrees with seed values for {family['key']}")
        stability = item.get("predictive_stability")
        if not isinstance(stability, dict):
            raise ValueError(f"missing typed R600 predictive stability for {family['key']}")
        minimum_ess = min(seed_ess_values.values())
        all_ess_positive = all(value > 0 for value in seed_ess_values.values())
        passes = (
            predictive_range <= R600_MAX_LOG_PREDICTIVE_RANGE_NATS
            and conditioned_separation <= R600_MAX_CONDITIONED_CENTROID_SEPARATION_NM
        )
        expected_stability_status = (
            "within_source_config_derived_descriptive_limits"
            if passes
            else "provisional_outside_source_config_derived_descriptive_limits"
        )
        expected_limit_origin = (
            "source convergence limits reused and frozen before R600 evaluation; not "
            "prospectively calibrated R600 thresholds"
        )
        typed_numbers = {
            "minimum_seed_conditioned_effective_sample_size": minimum_ess,
            "seed_log_predictive_density_range_nats": predictive_range,
            "maximum_seed_conditioned_mean_separation_nm": conditioned_separation,
            "maximum_allowed_log_predictive_density_range_nats": (
                R600_MAX_LOG_PREDICTIVE_RANGE_NATS
            ),
            "maximum_allowed_conditioned_mean_separation_nm": (
                R600_MAX_CONDITIONED_CENTROID_SEPARATION_NM
            ),
        }
        for field, expected_value in typed_numbers.items():
            if not math.isclose(
                finite_number(stability.get(field), f"{family['key']} stability {field}"),
                expected_value,
                rel_tol=0,
                abs_tol=2e-12,
            ):
                raise ValueError(f"typed R600 stability field disagrees: {family['key']} {field}")
        if (
            stability.get("all_conditioned_effective_sample_sizes_finite_positive")
            is not all_ess_positive
        ):
            raise ValueError(f"typed R600 ESS status disagrees for {family['key']}")
        if stability.get("descriptive_limit_origin") != expected_limit_origin:
            raise ValueError(f"typed R600 stability-limit origin disagrees for {family['key']}")
        if stability.get("passes_source_config_derived_descriptive_limits") is not passes:
            raise ValueError(f"typed R600 stability decision disagrees for {family['key']}")
        if stability.get("status") != expected_stability_status:
            raise ValueError(f"typed R600 stability label disagrees for {family['key']}")
        csv_stability = {
            "minimum_seed_conditioned_effective_sample_size": minimum_ess,
            "predictive_stability_maximum_allowed_log_predictive_density_range_nats": (
                R600_MAX_LOG_PREDICTIVE_RANGE_NATS
            ),
            "predictive_stability_maximum_allowed_conditioned_mean_separation_nm": (
                R600_MAX_CONDITIONED_CENTROID_SEPARATION_NM
            ),
        }
        for column, expected_value in csv_stability.items():
            if not math.isclose(
                finite_number(row[column], f"R600 CSV {column}"),
                expected_value,
                rel_tol=0,
                abs_tol=max(1e-12, abs(expected_value) * 5e-10),
            ):
                raise ValueError(f"R600 JSON/CSV predictive-stability mismatch: {column}")
        if row["predictive_stability_all_conditioned_ess_finite_positive"] != str(
            all_ess_positive
        ).lower():
            raise ValueError(f"R600 CSV conditioned-ESS flag disagrees for {family['key']}")
        if row["predictive_stability_passes_source_config_derived_limits"] != str(passes).lower():
            raise ValueError(f"R600 CSV predictive-stability pass flag disagrees for {family['key']}")
        if row["predictive_stability_status"] != expected_stability_status:
            raise ValueError(f"R600 CSV predictive-stability status disagrees for {family['key']}")
        item["_report_predictive_stability_pass"] = passes
        item["_report_predictive_stability_status"] = expected_stability_status
        for field in (
            "maximum_source_replay_separation_nm",
            "maximum_source_replay_track_difference_deg",
            "maximum_source_replay_heading_difference_deg",
            "maximum_source_replay_ground_speed_difference_kt",
        ):
            if item.get(field) is None or finite_number(item[field], field) < 0:
                raise ValueError(f"missing or invalid schema-v2 replay diagnostic {field}")
    ctt = by_name[FAMILIES[0][0]]
    ctt_log_predictive = ctt["_report_log_predictive_density"]
    for family in families:
        item = by_name[family["key"]]
        derived_log_ratio = item["_report_log_predictive_density"] - ctt_log_predictive
        stored_log_ratio = finite_number(
            item.get("log_predictive_likelihood_ratio_to_constant_true_track"),
            f"{family['key']} exact R600 log predictive ratio",
        )
        if not math.isclose(stored_log_ratio, derived_log_ratio, rel_tol=0, abs_tol=2e-12):
            raise ValueError(
                f"R600 exact log predictive ratio disagrees with densities for {family['key']}"
            )
        item["_report_log_predictive_ratio_to_ctt"] = stored_log_ratio
        row = table.loc[table["family"] == family["key"]].iloc[0]
        if not math.isclose(
            finite_number(
                row["log_predictive_likelihood_ratio_to_constant_true_track"],
                "R600 CSV exact log predictive ratio",
            ),
            stored_log_ratio,
            rel_tol=0,
            abs_tol=5e-10,
        ):
            raise ValueError(f"R600 JSON/CSV log-ratio mismatch for {family['key']}")

        stored_linear_ratio = item.get("predictive_likelihood_ratio_to_constant_true_track")
        csv_linear_ratio = row["predictive_likelihood_ratio_to_constant_true_track"]
        if stored_linear_ratio is None:
            if csv_linear_ratio != "":
                raise ValueError(f"nullable R600 linear ratio is not blank in CSV for {family['key']}")
        else:
            stored_linear_ratio = finite_number(
                stored_linear_ratio, f"{family['key']} optional R600 linear ratio"
            )
            if stored_linear_ratio <= 0:
                raise ValueError(f"invalid optional R600 linear ratio for {family['key']}")
            if not math.isclose(
                finite_number(csv_linear_ratio, "R600 CSV optional linear ratio"),
                stored_linear_ratio,
                rel_tol=0,
                abs_tol=max(1e-300, abs(stored_linear_ratio) * 5e-10),
            ):
                raise ValueError(f"R600 JSON/CSV linear-ratio mismatch for {family['key']}")
            if -700.0 < stored_log_ratio < 700.0 and not math.isclose(
                stored_linear_ratio,
                math.exp(stored_log_ratio),
                rel_tol=2e-10,
                abs_tol=1e-300,
            ):
                raise ValueError(f"R600 optional linear ratio disagrees for {family['key']}")
    if not math.isclose(
        ctt["_report_log_predictive_ratio_to_ctt"], 0.0, rel_tol=0, abs_tol=1e-12
    ):
        raise ValueError("CTT R600 log predictive ratio is not zero")
    any_provisional = any(
        not item["_report_predictive_stability_pass"] for item in by_name.values()
    )
    expected_status = (
        "complete_control_provisional_numerical_stability"
        if any_provisional
        else "complete_control"
    )
    if result.get("status") != expected_status:
        raise ValueError("R600 top-level status disagrees with typed family stability")
    return result, by_name, [
        result_path,
        csv_path,
        manifest_path,
        generator_path,
        *control_input_paths,
    ]


def weighted_quantile(values: np.ndarray, weights: np.ndarray, probabilities: list[float]) -> np.ndarray:
    order = np.argsort(values, kind="mergesort")
    ordered_values = np.asarray(values, dtype=float)[order]
    ordered_weights = np.asarray(weights, dtype=float)[order]
    cumulative = np.cumsum(ordered_weights)
    cumulative /= cumulative[-1]
    return np.interp(probabilities, cumulative, ordered_values)


def display_bounds(families: list[dict]) -> tuple[tuple[float, float], tuple[float, float]]:
    latitude_limits = []
    longitude_limits = []
    for family in families:
        frame = family["frame"]
        weights = frame["weight"].to_numpy()
        latitude_limits.append(
            weighted_quantile(frame["last_contact_latitude_deg"].to_numpy(), weights, [0.001, 0.999])
        )
        longitude_limits.append(
            weighted_quantile(frame["last_contact_longitude_deg"].to_numpy(), weights, [0.001, 0.999])
        )
    latitude_min = min(value[0] for value in latitude_limits)
    latitude_max = max(value[1] for value in latitude_limits)
    longitude_min = min(value[0] for value in longitude_limits)
    longitude_max = max(value[1] for value in longitude_limits)
    latitude_padding = max(0.35, 0.08 * (latitude_max - latitude_min))
    longitude_padding = max(0.45, 0.08 * (longitude_max - longitude_min))
    return (
        (latitude_min - latitude_padding, latitude_max + latitude_padding),
        (longitude_min - longitude_padding, longitude_max + longitude_padding),
    )


def hpd_threshold(mass: np.ndarray, probability: float) -> float:
    ranked = np.sort(mass.ravel())[::-1]
    index = min(int(np.searchsorted(np.cumsum(ranked), probability)), len(ranked) - 1)
    return float(ranked[index])


def density_surface(
    frame: pd.DataFrame,
    latitude_bounds: tuple[float, float],
    longitude_bounds: tuple[float, float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray, float, float]:
    latitude_edges = np.linspace(*latitude_bounds, 241)
    longitude_edges = np.linspace(*longitude_bounds, 321)
    mass, _, _ = np.histogram2d(
        frame["last_contact_latitude_deg"],
        frame["last_contact_longitude_deg"],
        bins=(latitude_edges, longitude_edges),
        weights=frame["weight"],
    )
    mid_latitude = 0.5 * sum(latitude_bounds)
    sigma_latitude = BANDWIDTH_NM / ((latitude_edges[1] - latitude_edges[0]) * 60.0405)
    sigma_longitude = BANDWIDTH_NM / (
        (longitude_edges[1] - longitude_edges[0])
        * 60.0405
        * max(0.15, math.cos(math.radians(mid_latitude)))
    )
    mass = gaussian_filter(mass, (sigma_latitude, sigma_longitude), mode="constant")
    if not np.isfinite(mass).all() or mass.sum() <= 0:
        raise ValueError("invalid display density")
    mass /= mass.sum()
    latitude_centres = 0.5 * (latitude_edges[:-1] + latitude_edges[1:])
    longitude_centres = 0.5 * (longitude_edges[:-1] + longitude_edges[1:])
    return (
        longitude_centres,
        latitude_centres,
        mass,
        hpd_threshold(mass, 0.5),
        hpd_threshold(mass, 0.9),
    )


def longitude_label(value: float) -> str:
    return f"{abs(value):.1f}°{'E' if value >= 0 else 'W'}"


def latitude_label(value: float) -> str:
    return f"{abs(value):.1f}°{'N' if value >= 0 else 'S'}"


def status_banner(suite: dict, r600_result: dict) -> tuple[str, str]:
    source_converged = suite["status"] == "complete_converged"
    r600_stable = r600_result["status"] == "complete_control"
    if source_converged and r600_stable:
        return "DECLARED SOURCE CONVERGENCE + DESCRIPTIVE R600 STABILITY PASSED", "#2A6F62"
    if not source_converged and not r600_stable:
        return "PROVISIONAL / SOURCE NONCONVERGENCE + R600 OUTSIDE DESCRIPTIVE LIMITS", "#A23B3B"
    if not source_converged:
        return "PROVISIONAL / SOURCE NONCONVERGENCE — integrated-fit and location diagnostics", "#A23B3B"
    return "PROVISIONAL / R600 OUTSIDE DESCRIPTIVE LIMITS — forward comparison is diagnostic", "#A23B3B"


def publication_plate(
    suite: dict,
    families: list[dict],
    r600_result: dict,
    r600: dict,
    output: Path,
) -> list[Path]:
    latitude_bounds, longitude_bounds = display_bounds(families)
    figure = plt.figure(figsize=(13.8, 8.5), facecolor="white")
    grid = figure.add_gridspec(
        2,
        2,
        width_ratios=(1.62, 1.0),
        height_ratios=(1.0, 1.0),
        left=0.075,
        right=0.985,
        bottom=0.145,
        top=0.865,
        wspace=0.22,
        hspace=0.38,
    )
    map_axis = figure.add_subplot(grid[:, 0])
    fit_axis = figure.add_subplot(grid[0, 1])
    lower_grid = grid[1, 1].subgridspec(1, 2, width_ratios=(1.0, 1.08), wspace=0.30)
    mass_axis = figure.add_subplot(lower_grid[0, 0])
    ratio_axis = figure.add_subplot(lower_grid[0, 1])

    mid_latitude = 0.5 * sum(latitude_bounds)
    map_axis.set_xlim(*longitude_bounds)
    map_axis.set_ylim(*latitude_bounds)
    map_axis.set_aspect(1 / max(0.15, math.cos(math.radians(mid_latitude))))
    map_axis.set_xlabel("Longitude")
    map_axis.set_ylabel("Latitude")
    map_axis.xaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda x, _: longitude_label(x)))
    map_axis.yaxis.set_major_formatter(mpl.ticker.FuncFormatter(lambda y, _: latitude_label(y)))
    map_axis.set_title("A. 00:11 conditional location densities", loc="left", weight="bold")

    label_offsets = ((8, 9), (8, -24), (-10, -24))
    for family, offset in zip(families, label_offsets):
        x, y, mass, threshold_50, threshold_90 = density_surface(
            family["frame"], latitude_bounds, longitude_bounds
        )
        color = family["color"]
        map_axis.contourf(
            x,
            y,
            mass,
            levels=[threshold_90, threshold_50, float(mass.max()) * (1 + 1e-9)],
            colors=[color, color],
            alpha=0.12,
            zorder=2,
        )
        map_axis.contour(x, y, mass, levels=[threshold_90], colors=[color], linewidths=2.0)
        map_axis.contour(
            x,
            y,
            mass,
            levels=[threshold_50],
            colors=[color],
            linewidths=1.25,
            linestyles="--",
        )
        for seed in family["seeds"]:
            map_axis.scatter(
                seed["longitude_deg"],
                seed["latitude_deg"],
                marker=family["marker"],
                s=29,
                facecolor="white",
                edgecolor=color,
                linewidth=1.0,
                zorder=5,
            )
        map_axis.scatter(
            family["mean_longitude_deg"],
            family["mean_latitude_deg"],
            marker=family["marker"],
            s=78,
            facecolor=color,
            edgecolor="white",
            linewidth=1.1,
            zorder=6,
        )
        map_axis.annotate(
            family["label"],
            (family["mean_longitude_deg"], family["mean_latitude_deg"]),
            xytext=offset,
            textcoords="offset points",
            fontsize=7.8,
            color=color,
            weight="bold",
            ha="right" if offset[0] < 0 else "left",
            bbox={"boxstyle": "round,pad=.18", "facecolor": "white", "alpha": 0.78, "edgecolor": "none"},
        )
    map_axis.legend(
        handles=[
            Line2D([0], [0], color="#34495e", lw=2.0, label="90% HPD"),
            Line2D([0], [0], color="#34495e", lw=1.25, ls="--", label="50% HPD"),
            Line2D(
                [0],
                [0],
                marker="o",
                markerfacecolor="white",
                markeredgecolor="#34495e",
                color="none",
                label="seed mean",
            ),
        ],
        loc="lower left",
        framealpha=0.95,
        fontsize=8,
    )
    map_axis.text(
        0.99,
        0.015,
        f"common frame; display kernel σ={BANDWIDTH_NM:.1f} NM\nno density pooling between families",
        transform=map_axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=7.4,
        color="#52606d",
    )

    reference_logmean = families[0]["equal_seed_logmean_evidence"]
    reference_by_seed = {
        item["seed"]: item["log_evidence"] for item in families[0]["seeds"]
    }
    fit_y = np.arange(len(families))[::-1]
    for y_value, family in zip(fit_y, families):
        seed_deltas = np.array(
            [
                item["log_evidence"] - reference_by_seed[item["seed"]]
                for item in family["seeds"]
            ]
        )
        combined_delta = family["equal_seed_logmean_evidence"] - reference_logmean
        fit_axis.plot(
            [float(seed_deltas.min()), float(seed_deltas.max())],
            [y_value, y_value],
            color=family["color"],
            lw=4.5,
            alpha=0.28,
            solid_capstyle="butt",
        )
        fit_axis.scatter(
            seed_deltas,
            np.full(len(seed_deltas), y_value),
            marker=family["marker"],
            s=27,
            facecolor="white",
            edgecolor=family["color"],
            linewidth=0.9,
            zorder=4,
        )
        fit_axis.scatter(
            combined_delta,
            y_value,
            marker=family["marker"],
            s=63,
            facecolor=family["color"],
            edgecolor="white",
            linewidth=1.0,
            zorder=5,
        )
        separation = finite_number(
            family["summary"]["maximum_seed_mean_separation_nm"], "seed separation"
        )
        convergence = "pass" if family["summary"]["converged"] is True else "FAIL"
        fit_axis.text(
            0.50,
            y_value,
            f"{convergence}; sep {separation:.1f} NM",
            transform=fit_axis.get_yaxis_transform(),
            ha="center",
            va="bottom",
            fontsize=6.8,
            color="#2A6F62" if convergence == "pass" else "#A23B3B",
            weight="bold",
        )
    fit_axis.axvline(0, color="#596673", lw=1.0, ls="--")
    fit_axis.set_yticks(fit_y)
    fit_axis.set_yticklabels([family["label"] for family in families])
    for tick, family in zip(fit_axis.get_yticklabels(), families):
        tick.set_color(family["color"])
        tick.set_fontsize(7.4)
        tick.set_weight("bold")
    fit_axis.set_xlabel("Δ log evidence relative to CTT (nats)", fontsize=8)
    fit_axis.set_title("B. Exploratory integrated fit and stability", loc="left", weight="bold")

    r600_y = np.arange(len(families))[::-1]
    log_ratios = [r600[family["key"]]["_report_log_predictive_ratio_to_ctt"] for family in families]
    ratio_span = max(log_ratios) - min(log_ratios)
    ratio_padding = max(0.35, 0.12 * max(1.0, ratio_span))
    ratio_limits = (
        min(0.0, min(log_ratios)) - ratio_padding,
        max(0.0, max(log_ratios)) + ratio_padding,
    )
    for y_value, family in zip(r600_y, families):
        item = r600[family["key"]]
        prior = item["propagated_prior_at_0019"]
        within_one = max(0.0, finite_number(prior["mass_within_one_bto_sd"], "R600 mass"))
        within_two = max(0.0, finite_number(prior["mass_within_two_bto_sd"], "R600 mass"))
        log_ratio = item["_report_log_predictive_ratio_to_ctt"]
        mass_axis.plot([0, within_two], [y_value, y_value], color=family["color"], lw=10, alpha=0.22)
        mass_axis.plot([0, within_one], [y_value, y_value], color=family["color"], lw=4.5)
        mass_axis.scatter(
            within_one,
            y_value,
            marker=family["marker"],
            s=40,
            facecolor=family["color"],
            edgecolor="white",
            zorder=4,
        )
        ratio_axis.plot(
            [min(0.0, log_ratio), max(0.0, log_ratio)],
            [y_value, y_value],
            color=family["color"],
            lw=3.5,
            alpha=0.28,
            solid_capstyle="butt",
        )
        ratio_axis.scatter(
            log_ratio,
            y_value,
            marker=family["marker"],
            s=55,
            facecolor=family["color"],
            edgecolor="white",
            zorder=4,
        )
        ratio_axis.annotate(
            f"{log_ratio:+.3f}",
            (log_ratio, y_value),
            xytext=(0, 8),
            textcoords="offset points",
            ha="center",
            fontsize=7,
            color=family["color"],
            weight="bold",
        )
    r600_provisional = any(
        not r600[family["key"]]["_report_predictive_stability_pass"]
        for family in families
    )
    labels = [
        family["label"].replace("Direct to ", "")
        + (
            " †"
            if not r600[family["key"]]["_report_predictive_stability_pass"]
            else ""
        )
        for family in families
    ]
    mass_axis.set_xlim(0, 1.02)
    mass_axis.set_ylim(-0.45, len(families) - 0.25)
    mass_axis.set_yticks(r600_y)
    mass_axis.set_yticklabels(labels, fontsize=6.8)
    mass_axis.set_xlabel("mass ±1σ / ±2σ", fontsize=7.4)
    mass_axis.set_title(
        "C. Forward R600 compatibility" + (" († provisional)" if r600_provisional else ""),
        loc="left",
        weight="bold",
    )
    mass_axis.legend(
        handles=[
            Line2D([0], [0], color="#526475", lw=4.5, label="±1σ"),
            Line2D([0], [0], color="#526475", lw=10, alpha=0.22, label="±2σ"),
        ],
        loc="upper center",
        ncol=2,
        framealpha=0.9,
        fontsize=6.3,
        handlelength=1.7,
        columnspacing=0.8,
        borderpad=0.3,
    )
    ratio_axis.set_xlim(*ratio_limits)
    ratio_axis.set_ylim(mass_axis.get_ylim())
    ratio_axis.set_yticks(r600_y)
    ratio_axis.set_yticklabels([])
    ratio_axis.axvline(0.0, color="#596673", lw=1.0, ls="--")
    ratio_axis.set_xlabel("log predictive ratio to CTT (nats)", fontsize=7.2)
    ratio_axis.set_title("Forward log density", fontsize=8.2)

    selection = r600_result["selection"]
    status_text, status_color = status_banner(suite, r600_result)
    figure.suptitle(
        "WGS84-geodesic direct-to conditionals: through-00:11 inference and R600 compatibility",
        y=0.975,
        fontsize=16.7,
        weight="bold",
        color="#10243e",
    )
    figure.text(
        0.5,
        0.937,
        "Common observations and radar/turn/Mach/altitude priors; lateral-guidance parameterizations differ; 4 Hz BFO and ERA5 active.",
        ha="center",
        fontsize=9.1,
        color="#465464",
    )
    figure.text(
        0.5,
        0.902,
        status_text,
        ha="center",
        fontsize=8.8,
        color="white",
        weight="bold",
        bbox={"boxstyle": "round,pad=.32", "facecolor": status_color, "edgecolor": "none"},
    )
    figure.text(
        0.5,
        0.093,
        f"R600 replay: {selection['time_utc']}; BTO {selection['observed_bto_us']:.0f} ± "
        f"{selection['standard_deviation_us']:.0f} μs was held out from fitting and is the only new likelihood; candidate set was not preregistered.",
        ha="center",
        fontsize=8.1,
        color="#52606d",
    )
    figure.text(0.5, 0.058, SCOPE, ha="center", fontsize=7.7, color="#52606d")
    figure.text(
        0.5,
        0.023,
        SELECTION_WARNING,
        ha="center",
        fontsize=7.8,
        color="#8a3b2f",
        weight="bold",
    )

    created = datetime(2014, 3, 8, 0, 10, 59, tzinfo=timezone.utc)
    outputs = []
    stem = "fixed_waypoint_candidate_comparison"
    title = "WGS84-geodesic direct-to conditionals: through-00:11 inference and R600 compatibility"
    for suffix in ("svg", "pdf", "png"):
        path = output / f"{stem}.{suffix}"
        temporary = path.with_name(f".{path.name}.tmp")
        if suffix == "svg":
            metadata = {"Creator": "MH370 fixed-waypoint reporter", "Title": title, "Date": SOURCE_EPOCH_UTC}
        elif suffix == "pdf":
            metadata = {
                "Creator": "MH370 fixed-waypoint reporter",
                "Title": title,
                "CreationDate": created,
                "ModDate": created,
            }
        else:
            metadata = {"Software": "MH370 fixed-waypoint reporter", "Title": title}
        figure.savefig(temporary, format=suffix, dpi=300, facecolor="white", metadata=metadata)
        os.replace(temporary, path)
        outputs.append(path)
    plt.close(figure)
    return outputs


def summary_rows(suite: dict, families: list[dict], r600: dict) -> list[dict]:
    reference = families[0]["equal_seed_logmean_evidence"]
    rows = []
    for family in families:
        aggregate = family["summary"]
        control = r600[family["key"]]
        prior = control["propagated_prior_at_0019"]
        conditioned = control["r600_conditioned_at_0019"]
        course = control["_report_course"]
        m1941 = control["m1941_through_m0011_smoothing_posterior"]
        waypoint = family["waypoint"] or {}
        row = {
            "family": family["key"],
            "label": family["label"],
            "lateral_mode": family["mode"],
            "fixed_waypoint_target": waypoint.get("target_name", ""),
            "fixed_waypoint_identity_sha256": family["route_identity_sha256"],
            "fixed_waypoint_latitude_deg": waypoint.get("latitude_deg", ""),
            "fixed_waypoint_longitude_deg": waypoint.get("longitude_deg", ""),
            "coordinate_source_title": waypoint.get("coordinate_source_title", ""),
            "coordinate_source_uri": waypoint.get("coordinate_source_uri", ""),
            "coordinate_source_date": waypoint.get("coordinate_source_date", ""),
            "coordinate_frame_assumption": waypoint.get("coordinate_frame_assumption", ""),
            "source_run_status": suite["status"],
            "era5_temperature_wind_active": str(aggregate["weather_applied"] is True).lower(),
            "igrf_declination_active": str(
                aggregate["magnetic_declination_applied"] is True
            ).lower(),
            "converged": str(aggregate["converged"] is True).lower(),
            "source_mean_latitude_deg": family["mean_latitude_deg"],
            "source_mean_longitude_deg": family["mean_longitude_deg"],
            "source_latitude_90_low_deg": aggregate["pooled_latitude_90_deg"][0],
            "source_latitude_90_high_deg": aggregate["pooled_latitude_90_deg"][1],
            "source_longitude_90_low_deg": aggregate["pooled_longitude_90_deg"][0],
            "source_longitude_90_high_deg": aggregate["pooled_longitude_90_deg"][1],
            "maximum_source_seed_mean_separation_nm": aggregate["maximum_seed_mean_separation_nm"],
            "source_log_evidence_range_nats": aggregate["log_evidence_range"],
            "source_minimum_mutation_acceptance": aggregate["minimum_mutation_acceptance"],
            "equal_seed_logmean_evidence": family["equal_seed_logmean_evidence"],
            "conditional_delta_log_evidence_to_ctt_nats": family["equal_seed_logmean_evidence"] - reference,
            "seed_370023_log_evidence": family["seeds"][0]["log_evidence"],
            "seed_370024_log_evidence": family["seeds"][1]["log_evidence"],
            "seed_370025_log_evidence": family["seeds"][2]["log_evidence"],
            "initial_post_turn_track_true_mean_deg": course["initial"][0],
            "initial_post_turn_track_true_90_low_deg": course["initial"][1][0],
            "initial_post_turn_track_true_90_high_deg": course["initial"][1][1],
            "m1941_through_m0011_smoothing_mean_latitude_deg": m1941["mean"]["latitude_deg"],
            "m1941_through_m0011_smoothing_mean_longitude_deg": m1941["mean"]["longitude_deg"],
            "m1941_through_m0011_smoothing_track_true_mean_deg": course["m1941"][0],
            "m1941_through_m0011_smoothing_track_true_90_low_deg": course["m1941"][1][0],
            "m1941_through_m0011_smoothing_track_true_90_high_deg": course["m1941"][1][1],
            "m0011_source_track_true_mean_deg": course["m0011"][0],
            "m0011_source_track_true_90_low_deg": course["m0011"][1][0],
            "m0011_source_track_true_90_high_deg": course["m0011"][1][1],
            "r600_prior_mean_latitude_deg": prior["mean"]["latitude_deg"],
            "r600_prior_mean_longitude_deg": prior["mean"]["longitude_deg"],
            "r600_prior_track_true_mean_deg": course["r600_predictive"][0],
            "r600_prior_track_true_90_low_deg": course["r600_predictive"][1][0],
            "r600_prior_track_true_90_high_deg": course["r600_predictive"][1][1],
            "r600_prior_bto_residual_mean_us": prior["bto_residual_mean_us"],
            "r600_prior_bto_residual_mae_us": prior["bto_residual_mae_us"],
            "r600_prior_bto_residual_rmse_us": prior["bto_residual_rmse_us"],
            "r600_prior_mass_within_one_bto_sd": prior["mass_within_one_bto_sd"],
            "r600_prior_mass_within_two_bto_sd": prior["mass_within_two_bto_sd"],
            "r600_maximum_source_replay_separation_nm": control[
                "maximum_source_replay_separation_nm"
            ],
            "r600_maximum_source_replay_track_difference_deg": control[
                "maximum_source_replay_track_difference_deg"
            ],
            "r600_maximum_source_replay_heading_difference_deg": control[
                "maximum_source_replay_heading_difference_deg"
            ],
            "r600_maximum_source_replay_ground_speed_difference_kt": control[
                "maximum_source_replay_ground_speed_difference_kt"
            ],
            "r600_conditioned_mean_latitude_deg": conditioned["mean"]["latitude_deg"],
            "r600_conditioned_mean_longitude_deg": conditioned["mean"]["longitude_deg"],
            "r600_conditioned_bto_residual_mean_us": conditioned["bto_residual_mean_us"],
            "r600_conditioned_bto_residual_mae_us": conditioned["bto_residual_mae_us"],
            "r600_conditioned_bto_residual_rmse_us": conditioned["bto_residual_rmse_us"],
            "r600_conditioned_mean_track_true_deg": course["r600_conditioned"][0],
            "r600_conditioned_track_true_90_low_deg": course["r600_conditioned"][1][0],
            "r600_conditioned_track_true_90_high_deg": course["r600_conditioned"][1][1],
            "r600_conditioned_mean_heading_true_deg": control["mean_heading_true_deg_after_conditioning"],
            "r600_equal_seed_log_predictive_density": control["equal_seed_log_predictive_density"],
            "r600_predictive_likelihood_ratio_to_ctt": control[
                "predictive_likelihood_ratio_to_constant_true_track"
            ],
            "r600_log_predictive_likelihood_ratio_to_ctt": control[
                "_report_log_predictive_ratio_to_ctt"
            ],
            "r600_seed_log_predictive_density_range": control["seed_log_predictive_density_range"],
            "r600_maximum_seed_conditioned_mean_separation_nm": control[
                "maximum_seed_conditioned_mean_separation_nm"
            ],
            "r600_minimum_seed_conditioned_effective_sample_size": control[
                "predictive_stability"
            ]["minimum_seed_conditioned_effective_sample_size"],
            "r600_predictive_stability_pass": str(
                control["_report_predictive_stability_pass"]
            ).lower(),
            "r600_predictive_stability_status": control[
                "_report_predictive_stability_status"
            ],
        }
        rows.append(row)
    return rows


def write_supporting_files(
    output: Path,
    suite: dict,
    families: list[dict],
    r600_result: dict,
    r600: dict,
    step_control: dict,
) -> list[Path]:
    rows = summary_rows(suite, families, r600)
    csv_path = output / "fixed_waypoint_candidate_summary.csv"
    temporary = csv_path.with_name(f".{csv_path.name}.tmp")
    with temporary.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    os.replace(temporary, csv_path)

    table = []
    for row in rows:
        log_ratio = row["r600_log_predictive_likelihood_ratio_to_ctt"]
        latitude_text = f"{abs(row['source_mean_latitude_deg']):.3f}°{'N' if row['source_mean_latitude_deg'] >= 0 else 'S'}"
        longitude_text = f"{abs(row['source_mean_longitude_deg']):.3f}°{'E' if row['source_mean_longitude_deg'] >= 0 else 'W'}"
        table.append(
            "| {label} | {status} | {position} | {delta:+.3f} | "
            "{mass:.3g}% | {ratio} |".format(
                label=row["label"],
                status=(
                    ("pass" if row["converged"] == "true" else "FAIL")
                    + " / "
                    + (
                        "stable"
                        if row["r600_predictive_stability_pass"] == "true"
                        else "PROVISIONAL"
                    )
                ),
                position=f"{latitude_text}, {longitude_text}",
                delta=row["conditional_delta_log_evidence_to_ctt_nats"],
                mass=100 * row["r600_prior_mass_within_two_bto_sd"],
                ratio=f"{log_ratio:+.3f}",
            )
        )
    course_table = []
    for family in families:
        course = r600[family["key"]]["_report_course"]
        formatted = []
        for key in ("initial", "m1941", "m0011", "r600_predictive", "r600_conditioned"):
            mean, interval = course[key]
            formatted.append(f"{mean:.2f}° [{interval[0]:.2f}, {interval[1]:.2f}]")
        course_table.append(
            f"| {family['label']} | " + " | ".join(formatted) + " |"
        )
    candidate_lines = []
    for family in families[1:]:
        waypoint = family["waypoint"]
        waypoint_latitude = f"{abs(waypoint['latitude_deg']):.8f}°{'N' if waypoint['latitude_deg'] >= 0 else 'S'}"
        waypoint_longitude = f"{abs(waypoint['longitude_deg']):.8f}°{'E' if waypoint['longitude_deg'] >= 0 else 'W'}"
        candidate_lines.append(
            f"- **{family['label']}:** {waypoint_latitude}, {waypoint_longitude}, carried from "
            f"[{waypoint['coordinate_source_title']}]({waypoint['coordinate_source_uri']}). "
            f"Route identity `{family['route_identity_sha256']}`. {waypoint['coordinate_note']}"
        )
    status_text, _ = status_banner(suite, r600_result)
    selection = r600_result["selection"]
    captions_path = output / "CAPTIONS.md"
    atomic_text(
        captions_path,
        "# Fixed-waypoint conditional comparison\n\n"
        "## Figure caption\n\n"
        "**WGS84-geodesic direct-to conditionals fitted through 00:11 UTC and checked for "
        "forward compatibility with corrected R600 BTO.** All families use the same observations, "
        "radar-state, turn-time, Mach and altitude priors and 4 Hz BFO model; their lateral-guidance "
        "parameterizations and effective prior dimensions differ. ERA5 temperature/wind is active and IGRF "
        "declination is inactive for these true-reference families. The direct-to guidance is "
        "a generic geodesic approximation, not a reproduction of certified Boeing 777 LNAV. "
        "Panel A shows the separately normalized 90% "
        "(solid) and 50% (dashed) highest-posterior-density contours for a fresh constant-"
        "true-track reference and two fixed-destination direct-to controls. "
        "Open symbols are individual-seed means and filled symbols are equal-seed within-"
        "family means; particles are never pooled between structural families. Panel B "
        "shows paired-seed and equal-seed log-mean integrated-fit differences relative to "
        "constant true track, together with each family’s declared numerical convergence. "
        "Because the destinations were selected after inspecting geometric alignment and "
        "there is no prior over the universe of possible destinations or look-elsewhere "
        "correction, and a point-target family has a different effective dimension/prior "
        "volume from CTT’s free 0–360° control, these differences are exploratory conditional-"
        "fit comparisons—not Bayes factors for pilot intent or posterior model probabilities. "
        "Panel C propagates "
        f"each fitted family unchanged to {selection['time_utc']}. Corrected R600 "
        f"BTO {selection['observed_bto_us']:.0f} ± {selection['standard_deviation_us']:.0f} μs "
        "was held out from estimator fitting and is the only new likelihood. Candidate "
        "discovery was nevertheless prompted by seventh-arc/186.2° geometry, so this is a "
        "forward predictive compatibility check rather than a pristine preregistered out-of-"
        "sample model-selection test. It reports prior predictive mass within one and two "
        "measurement standard deviations and the predictive-density ratio to constant true "
        "track in exact log space. The selected 30 s source/replay step is bound to the hashed "
        f"actual-grid integration-step control ({step_control['input_set_sha256']}); this control "
        "checks the declared numerical decision rule but is not an independent physical model. "
        "A dagger marks any family whose typed R600 stability status is provisional because "
        f"its cross-seed log-predictive range exceeds {R600_MAX_LOG_PREDICTIVE_RANGE_NATS:.1f} "
        "nat, its conditioned-centroid separation exceeds "
        f"{R600_MAX_CONDITIONED_CENTROID_SEPARATION_NM:.0f} NM. Conditioned seed ESS is required "
        "to be finite and positive but has no calibrated magnitude floor and does not otherwise "
        "enter that descriptive decision. This qualifies the post-R600 diagnostic rather than changing "
        "the source posterior’s convergence declaration. "
        "This forward check is not an impact PDF and does not evaluate BFO at R600, "
        "fuel, flameout, descent, or impact displacement.\n\n"
        f"**Run status:** {status_text}. Source nonconvergence makes its integrated-fit and location "
        "diagnostics provisional; R600 seed instability makes the affected forward comparison provisional.\n\n"
        "## Artifact-derived comparison\n\n"
        "| Family | source / R600 status | 00:11 mean (lat, lon) | conditional Δlog evidence vs CTT "
        "(nats) | R600 prior mass within ±2σ | R600 log predictive ratio to CTT (nats) |\n"
        "|---|---:|---:|---:|---:|---:|\n"
        + "\n".join(table)
        + "\n\n"
        "## True-ground-track course evolution\n\n"
        "Values are circular posterior means with central 90% intervals in degrees true. The "
        "interval endpoints are unwrapped about each circular mean and may therefore lie outside "
        "the conventional [0°, 360°) display range. The "
        "19:41 column is a **through-00:11 smoothing posterior at m1941**: its weights include "
        "later fitted observations and it is not a filtering estimate available at 19:41. "
        "For CTT, the initial post-turn value is the sampled selected-track setpoint; for each "
        "direct-to family it is the derived WGS84-geodesic tangent at the sampled turn. R600 "
        "predictive values precede the R600 likelihood; conditioned values follow separate "
        "within-seed updates and equal seed averaging. These are ground tracks, not headings.\n\n"
        "| Family | initial post-turn | 19:41 smoothing | 00:11 | R600 predictive | R600 conditioned |\n"
        "|---|---:|---:|---:|---:|---:|\n"
        + "\n".join(course_table)
        + "\n\n"
        "The full machine-readable table includes route identities, per-seed evidence, "
        "uncertainty bounds, mutation acceptance, R600 residual MAE/RMSE, exact source-replay "
        "diagnostics, conditioned positions, headings, and cross-seed predictive stability. "
        "Scientific numbers in the table and figure are "
        "read from hashed run artifacts; none are hand-entered.\n\n"
        "## Candidate provenance and interpretation boundary\n\n"
        + "\n".join(candidate_lines)
        + "\n\n"
        "The retrospective screen was non-exhaustive and used an X-Plane cycle-2012.08 "
        "simulator catalogue, not 9M-MRO’s certified navigation database; no frozen search "
        "universe, numeric tolerance or tie-breaking rule survives. The official AADC and "
        "COMNAP production coordinates above were later substitutions for screen-era "
        "locations. Candidate ranking also inspected near-R600 course and miss from a legacy "
        "CTT R600 mean, so the R600 comparison is not selection-blind.\n\n"
        "The coordinate sources describe landing-area/facility reference points, not exact "
        "historical runway thresholds. They do not establish that either destination was in "
        "9M-MRO’s March 2014 navigation database, could accept a Boeing 777, or was selected "
        "by the aircraft. The analysis does not establish that either destination was reachable "
        "on the remaining fuel. Neither admitted coordinate source states a horizontal datum; the "
        "run explicitly treats the published geographic latitude/longitude as WGS84 for "
        "propagation. Passage-level support and negative findings are recorded in "
        "[the citation ledger](../../../../.sources/antarctic-waypoint-navigation/README.md) "
        "and [retrospective selection ledger](../../../../.sources/antarctic-waypoint-navigation/SELECTION-LEDGER.md).\n",
    )
    return [csv_path, captions_path]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--step-control", type=Path, default=DEFAULT_STEP_CONTROL)
    arguments = parser.parse_args()
    run = arguments.run.resolve()
    output = arguments.output.resolve()
    step_control_folder = arguments.step_control.resolve()
    if output.parent != run:
        raise ValueError("output must be a direct child of the source run")
    require_file(CITATION_LEDGER, "passage-level citation ledger")
    require_file(SELECTION_LEDGER, "retrospective candidate-selection ledger")
    output.mkdir(parents=True, exist_ok=True)

    suite, families, run_inputs, source_context = load_run(run)
    step_control, step_control_inputs = load_step_control(
        step_control_folder, suite, families, source_context
    )
    r600_result, r600, r600_inputs = load_r600(
        run, suite, families, source_context
    )
    outputs = publication_plate(suite, families, r600_result, r600, output)
    outputs.extend(
        write_supporting_files(output, suite, families, r600_result, r600, step_control)
    )

    generator = Path(__file__).resolve()
    manifest = {
        "schema_version": 2,
        "artifact": "fixed-waypoint candidate conditional comparison",
        "generator": str(generator),
        "generator_sha256": digest(generator),
        "source_run": str(run),
        "source_run_status": suite["status"],
        "source_suite_artifact_schema_version": suite["schema_version"],
        "source_config_schema_version": suite["config_schema_version"],
        "source_handoff_schema_version": suite["handoff_schema_version"],
        "r600_result_schema_version": r600_result["schema_version"],
        "source_epoch_utc": SOURCE_EPOCH_UTC,
        "r600_control_input_set_sha256": r600_result["input_set_sha256"],
        "r600_control_status": r600_result["status"],
        "r600_predictive_stability": {
            family["key"]: r600[family["key"]]["predictive_stability"]
            for family in families
        },
        "integration_step_control": {
            "path": str(step_control_folder),
            "input_set_sha256": step_control["input_set_sha256"],
            "chosen_production_step_s": step_control["chosen_production_step_s"],
            "configured_production_step_s": step_control["configured_production_step_s"],
            "configured_step_matches_chosen": step_control["configured_step_matches_chosen"],
            "decision_rule": step_control["decision_rule"],
            "thresholds": step_control["thresholds"],
        },
        "display_bandwidth_nm": BANDWIDTH_NM,
        "structural_pooling": "none",
        "seed_pooling": (
            "equal weight within each family only; R600-conditioned particle weights are "
            "normalized separately within each seed before equal-seed averaging"
        ),
        "guidance_interpretation": (
            "WGS84-geodesic direct-to conditional; generic approximation, not certified "
            "Boeing 777 LNAV"
        ),
        "source_environment": {
            "era5_temperature_wind_active": True,
            "igrf_declination_active": False,
        },
        "conditional_fit_boundary": (
            "Candidate targets were selected after geometric inspection; no waypoint-universe "
            "prior or look-elsewhere correction exists, and point-target and free-control "
            "families have different effective dimensions/prior volumes. Delta log evidence "
            "is an exploratory conditional integrated-fit comparison, not intent/model odds."
        ),
        "scope": [SCOPE, SELECTION_WARNING],
        "r600_boundary": (
            "R600 BTO was held out from estimator fitting and is the only new likelihood, "
            "but candidate discovery was prompted by seventh-arc/186.2-degree geometry; this "
            "is a forward compatibility check, not a preregistered model-selection test."
        ),
        "citation_ledger": {
            "path": str(CITATION_LEDGER),
            "sha256": digest(CITATION_LEDGER),
        },
        "selection_ledger": {
            "path": str(SELECTION_LEDGER),
            "sha256": digest(SELECTION_LEDGER),
        },
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "matplotlib": mpl.__version__,
        },
        "inputs": {
            str(path.resolve()): digest(path)
            for path in sorted(
                set(
                    run_inputs
                    + r600_inputs
                    + step_control_inputs
                    + [CITATION_LEDGER, SELECTION_LEDGER]
                )
            )
        },
        "outputs": {path.name: digest(path) for path in sorted(outputs)},
        "reproduction_command": (
            f".venv/bin/python {generator.relative_to(ROOT)} --run {run} --output {output} "
            f"--step-control {step_control_folder}"
        ),
    }
    manifest_path = output / "figure_manifest.json"
    atomic_text(manifest_path, json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(f"generated {len(outputs)} artifacts and {manifest_path}")


if __name__ == "__main__":
    main()
