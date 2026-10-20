#!/usr/bin/env python3
"""Render bounded, deterministic broad-flight spatial posterior reports.

The renderer consumes one explicit JSON specification.  Every spatial bound,
bin width, grid spacing, and display-kernel bandwidth is physical and fixed by
that specification; none is inferred from posterior extrema or quantiles.
Families remain separate, while declared numerical seeds are equally weighted
within a family.  A report that does not satisfy the numerical-support standard
is refused unless both the specification marks it as diagnostic and the caller
passes ``--allow-failed-diagnostic``.  Such output is prominently watermarked
and is never publication eligible.

Supported particle sources are the broad powered-flight posterior CSV and the
broad terminal/impact JSON handoff.  A generic flat impact CSV is also accepted
through documented column aliases.  A flat export whose weights were already
conditioned on impact must declare ``weights_are_position_conditional`` and its
unconditional ``posterior_position_mass`` in the source specification.  Impact
locations are normalized only for the explicitly labelled distribution
conditional on impact; the unconditional posterior impact mass remains in the
audit.

An impact JSON source can instead render its parent checkpoint by declaring
``spatial_target: "parent_checkpoint"`` and an explicit ``parent_handoff``
path.  The referenced file's bytes must match ``parent.handoff_sha256``.  The
default ``terminal_outcome_selection: "all_outcomes"`` aggregates every
positive terminal posterior weight back to its exact parent identity before
plotting.  ``"impact_only"`` is an explicit conditional alternative whose
conditioning mass is retained in the audit.  Both are later-evidence-smoothed
views of the parent state and therefore require report semantics ``smoothed``.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import html
import json
import math
import os
from pathlib import Path
import sys
from typing import Any, Iterable

os.environ.setdefault("MPLBACKEND", "Agg")
os.environ.setdefault("SOURCE_DATE_EPOCH", "1394237459")

import matplotlib as mpl

mpl.use("Agg")
mpl.rcParams.update(
    {
        "axes.facecolor": "#fbfcfd",
        "axes.grid": True,
        "font.family": "DejaVu Sans",
        "font.size": 9.0,
        "grid.color": "#dfe4e9",
        "grid.linewidth": 0.65,
        "pdf.fonttype": 42,
        "savefig.dpi": 300,
        "svg.fonttype": "none",
        "svg.hashsalt": "mh370-broad-flight-spatial-report",
    }
)
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree


SCHEMA_ID = "mh370-broad-flight-spatial-report-spec"
SCHEMA_VERSION = 1
REPORT_SCHEMA_ID = "mh370-broad-flight-spatial-report"
REPORT_SCHEMA_VERSION = 1
BROAD_IMPACT_SCHEMA_ID = "mh370-broad-terminal-impact-handoff"
M0011_TIME_UNIX_S_UTC = 1_394_237_459.0
EARTH_RADIUS_KM = 6371.0088
KM_PER_NM = 1.852
HPD_MASSES = (0.50, 0.95, 0.99)
ROOT_MASS_THRESHOLDS = (1.0e-6, 1.0e-3)
TERMINAL_OUTCOMES = {
    "impact",
    "no_exhaustion_by_bound",
    "powered_continuation_rejected",
    "fuel_model_unavailable",
    "already_exhausted_before_checkpoint",
    "end_of_flight_non_impact",
}
MAX_FAMILIES = 8
MAX_SOURCES = 64
MAX_PARTICLE_ROWS_PER_SOURCE = 2_000_000
MAX_GRID_CELLS = 360_000
WEIGHT_TOLERANCE = 2.0e-8
PALETTE = (
    "#0072B2",
    "#D55E00",
    "#009E73",
    "#CC79A7",
    "#E69F00",
    "#56B4E9",
    "#6C5B7B",
    "#7A6A3A",
)

NUMERICAL_STANDARDS = {
    "milestone": {
        "minimum_root_ess": 50.0,
        "maximum_root_mass": 0.05,
        "minimum_particle_ess": 1000.0,
        "minimum_particle_ess_fraction": 0.005,
        "minimum_stratum_mass_for_check": 0.01,
        "minimum_stratum_root_ess": 20.0,
        "minimum_stratum_particle_ess": 100.0,
        "maximum_seed_tv_median": 0.10,
        "maximum_seed_tv": 0.20,
        "maximum_seed_mean_shift_nm": 25.0,
        "maximum_seed_95_endpoint_shift_nm": 30.0,
        "maximum_log_evidence_sd": 0.5,
        "maximum_log_evidence_range": 1.5,
        "maximum_fuel_mean_delta": 0.01,
        "maximum_fuel_exhaustion_mass_delta": 0.05,
    },
    "production": {
        "minimum_root_ess": 200.0,
        "maximum_root_mass": 0.02,
        "minimum_particle_ess": 1000.0,
        "minimum_particle_ess_fraction": 0.005,
        "minimum_stratum_mass_for_check": 0.01,
        "minimum_stratum_root_ess": 20.0,
        "minimum_stratum_particle_ess": 100.0,
        "maximum_seed_tv_median": 0.10,
        "maximum_seed_tv": 0.20,
        "maximum_seed_mean_shift_nm": 25.0,
        "maximum_seed_95_endpoint_shift_nm": 30.0,
        "maximum_log_evidence_sd": 0.5,
        "maximum_log_evidence_range": 1.5,
        "maximum_fuel_mean_delta": 0.01,
        "maximum_fuel_exhaustion_mass_delta": 0.05,
    },
}


class ReportInputError(ValueError):
    """The report request or a source artifact is invalid."""


class PublicationRefused(RuntimeError):
    """Numerical support is failed or unassessed."""

    def __init__(self, assessment: dict[str, Any]):
        self.assessment = assessment
        failures = [
            item
            for item in assessment["criteria"]
            if item["status"] != "passed"
        ]
        preview = "; ".join(
            f"{item['scope']}: {item['criterion']} ({item['status']})"
            for item in failures[:8]
        )
        if len(failures) > 8:
            preview += f"; and {len(failures) - 8} more"
        super().__init__(
            "numerical support does not permit publication; "
            f"use a diagnostic specification and explicit override to render: {preview}"
        )


@dataclass(frozen=True)
class SpatialGrid:
    origin_latitude_deg: float
    origin_longitude_deg: float
    along_axis_bearing_deg: float
    along_min_km: float
    along_max_km: float
    cross_min_km: float
    cross_max_km: float
    cell_size_km: float
    bandwidth_km: float
    kernel_truncation_sigma: float

    @property
    def along_edges(self) -> np.ndarray:
        return fixed_edges(self.along_min_km, self.along_max_km, self.cell_size_km)

    @property
    def cross_edges(self) -> np.ndarray:
        return fixed_edges(self.cross_min_km, self.cross_max_km, self.cell_size_km)


@dataclass(frozen=True)
class MarginalGrid:
    latitude_min_deg: float
    latitude_max_deg: float
    latitude_bin_width_deg: float
    along_min_km: float
    along_max_km: float
    along_bin_width_km: float

    @property
    def latitude_edges(self) -> np.ndarray:
        return fixed_edges(
            self.latitude_min_deg,
            self.latitude_max_deg,
            self.latitude_bin_width_deg,
        )

    @property
    def along_edges(self) -> np.ndarray:
        return fixed_edges(self.along_min_km, self.along_max_km, self.along_bin_width_km)


@dataclass
class ParticleSource:
    family_id: str
    seed: int
    logical_path: str
    path: Path
    source_format: str
    latitude_deg: np.ndarray
    longitude_deg: np.ndarray
    weights: np.ndarray
    particle_ids: np.ndarray | None
    root_ids: np.ndarray | None
    strata: np.ndarray | None
    fuel_flow_scale: np.ndarray | None
    fuel_exhausted: np.ndarray | None
    configured_particles: int
    posterior_position_mass: float
    posterior_total_mass: float
    summary: dict[str, Any]
    summary_logical_path: str | None
    summary_path: Path | None
    input_sha256: str
    summary_sha256: str | None
    source_metadata: dict[str, Any]
    east_km: np.ndarray | None = None
    north_km: np.ndarray | None = None
    along_km: np.ndarray | None = None
    cross_km: np.ndarray | None = None
    marginal_along_km: np.ndarray | None = None
    endpoint_coordinate_km: np.ndarray | None = None


@dataclass
class Family:
    family_id: str
    label: str
    color: str
    sources: list[ParticleSource]


@dataclass(frozen=True)
class ArcProjector:
    points_east_north_km: np.ndarray
    values_km: np.ndarray
    label: str
    tree: cKDTree

    def project(self, east_km: np.ndarray, north_km: np.ndarray) -> np.ndarray:
        query = np.column_stack((east_km, north_km))
        nearest = self.tree.query(query, workers=1)[1]
        segment_count = len(self.points_east_north_km) - 1
        candidates = np.column_stack(
            (
                np.clip(nearest - 1, 0, segment_count - 1),
                np.clip(nearest, 0, segment_count - 1),
            )
        )
        best_distance_squared = np.full(len(query), np.inf)
        best_values = np.empty(len(query), dtype=float)
        for column in range(candidates.shape[1]):
            indices = candidates[:, column]
            start = self.points_east_north_km[indices]
            end = self.points_east_north_km[indices + 1]
            vector = end - start
            denominator = np.einsum("ij,ij->i", vector, vector)
            fraction = np.divide(
                np.einsum("ij,ij->i", query - start, vector),
                denominator,
                out=np.zeros(len(query), dtype=float),
                where=denominator > 0.0,
            )
            fraction = np.clip(fraction, 0.0, 1.0)
            projected = start + fraction[:, None] * vector
            distance_squared = np.einsum(
                "ij,ij->i", query - projected, query - projected
            )
            replace = distance_squared < best_distance_squared
            best_distance_squared[replace] = distance_squared[replace]
            values = self.values_km[indices] + fraction * (
                self.values_km[indices + 1] - self.values_km[indices]
            )
            best_values[replace] = values[replace]
        return best_values


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def atomic_text(path: Path, value: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, path)


def atomic_figure(fig: plt.Figure, path: Path, metadata: dict[str, Any]) -> None:
    temporary = path.with_name(f".{path.name}.tmp")
    fig.savefig(
        temporary,
        format=path.suffix.removeprefix("."),
        dpi=300,
        facecolor="white",
        metadata=metadata,
    )
    os.replace(temporary, path)


def finite_number(value: Any, description: str) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ReportInputError(f"invalid {description}: {value!r}") from error
    if not math.isfinite(result):
        raise ReportInputError(f"non-finite {description}: {value!r}")
    return result


def finite_optional(value: Any, description: str) -> float | None:
    if value is None or value == "":
        return None
    return finite_number(value, description)


def integer(value: Any, description: str) -> int:
    if isinstance(value, bool):
        raise ReportInputError(f"invalid {description}: {value!r}")
    try:
        result = int(value)
    except (TypeError, ValueError) as error:
        raise ReportInputError(f"invalid {description}: {value!r}") from error
    if str(value).strip() not in {str(result), f"{result}.0"} and not isinstance(value, int):
        raise ReportInputError(f"non-integral {description}: {value!r}")
    return result


def fixed_edges(low: float, high: float, width: float) -> np.ndarray:
    count_float = (high - low) / width
    count = int(round(count_float))
    if count <= 0 or not math.isclose(count_float, count, rel_tol=0.0, abs_tol=1.0e-9):
        raise ReportInputError(
            f"fixed interval [{low}, {high}] is not an integer multiple of {width}"
        )
    return np.linspace(low, high, count + 1)


def resolve_path(spec_path: Path, raw: str, description: str) -> Path:
    candidate = Path(raw)
    path = candidate if candidate.is_absolute() else spec_path.parent / candidate
    path = path.resolve()
    if not path.is_file():
        raise ReportInputError(f"missing {description}: {path}")
    return path


def first_key(mapping: dict[str, Any], aliases: Iterable[str]) -> str | None:
    for name in aliases:
        if name in mapping:
            return name
    return None


def parse_bounds(value: Any, description: str) -> tuple[float, float]:
    if not isinstance(value, list) or len(value) != 2:
        raise ReportInputError(f"{description} must contain exactly two values")
    low = finite_number(value[0], f"{description} lower bound")
    high = finite_number(value[1], f"{description} upper bound")
    if low >= high:
        raise ReportInputError(f"{description} bounds are not increasing")
    return low, high


def load_spec(path: Path) -> dict[str, Any]:
    try:
        spec = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ReportInputError(f"cannot read report specification: {path}") from error
    if not isinstance(spec, dict):
        raise ReportInputError("report specification must be a JSON object")
    if spec.get("schema_id") != SCHEMA_ID or spec.get("schema_version") != SCHEMA_VERSION:
        raise ReportInputError(
            f"report specification must be {SCHEMA_ID!r} schema {SCHEMA_VERSION}"
        )
    if spec.get("artifact_class") not in {"publication", "diagnostic"}:
        raise ReportInputError("artifact_class must be publication or diagnostic")
    if spec.get("posterior_semantics") not in {
        "filtering",
        "smoothed",
        "conditional_impact",
    }:
        raise ReportInputError(
            "posterior_semantics must be filtering, smoothed, or conditional_impact"
        )
    for field in ("title", "conditioning_statement", "artifact_epoch_utc"):
        if not isinstance(spec.get(field), str) or not spec[field].strip():
            raise ReportInputError(f"missing non-empty {field}")
    try:
        datetime.fromisoformat(spec["artifact_epoch_utc"].replace("Z", "+00:00"))
    except ValueError as error:
        raise ReportInputError("artifact_epoch_utc is not ISO-8601") from error
    standard = spec.get("numerical_standard", "milestone")
    if standard not in NUMERICAL_STANDARDS:
        raise ReportInputError(
            f"numerical_standard must be one of {sorted(NUMERICAL_STANDARDS)}"
        )
    families = spec.get("families")
    if not isinstance(families, list) or not 1 <= len(families) <= MAX_FAMILIES:
        raise ReportInputError(f"families must contain 1..{MAX_FAMILIES} entries")
    total_sources = sum(
        len(family.get("sources", [])) if isinstance(family, dict) else 0
        for family in families
    )
    if total_sources > MAX_SOURCES:
        raise ReportInputError(f"report exceeds {MAX_SOURCES} particle sources")
    return spec


def spatial_grid(spec: dict[str, Any]) -> SpatialGrid:
    value = spec.get("spatial_grid")
    if not isinstance(value, dict):
        raise ReportInputError("missing spatial_grid")
    origin = value.get("projection_origin_deg")
    if not isinstance(origin, list) or len(origin) != 2:
        raise ReportInputError("projection_origin_deg must be [latitude, longitude]")
    origin_latitude = finite_number(origin[0], "projection origin latitude")
    origin_longitude = finite_number(origin[1], "projection origin longitude")
    if not -90.0 < origin_latitude < 90.0 or not -180.0 <= origin_longitude <= 180.0:
        raise ReportInputError("projection origin is outside WGS84 angular bounds")
    along = parse_bounds(value.get("along_bounds_km"), "along_bounds_km")
    cross = parse_bounds(value.get("cross_bounds_km"), "cross_bounds_km")
    result = SpatialGrid(
        origin_latitude_deg=origin_latitude,
        origin_longitude_deg=origin_longitude,
        along_axis_bearing_deg=finite_number(
            value.get("along_axis_bearing_deg"), "along-axis bearing"
        )
        % 360.0,
        along_min_km=along[0],
        along_max_km=along[1],
        cross_min_km=cross[0],
        cross_max_km=cross[1],
        cell_size_km=finite_number(value.get("cell_size_km"), "grid cell size"),
        bandwidth_km=finite_number(
            value.get("display_bandwidth_km"), "display bandwidth"
        ),
        kernel_truncation_sigma=finite_number(
            value.get("kernel_truncation_sigma", 4.0),
            "kernel truncation",
        ),
    )
    if (
        result.cell_size_km <= 0.0
        or result.bandwidth_km <= 0.0
        or not 3.0 <= result.kernel_truncation_sigma <= 8.0
    ):
        raise ReportInputError(
            "cell size and display bandwidth must be positive; kernel truncation must be 3..8 sigma"
        )
    along_edges = result.along_edges
    cross_edges = result.cross_edges
    cells = (len(along_edges) - 1) * (len(cross_edges) - 1)
    if cells > MAX_GRID_CELLS:
        raise ReportInputError(
            f"fixed grid has {cells} cells; maximum is {MAX_GRID_CELLS}"
        )
    return result


def marginal_grid(spec: dict[str, Any]) -> MarginalGrid:
    value = spec.get("marginals")
    if not isinstance(value, dict):
        raise ReportInputError("missing marginals")
    latitude = parse_bounds(value.get("latitude_bounds_deg"), "latitude_bounds_deg")
    along = parse_bounds(value.get("along_bounds_km"), "marginal along_bounds_km")
    result = MarginalGrid(
        latitude_min_deg=latitude[0],
        latitude_max_deg=latitude[1],
        latitude_bin_width_deg=finite_number(
            value.get("latitude_bin_width_deg"), "latitude bin width"
        ),
        along_min_km=along[0],
        along_max_km=along[1],
        along_bin_width_km=finite_number(
            value.get("along_bin_width_km"), "along-coordinate bin width"
        ),
    )
    if result.latitude_bin_width_deg <= 0.0 or result.along_bin_width_km <= 0.0:
        raise ReportInputError("marginal bin widths must be positive")
    if not -90.0 <= result.latitude_min_deg < result.latitude_max_deg <= 90.0:
        raise ReportInputError("latitude marginal bounds are outside WGS84")
    _ = result.latitude_edges
    _ = result.along_edges
    return result


def azimuthal_equidistant(
    latitude_deg: np.ndarray,
    longitude_deg: np.ndarray,
    origin_latitude_deg: float,
    origin_longitude_deg: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Project WGS84 angles to spherical local east/north kilometres."""

    latitude = np.deg2rad(latitude_deg)
    longitude = np.deg2rad(longitude_deg)
    latitude_zero = math.radians(origin_latitude_deg)
    longitude_zero = math.radians(origin_longitude_deg)
    delta_longitude = (longitude - longitude_zero + math.pi) % (2.0 * math.pi) - math.pi
    sin_latitude = np.sin(latitude)
    cos_latitude = np.cos(latitude)
    cosine_distance = np.clip(
        math.sin(latitude_zero) * sin_latitude
        + math.cos(latitude_zero) * cos_latitude * np.cos(delta_longitude),
        -1.0,
        1.0,
    )
    central_angle = np.arccos(cosine_distance)
    sine_distance = np.sin(central_angle)
    scale = np.divide(
        central_angle,
        sine_distance,
        out=np.ones_like(central_angle),
        where=np.abs(sine_distance) > 1.0e-14,
    )
    east = (
        EARTH_RADIUS_KM
        * scale
        * cos_latitude
        * np.sin(delta_longitude)
    )
    north = EARTH_RADIUS_KM * scale * (
        math.cos(latitude_zero) * sin_latitude
        - math.sin(latitude_zero) * cos_latitude * np.cos(delta_longitude)
    )
    if not np.all(np.isfinite(east)) or not np.all(np.isfinite(north)):
        raise ReportInputError("projection encountered an antipodal or non-finite point")
    return east, north


