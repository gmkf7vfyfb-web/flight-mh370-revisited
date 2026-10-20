#!/usr/bin/env python3
"""Transparent geometry and link-budget checks for the WSPR source audit."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


C_METRES_PER_SECOND = 299_792_458.0


def fraction_below_altitude(altitude_km: float, apex_height_km: float) -> float:
    """Path/time fraction below ``altitude_km`` in a straight triangular hop.

    Both sloping legs are linear in altitude, so the result is h/H. It is
    independent of hop length and of the number of identical hops.
    """
    if not 0.0 <= altitude_km <= apex_height_km:
        raise ValueError("altitude must lie between zero and the hop apex")
    return altitude_km / apex_height_km


def horizontal_offset_km(altitude_km: float, elevation_deg: float) -> float:
    """Horizontal distance from a ground landing point to a ray at altitude."""
    if altitude_km < 0.0 or not 0.0 < elevation_deg < 90.0:
        raise ValueError("invalid altitude or elevation angle")
    return altitude_km / math.tan(math.radians(elevation_deg))

def triangular_route_metrics(
    route_distance_km: float,
    hop_count: int,
    apex_height_km: float,
    altitude_km: float,
) -> dict[str, float]:
    """Geometric path/time and low-altitude zones for identical triangle hops."""
    if route_distance_km <= 0.0 or hop_count <= 0:
        raise ValueError("route distance and hop count must be positive")
    fraction = fraction_below_altitude(altitude_km, apex_height_km)
    half_hop_ground_km = route_distance_km / (2.0 * hop_count)
    half_hop_path_km = math.hypot(half_hop_ground_km, apex_height_km)
    total_path_km = 2.0 * hop_count * half_hop_path_km
    total_time_ms = total_path_km * 1_000_000.0 / C_METRES_PER_SECOND
    return {
        "route_distance_km": route_distance_km,
        "hop_count": hop_count,
        "apex_height_km": apex_height_km,
        "altitude_km": altitude_km,
        "path_fraction_below_altitude": fraction,
        "total_geometric_path_km": total_path_km,
        "total_geometric_time_ms": total_time_ms,
        "time_below_altitude_ms": fraction * total_time_ms,
        "ground_half_width_per_landing_km": altitude_km
        * half_hop_ground_km
        / apex_height_km,
    }



def watts_to_dbm(watts: float) -> float:
    if watts <= 0.0:
        raise ValueError("power must be positive")
    return 10.0 * math.log10(watts * 1000.0)


def bistatic_link_budget(values: dict[str, float]) -> dict[str, float]:
    wavelength_m = C_METRES_PER_SECOND / values["frequency_hz"]
    gain = values["transmitter_gain_linear"] * values["receiver_gain_linear"]
    direct_w = (
        values["transmit_power_w"]
        * gain
        * (wavelength_m / (4.0 * math.pi * values["direct_path_m"])) ** 2
    )
    scattered_w = (
        values["transmit_power_w"]
        * gain
        * wavelength_m**2
        * values["favourable_rcs_m2"]
        / (
            (4.0 * math.pi) ** 3
            * values["transmitter_to_aircraft_m"] ** 2
            * values["aircraft_to_receiver_m"] ** 2
        )
    )
    direct_dbm = watts_to_dbm(direct_w)
    scattered_dbm = watts_to_dbm(scattered_w)
    scattered_snr_db = scattered_dbm - values["optimistic_noise_floor_dbm"]
    field_ratio = math.sqrt(scattered_w / direct_w)
    return {
        "wavelength_m": wavelength_m,
        "direct_power_dbm": direct_dbm,
        "scattered_power_dbm": scattered_dbm,
        "direct_to_scatter_db": direct_dbm - scattered_dbm,
        "scattered_snr_db": scattered_snr_db,
        "threshold_deficit_db": values["wspr_threshold_snr_db"] - scattered_snr_db,
        "maximum_coherent_carrier_perturbation_db": 20.0
        * math.log10(1.0 + field_ratio),
    }


def build_outputs(parameters: dict) -> tuple[list[dict], dict]:
    hop = parameters["triangular_hop"]
    rows: list[dict] = []
    for apex_km in hop["representative_apex_heights_km"]:
        fraction = fraction_below_altitude(hop["aircraft_ceiling_km"], apex_km)
        rows.append(
            {
                "calculation": "path_below_aircraft_ceiling",
                "altitude_km": hop["aircraft_ceiling_km"],
                "apex_height_km": apex_km,
                "elevation_deg": "",
                "fraction": fraction,
                "percent": 100.0 * fraction,
                "horizontal_offset_km": "",
                "route_distance_below_ceiling_km": fraction
                * hop["route_distance_km"],
            }
        )
    for angle_deg in hop["arrival_angles_deg"]:
        rows.append(
            {
                "calculation": "distance_before_ground_landing_at_cruise_altitude",
                "altitude_km": hop["cruise_altitude_km"],
                "apex_height_km": "",
                "elevation_deg": angle_deg,
                "fraction": "",
                "percent": "",
                "horizontal_offset_km": horizontal_offset_km(
                    hop["cruise_altitude_km"], angle_deg
                ),
                "route_distance_below_ceiling_km": "",
            }
        )
    example_altitude_km = hop["published_example_altitude_ft"] * 0.0003048
    example = {
        "altitude_km": example_altitude_km,
        "elevation_deg": hop["published_example_elevation_deg"],
        "horizontal_offset_from_ground_endpoint_km": horizontal_offset_km(
            example_altitude_km, hop["published_example_elevation_deg"]
        ),
    }
    summary = {
        "model": "straight triangular virtual-height hops",
        "hop_count": hop["hop_count"],
        "fraction_is_independent_of_hop_count": True,
        "representative_route": triangular_route_metrics(
            hop["route_distance_km"],
            hop["hop_count"],
            hop["representative_route_apex_height_km"],
            hop["cruise_altitude_km"],
        ),
        "published_2024_example": example,
        "bistatic_link_budget": bistatic_link_budget(
            parameters["bistatic_link_budget"]
        ),
        "limitations": [
            "The triangular hop is an explanatory sensitivity, not ionospheric ray tracing.",
            "A path fraction below an altitude is not a probability of intersecting an aircraft.",
            "The link budget omits ionospheric, ground-reflection and polarization losses.",
            "Ionospheric focusing is not included; the calculation is an optimistic benchmark, not a universal impossibility proof."
        ],
    }
    return rows, summary


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parameters = json.loads((root / "data" / "physics_parameters.json").read_text())
    rows, summary = build_outputs(parameters)
    output_dir = root / "outputs"
    output_dir.mkdir(exist_ok=True)
    with (output_dir / "propagation_geometry.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (output_dir / "physics_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    main()
