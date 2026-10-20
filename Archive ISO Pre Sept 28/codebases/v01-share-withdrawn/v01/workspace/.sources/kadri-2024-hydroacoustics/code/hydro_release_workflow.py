#!/usr/bin/env python3
"""Generate the v0.1 hydroacoustic forward/reverse diagnostic release.

The workflow expands a 5 NM seventh-arc grid through ±100 NM by a fixed bank
of conditional impact scenarios. It predicts station arrival and reduced-order
pressure envelopes, attaches the already-computed complete publication-trace
correlation controls, and reverse-traces declared signal windows. No result is
converted into an estimator likelihood or particle-weight update.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import math
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

matplotlib.rcParams["svg.hashsalt"] = "mh370-hydroacoustic-release-v0.1"


HERE = Path(__file__).resolve().parents[1]
CONFIG_PATH = HERE / "data" / "hydro-release-config.json"
OUTPUT = HERE / "outputs" / "release-v0.1"
EARTH_RADIUS_KM = 6371.0088
TNT_SPECIFIC_ENERGY_J_KG = 4.184e6
PDF_METADATA = {"CreationDate": None, "ModDate": None}
REJECTED_DIRECTORY_NAMES = frozenset({"__pycache__", ".pytest_cache", ".mypy_cache"})
REJECTED_FILE_SUFFIXES = frozenset({".pyc", ".pyo", ".tmp", ".temp", ".swp"})


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rejected_artifacts(root: Path = HERE) -> list[str]:
    """Return package-relative cache, editor-backup, and temporary paths."""
    rejected = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in REJECTED_DIRECTORY_NAMES for part in relative.parts) or (
            path.is_file()
            and (path.suffix.lower() in REJECTED_FILE_SUFFIXES or path.name.endswith("~"))
        ):
            rejected.append(relative.as_posix())
    return sorted(rejected)


def assert_release_tree_clean(root: Path = HERE) -> None:
    rejected = rejected_artifacts(root)
    if rejected:
        raise ValueError(f"release tree contains rejected cache/temp artifacts: {rejected}")


def parse_utc(value: str) -> float:
    if not value.endswith("Z"):
        raise ValueError(f"UTC value lacks Z suffix: {value}")
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def iso_utc(value: float) -> str:
    return datetime.fromtimestamp(float(value), timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def seconds_after_midnight(value: float) -> float:
    midnight = parse_utc("2014-03-08T00:00:00Z")
    return value - midnight


def resolve(relative: str) -> Path:
    return (HERE / relative).resolve()


def validate_input_hash(path: Path, expected: str) -> None:
    actual = sha256(path)
    if actual != expected:
        raise ValueError(f"input hash mismatch for {path}: expected {expected}, found {actual}")


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"no rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def haversine_km(
    latitude: np.ndarray | float,
    longitude: np.ndarray | float,
    station_latitude: float,
    station_longitude: float,
) -> np.ndarray:
    latitude = np.asarray(latitude, dtype=float)
    longitude = np.asarray(longitude, dtype=float)
    lat_1 = np.radians(latitude)
    lat_2 = math.radians(station_latitude)
    delta_lat = lat_1 - lat_2
    delta_lon = np.radians(longitude - station_longitude)
    value = np.sin(delta_lat / 2.0) ** 2 + np.cos(lat_1) * math.cos(lat_2) * np.sin(delta_lon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(value, 0.0, 1.0)))


def initial_bearing_deg(
    station_latitude: float,
    station_longitude: float,
    source_latitude: float,
    source_longitude: float,
) -> float:
    lat_1 = math.radians(station_latitude)
    lat_2 = math.radians(source_latitude)
    delta_lon = math.radians(source_longitude - station_longitude)
    y = math.sin(delta_lon) * math.cos(lat_2)
    x = math.cos(lat_1) * math.sin(lat_2) - math.sin(lat_1) * math.cos(lat_2) * math.cos(delta_lon)
    return math.degrees(math.atan2(y, x)) % 360.0


def circular_residual_deg(actual: float, expected: float) -> float:
    return (actual - expected + 180.0) % 360.0 - 180.0


def pressure_from_coupled_energy(coupled_energy_j: np.ndarray, range_km: float) -> np.ndarray:
    effective_yield_kg_tnt = np.maximum(coupled_energy_j, 1.0e-30) / TNT_SPECIFIC_ENERGY_J_KG
    scaled_range_m = max(range_km, 1.0e-6) * 1000.0 / np.cbrt(effective_yield_kg_tnt)
    return 52.4e6 * scaled_range_m**-1.13


def load_inputs(configuration: dict) -> tuple[list[dict], dict[str, dict[str, float]], dict]:
    grid_config = configuration["source_grid"]
    grid_path = resolve(grid_config["path"])
    validate_input_hash(grid_path, grid_config["sha256"])
    cells = read_csv(grid_path)
    cells.sort(key=lambda row: (int(row["alongIndex"]), int(row["crossIndex"])))
    if len(cells) != int(grid_config["expected_cell_count"]):
        raise ValueError(f"expected {grid_config['expected_cell_count']} source cells")
    for row in cells:
        if row["current_model"] != "equal_transport_family_model_average":
            raise ValueError("unexpected grid family")

    controls = configuration["publication_trace_controls"]
    correlation_path = resolve(controls["grid_path"])
    validate_input_hash(correlation_path, controls["grid_sha256"])
    correlation: dict[str, dict[str, float]] = {}
    for row in read_csv(correlation_path):
        if row["variant"] not in {"no_airgun_suppression", "rank8_unmasked"}:
            continue
        correlation.setdefault(row["cell_id"], {})[row["variant"]] = float(row["correlation_r"])
    if len(correlation) != len(cells):
        raise ValueError("correlation control does not cover the source grid")

    for path_key, hash_key in (
        ("unfiltered_top_path", "unfiltered_top_sha256"),
        ("filtered_top_path", "filtered_top_sha256"),
        ("summary_path", "summary_sha256"),
    ):
        validate_input_hash(resolve(controls[path_key]), controls[hash_key])
    scan_summary = json.loads(resolve(controls["summary_path"]).read_text(encoding="utf-8"))
    return cells, correlation, scan_summary


def scenario_bank(configuration: dict) -> list[dict]:
    config = configuration["impact_scenario_bank"]
    times = np.linspace(
        parse_utc(config["impact_time_utc"][0]),
        parse_utc(config["impact_time_utc"][1]),
        int(config["time_count"]),
    )
    couplings = np.geomspace(
        float(config["coupling_fraction_range"][0]),
        float(config["coupling_fraction_range"][1]),
        times.size,
    )
    mass = float(config["mass_kg"])
    scenarios = []
    for family in config["impact_families"]:
        vertical = float(family["vertical_speed_m_s"])
        horizontal = float(family["horizontal_speed_m_s"])
        for index, (time_s, coupling) in enumerate(zip(times, couplings)):
            vertical_energy = 0.5 * mass * vertical**2
            total_energy = 0.5 * mass * (vertical**2 + horizontal**2)
            scenarios.append(
                {
                    "id": f"{family['id']}-t{index:02d}",
                    "impact_family": family["id"],
                    "impact_time_utc": iso_utc(time_s),
                    "impact_time_utc_unix_s": float(time_s),
                    "mass_kg": mass,
                    "vertical_speed_m_s": vertical,
                    "horizontal_speed_m_s": horizontal,
                    "contact_duration_s": float(family["contact_duration_s"]),
                    "vertical_kinetic_energy_j": vertical_energy,
                    "total_kinetic_energy_j": total_energy,
                    "coupling_fraction": float(coupling),
                    "coupled_vertical_energy_j": vertical_energy * float(coupling),
                    "sampling_weight": 1.0 / (len(config["impact_families"]) * times.size),
                    "likelihood_evaluated": False,
                    "log_weight_increment": 0.0,
                }
            )
    return scenarios


def forward_grid_rows(
    configuration: dict,
    cells: list[dict],
    correlation: dict[str, dict[str, float]],
    scenarios: list[dict],
) -> list[dict]:
    latitude = np.asarray([float(row["latitude"]) for row in cells])
    longitude = np.asarray([float(row["longitude"]) for row in cells])
    station_distance: dict[str, np.ndarray] = {}
    for station_id, station in configuration["stations"].items():
        station_distance[station_id] = haversine_km(
            latitude,
            longitude,
            float(station["latitude_deg"]),
            float(station["longitude_deg_e"]),
        )
    celerity_min, celerity_max = map(float, configuration["propagation"]["celerity_km_s"])
    celerity_central = float(configuration["propagation"]["central_celerity_km_s"])
    scenario_times = np.asarray([row["impact_time_utc_unix_s"] for row in scenarios])
    coupled_energy = np.asarray([row["coupled_vertical_energy_j"] for row in scenarios])
    rows = []
    for index, cell in enumerate(cells):
        distances = {station: float(values[index]) for station, values in station_distance.items()}
        arrivals = {
            station: scenario_times + distance / celerity_central
            for station, distance in distances.items()
        }
        pressure = {
            station: pressure_from_coupled_energy(coupled_energy, distance)
            for station, distance in distances.items()
        }
        distance_difference = distances["H08S"] - distances["H01W"]
        lag_bounds = sorted((distance_difference / celerity_min, distance_difference / celerity_max))
        row = {
            "cell_id": cell["id"],
            "along_nm": float(cell["alongNm"]),
            "cross_nm": float(cell["crossNm"]),
            "latitude_deg": float(cell["latitude"]),
            "longitude_deg_e": float(cell["longitude"]),
            "scenario_count": len(scenarios),
            "expanded_scenario_weight_sum": 1.0,
            "h01w_distance_km": distances["H01W"],
            "h08s_distance_km": distances["H08S"],
            "interstation_lag_min_s": lag_bounds[0],
            "interstation_lag_max_s": lag_bounds[1],
            "h01w_arrival_min_utc": iso_utc(float(np.min(scenario_times) + distances["H01W"] / celerity_max)),
            "h01w_arrival_median_utc": iso_utc(float(np.median(arrivals["H01W"]))),
            "h01w_arrival_max_utc": iso_utc(float(np.max(scenario_times) + distances["H01W"] / celerity_min)),
            "h08s_arrival_min_utc": iso_utc(float(np.min(scenario_times) + distances["H08S"] / celerity_max)),
            "h08s_arrival_median_utc": iso_utc(float(np.median(arrivals["H08S"]))),
            "h08s_arrival_max_utc": iso_utc(float(np.max(scenario_times) + distances["H08S"] / celerity_min)),
            "h01w_pressure_q05_pa": float(np.quantile(pressure["H01W"], 0.05)),
            "h01w_pressure_median_pa": float(np.median(pressure["H01W"])),
            "h01w_pressure_q95_pa": float(np.quantile(pressure["H01W"], 0.95)),
            "h08s_pressure_q05_pa": float(np.quantile(pressure["H08S"], 0.05)),
            "h08s_pressure_median_pa": float(np.median(pressure["H08S"])),
            "h08s_pressure_q95_pa": float(np.quantile(pressure["H08S"], 0.95)),
            "publication_trace_unfiltered_correlation_r": correlation[cell["id"]]["no_airgun_suppression"],
            "publication_trace_rank8_correlation_r": correlation[cell["id"]]["rank8_unmasked"],
            "likelihood_evaluated": False,
            "log_weight_increment": 0.0,
            "status": "DIAGNOSTIC_ZERO_WEIGHT",
        }
        rows.append(row)
    return rows


def reverse_matches(
    configuration: dict,
    cells: list[dict],
    scenarios: list[dict],
) -> tuple[list[dict], list[dict]]:
    celerity_min, celerity_max = map(float, configuration["propagation"]["celerity_km_s"])
    path_slack = float(configuration["propagation"]["unresolved_path_timing_s"])
    impact_min = parse_utc(configuration["impact_scenario_bank"]["impact_time_utc"][0])
    impact_max = parse_utc(configuration["impact_scenario_bank"]["impact_time_utc"][1])
    scenario_times = np.asarray([row["impact_time_utc_unix_s"] for row in scenarios])
    rows = []
    summaries = []
    for candidate in configuration["reverse_candidates"]:
        candidate_rows = []
        for cell in cells:
            latitude = float(cell["latitude"])
            longitude = float(cell["longitude"])
            compatible_min = impact_min
            compatible_max = impact_max
            residuals = {}
            valid = True
            for observation in candidate["observations"]:
                station = configuration["stations"][observation["station"]]
                distance = float(
                    haversine_km(
                        latitude,
                        longitude,
                        float(station["latitude_deg"]),
                        float(station["longitude_deg_e"]),
                    )
                )
                arrival = parse_utc(observation["arrival_utc"])
                half_width = float(observation["half_width_s"])
                implied_min = arrival - half_width - distance / celerity_min - path_slack
                implied_max = arrival + half_width - distance / celerity_max + path_slack
                compatible_min = max(compatible_min, implied_min)
                compatible_max = min(compatible_max, implied_max)
                if "bearing_deg" in observation:
                    actual = initial_bearing_deg(
                        float(station["latitude_deg"]),
                        float(station["longitude_deg_e"]),
                        latitude,
                        longitude,
                    )
                    residual = circular_residual_deg(actual, float(observation["bearing_deg"]))
                    residuals[observation["station"]] = residual
                    if abs(residual) > float(observation["bearing_half_width_deg"]):
                        valid = False
            if not valid or compatible_max < compatible_min:
                continue
            scenario_matches = int(np.count_nonzero((scenario_times >= compatible_min) & (scenario_times <= compatible_max)))
            row = {
                "candidate_id": candidate["id"],
                "candidate_status": candidate["status"],
                "cell_id": cell["id"],
                "along_nm": float(cell["alongNm"]),
                "cross_nm": float(cell["crossNm"]),
                "latitude_deg": latitude,
                "longitude_deg_e": longitude,
                "compatible_impact_start_utc": iso_utc(compatible_min),
                "compatible_impact_end_utc": iso_utc(compatible_max),
                "scenario_template_matches": scenario_matches,
                "h01w_bearing_residual_deg": residuals.get("H01W", ""),
                "h08s_bearing_residual_deg": residuals.get("H08S", ""),
                "likelihood_evaluated": False,
                "log_weight_increment": 0.0,
                "status": "CONDITIONAL_REVERSE_GEOMETRY_NOT_EVENT_ASSOCIATION",
            }
            rows.append(row)
            candidate_rows.append(row)
        summaries.append(
            {
                "candidate_id": candidate["id"],
                "candidate_status": candidate["status"],
                "compatible_cell_count": len(candidate_rows),
                "compatible_scenario_template_count": int(sum(row["scenario_template_matches"] for row in candidate_rows)),
                "along_arc_min_nm": min((row["along_nm"] for row in candidate_rows), default=None),
                "along_arc_max_nm": max((row["along_nm"] for row in candidate_rows), default=None),
                "cross_arc_min_nm": min((row["cross_nm"] for row in candidate_rows), default=None),
                "cross_arc_max_nm": max((row["cross_nm"] for row in candidate_rows), default=None),
                "likelihood_evaluated": False,
                "log_weight_increment": 0.0,
            }
        )
    if not rows:
        rows.append(
            {
                "candidate_id": "none",
                "candidate_status": "no declared candidate intersects the grid",
                "cell_id": "",
                "along_nm": "",
                "cross_nm": "",
                "latitude_deg": "",
                "longitude_deg_e": "",
                "compatible_impact_start_utc": "",
                "compatible_impact_end_utc": "",
                "scenario_template_matches": 0,
                "h01w_bearing_residual_deg": "",
                "h08s_bearing_residual_deg": "",
                "likelihood_evaluated": False,
                "log_weight_increment": 0.0,
                "status": "CONDITIONAL_REVERSE_GEOMETRY_NOT_EVENT_ASSOCIATION",
            }
        )
    return rows, summaries


def make_signal_bank(
    configuration: dict,
    forward_rows: list[dict],
    scenarios: list[dict],
) -> tuple[list[dict], str]:
    reference = min(
        forward_rows,
        key=lambda row: (float(row["latitude_deg"]) + 34.9167) ** 2 + (float(row["longitude_deg_e"]) - 92.0472) ** 2,
    )
    time = np.linspace(-8.0, 24.0, 641)
    rows = []
    coupling = 1.0e-4
    family_scenarios = {}
    for scenario in scenarios:
        family_scenarios.setdefault(scenario["impact_family"], scenario)
    for station_id, distance_key in (("H01W", "h01w_distance_km"), ("H08S", "h08s_distance_km")):
        distance = float(reference[distance_key])
        for family_id, scenario in family_scenarios.items():
            coupled = float(scenario["vertical_kinetic_energy_j"]) * coupling
            peak = float(pressure_from_coupled_energy(np.asarray([coupled]), distance)[0])
            sigma = max(0.12, float(scenario["contact_duration_s"]) / 3.0)
            envelope = np.exp(-0.5 * (time / sigma) ** 2) + 0.28 * np.exp(-0.5 * ((time - 2.2) / (2.2 * sigma + 0.3)) ** 2)
            carrier = np.cos(2.0 * np.pi * 5.0 * time) + 0.22 * np.cos(2.0 * np.pi * 11.0 * time)
            pressure = peak * envelope * carrier / 1.22
            for offset, value, envelope_value in zip(time, pressure, peak * envelope):
                rows.append(
                    {
                        "reference_cell_id": reference["cell_id"],
                        "station": station_id,
                        "impact_family": family_id,
                        "seconds_from_predicted_arrival": float(offset),
                        "simulated_pressure_pa": float(value),
                        "pressure_envelope_pa": float(envelope_value),
                        "coupling_fraction": coupling,
                        "status": "ILLUSTRATIVE_REDUCED_ORDER_SIGNAL_NOT_RECEIVER_TEMPLATE",
                    }
                )
    return rows, str(reference["cell_id"])


def save_figure(figure: plt.Figure, stem: str) -> list[Path]:
    paths = []
    for suffix in ("svg", "png", "pdf"):
        path = OUTPUT / f"{stem}.{suffix}"
        kwargs = {}
        if suffix == "png":
            kwargs["dpi"] = 260
        if suffix == "pdf":
            kwargs["metadata"] = PDF_METADATA
        if suffix == "svg":
            kwargs["metadata"] = {"Date": None}
        figure.savefig(path, **kwargs)
        paths.append(path)
    plt.close(figure)
    return paths


def make_overview_figure(
    configuration: dict,
    forward_rows: list[dict],
    reverse_rows: list[dict],
    scenarios: list[dict],
) -> list[Path]:
    figure, axes = plt.subplots(2, 2, figsize=(15.8, 11.2))
    latitude = np.asarray([float(row["latitude_deg"]) for row in forward_rows])
    longitude = np.asarray([float(row["longitude_deg_e"]) for row in forward_rows])
    lag = np.asarray([0.5 * (float(row["interstation_lag_min_s"]) + float(row["interstation_lag_max_s"])) / 60.0 for row in forward_rows])
    scatter = axes[0, 0].scatter(longitude, latitude, c=lag, s=5.5, cmap="viridis", rasterized=True)
    centre = [row for row in forward_rows if abs(float(row["cross_nm"])) < 1.0e-9]
    axes[0, 0].plot([float(row["longitude_deg_e"]) for row in centre], [float(row["latitude_deg"]) for row in centre], color="black", linewidth=1.0, label="Seventh arc")
    for station_id, station in configuration["stations"].items():
        axes[0, 0].scatter(float(station["longitude_deg_e"]), float(station["latitude_deg"]), marker="^", s=60, color="#C84C4C")
        axes[0, 0].annotate(station_id, (float(station["longitude_deg_e"]), float(station["latitude_deg"])), xytext=(4, 3), textcoords="offset points")
    axes[0, 0].set_xlim(70, 116)
    axes[0, 0].set_ylim(-47, -5)
    axes[0, 0].set_xlabel("Longitude (°E)")
    axes[0, 0].set_ylabel("Latitude (°)")
    axes[0, 0].set_title("A. 5 NM source boxes along the seventh arc and ±100 NM cross-arc")
    axes[0, 0].grid(alpha=0.14)
    figure.colorbar(scatter, ax=axes[0, 0], label="Central H08S−H01W travel-time difference (min)")

    along_values = sorted({float(row["along_nm"]) for row in forward_rows})
    cross_values = sorted({float(row["cross_nm"]) for row in forward_rows})
    along_index = {value: index for index, value in enumerate(along_values)}
    cross_index = {value: index for index, value in enumerate(cross_values)}
    correlation_grid = np.full((len(cross_values), len(along_values)), np.nan)
    for row in forward_rows:
        correlation_grid[cross_index[float(row["cross_nm"])]][along_index[float(row["along_nm"])]] = float(row["publication_trace_rank8_correlation_r"])
    image = axes[0, 1].imshow(
        correlation_grid,
        origin="lower",
        aspect="auto",
        extent=(min(along_values), max(along_values), min(cross_values), max(cross_values)),
        cmap="coolwarm",
        vmin=-0.13,
        vmax=0.13,
    )
    colours = ["#111111", "#E69F00", "#009E73", "#CC79A7"]
    for colour, candidate in zip(colours, configuration["reverse_candidates"]):
        selected = [row for row in reverse_rows if row["candidate_id"] == candidate["id"]]
        if selected:
            step = max(1, len(selected) // 350)
            axes[0, 1].scatter(
                [float(row["along_nm"]) for row in selected[::step]],
                [float(row["cross_nm"]) for row in selected[::step]],
                s=8,
                facecolors="none",
                edgecolors=colour,
                linewidths=0.55,
                label=candidate["id"].replace("_", " "),
            )
    axes[0, 1].set_xlabel("Along seventh arc (NM)")
    axes[0, 1].set_ylabel("Cross-arc offset (NM)")
    axes[0, 1].set_title("B. Rank-8 publication-trace correlation and reverse-window intersections")
    axes[0, 1].legend(fontsize=7.2, frameon=True, facecolor="white", loc="lower left")
    figure.colorbar(image, ax=axes[0, 1], label="Two-station energy correlation r")

    along = np.asarray([float(row["along_nm"]) for row in centre])
    for station_id, colour in (("h01w", "#4477AA"), ("h08s", "#CC6677")):
        minimum = np.asarray([seconds_after_midnight(parse_utc(row[f"{station_id}_arrival_min_utc"])) / 60.0 for row in centre])
        median = np.asarray([seconds_after_midnight(parse_utc(row[f"{station_id}_arrival_median_utc"])) / 60.0 for row in centre])
        maximum = np.asarray([seconds_after_midnight(parse_utc(row[f"{station_id}_arrival_max_utc"])) / 60.0 for row in centre])
        label = "Cape Leeuwin H01W" if station_id == "h01w" else "Diego Garcia H08S"
        axes[1, 0].fill_between(along, minimum, maximum, color=colour, alpha=0.15)
        axes[1, 0].plot(along, median, color=colour, linewidth=1.5, label=label)
    axes[1, 0].set_xlabel("Along seventh arc (NM); centreline boxes")
    axes[1, 0].set_ylabel("Predicted arrival, minutes after 00:00 UTC")
    axes[1, 0].set_title("C. Arrival envelopes across the 00:19:37–00:49:37 impact-time sensitivity")
    axes[1, 0].grid(alpha=0.16)
    axes[1, 0].legend(frameon=False)

    reference = min(forward_rows, key=lambda row: (float(row["latitude_deg"]) + 34.9167) ** 2 + (float(row["longitude_deg_e"]) - 92.0472) ** 2)
    family_ids = [row["id"] for row in configuration["impact_scenario_bank"]["impact_families"]]
    family_labels = [value.replace("_", " ") for value in family_ids]
    y = np.arange(len(family_ids), dtype=float)
    coupling = 1.0e-4
    for offset, (station, distance_key, colour) in enumerate((("H01W", "h01w_distance_km", "#4477AA"), ("H08S", "h08s_distance_km", "#CC6677"))):
        medians = []
        for family_id in family_ids:
            scenario = next(row for row in scenarios if row["impact_family"] == family_id)
            medians.append(float(pressure_from_coupled_energy(np.asarray([scenario["vertical_kinetic_energy_j"] * coupling]), float(reference[distance_key]))[0]))
        axes[1, 1].scatter(medians, y + (-0.08 if offset == 0 else 0.08), color=colour, label=station)
    axes[1, 1].set_xscale("log")
    axes[1, 1].set_yticks(y, family_labels)
    axes[1, 1].invert_yaxis()
    axes[1, 1].set_xlabel("Peak-pressure proxy (Pa), conditional coupling fraction 10⁻⁴")
    axes[1, 1].set_title(f"D. Source-family signal scale at representative box {reference['cell_id']}")
    axes[1, 1].grid(axis="x", which="both", alpha=0.16)
    axes[1, 1].legend(frameon=False)

    figure.suptitle(
        "Hydroacoustic v0.1 forward and reverse diagnostic\n"
        "169,248 box–scenario combinations; every result has zero estimator weight",
        fontsize=15.0,
    )
    figure.text(
        0.5,
        0.006,
        "Correlation uses already-filtered Figure 9 vectors. Complete-search controls give p=1.000 unfiltered and p=0.964 after rank-8 suppression; coloured maxima are not event associations or locations.",
        ha="center",
        fontsize=8.2,
    )
    figure.tight_layout(rect=(0.0, 0.025, 1.0, 0.95))
    return save_figure(figure, "hydroacoustic-forward-reverse-diagnostic")


def make_signal_figure(signal_rows: list[dict], reference_cell_id: str) -> list[Path]:
    figure, axes = plt.subplots(2, 1, figsize=(13.5, 8.2), sharex=True)
    colours = {
        "controlled_ditching_class": "#4477AA",
        "flight1549_contact_analogue": "#228833",
        "partially_arrested_bridge": "#CCBB44",
        "unarrested_high_rate": "#CC6677",
    }
    for axis, station in zip(axes, ("H01W", "H08S")):
        for family, colour in colours.items():
            selected = [row for row in signal_rows if row["station"] == station and row["impact_family"] == family]
            axis.plot(
                [row["seconds_from_predicted_arrival"] for row in selected],
                [row["simulated_pressure_pa"] for row in selected],
                color=colour,
                linewidth=1.0,
                label=family.replace("_", " "),
            )
        axis.set_ylabel("Pressure proxy (Pa)")
        axis.set_title(station)
        axis.grid(alpha=0.15)
    axes[0].legend(ncol=2, frameon=False, fontsize=8.0)
    axes[1].set_xlabel("Seconds from predicted station arrival")
    figure.suptitle(
        f"Illustrative reduced-order impact signal bank — box {reference_cell_id}\n"
        "Fixed coupling 10⁻⁴; waveform shape is illustrative and is not a receiver template",
        fontsize=14.0,
    )
    figure.tight_layout(rect=(0.0, 0.01, 1.0, 0.93))
    return save_figure(figure, "representative-simulated-signals")


def write_html(summary: dict, reverse_summaries: list[dict]) -> Path:
    def inline_svg(path: Path) -> str:
        document = path.read_text(encoding="utf-8")
        return document[document.index("<svg") :]

    overview_svg = inline_svg(OUTPUT / "hydroacoustic-forward-reverse-diagnostic.svg")
    signal_svg = inline_svg(OUTPUT / "representative-simulated-signals.svg")
    reverse_rows = "".join(
        "<tr>"
        f"<td>{html.escape(row['candidate_id'])}</td>"
        f"<td>{row['compatible_cell_count']}</td>"
        f"<td>{html.escape(str(row['along_arc_min_nm']))}–{html.escape(str(row['along_arc_max_nm']))}</td>"
        f"<td>{html.escape(str(row['cross_arc_min_nm']))}–{html.escape(str(row['cross_arc_max_nm']))}</td>"
        f"<td>{html.escape(row['candidate_status'])}</td>"
        "</tr>"
        for row in reverse_summaries
    )
    document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>MH370 hydroacoustic v0.1 diagnostic</title>
<style>
body{{font-family:Arial,sans-serif;max-width:1500px;margin:0 auto;padding:24px;color:#1f2933}}h1,h2{{color:#17324d}}
.warning{{background:#fff3cd;border-left:6px solid #d99b00;padding:14px;margin:18px 0}}.good{{background:#eaf4ef;border-left:6px solid #2d7d5c;padding:14px}}
table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border:1px solid #ccd6df;padding:7px;text-align:left}}th{{background:#edf2f7}}
svg{{width:100%;height:auto}}code{{background:#eef2f5;padding:2px 4px}}a{{color:#175a9b}}
</style></head><body>
<h1>MH370 hydroacoustic v0.1 forward/reverse diagnostic</h1>
<div class="warning"><strong>Evidence disposition: diagnostic, zero weight.</strong> No publication-trace or simulated signal changes the impact posterior. The most attractive complete-grid match is expected under the available nulls: unfiltered scan-adjusted p={summary['publication_trace_control']['unfiltered_scan_adjusted_p']:.3f}; rank-8 p={summary['publication_trace_control']['rank8_scan_adjusted_p']:.3f}.</div>
<div class="good">The release evaluates {summary['source_cell_count']:,} source boxes × {summary['scenario_template_count']} conditional impact templates = {summary['expanded_box_scenario_count']:,} forward combinations at Cape Leeuwin and Diego Garcia. It also reverse-traces four declared candidate constructions against the same grid.</div>
<h2>Forward and reverse geometry</h2>{overview_svg}
<h2>Reverse candidate summaries</h2><table><thead><tr><th>Candidate</th><th>Compatible boxes</th><th>Along arc (NM)</th><th>Cross arc (NM)</th><th>Boundary</th></tr></thead><tbody>{reverse_rows}</tbody></table>
<h2>Illustrative simulated signals</h2>{signal_svg}
<p>These pulses communicate amplitude and duration sensitivity only. They are not CFD-derived water-entry waveforms, path-specific Green-function outputs, or calibrated receiver templates.</p>
<h2>Raw-triad path</h2>
<p><code>raw_triad_adapter.py</code> validates/calibrates each three-channel CSV and emits deterministic NPY arrays plus a hash receipt. <code>raw_triad_search.py</code> then runs a complete-grid, channel-incoherent 2–40 Hz energy correlation with station time-slide maxima. It can be run by Kadri without sharing restricted raw samples. A coherent bearing likelihood remains out of scope until array geometry, responses, clock corrections and blinded injections are available.</p>
<p>Machine outputs: <a href="forward-grid.csv">forward grid</a>, <a href="impact-scenario-templates.json">scenario templates</a>, <a href="reverse-matches.csv">reverse matches</a>, <a href="summary.json">summary</a>, <a href="manifest.json">manifest</a>, and <a href="citation-ledger.md">citation ledger</a>.</p>
</body></html>"""
    path = OUTPUT / "index.html"
    path.write_text(document, encoding="utf-8")
    return path