def rotate_local_axes(
    east_km: np.ndarray, north_km: np.ndarray, bearing_deg: float
) -> tuple[np.ndarray, np.ndarray]:
    bearing = math.radians(bearing_deg)
    along = east_km * math.sin(bearing) + north_km * math.cos(bearing)
    cross = east_km * math.cos(bearing) - north_km * math.sin(bearing)
    return along, cross


def column_name(fieldnames: list[str], aliases: Iterable[str], description: str) -> str:
    for alias in aliases:
        if alias in fieldnames:
            return alias
    raise ReportInputError(
        f"particle table lacks {description}; accepted columns: {', '.join(aliases)}"
    )


def optional_column(fieldnames: list[str], aliases: Iterable[str]) -> str | None:
    return next((alias for alias in aliases if alias in fieldnames), None)


def canonical_identity(value: Any) -> str:
    if isinstance(value, (dict, list)):
        return json.dumps(value, sort_keys=True, separators=(",", ":"))
    return str(value)


def normalize_position_weights(
    weights: np.ndarray,
    total_mass: float,
    semantics: str,
    description: str,
) -> tuple[np.ndarray, float]:
    position_mass = float(np.sum(weights))
    if position_mass <= 0.0 or not math.isfinite(position_mass):
        raise ReportInputError(f"{description} has no positive spatial posterior mass")
    if semantics in {"filtering", "smoothed"}:
        if not math.isclose(total_mass, 1.0, rel_tol=0.0, abs_tol=WEIGHT_TOLERANCE):
            raise ReportInputError(
                f"{description} weights sum to {total_mass:.17g}, not one"
            )
        if not math.isclose(position_mass, 1.0, rel_tol=0.0, abs_tol=WEIGHT_TOLERANCE):
            raise ReportInputError(
                f"{description} omits positive location mass under {semantics} semantics"
            )
    elif position_mass > 1.0 + WEIGHT_TOLERANCE:
        raise ReportInputError(f"{description} position mass exceeds one")
    return weights / position_mass, position_mass


def summary_value(
    summary: dict[str, Any], aliases: Iterable[str], description: str
) -> float | None:
    for alias in aliases:
        value: Any = summary
        ok = True
        for component in alias.split("."):
            if not isinstance(value, dict) or component not in value:
                ok = False
                break
            value = value[component]
        if ok and value is not None:
            return finite_number(value, description)
    return None


def load_summary(
    source_spec: dict[str, Any], spec_path: Path, family_id: str, seed: int
) -> tuple[dict[str, Any], str | None, Path | None, str | None]:
    raw = source_spec.get("summary")
    if raw is None:
        return {}, None, None, None
    if not isinstance(raw, str) or not raw:
        raise ReportInputError(f"summary path for {family_id} seed {seed} is invalid")
    path = resolve_path(spec_path, raw, "seed summary")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ReportInputError(f"invalid seed summary JSON: {path}") from error
    if not isinstance(value, dict):
        raise ReportInputError(f"seed summary is not an object: {path}")
    reported_family = value.get("family")
    reported_seed = value.get("seed")
    if reported_family is not None and reported_family != family_id:
        raise ReportInputError(f"seed summary family mismatch: {path}")
    if reported_seed is not None and integer(reported_seed, "summary seed") != seed:
        raise ReportInputError(f"seed summary seed mismatch: {path}")
    return value, raw, path, sha256(path)


def load_csv_source(
    source_spec: dict[str, Any],
    spec_path: Path,
    family_id: str,
    semantics: str,
) -> ParticleSource:
    raw_path = source_spec.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise ReportInputError(f"missing source path for family {family_id}")
    path = resolve_path(spec_path, raw_path, "particle CSV")
    seed = integer(source_spec.get("seed"), f"seed for {raw_path}")
    summary, summary_logical, summary_path, summary_digest = load_summary(
        source_spec, spec_path, family_id, seed
    )
    latitude: list[float] = []
    longitude: list[float] = []
    weights: list[float] = []
    particle_ids: list[str] = []
    roots: list[str] = []
    strata: list[str] = []
    fuel_scales: list[float] = []
    exhausted: list[float] = []
    all_have_particles = True
    all_have_roots = True
    all_have_strata = True
    all_have_fuel = True
    all_have_exhaustion = True
    total_mass = 0.0
    row_count = 0
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ReportInputError(f"particle CSV has no header: {path}")
        fields = reader.fieldnames
        latitude_name = column_name(
            fields,
            ("latitude_deg", "last_contact_latitude_deg", "impact_latitude_deg", "latitude"),
            "latitude",
        )
        longitude_name = column_name(
            fields,
            ("longitude_deg", "last_contact_longitude_deg", "impact_longitude_deg", "longitude"),
            "longitude",
        )
        linear_weight_name = optional_column(
            fields,
            ("weight", "posterior_weight", "normalized_weight", "baseline_weight"),
        )
        log_weight_name = optional_column(
            fields,
            ("posterior_normalized_log_weight", "normalized_log_weight", "log_weight"),
        )
        if (linear_weight_name is None) == (log_weight_name is None):
            raise ReportInputError(
                f"particle CSV must have exactly one recognized linear or log weight: {path}"
            )
        particle_name = optional_column(
            fields, ("particle", "particle_index", "parent_particle", "parent_particle_index")
        )
        root_name = optional_column(
            fields, ("root", "prior_root", "prior_root_id", "root_id", "initial_particle")
        )
        stratum_name = optional_column(fields, ("stratum", "stratum_id"))
        fuel_name = optional_column(fields, ("fuel_flow_scale", "flow_scale"))
        exhaustion_name = optional_column(
            fields,
            (
                "dual_engine_exhaustion_time_s",
                "dual_engine_exhaustion_time_unix_s",
                "fuel_exhausted",
            ),
        )
        for row_count, row in enumerate(reader, start=1):
            if row_count > MAX_PARTICLE_ROWS_PER_SOURCE:
                raise ReportInputError(
                    f"particle CSV exceeds {MAX_PARTICLE_ROWS_PER_SOURCE} rows: {path}"
                )
            raw_weight = row[linear_weight_name] if linear_weight_name else row[log_weight_name]
            if raw_weight in (None, "") and log_weight_name:
                weight = 0.0
            else:
                parsed_weight = finite_number(raw_weight, f"weight row {row_count} in {path}")
                if log_weight_name:
                    if parsed_weight > WEIGHT_TOLERANCE:
                        raise ReportInputError(f"positive normalized log weight in {path}")
                    weight = math.exp(parsed_weight)
                else:
                    weight = parsed_weight
            if weight < 0.0:
                raise ReportInputError(f"negative weight row {row_count} in {path}")
            total_mass += weight
            if weight == 0.0:
                continue
            lat = finite_number(row[latitude_name], f"latitude row {row_count} in {path}")
            lon = finite_number(row[longitude_name], f"longitude row {row_count} in {path}")
            if not -90.0 <= lat <= 90.0 or not -180.0 <= lon <= 180.0:
                raise ReportInputError(f"invalid WGS84 position row {row_count} in {path}")
            latitude.append(lat)
            longitude.append(lon)
            weights.append(weight)
            if particle_name and row[particle_name] not in (None, ""):
                particle_ids.append(canonical_identity(row[particle_name]))
            else:
                all_have_particles = False
            if root_name and row[root_name] not in (None, ""):
                roots.append(canonical_identity(row[root_name]))
            else:
                all_have_roots = False
            if stratum_name and row[stratum_name] not in (None, ""):
                strata.append(canonical_identity(row[stratum_name]))
            else:
                all_have_strata = False
            fuel_value = finite_optional(
                row[fuel_name] if fuel_name else None,
                f"fuel-flow scale row {row_count} in {path}",
            )
            if fuel_value is None:
                all_have_fuel = False
            else:
                fuel_scales.append(fuel_value)
            if exhaustion_name:
                raw_exhaustion = row[exhaustion_name]
                if exhaustion_name == "fuel_exhausted":
                    normalized = str(raw_exhaustion).strip().lower()
                    if normalized not in {"true", "false", "1", "0"}:
                        all_have_exhaustion = False
                    else:
                        exhausted.append(float(normalized in {"true", "1"}))
                else:
                    exhausted.append(float(raw_exhaustion not in (None, "")))
            else:
                all_have_exhaustion = False
    if row_count == 0:
        raise ReportInputError(f"particle CSV is empty: {path}")
    raw_weights = np.asarray(weights, dtype=float)
    weights_are_position_conditional = source_spec.get(
        "weights_are_position_conditional", False
    )
    if not isinstance(weights_are_position_conditional, bool):
        raise ReportInputError(
            f"weights_are_position_conditional must be boolean for {path}"
        )
    if weights_are_position_conditional:
        if semantics != "conditional_impact":
            raise ReportInputError(
                f"position-conditional input is only valid for conditional_impact: {path}"
            )
        if not math.isclose(total_mass, 1.0, rel_tol=0.0, abs_tol=WEIGHT_TOLERANCE):
            raise ReportInputError(
                f"declared position-conditional weights do not sum to one: {path}"
            )
        position_mass = finite_number(
            source_spec.get("posterior_position_mass"),
            f"unconditional posterior position mass for {path}",
        )
        if not 0.0 < position_mass <= 1.0:
            raise ReportInputError(
                f"unconditional posterior position mass must be in (0, 1]: {path}"
            )
        normalized = raw_weights / total_mass
        posterior_total_mass = 1.0
    else:
        normalized, position_mass = normalize_position_weights(
            raw_weights, total_mass, semantics, str(path)
        )
        posterior_total_mass = 1.0 if semantics == "conditional_impact" else total_mass
    configured = integer(
        source_spec.get(
            "configured_particles",
            summary.get("configured_particles", row_count),
        ),
        f"configured particles for {path}",
    )
    if configured <= 0:
        raise ReportInputError(f"configured particle count is not positive: {path}")
    return ParticleSource(
        family_id=family_id,
        seed=seed,
        logical_path=raw_path,
        path=path,
        source_format="csv",
        latitude_deg=np.asarray(latitude, dtype=float),
        longitude_deg=np.asarray(longitude, dtype=float),
        weights=normalized,
        particle_ids=np.asarray(particle_ids, dtype=object) if all_have_particles else None,
        root_ids=np.asarray(roots, dtype=object) if all_have_roots else None,
        strata=np.asarray(strata, dtype=object) if all_have_strata else None,
        fuel_flow_scale=np.asarray(fuel_scales, dtype=float) if all_have_fuel else None,
        fuel_exhausted=np.asarray(exhausted, dtype=float) if all_have_exhaustion else None,
        configured_particles=configured,
        posterior_position_mass=position_mass,
        posterior_total_mass=posterior_total_mass,
        summary=summary,
        summary_logical_path=summary_logical,
        summary_path=summary_path,
        input_sha256=sha256(path),
        summary_sha256=summary_digest,
        source_metadata={},
    )


