#!/usr/bin/env python3
"""Run the declared Davey-configuration bootstrap particle filter.

This is a published-parameter reconstruction. See model-configuration.json for
the exact published values and the five explicitly declared input substitutes.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import gzip
import hashlib
import json
import math
import platform
import time
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from model import (
    G_M_S2,
    angle_difference,
    bfo_components,
    bto_us,
    destination,
    final_bearing,
    isa_temperature_kelvin,
    normalize_log_weights,
    normal_logpdf,
    ou_step,
    speed_of_sound_knots,
    systematic_resample,
    weighted_quantile,
    wrap360,
)


BUNDLE = Path(__file__).resolve().parents[1]
ROOT = BUNDLE
INPUTS = BUNDLE / "data"
OUTPUT = BUNDLE / "outputs"
CONFIG_PATH = INPUTS / "model-configuration.json"
OBS_PATH = INPUTS / "observations.csv"
SAT_PATH = INPUTS / "satellite_ephemeris.csv"
T0 = dt.datetime(2014, 3, 7, 18, 1, 49)
MODE_LABELS = np.array(["constant_true_heading", "constant_magnetic_heading", "constant_true_track", "constant_magnetic_track", "lateral_navigation"])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_inputs():
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    with OBS_PATH.open(newline="", encoding="utf-8") as handle:
        observations = list(csv.DictReader(handle))
    with SAT_PATH.open(newline="", encoding="utf-8") as handle:
        satellites = {row["epoch_id"]: row for row in csv.DictReader(handle)}
    for observation in observations:
        for field in ("seconds_from_t0", "bto_us", "bto_sd_us", "bfo_hz", "bfo_sd_hz", "satellite_afc_hz"):
            observation[field] = None if observation[field] == "" else float(observation[field])
        sat = satellites[observation["epoch_id"]]
        observation["sat_position"] = np.array([float(sat[key]) for key in ("x_km", "y_km", "z_km")])
        observation["sat_velocity"] = np.array([float(sat[key]) for key in ("vx_km_s", "vy_km_s", "vz_km_s")])
    return config, observations


def initialize(n, rng, config):
    radar = config["radar_prior"]
    dynamics = config["dynamics"]
    north_nm = rng.normal(0.0, radar["position_sd_nm"], n)
    east_nm = rng.normal(0.0, radar["position_sd_nm"], n)
    lat = radar["mean_latitude_deg"] + north_nm / 60.0
    lon = radar["mean_longitude_deg"] + east_nm / (60.0 * math.cos(math.radians(radar["mean_latitude_deg"])))
    control_set = rng.normal(radar["mean_control_angle_deg_true"], radar["control_angle_sd_deg"], n)
    control = control_set + rng.normal(0.0, dynamics["angle_initial_deviation_sd_deg"], n)
    mach_set = rng.uniform(radar["mach_min"], radar["mach_max"], n)
    mach = mach_set + rng.normal(0.0, dynamics["mach_initial_deviation_sd"], n)
    altitude = rng.integers(25, 44, n).astype(float) * 1000.0
    tau = np.exp(rng.uniform(math.log(dynamics["manoeuvre_tau_hours_min"]), math.log(dynamics["manoeuvre_tau_hours_max"]), n))
    scale = tau * 3600.0
    weights_by_mode = np.array(list(dynamics["mode_weights_substitute"].values()), dtype=float)
    weights_by_mode /= weights_by_mode.sum()
    mode = rng.choice(5, n, p=weights_by_mode)
    state = {
        "lat": lat,
        "lon": lon,
        "mach": mach,
        "mach_set": mach_set,
        "mach_target": mach_set.copy(),
        "control": control,
        "control_set": control_set,
        "control_target": control_set.copy(),
        "altitude_ft": altitude,
        "altitude_target_ft": altitude.copy(),
        "vertical_speed_fpm": np.zeros(n),
        "wind_north_kt": rng.normal(0.0, dynamics["wind_initial_deviation_sd_kt"], n),
        "wind_east_kt": rng.normal(0.0, dynamics["wind_initial_deviation_sd_kt"], n),
        "ground_north_kt": np.zeros(n),
        "ground_east_kt": np.zeros(n),
        "ground_speed_kt": np.zeros(n),
        "ground_track_deg": wrap360(control),
        "tau_hours": tau,
        "mode": mode,
        "next_turn_s": rng.exponential(scale),
        "next_speed_s": rng.exponential(scale),
        "next_altitude_s": rng.exponential(scale),
        "lnav_switch_s": rng.exponential(dynamics["lnav_heading_hold_switch_mean_hours"] * 3600.0, n),
        "turn_count": np.zeros(n, dtype=np.int16),
        "turn_count_after_1839": np.zeros(n, dtype=np.int16),
        "speed_change_count": np.zeros(n, dtype=np.int16),
        "altitude_change_count": np.zeros(n, dtype=np.int16),
        "bfo_bias_mean_hz": np.full(n, config["satcom"]["bfo_bias_prior_mean_hz"]),
        "bfo_bias_variance_hz2": np.full(n, config["satcom"]["bfo_bias_prior_sd_hz"] ** 2),
    }
    update_ground_velocity(state)
    return state


def fire_events(state, current_time_s, rng, config):
    dynamics = config["dynamics"]
    tau_seconds = state["tau_hours"] * 3600.0
    turn = state["next_turn_s"] <= current_time_s
    if np.any(turn):
        state["control_target"][turn] = state["control_set"][turn] + rng.uniform(
            dynamics["turn_delta_min_deg"], dynamics["turn_delta_max_deg"], np.count_nonzero(turn)
        )
        state["next_turn_s"][turn] = current_time_s + rng.exponential(tau_seconds[turn])
        state["turn_count"][turn] += 1
        if current_time_s >= (dt.datetime(2014, 3, 7, 18, 39, 55) - T0).total_seconds():
            state["turn_count_after_1839"][turn] += 1

    speed = state["next_speed_s"] <= current_time_s
    if np.any(speed):
        state["mach_target"][speed] = rng.uniform(dynamics["new_mach_min"], dynamics["new_mach_max"], np.count_nonzero(speed))
        state["next_speed_s"][speed] = current_time_s + rng.exponential(tau_seconds[speed])
        state["speed_change_count"][speed] += 1

    altitude = state["next_altitude_s"] <= current_time_s
    if np.any(altitude):
        state["altitude_target_ft"][altitude] = rng.integers(25, 44, np.count_nonzero(altitude)) * 1000.0
        state["next_altitude_s"][altitude] = current_time_s + rng.exponential(tau_seconds[altitude])
        state["altitude_change_count"][altitude] += 1

    lnav_switch = (state["mode"] == 4) & (state["lnav_switch_s"] <= current_time_s)
    if np.any(lnav_switch):
        # Equal split between true and magnetic heading is an unpublished mode-prior substitute.
        state["mode"][lnav_switch] = rng.integers(0, 2, np.count_nonzero(lnav_switch))
        state["lnav_switch_s"][lnav_switch] = np.inf


def update_ground_velocity(state):
    tas = state["mach"] * speed_of_sound_knots(isa_temperature_kelvin(state["altitude_ft"]))
    angle = np.radians(wrap360(state["control"]))
    desired_north = np.cos(angle)
    desired_east = np.sin(angle)
    heading_mode = state["mode"] <= 1
    track_mode = ~heading_mode
    north = np.empty_like(tas)
    east = np.empty_like(tas)
    north[heading_mode] = tas[heading_mode] * desired_north[heading_mode] + state["wind_north_kt"][heading_mode]
    east[heading_mode] = tas[heading_mode] * desired_east[heading_mode] + state["wind_east_kt"][heading_mode]
    if np.any(track_mode):
        along = state["wind_north_kt"] * desired_north + state["wind_east_kt"] * desired_east
        cross = -state["wind_north_kt"] * desired_east + state["wind_east_kt"] * desired_north
        ground_speed = along + np.sqrt(np.maximum(tas * tas - cross * cross, 1.0))
        north[track_mode] = ground_speed[track_mode] * desired_north[track_mode]
        east[track_mode] = ground_speed[track_mode] * desired_east[track_mode]
    state["ground_north_kt"] = north
    state["ground_east_kt"] = east
    state["ground_speed_kt"] = np.hypot(north, east)
    state["ground_track_deg"] = wrap360(np.degrees(np.arctan2(east, north)))


def step(state, dt_seconds, current_time_s, rng, config):
    dynamics = config["dynamics"]
    fire_events(state, current_time_s, rng, config)

    state["mach_set"] += np.clip(
        state["mach_target"] - state["mach_set"],
        -dynamics["mach_change_rate_per_min"] * dt_seconds / 60.0,
        dynamics["mach_change_rate_per_min"] * dt_seconds / 60.0,
    )
    tas_m_s = state["mach"] * speed_of_sound_knots(isa_temperature_kelvin(state["altitude_ft"])) * 0.5144444444444445
    max_turn_deg = np.degrees(np.tan(math.radians(dynamics["bank_angle_deg"])) * G_M_S2 / np.maximum(tas_m_s, 1.0)) * dt_seconds
    state["control_set"] += np.clip(angle_difference(state["control_target"], state["control_set"]), -max_turn_deg, max_turn_deg)
    altitude_difference = state["altitude_target_ft"] - state["altitude_ft"]
    max_altitude_step = dynamics["altitude_change_rate_ft_per_min"] * dt_seconds / 60.0
    altitude_step = np.clip(altitude_difference, -max_altitude_step, max_altitude_step)
    state["altitude_ft"] += altitude_step
    state["vertical_speed_fpm"] = altitude_step / dt_seconds * 60.0

    state["mach"] = ou_step(state["mach"], state["mach_set"], dynamics["mach_reversion_rate_s"], dynamics["mach_noise_strength_per_s"], dt_seconds, rng)
    angle_q_deg2 = dynamics["angle_noise_strength_rad2_per_s"] * (180.0 / math.pi) ** 2
    state["control"] = ou_step(state["control"], state["control_set"], dynamics["angle_reversion_rate_s"], angle_q_deg2, dt_seconds, rng)
    zeros = np.zeros_like(state["wind_north_kt"])
    state["wind_north_kt"] = ou_step(state["wind_north_kt"], zeros, dynamics["wind_reversion_rate_s"], dynamics["wind_noise_strength_kt2_per_s"], dt_seconds, rng)
    state["wind_east_kt"] = ou_step(state["wind_east_kt"], zeros, dynamics["wind_reversion_rate_s"], dynamics["wind_noise_strength_kt2_per_s"], dt_seconds, rng)
    update_ground_velocity(state)

    old_lat = state["lat"]
    old_lon = state["lon"]
    new_lat, new_lon = destination(old_lat, old_lon, state["ground_track_deg"], state["ground_speed_kt"] * dt_seconds / 3600.0)
    lnav = state["mode"] == 4
    if np.any(lnav):
        next_bearing = final_bearing(old_lat[lnav], old_lon[lnav], new_lat[lnav], new_lon[lnav])
        delta = angle_difference(next_bearing, state["ground_track_deg"][lnav])
        state["control"][lnav] += delta
        state["control_set"][lnav] += delta
        state["control_target"][lnav] += delta
    state["lat"] = new_lat
    state["lon"] = new_lon


def propagate(state, start_s, end_s, rng, config):
    current = start_s
    base_step = config["particles"]["integration_step_seconds"]
    while current < end_s - 1e-9:
        dt_seconds = min(base_step, end_s - current)
        step(state, dt_seconds, current, rng, config)
        current += dt_seconds


def resample_state(state, weights, rng):
    index = systematic_resample(weights, rng)
    for key, value in tuple(state.items()):
        state[key] = value[index]
    return np.full(len(index), 1.0 / len(index))


def measurement_update(state, weights, observation, use_bfo, config):
    satcom = config["satcom"]
    log_likelihood = np.zeros_like(weights)
    output = {"epoch_id": observation["epoch_id"], "time_utc": observation["time_utc"]}
    if observation["bto_us"] is not None:
        predicted_bto = bto_us(
            state["lat"], state["lon"], state["altitude_ft"], observation["sat_position"], satcom["perth_ges_ecef_km"],
            satcom["speed_of_light_km_s"], satcom["bto_nominal_delay_us"], satcom["bto_r1200_channel_term_us"],
        )
        residual = observation["bto_us"] - predicted_bto
        state[f"bto_residual_{observation['epoch_id']}"] = residual
        log_likelihood += normal_logpdf(residual, observation["bto_sd_us"])
        output["bto_residual_prior_weighted_mean_us"] = float(np.sum(weights * residual))
    if use_bfo and observation["bfo_hz"] is not None:
        components = bfo_components(
            state["lat"], state["lon"], state["altitude_ft"], state["ground_north_kt"], state["ground_east_kt"], state["vertical_speed_fpm"],
            observation["sat_position"], observation["sat_velocity"], satcom["perth_ges_ecef_km"], observation["satellite_afc_hz"],
            satcom["bfo_uplink_hz"], satcom["bfo_downlink_hz"], satcom["speed_of_light_km_s"], satcom["nominal_satellite_longitude_deg"], satcom["nominal_satellite_altitude_km"],
        )
        base = components["base_without_bias_hz"]
        innovation = observation["bfo_hz"] - base - state["bfo_bias_mean_hz"]
        innovation_variance = state["bfo_bias_variance_hz2"] + observation["bfo_sd_hz"] ** 2
        state[f"bfo_residual_{observation['epoch_id']}"] = innovation
        log_likelihood += -0.5 * innovation * innovation / innovation_variance - 0.5 * np.log(2.0 * math.pi * innovation_variance)
        gain = state["bfo_bias_variance_hz2"] / innovation_variance
        state["bfo_bias_mean_hz"] += gain * innovation
        state["bfo_bias_variance_hz2"] *= 1.0 - gain
        output["bfo_innovation_prior_weighted_mean_hz"] = float(np.sum(weights * innovation))
    updated = normalize_log_weights(np.log(np.maximum(weights, np.finfo(float).tiny)) + log_likelihood)
    output["effective_sample_size"] = float(1.0 / np.sum(updated * updated))
    output["effective_sample_fraction"] = output["effective_sample_size"] / len(updated)
    output["log_likelihood_increment_max_shifted"] = float(np.log(np.sum(np.exp(log_likelihood - np.max(log_likelihood)))) + np.max(log_likelihood) - math.log(len(log_likelihood)))
    return updated, output


def state_summary(state, weights):
    def q(key):
        values = weighted_quantile(state[key], weights, (0.025, 0.5, 0.975))
        return {"q025": float(values[0]), "median": float(values[1]), "q975": float(values[2])}
    bins = np.arange(-50.0, 30.0001, 0.2)
    counts, edges = np.histogram(state["lat"], bins=bins, weights=weights)
    mode_lat = float((edges[np.argmax(counts)] + edges[np.argmax(counts) + 1]) / 2.0)
    mode_mass = {label: float(np.sum(weights[state["mode"] == index])) for index, label in enumerate(MODE_LABELS)}
    return {
        "latitude_deg": q("lat"),
        "longitude_deg_E": q("lon"),
        "altitude_ft": q("altitude_ft"),
        "mach": q("mach"),
        "tau_hours": q("tau_hours"),
        "bfo_bias_mean_hz": q("bfo_bias_mean_hz"),
        "latitude_mode_deg_bin_0_2": mode_lat,
        "probability_north_of_equator": float(np.sum(weights[state["lat"] > 0.0])),
        "probability_tau_gt_1h": float(np.sum(weights[state["tau_hours"] > 1.0])),
        "probability_tau_gt_2h": float(np.sum(weights[state["tau_hours"] > 2.0])),
        "mean_turn_count": float(np.sum(weights * state["turn_count"])),
        "mean_turn_count_after_1839": float(np.sum(weights * state["turn_count_after_1839"])),
        "mean_speed_change_count": float(np.sum(weights * state["speed_change_count"])),
        "mode_probability": mode_mass,
        "final_effective_sample_size": float(1.0 / np.sum(weights * weights)),
    }


def latitude_curve(state, weights, minimum=-50.0, maximum=30.0, width=0.2):
    edges = np.arange(minimum, maximum + width * 1.01, width)
    density, edges = np.histogram(state["lat"], bins=edges, weights=weights, density=False)
    centers = (edges[:-1] + edges[1:]) / 2.0
    kernel_x = np.arange(-4, 5)
    kernel = np.exp(-0.5 * (kernel_x / 1.5) ** 2)
    kernel /= kernel.sum()
    density = np.convolve(density, kernel, mode="same")
    density /= max(np.trapezoid(density, centers), np.finfo(float).tiny)
    return centers, density


def write_curve(tag, state, weights):
    centers, density = latitude_curve(state, weights)
    path = OUTPUT / f"latitude_pdf_{tag}.csv"
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(("latitude_deg", "density_per_deg"))
        writer.writerows(zip(centers, density))
    return path


def write_samples(tag, state, weights, rng, count=80000):
    count = min(count, len(weights))
    index = rng.choice(len(weights), size=count, replace=True, p=weights)
    columns = [
        "lat", "lon", "altitude_ft", "mach", "control", "ground_speed_kt", "ground_track_deg", "tau_hours", "mode",
        "turn_count", "turn_count_after_1839", "speed_change_count", "altitude_change_count", "bfo_bias_mean_hz",
    ]
    residual_columns = sorted(key for key in state if key.startswith("bto_residual_") or key.startswith("bfo_residual_"))
    path = OUTPUT / f"posterior_samples_{tag}.csv.gz"
    with gzip.open(path, "wt", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns + residual_columns)
        for particle in index:
            row = []
            for key in columns:
                value = state[key][particle]
                if key == "mode":
                    value = MODE_LABELS[int(value)]
                row.append(value)
            row.extend(state[key][particle] for key in residual_columns)
            writer.writerow(row)
    return path


def plot_map(tag, state, weights):
    fig, axis = plt.subplots(figsize=(8.4, 8.0), constrained_layout=True)
    histogram, xedges, yedges = np.histogram2d(state["lon"], state["lat"], bins=(220, 220), range=((70, 115), (-48, 18)), weights=weights)
    image = axis.pcolormesh(xedges, yedges, histogram.T, shading="auto", cmap="magma")
    axis.set_xlim(80, 110)
    axis.set_ylim(-45, 12)
    axis.set_xlabel("Longitude (°E)")
    axis.set_ylabel("Latitude (°)")
    axis.grid(color="white", alpha=0.18, linewidth=0.5)
    axis.set_title(f"Davey-configuration reconstruction: aircraft position at 00:19 UTC\n{tag.replace('_', ' ')}")
    fig.colorbar(image, ax=axis, label="posterior probability per grid cell")
    path = OUTPUT / f"map_{tag}.png"
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return path


def run_filter(n, seed, use_bfo, tag, make_plot=False):
    config, observations = load_inputs()
    rng = np.random.default_rng(seed)
    state = initialize(n, rng, config)
    weights = np.full(n, 1.0 / n)
    current = 0.0
    diagnostics = []
    snapshot_0011 = None
    start_wall = time.time()
    for index, observation in enumerate(observations):
        propagate(state, current, observation["seconds_from_t0"], rng, config)
        current = observation["seconds_from_t0"]
        weights, diagnostic = measurement_update(state, weights, observation, use_bfo, config)
        is_final = index == len(observations) - 1
        if not is_final and diagnostic["effective_sample_fraction"] < config["particles"]["resample_ess_fraction"]:
            weights = resample_state(state, weights, rng)
            diagnostic["resampled"] = True
        else:
            diagnostic["resampled"] = False
        diagnostics.append(diagnostic)
        if observation["epoch_id"] == "m0011":
            snapshot_0011 = state_summary(state, weights)
        print(json.dumps({"tag": tag, "epoch": observation["epoch_id"], "ess_fraction": diagnostic["effective_sample_fraction"], "resampled": diagnostic["resampled"]}), flush=True)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    summary = {
        "model": "davey-configuration-reconstruction",
        "tag": tag,
        "status": "PUBLISHED_PARAMETER_RECONSTRUCTION",
        "uses_bfo_through_0011": use_bfo,
        "uses_final_bfo": False,
        "particle_count": n,
        "seed": seed,
        "elapsed_seconds": time.time() - start_wall,
        "state_0011": snapshot_0011,
        "state_0019": state_summary(state, weights),
        "measurement_diagnostics": diagnostics,
        "input_hashes": {path.name: sha256(path) for path in (CONFIG_PATH, OBS_PATH, SAT_PATH, INPUTS / "input-manifest.json")},
        "runtime": {"python": platform.python_version(), "numpy": np.__version__, "platform": platform.platform()},
        "fidelity_limits": [
            "reconstructed rather than tabulated 18:01:49 mean and diffuse initial-altitude substitute",
            "ISA/zero nominal wind replaces unavailable ACCESS-G cube; published OU wind error retained",
            "equal autopilot-mode weights, zero magnetic declination and unspecified LNAV destination substitutes",
            "fixed-N bootstrap SMC replaces Davey depth-first branching implementation",
            "released regular-epoch satellite/EAFC corrections with linear C-channel interpolation replace proprietary 10-second series",
        ],
    }
    curve_path = write_curve(tag, state, weights)
    sample_path = write_samples(tag, state, weights, rng)
    artifacts = {"latitude_pdf": str(curve_path.relative_to(ROOT)), "posterior_samples": str(sample_path.relative_to(ROOT))}
    if make_plot:
        artifacts["map"] = str(plot_map(tag, state, weights).relative_to(ROOT))
    summary["artifacts"] = artifacts
    summary_path = OUTPUT / f"summary_{tag}.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"completed": tag, "summary": summary["state_0019"], "path": str(summary_path)}, indent=2))
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--particles", type=int, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--case", choices=("bto_bfo", "bto_only"), required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--plot", action="store_true")
    args = parser.parse_args()
    run_filter(args.particles, args.seed, args.case == "bto_bfo", args.tag, args.plot)


if __name__ == "__main__":
    main()