def main() -> None:
    assert_release_tree_clean()
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    if configuration["schema_id"] != "mh370-hydroacoustic-release-workflow" or configuration["schema_version"] != 1:
        raise ValueError("unsupported release configuration")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    cells, correlation, scan_summary = load_inputs(configuration)
    scenarios = scenario_bank(configuration)
    forward = forward_grid_rows(configuration, cells, correlation, scenarios)
    reverse, reverse_summaries = reverse_matches(configuration, cells, scenarios)
    signals, reference_cell_id = make_signal_bank(configuration, forward, scenarios)

    forward_path = OUTPUT / "forward-grid.csv"
    reverse_path = OUTPUT / "reverse-matches.csv"
    signal_path = OUTPUT / "representative-simulated-signals.csv"
    scenario_path = OUTPUT / "impact-scenario-templates.json"
    write_csv(forward_path, forward)
    write_csv(reverse_path, reverse)
    write_csv(signal_path, signals)
    scenario_path.write_text(json.dumps({"schema_id": "mh370-hydroacoustic-impact-scenario-templates", "schema_version": 1, "templates": scenarios}, indent=2) + "\n", encoding="utf-8")

    figure_paths = make_overview_figure(configuration, forward, reverse, scenarios)
    figure_paths += make_signal_figure(signals, reference_cell_id)
    unfiltered = read_csv(resolve(configuration["publication_trace_controls"]["unfiltered_top_path"]))[0]
    filtered = read_csv(resolve(configuration["publication_trace_controls"]["filtered_top_path"]))[0]
    summary = {
        "schema_id": "mh370-hydroacoustic-release-summary",
        "schema_version": 1,
        "status": "RELEASEABLE_DIAGNOSTIC_ZERO_WEIGHT",
        "source_cell_count": len(cells),
        "source_grid_extent": configuration["source_grid"],
        "scenario_template_count": len(scenarios),
        "expanded_box_scenario_count": len(cells) * len(scenarios),
        "station_prediction_count": len(cells) * len(scenarios) * len(configuration["stations"]),
        "reference_signal_cell_id": reference_cell_id,
        "reverse_candidates": reverse_summaries,
        "publication_trace_control": {
            "unfiltered_maximum_energy_correlation_r": float(unfiltered["energy_correlation_r"]),
            "unfiltered_scan_adjusted_p": float(unfiltered["iaaft_scan_max_p"]),
            "rank8_maximum_energy_correlation_r": float(filtered["energy_correlation_r"]),
            "rank8_scan_adjusted_p": float(filtered["iaaft_scan_max_p"]),
            "complete_scan_status": scan_summary["status"],
            "conclusion": "no two-station association survives complete-search correction in the publication traces",
        },
        "evidence_disposition": "diagnostic_zero_weight",
        "likelihood_evaluated": False,
        "log_weight_increment": 0.0,
        "release_boundaries": [
            "impact families and coupling values form an unweighted sensitivity bank",
            "straight-path celerity bounds are not bathymetric propagation Green functions",
            "publication vectors are already-filtered plotted paths, not raw CTBTO triad channels",
            "correlation, arrival, pressure and reverse-window results cannot reweight the estimator",
            "raw-triad likelihood remains blocked on response/timing metadata and blinded injection calibration",
        ],
    }
    summary_path = OUTPUT / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    html_path = write_html(summary, reverse_summaries)

    citation_path = OUTPUT / "citation-ledger.md"
    citation_path.write_text(
        "# Hydroacoustic v0.1 citation ledger\n\n"
        "| Claim | Source | Locator | Located passage | Status |\n"
        "| --- | --- | --- | --- | --- |\n"
        "| Kadri's declared propagation control is 1.50 ± 0.07 km/s. | Kadri (2024), doi:10.1038/s41598-024-60529-1 | PDF p. 13 | “an acoustic signal travelling with a speed of c = 1500 ± 70 m/s” | FOUND; used only as a broad timing control |\n"
        "| The preferred H01W catalogue candidate is 00:54:30 UTC at 306.18°. | Kadri (2024) | PDF p. 14, Table 1 caption and row | “00:54:30 UTC with bearing 306.18°” | FOUND; selected candidate, not an association |\n"
        "| Bearing reconstruction needs all three channels. | Kadri (2024) | PDF p. 11 | time of arrival is estimated from the “maximum of the cross-correlation function across channel pairs” | FOUND; unavailable in the publication trace |\n"
        "| The paper applies a 2–40 Hz band-pass and an additional high-pass below 5 Hz. | Kadri (2024) | PDF p. 11 | “a 2–40 [Hz] band-pass filter was applied” | FOUND; raw baseline uses 2–40 Hz and records the difference |\n"
        "| Scientific users can request IMS data through vDEC, but access is generally organization-based and raw data may not be redistributed. | CTBTO vDEC | https://www.ctbto.org/resources/for-researchers-experts/vdec, ‘How to request data’ and ‘Conditions of Use’ | “open to organizations rather than individual researchers”; “Data shall not be redistributed to third parties.” | FOUND; explains Kadri-run adapter |\n"
        "| The publication-trace complete scan is not significant. | This source package | two-station-correlation summary/top-10 tables | unfiltered p=1.000; rank-8 p=0.964 | DERIVED; complete-search stationary-surrogate control |\n",
        encoding="utf-8",
    )

    stable_paths = [
        forward_path,
        reverse_path,
        signal_path,
        scenario_path,
        summary_path,
        html_path,
        citation_path,
        *figure_paths,
    ]
    manifest = {
        "schema_id": "mh370-hydroacoustic-release-manifest",
        "schema_version": 1,
        "status": "REPRODUCIBLE_DIAGNOSTIC_ZERO_WEIGHT",
        "command": ".venv/bin/python -B .sources/kadri-2024-hydroacoustics/code/hydro_release_workflow.py",
        "configuration_sha256": sha256(CONFIG_PATH),
        "code_sha256": sha256(Path(__file__)),
        "input_sha256": {
            configuration["source_grid"]["path"]: configuration["source_grid"]["sha256"],
            configuration["publication_trace_controls"]["grid_path"]: configuration["publication_trace_controls"]["grid_sha256"],
            configuration["publication_trace_controls"]["unfiltered_top_path"]: configuration["publication_trace_controls"]["unfiltered_top_sha256"],
            configuration["publication_trace_controls"]["filtered_top_path"]: configuration["publication_trace_controls"]["filtered_top_sha256"],
            configuration["publication_trace_controls"]["summary_path"]: configuration["publication_trace_controls"]["summary_sha256"],
        },
        "outputs": {path.name: sha256(path) for path in stable_paths},
        "artifact_hygiene": {
            "verified_clean": True,
            "rejected_directory_names": sorted(REJECTED_DIRECTORY_NAMES),
            "rejected_file_suffixes": sorted(REJECTED_FILE_SUFFIXES),
            "rejected_backup_suffix": "~",
            "scope": ".sources/kadri-2024-hydroacoustics",
        },
        "evidence_disposition": "diagnostic_zero_weight",
    }
    manifest_path = OUTPUT / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    assert_release_tree_clean()
    hash_ledger = {
        "schema_id": "mh370-hydroacoustic-artifact-hash-ledger",
        "schema_version": 1,
        "artifact_hygiene": manifest["artifact_hygiene"],
        "sha256": {path.name: sha256(path) for path in [*stable_paths, manifest_path]},
    }
    (OUTPUT / "artifact-sha256.json").write_text(json.dumps(hash_ledger, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