def conditioning_name(value: Any) -> str | None:
    if not isinstance(value, dict) or len(value) != 1:
        return None
    key = next(iter(value))
    return key if key in {"filtering", "smoothed"} else None


def terminal_outcome_name(value: Any) -> str | None:
    """Return the serde outcome tag for old flat and current tagged encodings."""

    if isinstance(value, str):
        return value
    if not isinstance(value, dict):
        return None
    tagged = value.get("outcome")
    if isinstance(tagged, str):
        return tagged
    if len(value) == 1:
        key = next(iter(value))
        if isinstance(key, str):
            return key
    return None


def normalized_log_weights(
    values: list[float], description: str, require_unit_mass: bool = False
) -> tuple[np.ndarray, float, float]:
    if not values:
        raise ReportInputError(f"{description} has no positive posterior support")
    logs = np.asarray(values, dtype=float)
    if np.any(~np.isfinite(logs)) or np.any(logs > WEIGHT_TOLERANCE):
        raise ReportInputError(f"{description} contains invalid normalized log weights")
    maximum = float(np.max(logs))
    scaled = np.exp(logs - maximum)
    scaled_sum = float(np.sum(scaled))
    log_mass = maximum + math.log(scaled_sum)
    mass = math.exp(log_mass)
    if require_unit_mass and not math.isclose(
        mass, 1.0, rel_tol=0.0, abs_tol=WEIGHT_TOLERANCE
    ):
        raise ReportInputError(
            f"{description} weights sum to {mass:.17g}, not one"
        )
    return scaled / scaled_sum, mass, log_mass


def utc_posix_seconds(value: Any, description: str) -> float:
    if not isinstance(value, str) or not value.strip():
        raise ReportInputError(f"missing {description}")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ReportInputError(f"invalid {description}: {value!r}") from error
    if parsed.tzinfo is None:
        raise ReportInputError(f"{description} must include a UTC offset")
    return parsed.timestamp()


def load_impact_json_source(
    source_spec: dict[str, Any],
    spec_path: Path,
    family_id: str,
    semantics: str,
) -> ParticleSource:
    if semantics != "conditional_impact":
        raise ReportInputError(
            "broad impact JSON requires conditional_impact report semantics"
        )
    raw_path = source_spec.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise ReportInputError(f"missing source path for family {family_id}")
    path = resolve_path(spec_path, raw_path, "broad impact handoff")
    try:
        handoff = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ReportInputError(f"invalid broad impact JSON: {path}") from error
    if (
        not isinstance(handoff, dict)
        or handoff.get("schema_id") != BROAD_IMPACT_SCHEMA_ID
        or handoff.get("schema_version") != 1
    ):
        raise ReportInputError(f"unsupported broad impact handoff: {path}")
    parent = handoff.get("parent")
    run = handoff.get("run")
    if not isinstance(parent, dict) or not isinstance(run, dict):
        raise ReportInputError(f"broad impact handoff lacks parent/run provenance: {path}")
    seed = integer(source_spec.get("seed", parent.get("seed")), f"seed for {path}")
    if integer(parent.get("seed"), "impact parent seed") != seed:
        raise ReportInputError(f"broad impact parent seed mismatch: {path}")
    declared_parent_semantics = conditioning_name(parent.get("conditioning"))
    if declared_parent_semantics is None:
        raise ReportInputError(f"broad impact parent conditioning is invalid: {path}")
    expected_parent = source_spec.get("parent_semantics")
    if expected_parent is not None and expected_parent != declared_parent_semantics:
        raise ReportInputError(f"broad impact parent semantics mismatch: {path}")
    summary, summary_logical, summary_path, summary_digest = load_summary(
        source_spec, spec_path, family_id, seed
    )
    particles = handoff.get("particles")
    if not isinstance(particles, list) or not particles:
        raise ReportInputError(f"broad impact handoff has no particles: {path}")
    if len(particles) > MAX_PARTICLE_ROWS_PER_SOURCE:
        raise ReportInputError(
            f"broad impact handoff exceeds {MAX_PARTICLE_ROWS_PER_SOURCE} particles"
        )
    latitude: list[float] = []
    longitude: list[float] = []
    selected_logs: list[float] = []
    particle_ids: list[str] = []
    roots: list[str] = []
    strata: list[str] = []
    all_logs: list[float] = []
    for index, particle in enumerate(particles):
        if not isinstance(particle, dict):
            raise ReportInputError(f"invalid impact particle {index} in {path}")
        log_weight = particle.get("posterior_normalized_log_weight")
        if log_weight is None:
            continue
        log_weight = finite_number(log_weight, f"impact log weight {index} in {path}")
        if log_weight > WEIGHT_TOLERANCE:
            raise ReportInputError(f"positive normalized impact log weight in {path}")
        all_logs.append(log_weight)
        impact = particle.get("impact")
        outcome = particle.get("outcome")
        is_impact = terminal_outcome_name(outcome) == "impact"
        if not is_impact:
            if impact is not None:
                raise ReportInputError(f"non-impact particle carries impact data in {path}")
            continue
        if not isinstance(impact, dict) or not isinstance(
            impact.get("position_wgs84"), dict
        ):
            raise ReportInputError(f"impact particle lacks position in {path}")
        position = impact["position_wgs84"]
        lat = finite_number(position.get("latitude"), f"impact latitude {index}")
        lon = finite_number(position.get("longitude"), f"impact longitude {index}")
        if not -90.0 <= lat <= 90.0 or not -180.0 <= lon <= 180.0:
            raise ReportInputError(f"invalid impact position {index} in {path}")
        identity = particle.get("identity")
        if not isinstance(identity, dict):
            raise ReportInputError(f"impact particle lacks identity in {path}")
        prior_root = identity.get("prior_root")
        parent_identity = identity.get("parent")
        if prior_root is None or parent_identity is None or "stratum" not in identity:
            raise ReportInputError(f"impact particle identity is incomplete in {path}")
        latitude.append(lat)
        longitude.append(lon)
        selected_logs.append(log_weight)
        particle_ids.append(canonical_identity(parent_identity))
        roots.append(canonical_identity(prior_root))
        strata.append(canonical_identity(identity["stratum"]))
    if not all_logs:
        raise ReportInputError(f"broad impact handoff has no positive posterior support: {path}")
    _, total_mass, _ = normalized_log_weights(
        all_logs, f"broad impact posterior in {path}", require_unit_mass=True
    )
    if not selected_logs:
        raise ReportInputError(f"broad impact handoff has zero posterior impact mass: {path}")
    normalized, position_mass, _ = normalized_log_weights(
        selected_logs, f"broad impact positions in {path}"
    )
    declared_impact_mass = finite_number(
        handoff.get("outcome_mass", {}).get("impact", {}).get(
            "posterior_normalized_mass"
        ),
        "declared impact posterior mass",
    )
    if not math.isclose(
        position_mass, declared_impact_mass, rel_tol=0.0, abs_tol=WEIGHT_TOLERANCE
    ):
        raise ReportInputError(f"impact outcome mass does not match particles: {path}")
    configured = integer(
        source_spec.get(
            "configured_particles", parent.get("configured_particle_count")
        ),
        f"configured parent particles for {path}",
    )
    return ParticleSource(
        family_id=family_id,
        seed=seed,
        logical_path=raw_path,
        path=path,
        source_format="broad_impact_json",
        latitude_deg=np.asarray(latitude, dtype=float),
        longitude_deg=np.asarray(longitude, dtype=float),
        weights=normalized,
        particle_ids=np.asarray(particle_ids, dtype=object),
        root_ids=np.asarray(roots, dtype=object),
        strata=np.asarray(strata, dtype=object),
        fuel_flow_scale=None,
        fuel_exhausted=None,
        configured_particles=configured,
        posterior_position_mass=position_mass,
        posterior_total_mass=total_mass,
        summary=summary,
        summary_logical_path=summary_logical,
        summary_path=summary_path,
        input_sha256=sha256(path),
        summary_sha256=summary_digest,
        source_metadata={},
    )


def required_object(value: Any, description: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReportInputError(f"{description} must be an object")
    return value


def load_parent_checkpoint_json_source(
    source_spec: dict[str, Any],
    spec_path: Path,
    family_id: str,
    semantics: str,
) -> ParticleSource:
    """Aggregate a terminal posterior once onto each exact 00:11 parent."""

    if semantics != "smoothed":
        raise ReportInputError(
            "a terminal-evidence-weighted parent checkpoint requires smoothed "
            "report semantics"
        )
    raw_path = source_spec.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise ReportInputError(f"missing source path for family {family_id}")
    path = resolve_path(spec_path, raw_path, "broad impact handoff")
    try:
        handoff = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ReportInputError(f"invalid broad impact JSON: {path}") from error
    if (
        not isinstance(handoff, dict)
        or handoff.get("schema_id") != BROAD_IMPACT_SCHEMA_ID
        or handoff.get("schema_version") != 1
    ):
        raise ReportInputError(f"unsupported broad impact handoff: {path}")
    parent_reference = required_object(
        handoff.get("parent"), f"broad impact parent provenance in {path}"
    )
    required_object(handoff.get("run"), f"broad impact run provenance in {path}")
    seed = integer(
        source_spec.get("seed", parent_reference.get("seed")), f"seed for {path}"
    )
    if integer(parent_reference.get("seed"), "impact parent seed") != seed:
        raise ReportInputError(f"broad impact parent seed mismatch: {path}")

    selection = source_spec.get("terminal_outcome_selection", "all_outcomes")
    if selection not in {"all_outcomes", "impact_only"}:
        raise ReportInputError(
            "terminal_outcome_selection must be all_outcomes or impact_only"
        )
    raw_parent_path = source_spec.get("parent_handoff")
    if not isinstance(raw_parent_path, str) or not raw_parent_path:
        raise ReportInputError(
            f"parent_checkpoint source requires an explicit parent_handoff: {path}"
        )
    parent_path = resolve_path(spec_path, raw_parent_path, "parent broad handoff")
    parent_digest = sha256(parent_path)
    expected_parent_digest = parent_reference.get("handoff_sha256")
    if (
        not isinstance(expected_parent_digest, str)
        or len(expected_parent_digest) != 64
        or any(character not in "0123456789abcdef" for character in expected_parent_digest)
    ):
        raise ReportInputError(f"broad impact parent hash is invalid: {path}")
    if parent_digest != expected_parent_digest:
        raise ReportInputError(
            "parent broad handoff SHA-256 mismatch: "
            f"expected {expected_parent_digest}, observed {parent_digest}: {parent_path}"
        )
    try:
        parent_handoff = json.loads(parent_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ReportInputError(f"invalid parent broad handoff JSON: {parent_path}") from error
    if not isinstance(parent_handoff, dict) or parent_handoff.get("schema_version") != 1:
        raise ReportInputError(f"unsupported parent broad handoff: {parent_path}")
    if integer(parent_reference.get("schema_version"), "impact parent schema") != 1:
        raise ReportInputError(f"broad impact parent schema mismatch: {path}")

    parent_run = required_object(
        parent_handoff.get("run"), f"parent broad run provenance in {parent_path}"
    )
    checkpoint = required_object(
        parent_handoff.get("checkpoint"), f"parent checkpoint in {parent_path}"
    )
    parent_particles = parent_handoff.get("particles")
    if not isinstance(parent_particles, list) or not parent_particles:
        raise ReportInputError(f"parent broad handoff has no particles: {parent_path}")
    if len(parent_particles) > MAX_PARTICLE_ROWS_PER_SOURCE:
        raise ReportInputError(
            f"parent broad handoff exceeds {MAX_PARTICLE_ROWS_PER_SOURCE} particles"
        )

    parent_semantics = conditioning_name(checkpoint.get("conditioning"))
    if parent_semantics is None:
        raise ReportInputError(f"parent checkpoint conditioning is invalid: {parent_path}")
    expected_parent_semantics = source_spec.get("parent_semantics")
    if (
        expected_parent_semantics is not None
        and expected_parent_semantics != parent_semantics
    ):
        raise ReportInputError(f"parent checkpoint semantics mismatch: {parent_path}")
    provenance_pairs = (
        (
            "model family",
            parent_run.get("model_family"),
            parent_reference.get("model_family"),
        ),
        (
            "run identity",
            parent_run.get("run_identity_sha256"),
            parent_reference.get("run_identity_sha256"),
        ),
        (
            "configuration",
            parent_run.get("config_sha256"),
            parent_reference.get("config_sha256"),
        ),
        (
            "input identities",
            parent_run.get("input_sha256"),
            parent_reference.get("input_sha256"),
        ),
        (
            "source epoch",
            parent_run.get("source_epoch_id"),
            parent_reference.get("source_epoch_id"),
        ),
        (
            "checkpoint identity",
            checkpoint.get("checkpoint_id"),
            parent_reference.get("checkpoint_id"),
        ),
        (
            "checkpoint conditioning",
            checkpoint.get("conditioning"),
            parent_reference.get("conditioning"),
        ),
    )
    for description, observed, expected in provenance_pairs:
        if observed != expected:
            raise ReportInputError(
                f"parent broad handoff {description} disagrees with impact provenance: "
                f"{parent_path}"
            )
    if integer(parent_run.get("seed"), "parent broad seed") != seed:
        raise ReportInputError(f"parent broad handoff seed mismatch: {parent_path}")
    configured = integer(
        parent_run.get("configured_particles"), "parent configured particle count"
    )
    if configured <= 0 or configured != integer(
        parent_reference.get("configured_particle_count"),
        "impact parent configured particle count",
    ):
        raise ReportInputError(
            f"parent configured particle count disagrees with impact provenance: {parent_path}"
        )
    if "configured_particles" in source_spec and integer(
        source_spec["configured_particles"], "source configured particle count"
    ) != configured:
        raise ReportInputError(
            f"source configured particle count disagrees with parent handoff: {parent_path}"
        )
    retained = integer(
        parent_reference.get("retained_particle_count"),
        "impact retained parent count",
    )
    if retained != len(parent_particles):
        raise ReportInputError(
            f"retained parent count disagrees with parent handoff: {parent_path}"
        )
    if checkpoint.get("state_epoch_id") != "m0011":
        raise ReportInputError(
            f"parent_checkpoint target requires the m0011 state epoch: {parent_path}"
        )
    referenced_checkpoint_time = finite_number(
        parent_reference.get("checkpoint_time_unix_s_utc"),
        "impact parent checkpoint time",
    )
    checkpoint_time = utc_posix_seconds(
        checkpoint.get("state_time_utc"), "parent checkpoint state_time_utc"
    )
    origin_time = utc_posix_seconds(
        parent_run.get("time_origin_utc"), "parent run time_origin_utc"
    )
    relative_checkpoint_time = finite_number(
        checkpoint.get("state_time"), "parent checkpoint state_time"
    )
    if (
        abs(referenced_checkpoint_time - M0011_TIME_UNIX_S_UTC) > 1.0e-6
        or abs(checkpoint_time - referenced_checkpoint_time) > 1.0e-6
        or abs(origin_time + relative_checkpoint_time - referenced_checkpoint_time)
        > 1.0e-6
    ):
        raise ReportInputError(
            f"parent checkpoint time is not the referenced 00:11 epoch: {parent_path}"
        )

    parent_by_identity: dict[str, dict[str, Any]] = {}
    parent_logs: list[float] = []
    for index, particle in enumerate(parent_particles):
        particle = required_object(
            particle, f"parent broad particle {index} in {parent_path}"
        )
        identity = required_object(
            particle.get("identity"), f"parent particle identity {index}"
        )
        if (
            identity.get("model_family") != parent_reference.get("model_family")
            or integer(identity.get("seed"), f"parent identity seed {index}") != seed
            or identity.get("checkpoint_id") != checkpoint.get("checkpoint_id")
        ):
            raise ReportInputError(
                f"parent particle identity disagrees with parent provenance: {parent_path}"
            )
        particle_number = integer(
            identity.get("particle"), f"parent particle number {index}"
        )
        if not 0 <= particle_number < configured:
            raise ReportInputError(f"parent particle number is out of range: {parent_path}")
        identity_key = canonical_identity(identity)
        if identity_key in parent_by_identity:
            raise ReportInputError(f"duplicate parent particle identity: {parent_path}")
        prior_root = required_object(
            particle.get("prior_root"), f"parent prior-root identity {index}"
        )
        if (
            prior_root.get("model_family") != parent_reference.get("model_family")
            or integer(prior_root.get("seed"), f"parent prior-root seed {index}")
            != seed
            or prior_root.get("source_epoch_id")
            != parent_reference.get("source_epoch_id")
            or canonical_identity(prior_root.get("stratum"))
            != canonical_identity(particle.get("stratum"))
        ):
            raise ReportInputError(
                f"parent prior-root identity disagrees with parent provenance: {parent_path}"
            )
        root_particle = integer(
            prior_root.get("initial_particle"), f"parent prior-root number {index}"
        )
        if not 0 <= root_particle < configured:
            raise ReportInputError(f"parent prior-root number is out of range: {parent_path}")
        log_weight = finite_number(
            particle.get("normalized_log_weight"), f"parent log weight {index}"
        )
        parent_logs.append(log_weight)
        powered_flight = required_object(
            particle.get("powered_flight"), f"parent powered-flight state {index}"
        )
        aircraft = required_object(
            powered_flight.get("aircraft"), f"parent aircraft state {index}"
        )
        position = required_object(
            aircraft.get("position"), f"parent WGS84 position {index}"
        )
        latitude = finite_number(position.get("latitude"), f"parent latitude {index}")
        longitude = finite_number(
            position.get("longitude"), f"parent longitude {index}"
        )
        if not -90.0 <= latitude <= 90.0 or not -180.0 <= longitude <= 180.0:
            raise ReportInputError(f"invalid parent WGS84 position {index}: {parent_path}")
        fuel = required_object(particle.get("fuel"), f"parent fuel state {index}")
        exhaustion = fuel.get("dual_engine_exhaustion_time")
        if exhaustion is not None:
            finite_number(exhaustion, f"parent dual-engine exhaustion time {index}")
        fuel_scale = finite_number(
            particle.get("fuel_flow_scale"), f"parent fuel-flow scale {index}"
        )
        if fuel_scale <= 0.0:
            raise ReportInputError(f"invalid parent fuel-flow scale {index}: {parent_path}")
        parent_by_identity[identity_key] = {
            "identity": identity,
            "prior_root": prior_root,
            "stratum": particle.get("stratum"),
            "normalized_log_weight": log_weight,
            "latitude": latitude,
            "longitude": longitude,
            "fuel_flow_scale": fuel_scale,
            "fuel_exhausted": float(exhaustion is not None),
        }
    normalized_log_weights(
        parent_logs,
        f"parent broad posterior in {parent_path}",
        require_unit_mass=True,
    )

    terminal_particles = handoff.get("particles")
    if not isinstance(terminal_particles, list) or not terminal_particles:
        raise ReportInputError(f"broad impact handoff has no particles: {path}")
    if len(terminal_particles) > MAX_PARTICLE_ROWS_PER_SOURCE:
        raise ReportInputError(
            f"broad impact handoff exceeds {MAX_PARTICLE_ROWS_PER_SOURCE} particles"
        )
    terminal_identities: set[str] = set()
    referenced_parents: set[str] = set()
    all_logs: list[float] = []
    impact_logs: list[float] = []
    selected: list[tuple[str, float]] = []
    positive_terminal_rows = 0
    selected_positive_rows = 0
    for index, particle in enumerate(terminal_particles):
        particle = required_object(particle, f"terminal particle {index} in {path}")
        identity = required_object(
            particle.get("identity"), f"terminal particle identity {index}"
        )
        parent_identity = required_object(
            identity.get("parent"), f"terminal parent identity {index}"
        )
        prior_root = required_object(
            identity.get("prior_root"), f"terminal prior-root identity {index}"
        )
        required_object(
            identity.get("terminal_draw"), f"terminal draw identity {index}"
        )
        terminal_identity_key = canonical_identity(identity)
        if terminal_identity_key in terminal_identities:
            raise ReportInputError(f"duplicate terminal particle identity: {path}")
        terminal_identities.add(terminal_identity_key)
        parent_identity_key = canonical_identity(parent_identity)
        parent_record = parent_by_identity.get(parent_identity_key)
        if parent_record is None:
            raise ReportInputError(
                f"terminal particle references an unknown parent identity: {path}"
            )
        referenced_parents.add(parent_identity_key)
        if (
            canonical_identity(prior_root)
            != canonical_identity(parent_record["prior_root"])
            or canonical_identity(identity.get("stratum"))
            != canonical_identity(parent_record["stratum"])
        ):
            raise ReportInputError(
                f"terminal genealogy disagrees with its parent particle: {path}"
            )
        upstream_log_weight = finite_number(
            particle.get("upstream_normalized_log_weight"),
            f"terminal upstream log weight {index}",
        )
        if upstream_log_weight != parent_record["normalized_log_weight"]:
            raise ReportInputError(
                f"terminal upstream weight disagrees with its exact parent: {path}"
            )
        outcome_name = terminal_outcome_name(particle.get("outcome"))
        if outcome_name not in TERMINAL_OUTCOMES:
            raise ReportInputError(f"invalid terminal outcome {index}: {path}")
        is_impact = outcome_name == "impact"
        if is_impact != isinstance(particle.get("impact"), dict):
            raise ReportInputError(
                f"terminal outcome/impact payload mismatch at row {index}: {path}"
            )
        raw_log_weight = particle.get("posterior_normalized_log_weight")
        if raw_log_weight is None:
            continue
        log_weight = finite_number(
            raw_log_weight, f"terminal posterior log weight {index}"
        )
        if log_weight > WEIGHT_TOLERANCE:
            raise ReportInputError(f"positive normalized terminal log weight in {path}")
        positive_terminal_rows += 1
        all_logs.append(log_weight)
        if is_impact:
            impact_logs.append(log_weight)
        if selection == "all_outcomes" or is_impact:
            selected.append((parent_identity_key, log_weight))
            selected_positive_rows += 1
    if referenced_parents != set(parent_by_identity):
        missing_count = len(set(parent_by_identity) - referenced_parents)
        raise ReportInputError(
            f"terminal handoff omits {missing_count} retained parent identities: {path}"
        )
    _, total_mass, _ = normalized_log_weights(
        all_logs, f"broad terminal posterior in {path}", require_unit_mass=True
    )
    if impact_logs:
        _, calculated_impact_mass, calculated_impact_log_mass = normalized_log_weights(
            impact_logs, f"impact outcomes in {path}"
        )
    else:
        calculated_impact_mass = 0.0
        calculated_impact_log_mass = None
    outcome_mass = required_object(handoff.get("outcome_mass"), f"outcome mass in {path}")
    impact_mass_record = required_object(
        outcome_mass.get("impact"), f"impact outcome mass in {path}"
    )
    declared_impact_mass = finite_number(
        impact_mass_record.get("posterior_normalized_mass"),
        f"declared impact posterior mass in {path}",
    )
    if not math.isclose(
        calculated_impact_mass,
        declared_impact_mass,
        rel_tol=0.0,
        abs_tol=WEIGHT_TOLERANCE,
    ):
        raise ReportInputError(f"impact outcome mass does not match particles: {path}")
    selected_logs = [log_weight for _, log_weight in selected]
    normalized_selected, selection_mass, selection_log_mass = normalized_log_weights(
        selected_logs,
        f"{selection} terminal posterior selection in {path}",
    )
    if selection_mass <= 0.0:
        raise ReportInputError(
            f"{selection} conditioning mass is not representable as positive: {path}"
        )
    if selection == "all_outcomes" and not math.isclose(
        selection_mass, 1.0, rel_tol=0.0, abs_tol=WEIGHT_TOLERANCE
    ):
        raise ReportInputError(f"all-outcomes selection does not retain unit mass: {path}")

    aggregated: dict[str, float] = {}
    for (parent_identity_key, _), normalized_weight in zip(
        selected, normalized_selected
    ):
        aggregated[parent_identity_key] = (
            aggregated.get(parent_identity_key, 0.0) + float(normalized_weight)
        )
    selected_parent_keys = sorted(aggregated)
    latitude = np.asarray(
        [parent_by_identity[key]["latitude"] for key in selected_parent_keys],
        dtype=float,
    )
    longitude = np.asarray(
        [parent_by_identity[key]["longitude"] for key in selected_parent_keys],
        dtype=float,
    )
    weights = np.asarray([aggregated[key] for key in selected_parent_keys], dtype=float)
    weights /= float(np.sum(weights))
    particle_ids = np.asarray(selected_parent_keys, dtype=object)
    roots = np.asarray(
        [
            canonical_identity(parent_by_identity[key]["prior_root"])
            for key in selected_parent_keys
        ],
        dtype=object,
    )
    strata = np.asarray(
        [
            canonical_identity(parent_by_identity[key]["stratum"])
            for key in selected_parent_keys
        ],
        dtype=object,
    )
    fuel_scales = np.asarray(
        [parent_by_identity[key]["fuel_flow_scale"] for key in selected_parent_keys],
        dtype=float,
    )
    fuel_exhausted = np.asarray(
        [parent_by_identity[key]["fuel_exhausted"] for key in selected_parent_keys],
        dtype=float,
    )
    summary, summary_logical, summary_path, summary_digest = load_summary(
        source_spec, spec_path, family_id, seed
    )
    selection_description = (
        "future-evidence-smoothed parent state; all terminal outcomes retained"
        if selection == "all_outcomes"
        else "future-evidence-smoothed parent state conditional on terminal impact"
    )
    source_metadata = {
        "spatial_target": "parent_checkpoint",
        "parent_handoff": {
            "logical_path": raw_parent_path,
            "sha256": parent_digest,
            "required_sha256": expected_parent_digest,
        },
        "parent_checkpoint": {
            "checkpoint_id": checkpoint.get("checkpoint_id"),
            "state_epoch_id": checkpoint.get("state_epoch_id"),
            "state_time_utc": checkpoint.get("state_time_utc"),
            "input_conditioning": checkpoint.get("conditioning"),
            "input_semantics": parent_semantics,
        },
        "rendered_semantics": "smoothed",
        "rendered_conditioning": selection_description,
        "terminal_outcome_selection": selection,
        "terminal_conditioning_mass": selection_mass,
        "terminal_conditioning_log_mass": selection_log_mass,
        "unconditional_terminal_impact_mass": calculated_impact_mass,
        "unconditional_terminal_impact_log_mass": calculated_impact_log_mass,
        "terminal_rows": len(terminal_particles),
        "positive_terminal_rows": positive_terminal_rows,
        "selected_positive_terminal_rows": selected_positive_rows,
        "retained_parent_rows": len(parent_particles),
        "positive_aggregated_parent_rows": len(selected_parent_keys),
        "aggregation": (
            "sum selected normalized terminal descendant weights by exact parent "
            "identity before spatial rendering; one plotted row per positive parent"
        ),
        "terminal_family": handoff.get("terminal_family"),
        "r600_evidence": handoff.get("r600_evidence"),
        "terminal_evidence_model": handoff.get("terminal_evidence_model"),
    }
    return ParticleSource(
        family_id=family_id,
        seed=seed,
        logical_path=raw_path,
        path=path,
        source_format="broad_impact_parent_checkpoint_json",
        latitude_deg=latitude,
        longitude_deg=longitude,
        weights=weights,
        particle_ids=particle_ids,
        root_ids=roots,
        strata=strata,
        fuel_flow_scale=fuel_scales,
        fuel_exhausted=fuel_exhausted,
        configured_particles=configured,
        posterior_position_mass=selection_mass,
        posterior_total_mass=total_mass,
        summary=summary,
        summary_logical_path=summary_logical,
        summary_path=summary_path,
        input_sha256=sha256(path),
        summary_sha256=summary_digest,
        source_metadata=source_metadata,
    )


def load_families(
    spec: dict[str, Any], spec_path: Path
) -> list[Family]:
    result: list[Family] = []
    seen_families: set[str] = set()
    for family_index, family_spec in enumerate(spec["families"]):
        if not isinstance(family_spec, dict):
            raise ReportInputError("family entry must be an object")
        family_id = family_spec.get("id")
        label = family_spec.get("label")
        if not isinstance(family_id, str) or not family_id.strip() or family_id in seen_families:
            raise ReportInputError("family identifiers must be unique and non-empty")
        if not isinstance(label, str) or not label.strip():
            raise ReportInputError(f"family {family_id} lacks a label")
        seen_families.add(family_id)
        color = family_spec.get("color", PALETTE[family_index])
        if (
            not isinstance(color, str)
            or len(color) != 7
            or color[0] != "#"
            or any(character not in "0123456789abcdefABCDEF" for character in color[1:])
        ):
            raise ReportInputError(f"invalid color for family {family_id}")
        source_specs = family_spec.get("sources")
        if not isinstance(source_specs, list) or not source_specs:
            raise ReportInputError(f"family {family_id} has no sources")
        sources: list[ParticleSource] = []
        seen_seeds: set[int] = set()
        for source_spec in source_specs:
            if not isinstance(source_spec, dict):
                raise ReportInputError(f"source in {family_id} is not an object")
            raw_format = source_spec.get("format", "auto")
            raw_path = source_spec.get("path", "")
            if raw_format == "auto":
                raw_format = "broad_impact_json" if str(raw_path).lower().endswith(".json") else "csv"
            if raw_format == "csv":
                source = load_csv_source(
                    source_spec,
                    spec_path,
                    family_id,
                    spec["posterior_semantics"],
                )
            elif raw_format == "broad_impact_json":
                spatial_target = source_spec.get("spatial_target", "impact_location")
                if spatial_target == "parent_checkpoint":
                    source = load_parent_checkpoint_json_source(
                        source_spec,
                        spec_path,
                        family_id,
                        spec["posterior_semantics"],
                    )
                elif spatial_target == "impact_location":
                    source = load_impact_json_source(
                        source_spec,
                        spec_path,
                        family_id,
                        spec["posterior_semantics"],
                    )
                else:
                    raise ReportInputError(
                        "broad impact spatial_target must be impact_location or "
                        "parent_checkpoint"
                    )
            else:
                raise ReportInputError(f"unsupported source format {raw_format!r}")
            if source.seed in seen_seeds:
                raise ReportInputError(
                    f"family {family_id} repeats numerical seed {source.seed}"
                )
            seen_seeds.add(source.seed)
            sources.append(source)
        sources.sort(key=lambda item: item.seed)
        result.append(Family(family_id, label, color, sources))
    return result


def load_arc_projector(
    spec: dict[str, Any], spec_path: Path, grid: SpatialGrid
) -> tuple[ArcProjector | None, dict[str, Any] | None]:
    arc = spec.get("along_arc")
    if arc is None:
        return None, None
    if not isinstance(arc, dict):
        raise ReportInputError("along_arc must be an object")
    raw_path = arc.get("path")
    label = arc.get("label")
    if not isinstance(raw_path, str) or not raw_path or not isinstance(label, str) or not label:
        raise ReportInputError("along_arc needs non-empty path and label")
    path = resolve_path(spec_path, raw_path, "along-arc coordinate table")
    with path.open("r", encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None:
            raise ReportInputError(f"along-arc table has no header: {path}")
        lat_name = column_name(
            reader.fieldnames,
            ("latitude_deg", "latitude"),
            "arc latitude",
        )
        lon_name = column_name(
            reader.fieldnames,
            ("longitude_deg", "longitude"),
            "arc longitude",
        )
        value_name = optional_column(
            reader.fieldnames,
            ("along_arc_km", "along_km", "distance_km", "along_arc_nm", "distance_nm"),
        )
        latitude: list[float] = []
        longitude: list[float] = []
        values: list[float] = []
        for index, row in enumerate(reader):
            latitude.append(finite_number(row[lat_name], f"arc latitude row {index}"))
            longitude.append(finite_number(row[lon_name], f"arc longitude row {index}"))
            if value_name:
                value = finite_number(row[value_name], f"arc coordinate row {index}")
                if value_name.endswith("_nm"):
                    value *= KM_PER_NM
                values.append(value)
    if len(latitude) < 2:
        raise ReportInputError("along-arc table needs at least two points")
    east, north = azimuthal_equidistant(
        np.asarray(latitude),
        np.asarray(longitude),
        grid.origin_latitude_deg,
        grid.origin_longitude_deg,
    )
    points = np.column_stack((east, north))
    if values:
        coordinates = np.asarray(values, dtype=float)
        differences = np.diff(coordinates)
        if not (np.all(differences > 0.0) or np.all(differences < 0.0)):
            raise ReportInputError("supplied along-arc coordinates must be strictly monotone")
    else:
        lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
        if np.any(lengths <= 0.0):
            raise ReportInputError("along-arc table repeats a point")
        coordinates = np.concatenate(([0.0], np.cumsum(lengths)))
    projector = ArcProjector(points, coordinates, label, cKDTree(points))
    return projector, {
        "logical_path": raw_path,
        "sha256": sha256(path),
        "label": label,
        "coordinate_source": "provided" if values else "cumulative projected polyline length",
    }


def project_sources(
    families: list[Family], grid: SpatialGrid, arc: ArcProjector | None
) -> None:
    for family in families:
        for source in family.sources:
            east, north = azimuthal_equidistant(
                source.latitude_deg,
                source.longitude_deg,
                grid.origin_latitude_deg,
                grid.origin_longitude_deg,
            )
            along, cross = rotate_local_axes(east, north, grid.along_axis_bearing_deg)
            source.east_km = east
            source.north_km = north
            source.along_km = along
            source.cross_km = cross
            if arc is None:
                source.marginal_along_km = along
                source.endpoint_coordinate_km = north
            else:
                projected_arc = arc.project(east, north)
                source.marginal_along_km = projected_arc
                source.endpoint_coordinate_km = projected_arc


def surface(
    along_km: np.ndarray,
    cross_km: np.ndarray,
    weights: np.ndarray,
    grid: SpatialGrid,
) -> dict[str, Any]:
    """Fixed-bandwidth display mass on the fixed metric grid.

    The histogram is padded by a fixed multiple of the physical bandwidth
    before convolution.  The cropped grid is deliberately not renormalized;
    HPD masses therefore cannot silently ignore posterior mass beyond the
    declared plotting window.
    """

    along_edges = grid.along_edges
    cross_edges = grid.cross_edges
    padding_cells = int(
        math.ceil(grid.kernel_truncation_sigma * grid.bandwidth_km / grid.cell_size_km)
    ) + 1
    expanded_along = np.arange(
        along_edges[0] - padding_cells * grid.cell_size_km,
        along_edges[-1] + (padding_cells + 0.5) * grid.cell_size_km,
        grid.cell_size_km,
    )
    expanded_cross = np.arange(
        cross_edges[0] - padding_cells * grid.cell_size_km,
        cross_edges[-1] + (padding_cells + 0.5) * grid.cell_size_km,
        grid.cell_size_km,
    )
    histogram, _, _ = np.histogram2d(
        along_km,
        cross_km,
        bins=(expanded_along, expanded_cross),
        weights=weights,
    )
    sigma_cells = grid.bandwidth_km / grid.cell_size_km
    smoothed = gaussian_filter(
        histogram,
        sigma=(sigma_cells, sigma_cells),
        mode="constant",
        cval=0.0,
        truncate=grid.kernel_truncation_sigma,
    )
    nx = len(along_edges) - 1
    ny = len(cross_edges) - 1
    cropped = smoothed[
        padding_cells : padding_cells + nx,
        padding_cells : padding_cells + ny,
    ]
    inside = (
        (along_km >= grid.along_min_km)
        & (along_km <= grid.along_max_km)
        & (cross_km >= grid.cross_min_km)
        & (cross_km <= grid.cross_max_km)
    )
    expanded_inside = (
        (along_km >= expanded_along[0])
        & (along_km <= expanded_along[-1])
        & (cross_km >= expanded_cross[0])
        & (cross_km <= expanded_cross[-1])
    )
    outside_mass = float(np.sum(weights[~inside]))
    ignored_mass = float(np.sum(weights[~expanded_inside]))
    thresholds: dict[str, float | None] = {}
    achieved: dict[str, float | None] = {}
    areas: dict[str, float | None] = {}
    ordered = np.sort(cropped.ravel())[::-1]
    cumulative = np.cumsum(ordered)
    for probability in HPD_MASSES:
        key = f"{probability:.2f}"
        if cumulative.size == 0 or cumulative[-1] + 1.0e-12 < probability:
            thresholds[key] = None
            achieved[key] = None
            areas[key] = None
            continue
        index = min(
            int(np.searchsorted(cumulative, probability, side="left")),
            len(ordered) - 1,
        )
        threshold = float(ordered[index])
        mask = cropped >= threshold
        thresholds[key] = threshold
        achieved[key] = float(np.sum(cropped[mask]))
        areas[key] = float(np.count_nonzero(mask) * grid.cell_size_km**2)
    return {
        "mass": cropped,
        "along_centers_km": (along_edges[:-1] + along_edges[1:]) / 2.0,
        "cross_centers_km": (cross_edges[:-1] + cross_edges[1:]) / 2.0,
        "raw_mass_outside_plot": outside_mass,
        "raw_mass_beyond_kernel_padding": ignored_mass,
        "display_smoothed_mass_inside_plot": float(np.sum(cropped)),
        "thresholds": thresholds,
        "achieved_masses": achieved,
        "areas_km2": areas,
        "bandwidth_km": grid.bandwidth_km,
        "cell_size_km": grid.cell_size_km,
        "padding_cells": padding_cells,
    }


def weighted_quantile(
    values: np.ndarray, weights: np.ndarray, probabilities: Iterable[float]
) -> np.ndarray:
    order = np.argsort(values, kind="stable")
    ordered_values = values[order]
    ordered_weights = weights[order]
    cumulative = np.cumsum(ordered_weights)
    cumulative /= cumulative[-1]
    probabilities_array = np.asarray(tuple(probabilities), dtype=float)
    indices = np.searchsorted(cumulative, probabilities_array, side="left")
    return ordered_values[np.minimum(indices, len(ordered_values) - 1)]


def grouped_masses(ids: np.ndarray, weights: np.ndarray) -> np.ndarray:
    order = np.argsort(ids.astype(str), kind="stable")
    ordered_ids = ids[order].astype(str)
    ordered_weights = weights[order]
    first = np.concatenate(([True], ordered_ids[1:] != ordered_ids[:-1]))
    starts = np.flatnonzero(first)
    return np.add.reduceat(ordered_weights, starts)


def effective_sample_size(weights: np.ndarray) -> float:
    denominator = float(np.square(weights).sum())
    return 1.0 / denominator if denominator > 0.0 else 0.0


def source_metrics(source: ParticleSource) -> dict[str, Any]:
    particle_masses = (
        grouped_masses(source.particle_ids, source.weights)
        if source.particle_ids is not None
        else source.weights
    )
    result: dict[str, Any] = {
        "configured_particles": source.configured_particles,
        "positive_position_rows": len(source.weights),
        "posterior_total_mass": source.posterior_total_mass,
        "posterior_position_mass_before_conditioning": source.posterior_position_mass,
        "particle_ess": effective_sample_size(particle_masses),
        "row_ess": effective_sample_size(source.weights),
        "root_diagnostics_available": source.root_ids is not None,
        "stratum_diagnostics_available": source.strata is not None,
        "mass_outside_plot": None,
    }
    if source.root_ids is not None:
        root_masses = grouped_masses(source.root_ids, source.weights)
        result.update(
            {
                "root_ess": effective_sample_size(root_masses),
                "top_root_mass": float(np.max(root_masses)),
                "positive_roots": len(root_masses),
                "roots_over_1e-6": int(np.count_nonzero(root_masses > ROOT_MASS_THRESHOLDS[0])),
                "roots_over_1e-3": int(np.count_nonzero(root_masses > ROOT_MASS_THRESHOLDS[1])),
            }
        )
    else:
        result.update(
            {
                "root_ess": None,
                "top_root_mass": None,
                "positive_roots": None,
                "roots_over_1e-6": None,
                "roots_over_1e-3": None,
            }
        )
    stratum_metrics: list[dict[str, Any]] = []
    if source.strata is not None:
        stratum_text = source.strata.astype(str)
        for stratum in sorted(set(stratum_text)):
            mask = stratum_text == stratum
            mass = float(source.weights[mask].sum())
            conditional_weights = source.weights[mask] / mass
            conditional_particles = (
                grouped_masses(source.particle_ids[mask], conditional_weights)
                if source.particle_ids is not None
                else conditional_weights
            )
            conditional_roots = (
                grouped_masses(source.root_ids[mask], conditional_weights)
                if source.root_ids is not None
                else None
            )
            stratum_metrics.append(
                {
                    "stratum": stratum,
                    "posterior_mass": mass,
                    "particle_ess": effective_sample_size(conditional_particles),
                    "root_ess": (
                        effective_sample_size(conditional_roots)
                        if conditional_roots is not None
                        else None
                    ),
                }
            )
    result["strata"] = stratum_metrics
    if source.fuel_flow_scale is not None:
        result["mean_fuel_flow_scale"] = float(
            np.dot(source.weights, source.fuel_flow_scale)
        )
    else:
        result["mean_fuel_flow_scale"] = summary_value(
            source.summary,
            ("mean_fuel_flow_scale", "summary.mean_fuel_flow_scale"),
            "summary mean fuel-flow scale",
        )
    if source.fuel_exhausted is not None:
        result["fuel_exhaustion_mass"] = float(
            np.dot(source.weights, source.fuel_exhausted)
        )
    else:
        result["fuel_exhaustion_mass"] = summary_value(
            source.summary,
            (
                "fuel_exhausted_by_checkpoint_mass",
                "summary.fuel_exhausted_by_checkpoint_mass",
            ),
            "summary fuel exhaustion mass",
        )
    result["log_evidence"] = summary_value(
        source.summary,
        ("log_evidence", "summary.log_evidence"),
        "summary log evidence",
    )
    assert source.along_km is not None
    assert source.cross_km is not None
    assert source.north_km is not None
    assert source.endpoint_coordinate_km is not None
    result["mean_along_km"] = float(np.dot(source.weights, source.along_km))
    result["mean_cross_km"] = float(np.dot(source.weights, source.cross_km))
    result["mean_north_km"] = float(np.dot(source.weights, source.north_km))
    endpoints = weighted_quantile(
        source.endpoint_coordinate_km, source.weights, (0.025, 0.975)
    )
    result["endpoint_equal_tail_95_km"] = [float(endpoints[0]), float(endpoints[1])]
    return result


def criterion(
    scope: str,
    name: str,
    comparison: str,
    limit: float,
    observed: float | None,
    detail: str = "",
) -> dict[str, Any]:
    if observed is None:
        status = "unassessed"
    elif comparison == "minimum":
        status = "passed" if observed >= limit - 1.0e-12 else "failed"
    elif comparison == "maximum":
        status = "passed" if observed <= limit + 1.0e-12 else "failed"
    else:
        raise AssertionError(comparison)
    return {
        "scope": scope,
        "criterion": name,
        "comparison": comparison,
        "limit": limit,
        "observed": observed,
        "status": status,
        "detail": detail,
    }


def pairwise(values: list[Any]) -> Iterable[tuple[Any, Any]]:
    for first in range(len(values)):
        for second in range(first + 1, len(values)):
            yield values[first], values[second]


def total_variation(first: np.ndarray, second: np.ndarray) -> float:
    first_outside = max(0.0, 1.0 - float(first.sum()))
    second_outside = max(0.0, 1.0 - float(second.sum()))
    return 0.5 * (
        float(np.abs(first - second).sum()) + abs(first_outside - second_outside)
    )


def assess_numerical_support(
    families: list[Family],
    surfaces: dict[tuple[str, int | None], dict[str, Any]],
    standard_name: str,
    endpoint_coordinate_label: str,
) -> tuple[dict[str, Any], dict[tuple[str, int], dict[str, Any]]]:
    standard = NUMERICAL_STANDARDS[standard_name]
    criteria: list[dict[str, Any]] = []
    metrics: dict[tuple[str, int], dict[str, Any]] = {}
    cross_seed: dict[str, Any] = {}
    for family in families:
        for source in family.sources:
            scope = f"{family.family_id}/seed-{source.seed}"
            item = source_metrics(source)
            source_surface = surfaces[(family.family_id, source.seed)]
            item["mass_outside_plot"] = source_surface["raw_mass_outside_plot"]
            item["display_smoothed_mass_inside_plot"] = source_surface[
                "display_smoothed_mass_inside_plot"
            ]
            metrics[(family.family_id, source.seed)] = item
            particle_limit = max(
                standard["minimum_particle_ess"],
                standard["minimum_particle_ess_fraction"]
                * source.configured_particles,
            )
            criteria.append(
                criterion(
                    scope,
                    "final particle ESS",
                    "minimum",
                    particle_limit,
                    item["particle_ess"],
                    "parent-particle masses are aggregated when terminal draws are present",
                )
            )
            criteria.append(
                criterion(
                    scope,
                    "final prior-root ESS",
                    "minimum",
                    standard["minimum_root_ess"],
                    item["root_ess"],
                )
            )
            criteria.append(
                criterion(
                    scope,
                    "largest prior-root mass",
                    "maximum",
                    standard["maximum_root_mass"],
                    item["top_root_mass"],
                )
            )
            eligible_strata = [
                stratum
                for stratum in item["strata"]
                if stratum["posterior_mass"]
                >= standard["minimum_stratum_mass_for_check"] - 1.0e-12
            ]
            if source.strata is None:
                criteria.append(
                    criterion(
                        scope,
                        "stratum-conditional numerical support",
                        "minimum",
                        1.0,
                        None,
                        "stratum identity is unavailable",
                    )
                )
            for stratum in eligible_strata:
                stratum_scope = f"{scope}/stratum-{stratum['stratum']}"
                criteria.append(
                    criterion(
                        stratum_scope,
                        "conditional particle ESS at >=1% stratum mass",
                        "minimum",
                        standard["minimum_stratum_particle_ess"],
                        stratum["particle_ess"],
                        f"stratum posterior mass {stratum['posterior_mass']:.9g}",
                    )
                )
                criteria.append(
                    criterion(
                        stratum_scope,
                        "conditional prior-root ESS at >=1% stratum mass",
                        "minimum",
                        standard["minimum_stratum_root_ess"],
                        stratum["root_ess"],
                        f"stratum posterior mass {stratum['posterior_mass']:.9g}",
                    )
                )

        family_metrics = [metrics[(family.family_id, source.seed)] for source in family.sources]
        family_surfaces = [
            surfaces[(family.family_id, source.seed)]["mass"] for source in family.sources
        ]
        tv_values = [total_variation(a, b) for a, b in pairwise(family_surfaces)]
        mean_shifts = [
            math.hypot(
                first["mean_along_km"] - second["mean_along_km"],
                first["mean_cross_km"] - second["mean_cross_km"],
            )
            / KM_PER_NM
            for first, second in pairwise(family_metrics)
        ]
        endpoint_shifts = [
            max(
                abs(first["endpoint_equal_tail_95_km"][0] - second["endpoint_equal_tail_95_km"][0]),
                abs(first["endpoint_equal_tail_95_km"][1] - second["endpoint_equal_tail_95_km"][1]),
            )
            / KM_PER_NM
            for first, second in pairwise(family_metrics)
        ]
        log_evidence = [item["log_evidence"] for item in family_metrics]
        fuel_mean = [item["mean_fuel_flow_scale"] for item in family_metrics]
        exhaustion_mass = [item["fuel_exhaustion_mass"] for item in family_metrics]

        def complete(values: list[float | None]) -> list[float] | None:
            return None if len(values) < 2 or any(value is None for value in values) else [float(value) for value in values]

        logs = complete(log_evidence)
        fuels = complete(fuel_mean)
        exhaustion = complete(exhaustion_mass)
        observed = {
            "seed_count": len(family.sources),
            "pairwise_fixed_grid_tv": tv_values,
            "median_fixed_grid_tv": float(np.median(tv_values)) if tv_values else None,
            "maximum_fixed_grid_tv": max(tv_values) if tv_values else None,
            "pairwise_mean_shift_nm": mean_shifts,
            "maximum_mean_shift_nm": max(mean_shifts) if mean_shifts else None,
            "pairwise_equal_tail_95_endpoint_shift_nm": endpoint_shifts,
            "maximum_equal_tail_95_endpoint_shift_nm": (
                max(endpoint_shifts) if endpoint_shifts else None
            ),
            "endpoint_coordinate": endpoint_coordinate_label,
            "log_evidence_sd": (
                float(np.std(logs, ddof=1)) if logs is not None else None
            ),
            "log_evidence_range": (
                max(logs) - min(logs) if logs is not None else None
            ),
            "fuel_mean_delta": (
                max(fuels) - min(fuels) if fuels is not None else None
            ),
            "fuel_exhaustion_mass_delta": (
                max(exhaustion) - min(exhaustion) if exhaustion is not None else None
            ),
            "tv_definition": (
                "half L1 distance on the fixed-bandwidth fixed metric grid, with all "
                "smoothed mass outside the plot represented by one overflow cell"
            ),
        }
        cross_seed[family.family_id] = observed
        scope = f"{family.family_id}/across-seeds"
        criteria.extend(
            [
                criterion(
                    scope,
                    "median pairwise fixed-grid total variation",
                    "maximum",
                    standard["maximum_seed_tv_median"],
                    observed["median_fixed_grid_tv"],
                ),
                criterion(
                    scope,
                    "maximum pairwise fixed-grid total variation",
                    "maximum",
                    standard["maximum_seed_tv"],
                    observed["maximum_fixed_grid_tv"],
                ),
                criterion(
                    scope,
                    "maximum endpoint mean shift (NM)",
                    "maximum",
                    standard["maximum_seed_mean_shift_nm"],
                    observed["maximum_mean_shift_nm"],
                ),
                criterion(
                    scope,
                    "maximum raw equal-tail 95% endpoint shift (NM)",
                    "maximum",
                    standard["maximum_seed_95_endpoint_shift_nm"],
                    observed["maximum_equal_tail_95_endpoint_shift_nm"],
                    endpoint_coordinate_label,
                ),
                criterion(
                    scope,
                    "log-evidence sample SD (nats)",
                    "maximum",
                    standard["maximum_log_evidence_sd"],
                    observed["log_evidence_sd"],
                ),
                criterion(
                    scope,
                    "log-evidence range (nats)",
                    "maximum",
                    standard["maximum_log_evidence_range"],
                    observed["log_evidence_range"],
                ),
                criterion(
                    scope,
                    "fuel-flow mean range",
                    "maximum",
                    standard["maximum_fuel_mean_delta"],
                    observed["fuel_mean_delta"],
                ),
                criterion(
                    scope,
                    "fuel-exhaustion mass range",
                    "maximum",
                    standard["maximum_fuel_exhaustion_mass_delta"],
                    observed["fuel_exhaustion_mass_delta"],
                ),
            ]
        )
    failed = sum(item["status"] == "failed" for item in criteria)
    unassessed = sum(item["status"] == "unassessed" for item in criteria)
    status = "failed" if failed else "unassessed" if unassessed else "passed"
    assessment = {
        "standard": standard_name,
        "thresholds": standard,
        "status": status,
        "publication_eligible": status == "passed",
        "failed_criteria": failed,
        "unassessed_criteria": unassessed,
        "criteria": criteria,
        "across_seed_metrics": cross_seed,
    }
    return assessment, metrics


def pooled_arrays(family: Family, attribute: str) -> tuple[np.ndarray, np.ndarray]:
    count = len(family.sources)
    values = np.concatenate([getattr(source, attribute) for source in family.sources])
    weights = np.concatenate([source.weights / count for source in family.sources])
    return values, weights


def build_surfaces(
    families: list[Family], grid: SpatialGrid
) -> dict[tuple[str, int | None], dict[str, Any]]:
    result: dict[tuple[str, int | None], dict[str, Any]] = {}
    for family in families:
        for source in family.sources:
            assert source.along_km is not None and source.cross_km is not None
            result[(family.family_id, source.seed)] = surface(
                source.along_km, source.cross_km, source.weights, grid
            )
        along, weights = pooled_arrays(family, "along_km")
        cross, cross_weights = pooled_arrays(family, "cross_km")
        if not np.array_equal(weights, cross_weights):
            raise AssertionError("pooled coordinates lost aligned weights")
        result[(family.family_id, None)] = surface(along, cross, weights, grid)
    return result


def load_land(
    spec: dict[str, Any], spec_path: Path, grid: SpatialGrid
) -> tuple[list[np.ndarray], dict[str, Any] | None]:
    raw = spec.get("land_geojson")
    if raw is None:
        return [], None
    if not isinstance(raw, str) or not raw:
        raise ReportInputError("land_geojson must be a path")
    path = resolve_path(spec_path, raw, "land GeoJSON")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ReportInputError(f"invalid land GeoJSON: {path}") from error
    polygons: list[np.ndarray] = []
    for feature in value.get("features", []):
        geometry = feature.get("geometry", {})
        coordinates = geometry.get("coordinates", [])
        if geometry.get("type") == "Polygon":
            coordinates = [coordinates]
        elif geometry.get("type") != "MultiPolygon":
            continue
        for polygon in coordinates:
            if not polygon or len(polygon[0]) < 3:
                continue
            ring = np.asarray(polygon[0], dtype=float)
            east, north = azimuthal_equidistant(
                ring[:, 1],
                ring[:, 0],
                grid.origin_latitude_deg,
                grid.origin_longitude_deg,
            )
            along, cross = rotate_local_axes(east, north, grid.along_axis_bearing_deg)
            points = np.column_stack((along, cross))
            jumps = np.linalg.norm(np.diff(points, axis=0), axis=1)
            if len(jumps) and float(np.max(jumps)) > 5000.0:
                continue
            polygons.append(points)
    return polygons, {"logical_path": raw, "sha256": sha256(path)}


def add_land(ax: plt.Axes, polygons: list[np.ndarray], grid: SpatialGrid) -> None:
    for points in polygons:
        if (
            points[:, 0].max() < grid.along_min_km
            or points[:, 0].min() > grid.along_max_km
            or points[:, 1].max() < grid.cross_min_km
            or points[:, 1].min() > grid.cross_max_km
        ):
            continue
        ax.add_patch(
            Polygon(
                points,
                closed=True,
                facecolor="#f2f1ec",
                edgecolor="#8b9298",
                linewidth=0.45,
                zorder=0,
            )
        )


def plot_hpd(
    ax: plt.Axes,
    rendered_surface: dict[str, Any],
    color: str,
    filled: bool,
    linewidth_scale: float = 1.0,
    linestyle: Any = "solid",
    alpha_scale: float = 1.0,
) -> None:
    mass = rendered_surface["mass"].T
    x = rendered_surface["along_centers_km"]
    y = rendered_surface["cross_centers_km"]
    for probability, alpha, linewidth in (
        (0.99, 0.10, 0.85),
        (0.95, 0.16, 1.2),
        (0.50, 0.25, 1.65),
    ):
        threshold = rendered_surface["thresholds"][f"{probability:.2f}"]
        if threshold is None or threshold <= 0.0:
            continue
        mask = (mass >= threshold).astype(float)
        if filled:
            ax.contourf(
                x,
                y,
                mask,
                levels=(0.5, 1.5),
                colors=(color,),
                alpha=alpha * alpha_scale,
                zorder=2,
            )
        ax.contour(
            x,
            y,
            mass,
            levels=(threshold,),
            colors=(color,),
            linewidths=linewidth * linewidth_scale,
            linestyles=linestyle,
            alpha=min(1.0, 0.88 * alpha_scale),
            zorder=3,
        )


def raw_histogram(values: np.ndarray, weights: np.ndarray, edges: np.ndarray) -> np.ndarray:
    return np.histogram(values, bins=edges, weights=weights)[0]


def figure_report(
    spec: dict[str, Any],
    families: list[Family],
    grid: SpatialGrid,
    marginals: MarginalGrid,
    arc: ArcProjector | None,
    surfaces: dict[tuple[str, int | None], dict[str, Any]],
    assessment: dict[str, Any],
    metrics: dict[tuple[str, int], dict[str, Any]],
    land: list[np.ndarray],
) -> plt.Figure:
    rows = len(families)
    # A one-family report still needs enough fixed physical height to keep the
    # title, semantics, conditioning statement, and support banner disjoint.
    figure = plt.figure(figsize=(15.0, max(9.2, 3.7 * rows + 2.2)))
    layout = figure.add_gridspec(
        rows,
        3,
        width_ratios=(1.55, 0.82, 1.0),
        left=0.065,
        right=0.985,
        bottom=0.12,
        top=0.84,
        wspace=0.22,
        hspace=0.30,
    )
    semantic_title = {
        "filtering": "FILTERING POSTERIOR",
        "smoothed": "SMOOTHED / LATER-EVIDENCE-CONDITIONAL POSTERIOR",
        "conditional_impact": "IMPACT LOCATION CONDITIONAL ON IMPACT",
    }[spec["posterior_semantics"]]
    failed = not assessment["publication_eligible"]
    for row, family in enumerate(families):
        map_ax = figure.add_subplot(layout[row, 0])
        latitude_ax = figure.add_subplot(layout[row, 1])
        along_ax = figure.add_subplot(layout[row, 2])
        add_land(map_ax, land, grid)
        pooled = surfaces[(family.family_id, None)]
        plot_hpd(map_ax, pooled, family.color, True)
        dash_styles = ("solid", "dashed", "dotted", "dashdot")
        for source_index, source in enumerate(family.sources):
            seed_surface = surfaces[(family.family_id, source.seed)]
            threshold_95 = seed_surface["thresholds"]["0.95"]
            if threshold_95 is not None and threshold_95 > 0.0:
                map_ax.contour(
                    seed_surface["along_centers_km"],
                    seed_surface["cross_centers_km"],
                    seed_surface["mass"].T,
                    levels=(threshold_95,),
                    colors=(family.color,),
                    linewidths=0.65,
                    linestyles=[dash_styles[source_index % len(dash_styles)]],
                    alpha=0.55,
                    zorder=4,
                )
            item = metrics[(family.family_id, source.seed)]
            map_ax.scatter(
                item["mean_along_km"],
                item["mean_cross_km"],
                s=27,
                facecolor="white",
                edgecolor=family.color,
                linewidth=0.9,
                zorder=5,
            )
            map_ax.annotate(
                str(source.seed),
                (item["mean_along_km"], item["mean_cross_km"]),
                xytext=(4, 4),
                textcoords="offset points",
                fontsize=6.3,
                color=family.color,
                zorder=6,
            )
        map_ax.set_xlim(grid.along_min_km, grid.along_max_km)
        map_ax.set_ylim(grid.cross_min_km, grid.cross_max_km)
        map_ax.set_aspect("equal", adjustable="box")
        map_ax.set_title(
            f"{family.label} — display-smoothed spatial HPD",
            loc="left",
            color=family.color,
            fontweight="bold",
        )
        if row == 0:
            map_ax.legend(
                handles=[
                    Line2D([0], [0], color=family.color, linewidth=1.65, label="50% HPD"),
                    Line2D([0], [0], color=family.color, linewidth=1.2, label="95% HPD"),
                    Line2D([0], [0], color=family.color, linewidth=0.85, label="99% HPD"),
                    Line2D(
                        [0],
                        [0],
                        color=family.color,
                        linewidth=0.65,
                        linestyle="dashed",
                        label="seed 95% HPD",
                    ),
                ],
                loc="upper right",
                ncol=2,
                fontsize=6.5,
                framealpha=0.88,
            )
        map_ax.set_xlabel(
            f"Along-axis coordinate (km; bearing {grid.along_axis_bearing_deg:.1f}° true)"
        )
        map_ax.set_ylabel("Cross-axis coordinate (km; positive right of axis)")
        pooled_outside = pooled["raw_mass_outside_plot"]
        map_ax.text(
            0.015,
            0.018,
            f"raw positive mass outside fixed plot: {100.0 * pooled_outside:.6g}%",
            transform=map_ax.transAxes,
            fontsize=7.0,
            color="#8a3b2f" if pooled_outside > 0.0 else "#4c5966",
            bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.84},
        )
        missing_hpd = [
            f"{100 * probability:.0f}%"
            for probability in HPD_MASSES
            if pooled["thresholds"][f"{probability:.2f}"] is None
        ]
        if missing_hpd:
            map_ax.text(
                0.985,
                0.018,
                f"HPD not contained: {', '.join(missing_hpd)}",
                transform=map_ax.transAxes,
                ha="right",
                fontsize=7.0,
                color="#A23B3B",
                fontweight="bold",
                bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.84},
            )

        latitude_edges = marginals.latitude_edges
        latitude_centers = (latitude_edges[:-1] + latitude_edges[1:]) / 2.0
        lat_values, lat_weights = pooled_arrays(family, "latitude_deg")
        lat_mass = raw_histogram(lat_values, lat_weights, latitude_edges)
        latitude_ax.fill_between(
            latitude_centers,
            0.0,
            lat_mass,
            step="mid",
            color=family.color,
            alpha=0.20,
        )
        latitude_ax.step(
            latitude_centers, lat_mass, where="mid", color=family.color, linewidth=1.6
        )
        for source_index, source in enumerate(family.sources):
            source_mass = raw_histogram(
                source.latitude_deg, source.weights, latitude_edges
            )
            latitude_ax.step(
                latitude_centers,
                source_mass,
                where="mid",
                color=family.color,
                linewidth=0.65,
                linestyle=dash_styles[source_index % len(dash_styles)],
                alpha=0.55,
            )
        latitude_ax.set_xlim(marginals.latitude_min_deg, marginals.latitude_max_deg)
        latitude_ax.set_title("Raw weighted latitude bins — no KDE", loc="left")
        latitude_ax.set_xlabel("Latitude (degrees north)")
        latitude_ax.set_ylabel("Posterior mass per fixed bin")

        along_edges = marginals.along_edges
        along_centers = (along_edges[:-1] + along_edges[1:]) / 2.0
        along_values, along_weights = pooled_arrays(family, "marginal_along_km")
        along_mass = raw_histogram(along_values, along_weights, along_edges)
        along_ax.fill_between(
            along_centers,
            0.0,
            along_mass,
            step="mid",
            color=family.color,
            alpha=0.20,
        )
        along_ax.step(
            along_centers, along_mass, where="mid", color=family.color, linewidth=1.6
        )
        for source_index, source in enumerate(family.sources):
            assert source.marginal_along_km is not None
            source_mass = raw_histogram(
                source.marginal_along_km, source.weights, along_edges
            )
            along_ax.step(
                along_centers,
                source_mass,
                where="mid",
                color=family.color,
                linewidth=0.65,
                linestyle=dash_styles[source_index % len(dash_styles)],
                alpha=0.55,
            )
        along_ax.set_xlim(marginals.along_min_km, marginals.along_max_km)
        along_label = arc.label if arc is not None else "declared local along axis"
        along_ax.set_title("Raw weighted along-coordinate bins — no KDE", loc="left")
        along_ax.set_xlabel(f"{along_label} coordinate (km)")
        along_ax.set_ylabel("Posterior mass per fixed bin")

    status_text = (
        "NUMERICAL SUPPORT PASSED"
        if not failed
        else "FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY"
    )
    status_color = "#2A6F62" if not failed else "#A23B3B"
    figure.suptitle(spec["title"], y=0.985, fontsize=16.5, fontweight="bold", color="#10243e")
    figure.text(
        0.5,
        0.946,
        semantic_title,
        ha="center",
        fontsize=10.5,
        fontweight="bold",
        color="#24384d",
    )
    figure.text(
        0.5,
        0.916,
        spec["conditioning_statement"],
        ha="center",
        fontsize=8.6,
        color="#465464",
    )
    figure.text(
        0.5,
        0.882,
        status_text,
        ha="center",
        fontsize=10.2,
        fontweight="bold",
        color="white",
        bbox={"boxstyle": "round,pad=0.35", "facecolor": status_color, "edgecolor": "none"},
    )
    if failed:
        figure.text(
            0.5,
            0.52,
            "FAILED",
            ha="center",
            va="center",
            fontsize=76,
            fontweight="bold",
            color="#A23B3B",
            alpha=0.065,
            rotation=28,
        )
    figure.text(
        0.5,
        0.067,
        (
            f"Pooled fill/lines: 99% / 95% / 50% HPD on a fixed {grid.cell_size_km:g} km grid; "
            f"Gaussian display kernel σ={grid.bandwidth_km:g} km. Thin 95% lines and open means: seeds."
        ),
        ha="center",
        fontsize=8.0,
        color="#4c5966",
    )
    figure.text(
        0.5,
        0.041,
        (
            "Spatial smoothing is display-only; latitude and along-coordinate panels are raw fixed-bin mass. "
            "Bounds, bins, and bandwidth are specification constants, never posterior-derived."
        ),
        ha="center",
        fontsize=7.8,
        color="#4c5966",
    )
    figure.text(
        0.5,
        0.015,
        (
            "Families are separate alternatives; equal weighting is used only among declared numerical seeds "
            "within one family."
        ),
        ha="center",
        fontsize=7.8,
        color="#4c5966",
    )
    return figure


def serializable_surface(value: dict[str, Any]) -> dict[str, Any]:
    return {
        "raw_mass_outside_plot": value["raw_mass_outside_plot"],
        "raw_mass_beyond_kernel_padding": value["raw_mass_beyond_kernel_padding"],
        "display_smoothed_mass_inside_plot": value["display_smoothed_mass_inside_plot"],
        "hpd_threshold_mass_per_cell": value["thresholds"],
        "hpd_achieved_mass": value["achieved_masses"],
        "hpd_area_km2": value["areas_km2"],
        "display_bandwidth_km": value["bandwidth_km"],
        "cell_size_km": value["cell_size_km"],
        "kernel_padding_cells": value["padding_cells"],
    }


def semantics_description(spec: dict[str, Any]) -> str:
    return {
        "filtering": (
            "State and weights use only evidence through the declared filtering checkpoint; "
            "the map is not an impact posterior."
        ),
        "smoothed": (
            "State is shown at an earlier checkpoint while weights include explicitly declared later evidence."
        ),
        "conditional_impact": (
            "Spatial weights are explicitly renormalized among impact outcomes; unconditional impact mass is "
            "reported for every source and non-impact posterior mass is not hidden."
        ),
    }[spec["posterior_semantics"]]


def display_number(value: Any) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, float):
        return f"{value:.8g}"
    return str(value)


def html_report(audit: dict[str, Any], figure_name: str) -> str:
    assessment = audit["numerical_support"]
    eligible = assessment["publication_eligible"]
    status_class = "pass" if eligible else "fail"
    source_rows = []
    for family in audit["families"]:
        for source in family["sources"]:
            metrics = source["metrics"]
            source_rows.append(
                "<tr>"
                f"<td>{html.escape(family['label'])}</td>"
                f"<td>{source['seed']}</td>"
                f"<td>{html.escape(source['source_format'])}</td>"
                f"<td>{display_number(metrics['particle_ess'])}</td>"
                f"<td>{display_number(metrics['root_ess'])}</td>"
                f"<td>{display_number(metrics['top_root_mass'])}</td>"
                f"<td>{display_number(metrics['roots_over_1e-6'])}</td>"
                f"<td>{display_number(metrics['roots_over_1e-3'])}</td>"
                f"<td>{100.0 * metrics['mass_outside_plot']:.7g}%</td>"
                f"<td>{100.0 * source['posterior_position_mass_before_conditioning']:.7g}%</td>"
                "</tr>"
            )
    criterion_rows = []
    for item in assessment["criteria"]:
        criterion_rows.append(
            f"<tr class='{item['status']}'>"
            f"<td>{html.escape(item['scope'])}</td>"
            f"<td>{html.escape(item['criterion'])}</td>"
            f"<td>{html.escape(item['status'].upper())}</td>"
            f"<td>{html.escape(item['comparison'])} {display_number(item['limit'])}</td>"
            f"<td>{display_number(item['observed'])}</td>"
            f"<td>{html.escape(item['detail'])}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(audit['title'])}</title>
<style>
body {{ margin: 0 auto; max-width: 1500px; padding: 24px; color: #172334; background: #fff; font: 15px/1.45 'DejaVu Sans', Arial, sans-serif; }}
h1, h2 {{ color: #10243e; }}
.banner {{ padding: 12px 16px; border-radius: 6px; color: white; font-weight: 700; letter-spacing: .04em; }}
.pass {{ background: #2A6F62; }} .fail {{ background: #A23B3B; }}
.figure {{ width: 100%; height: auto; border: 1px solid #d7dde3; }}
.note {{ padding: 10px 14px; background: #f3f6f8; border-left: 4px solid #526475; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; }}
th, td {{ padding: 7px; border: 1px solid #d7dde3; text-align: right; vertical-align: top; }}
th:first-child, td:first-child, th:nth-child(2), td:nth-child(2) {{ text-align: left; }}
tr.failed td {{ background: #fff0ed; }} tr.unassessed td {{ background: #fff8df; }}
code {{ overflow-wrap: anywhere; }}
</style>
</head>
<body>
<h1>{html.escape(audit['title'])}</h1>
<p class="banner {status_class}">{'NUMERICAL SUPPORT PASSED' if eligible else 'FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY'}</p>
<p><strong>{html.escape(audit['posterior_semantics'].upper())}</strong> — {html.escape(audit['semantics_description'])}</p>
<p>{html.escape(audit['conditioning_statement'])}</p>
<p class="note">The spatial grid, bounds, marginal bins and Gaussian display bandwidth are fixed physical constants from the input specification. The raw latitude and along-coordinate marginals are unsmoothed. Families are not pooled.</p>
<p><a href="{html.escape(figure_name.replace('.png', '.svg'))}">SVG</a> · <a href="{html.escape(figure_name.replace('.png', '.pdf'))}">PDF</a> · <a href="{html.escape(figure_name)}">PNG</a> · <a href="broad_flight_spatial_report.json">JSON audit</a></p>
<img class="figure" src="{html.escape(figure_name)}" alt="Broad-flight posterior report">
<h2>Particle and genealogy diagnostics</h2>
<table><thead><tr><th>Family</th><th>Seed</th><th>Source</th><th>Particle ESS</th><th>Root ESS</th><th>Top root</th><th>Roots &gt;1e-6</th><th>Roots &gt;1e-3</th><th>Mass outside plot</th><th>Position mass before conditioning</th></tr></thead>
<tbody>{''.join(source_rows)}</tbody></table>
<h2>Numerical-support assessment</h2>
<p>{assessment['failed_criteria']} failed; {assessment['unassessed_criteria']} unassessed. Standard: <code>{html.escape(assessment['standard'])}</code>.</p>
<table><thead><tr><th>Scope</th><th>Criterion</th><th>Status</th><th>Requirement</th><th>Observed</th><th>Detail</th></tr></thead>
<tbody>{''.join(criterion_rows)}</tbody></table>
<h2>Reproduction and provenance</h2>
<p><code>{html.escape(audit['reproduction_command'])}</code></p>
<p>Generator SHA-256: <code>{audit['generator_sha256']}</code><br>Specification SHA-256: <code>{audit['specification_sha256']}</code></p>
</body>
</html>
"""


def empty_output(path: Path) -> None:
    if path.exists():
        if not path.is_dir():
            raise ReportInputError(f"output is not a directory: {path}")
        if any(path.iterdir()):
            raise ReportInputError(f"output directory must be empty: {path}")
    else:
        path.mkdir(parents=True)


def assemble_audit(
    spec: dict[str, Any],
    spec_path: Path,
    families: list[Family],
    grid: SpatialGrid,
    marginals: MarginalGrid,
    arc_metadata: dict[str, Any] | None,
    land_metadata: dict[str, Any] | None,
    surfaces: dict[tuple[str, int | None], dict[str, Any]],
    assessment: dict[str, Any],
    metrics: dict[tuple[str, int], dict[str, Any]],
) -> dict[str, Any]:
    family_records = []
    for family in families:
        sources = []
        for source in family.sources:
            input_record: dict[str, Any] = {
                "logical_path": source.logical_path,
                "sha256": source.input_sha256,
            }
            if source.summary_logical_path is not None:
                input_record["summary"] = {
                    "logical_path": source.summary_logical_path,
                    "sha256": source.summary_sha256,
                }
            parent_input = source.source_metadata.get("parent_handoff")
            if isinstance(parent_input, dict):
                input_record["parent_handoff"] = parent_input
            sources.append(
                {
                    "seed": source.seed,
                    "source_format": source.source_format,
                    "input": input_record,
                    "configured_particles": source.configured_particles,
                    "positive_position_rows": len(source.weights),
                    "posterior_total_mass": source.posterior_total_mass,
                    "posterior_position_mass_before_conditioning": source.posterior_position_mass,
                    "source_metadata": source.source_metadata,
                    "metrics": metrics[(family.family_id, source.seed)],
                    "spatial_surface": serializable_surface(
                        surfaces[(family.family_id, source.seed)]
                    ),
                }
            )
        family_records.append(
            {
                "id": family.family_id,
                "label": family.label,
                "color": family.color,
                "seed_pooling": "equal numerical-replicate weight within this family",
                "sources": sources,
                "pooled_spatial_surface": serializable_surface(
                    surfaces[(family.family_id, None)]
                ),
            }
        )
    generator = Path(__file__).resolve()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "schema_version": REPORT_SCHEMA_VERSION,
        "title": spec["title"],
        "artifact_class": spec["artifact_class"],
        "artifact_epoch_utc": spec["artifact_epoch_utc"],
        "posterior_semantics": spec["posterior_semantics"],
        "semantics_description": semantics_description(spec),
        "conditioning_statement": spec["conditioning_statement"],
        "publication_eligible": assessment["publication_eligible"],
        "family_pooling": "none",
        "spatial_grid": {
            "projection": "spherical azimuthal equidistant, then fixed bearing rotation",
            "earth_radius_km": EARTH_RADIUS_KM,
            "projection_origin_deg": [
                grid.origin_latitude_deg,
                grid.origin_longitude_deg,
            ],
            "along_axis_bearing_deg_true": grid.along_axis_bearing_deg,
            "along_bounds_km": [grid.along_min_km, grid.along_max_km],
            "cross_bounds_km": [grid.cross_min_km, grid.cross_max_km],
            "cell_size_km": grid.cell_size_km,
            "display_kernel": "isotropic Gaussian",
            "display_bandwidth_sigma_km": grid.bandwidth_km,
            "kernel_truncation_sigma": grid.kernel_truncation_sigma,
            "bounds_source": "report specification; never posterior-derived",
            "bandwidth_source": "report specification; never bounds- or posterior-derived",
        },
        "marginals": {
            "smoothing": "none",
            "latitude_bounds_deg": [
                marginals.latitude_min_deg,
                marginals.latitude_max_deg,
            ],
            "latitude_bin_width_deg": marginals.latitude_bin_width_deg,
            "along_bounds_km": [marginals.along_min_km, marginals.along_max_km],
            "along_bin_width_km": marginals.along_bin_width_km,
            "along_coordinate": (
                arc_metadata["label"]
                if arc_metadata is not None
                else "declared local along axis"
            ),
            "equal_tail_95_endpoint_comparison_coordinate": (
                arc_metadata["label"]
                if arc_metadata is not None
                else "local northing (not a seventh-arc coordinate)"
            ),
        },
        "along_arc": arc_metadata,
        "land_context": land_metadata,
        "families": family_records,
        "numerical_support": assessment,
        "generator": str(generator),
        "generator_sha256": sha256(generator),
        "specification_logical_path": str(spec_path),
        "specification_sha256": sha256(spec_path),
        "software": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "scipy": __import__("scipy").__version__,
            "matplotlib": mpl.__version__,
        },
        "reproduction_command": (
            f".venv/bin/python {Path(__file__).as_posix()} --spec {spec_path.as_posix()} "
            "--output <new-empty-output-directory>"
            + (
                " --allow-failed-diagnostic"
                if not assessment["publication_eligible"]
                else ""
            )
        ),
    }


def render(
    spec_path: Path,
    output: Path,
    allow_failed_diagnostic: bool = False,
) -> dict[str, Any]:
    spec_path = spec_path.resolve()
    spec = load_spec(spec_path)
    grid = spatial_grid(spec)
    marginals = marginal_grid(spec)
    families = load_families(spec, spec_path)
    arc, arc_metadata = load_arc_projector(spec, spec_path, grid)
    project_sources(families, grid, arc)
    surfaces = build_surfaces(families, grid)
    endpoint_label = (
        arc.label if arc is not None else "local northing (not a seventh-arc coordinate)"
    )
    assessment, metrics = assess_numerical_support(
        families,
        surfaces,
        spec.get("numerical_standard", "milestone"),
        endpoint_label,
    )
    if not assessment["publication_eligible"] and not (
        allow_failed_diagnostic and spec["artifact_class"] == "diagnostic"
    ):
        raise PublicationRefused(assessment)
    if allow_failed_diagnostic and spec["artifact_class"] != "diagnostic":
        raise ReportInputError(
            "--allow-failed-diagnostic requires artifact_class=diagnostic"
        )
    land, land_metadata = load_land(spec, spec_path, grid)
    audit = assemble_audit(
        spec,
        spec_path,
        families,
        grid,
        marginals,
        arc_metadata,
        land_metadata,
        surfaces,
        assessment,
        metrics,
    )
    output = output.resolve()
    empty_output(output)
    figure = figure_report(
        spec,
        families,
        grid,
        marginals,
        arc,
        surfaces,
        assessment,
        metrics,
        land,
    )
    stem = "broad_flight_spatial_posterior"
    epoch = datetime.fromisoformat(spec["artifact_epoch_utc"].replace("Z", "+00:00"))
    if epoch.tzinfo is None:
        epoch = epoch.replace(tzinfo=timezone.utc)
    title = spec["title"]
    output_paths: list[Path] = []
    for suffix in ("svg", "pdf", "png"):
        path = output / f"{stem}.{suffix}"
        if suffix == "svg":
            metadata = {
                "Creator": "MH370 broad-flight spatial reporter",
                "Title": title,
                "Date": spec["artifact_epoch_utc"],
            }
        elif suffix == "pdf":
            metadata = {
                "Creator": "MH370 broad-flight spatial reporter",
                "Title": title,
                "CreationDate": epoch,
                "ModDate": epoch,
            }
        else:
            metadata = {
                "Software": "MH370 broad-flight spatial reporter",
                "Title": title,
                "Creation Time": spec["artifact_epoch_utc"],
            }
        atomic_figure(figure, path, metadata)
        output_paths.append(path)
    plt.close(figure)
    html_path = output / "broad_flight_spatial_report.html"
    atomic_text(html_path, html_report(audit, f"{stem}.png"))
    output_paths.append(html_path)
    audit["outputs"] = {path.name: sha256(path) for path in sorted(output_paths)}
    json_path = output / "broad_flight_spatial_report.json"
    atomic_text(json_path, json.dumps(audit, indent=2, sort_keys=True) + "\n")
    return audit


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--allow-failed-diagnostic",
        action="store_true",
        help="render a failed diagnostic with an explicit watermark; never makes it publication eligible",
    )
    args = parser.parse_args(argv)
    try:
        audit = render(args.spec, args.output, args.allow_failed_diagnostic)
    except (ReportInputError, PublicationRefused) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    status = audit["numerical_support"]["status"]
    print(
        f"generated deterministic {status} broad-flight report in {args.output.resolve()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
