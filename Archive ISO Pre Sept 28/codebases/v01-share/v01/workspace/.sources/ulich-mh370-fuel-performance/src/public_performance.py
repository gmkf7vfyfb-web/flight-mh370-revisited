#!/usr/bin/env python3
"""Clean-room public-equation fuel-flow proxy.

This module deliberately does not read the audited workbook.  Its narrow
purpose is to make the public approximation and its failure mode executable.
All scientific coefficients are loaded from provenance-tagged JSON.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
import math
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class FlightState:
    altitude_ft: float
    mach: float
    sat_c: float


@dataclass(frozen=True)
class FlowDiagnostic:
    total_fuel_flow_kg_s: float
    raw_thrust_fraction: float
    used_thrust_fraction: float
    lift_coefficient: float
    drag_n: float
    tas_m_s: float
    pressure_ratio: float
    temperature_ratio: float


class PublicPerformanceModel:
    """Point-mass drag plus linearly interpolated LTO/BFFM2 fuel flow."""

    def __init__(self, model_document: dict[str, Any]) -> None:
        self.document = model_document
        self.parameters = model_document["parameters"]
        self._validate_parameter_provenance(self.parameters)

    @classmethod
    def from_json(cls, path: Path) -> "PublicPerformanceModel":
        return cls(json.loads(path.read_text(encoding="utf-8")))

    @staticmethod
    def _validate_parameter_provenance(node: Any, path: str = "parameters") -> None:
        if isinstance(node, dict):
            if "value" in node:
                missing = {"classification", "source_ref", "unit"} - set(node)
                if missing:
                    raise ValueError(f"{path} lacks provenance fields: {sorted(missing)}")
                if node["classification"] not in {"measured", "source-derived", "model-choice"}:
                    raise ValueError(f"{path} has invalid classification")
            for key, value in node.items():
                PublicPerformanceModel._validate_parameter_provenance(value, f"{path}.{key}")
        elif isinstance(node, list):
            for index, value in enumerate(node):
                PublicPerformanceModel._validate_parameter_provenance(value, f"{path}[{index}]")

    def p(self, name: str) -> Any:
        return self.parameters[name]["value"]

    def standard_atmosphere(self, altitude_ft: float, sat_c: float | None = None) -> dict[str, float]:
        altitude_m = altitude_ft * self.p("feet_to_metres")
        t0 = self.p("sea_level_temperature_k")
        p0 = self.p("sea_level_pressure_pa")
        lapse = self.p("tropospheric_lapse_k_m")
        tropopause = self.p("tropopause_height_m")
        tropopause_t = self.p("tropopause_temperature_k")
        gas_constant = self.p("air_gas_constant_j_kg_k")
        gravity = self.p("gravity_m_s2")

        if altitude_m <= tropopause:
            isa_temperature = t0 + lapse * altitude_m
            pressure = p0 * (isa_temperature / t0) ** (-gravity / (lapse * gas_constant))
        else:
            pressure_at_tropopause = p0 * (tropopause_t / t0) ** (
                -gravity / (lapse * gas_constant)
            )
            pressure = pressure_at_tropopause * math.exp(
                -gravity * (altitude_m - tropopause) / (gas_constant * tropopause_t)
            )
            isa_temperature = tropopause_t

        actual_temperature = (
            isa_temperature if sat_c is None else sat_c + self.p("celsius_zero_kelvin")
        )
        density = pressure / (gas_constant * actual_temperature)
        speed_of_sound = math.sqrt(
            self.p("ratio_specific_heats") * gas_constant * actual_temperature
        )
        return {
            "pressure_pa": pressure,
            "isa_temperature_k": isa_temperature,
            "actual_temperature_k": actual_temperature,
            "density_kg_m3": density,
            "speed_of_sound_m_s": speed_of_sound,
            "delta": pressure / p0,
            "theta": actual_temperature / t0,
        }

    def _reference_fuel_flow_per_engine(self, thrust_fraction: float) -> float:
        points = []
        for point in self.parameters["lto_reference_points"]:
            power = point["power_setting"]["value"]
            installed_flow = (
                point["fuel_flow_per_engine_kg_s"]["value"]
                * point["installation_factor"]["value"]
            )
            points.append((power, installed_flow))

        used = min(
            max(thrust_fraction, self.p("thrust_fraction_lower_clamp")),
            self.p("thrust_fraction_upper_clamp"),
        )
        for (power0, flow0), (power1, flow1) in zip(points, points[1:]):
            if used <= power1:
                fraction = (used - power0) / (power1 - power0)
                return flow0 + fraction * (flow1 - flow0)
        return points[-1][1]

    def flow(
        self,
        mass_kg: float,
        state: FlightState,
        vertical_speed_m_s: float = 0.0,
        acceleration_m_s2: float = 0.0,
    ) -> FlowDiagnostic:
        atmosphere = self.standard_atmosphere(state.altitude_ft, state.sat_c)
        tas = state.mach * atmosphere["speed_of_sound_m_s"]
        path_angle = math.atan2(vertical_speed_m_s, tas)
        dynamic_area = (
            0.5
            * atmosphere["density_kg_m3"]
            * tas
            * tas
            * self.p("wing_area_m2")
        )
        lift_coefficient = (
            mass_kg
            * self.p("gravity_m_s2")
            * math.cos(path_angle)
            * self.p("load_factor")
            / dynamic_area
        )
        drag_coefficient = self.p("clean_drag_coefficient") + self.p(
            "induced_drag_factor"
        ) * lift_coefficient * lift_coefficient
        drag = drag_coefficient * dynamic_area
        required_thrust = max(
            self.p("minimum_required_thrust_n"),
            drag
            + mass_kg * self.p("gravity_m_s2") * math.sin(path_angle)
            + mass_kg * acceleration_m_s2,
        )
        raw_thrust_fraction = required_thrust / (
            self.p("engine_count") * self.p("maximum_static_thrust_per_engine_n")
        )
        used_thrust_fraction = min(
            max(raw_thrust_fraction, self.p("thrust_fraction_lower_clamp")),
            self.p("thrust_fraction_upper_clamp"),
        )
        reference_flow = self._reference_fuel_flow_per_engine(raw_thrust_fraction)
        per_engine_flow = (
            reference_flow
            * atmosphere["delta"]
            / (
                atmosphere["theta"] ** self.p("bffm2_temperature_exponent")
                * math.exp(self.p("bffm2_mach_exponent") * state.mach * state.mach)
            )
        )
        total_flow = (
            per_engine_flow * self.p("engine_count") * self.p("fuel_flow_scale")
        )
        return FlowDiagnostic(
            total_fuel_flow_kg_s=total_flow,
            raw_thrust_fraction=raw_thrust_fraction,
            used_thrust_fraction=used_thrust_fraction,
            lift_coefficient=lift_coefficient,
            drag_n=drag,
            tas_m_s=tas,
            pressure_ratio=atmosphere["delta"],
            temperature_ratio=atmosphere["theta"],
        )

    def simulate_linear_interval(
        self,
        start: FlightState,
        end: FlightState,
        duration_s: float,
        zero_fuel_weight_kg: float,
        start_fuel_kg: float,
        step_s: float | None = None,
    ) -> dict[str, float]:
        step = self.p("integration_step_s") if step_s is None else step_s
        start_tas = start.mach * self.standard_atmosphere(start.altitude_ft, start.sat_c)[
            "speed_of_sound_m_s"
        ]
        end_tas = end.mach * self.standard_atmosphere(end.altitude_ft, end.sat_c)[
            "speed_of_sound_m_s"
        ]
        acceleration = (end_tas - start_tas) / duration_s
        vertical_speed = (
            (end.altitude_ft - start.altitude_ft)
            * self.p("feet_to_metres")
            / duration_s
        )

        elapsed = 0.0
        fuel = start_fuel_kg
        while elapsed < duration_s:
            dt = min(step, duration_s - elapsed)
            fraction = (
                elapsed + self.p("integration_midpoint_fraction") * dt
            ) / duration_s
            state = FlightState(
                altitude_ft=start.altitude_ft + fraction * (end.altitude_ft - start.altitude_ft),
                mach=start.mach + fraction * (end.mach - start.mach),
                sat_c=start.sat_c + fraction * (end.sat_c - start.sat_c),
            )
            diagnostic = self.flow(
                zero_fuel_weight_kg + fuel,
                state,
                vertical_speed_m_s=vertical_speed,
                acceleration_m_s2=acceleration,
            )
            fuel -= diagnostic.total_fuel_flow_kg_s * dt
            elapsed += dt
        return {
            "burn_kg": start_fuel_kg - fuel,
            "ending_fuel_kg": fuel,
            "vertical_speed_m_s": vertical_speed,
            "acceleration_m_s2": acceleration,
        }

    def simulate_constant_segment(
        self,
        altitude_ft: float,
        mach: float,
        duration_s: float,
        zero_fuel_weight_kg: float,
        start_fuel_kg: float,
        step_s: float | None = None,
        isa_offset_c: float = 0.0,
    ) -> dict[str, float]:
        isa_temperature = self.standard_atmosphere(altitude_ft)["isa_temperature_k"]
        state = FlightState(
            altitude_ft,
            mach,
            isa_temperature - self.p("celsius_zero_kelvin") + isa_offset_c,
        )
        step = self.p("integration_step_s") if step_s is None else step_s
        elapsed = 0.0
        fuel = start_fuel_kg
        while elapsed < duration_s:
            dt = min(step, duration_s - elapsed)
            diagnostic = self.flow(zero_fuel_weight_kg + fuel, state)
            fuel -= diagnostic.total_fuel_flow_kg_s * dt
            elapsed += dt
        return {"burn_kg": start_fuel_kg - fuel, "ending_fuel_kg": fuel}


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_official_anchor(acars: dict[str, Any]) -> None:
    record = acars["records"][-1]
    anchor = acars["required_anchor"]
    expected = {
        "utc": record["utc"],
        "zero_fuel_weight_kg": acars["zero_fuel_weight"]["value"],
        "fuel_kg": record["fuel_kg"],
        "altitude_ft": record["altitude_ft"],
        "mach": record["mach"],
        "sat_c": record["sat_c"],
    }
    if anchor != expected:
        raise ValueError(f"official anchor does not equal final ACARS row: {anchor!r}")


def recreate_acars(model: PublicPerformanceModel, acars: dict[str, Any]) -> dict[str, Any]:
    validate_official_anchor(acars)
    records = acars["records"]
    zfw = acars["zero_fuel_weight"]["value"]
    fuel = records[0]["fuel_kg"]
    intervals = []
    for start_record, end_record in zip(records, records[1:]):
        duration = (parse_utc(end_record["utc"]) - parse_utc(start_record["utc"])).total_seconds()
        start = FlightState(start_record["altitude_ft"], start_record["mach"], start_record["sat_c"])
        end = FlightState(end_record["altitude_ft"], end_record["mach"], end_record["sat_c"])
        simulation = model.simulate_linear_interval(start, end, duration, zfw, fuel)
        observed_burn = start_record["fuel_kg"] - end_record["fuel_kg"]
        predicted_burn = simulation["burn_kg"]
        intervals.append(
            {
                "start_utc": start_record["utc"],
                "end_utc": end_record["utc"],
                "observed_burn_kg": observed_burn,
                "predicted_burn_kg": predicted_burn,
                "error_predicted_minus_observed_kg": predicted_burn - observed_burn,
            }
        )
        fuel = simulation["ending_fuel_kg"]

    observed_total = records[0]["fuel_kg"] - records[-1]["fuel_kg"]
    predicted_total = records[0]["fuel_kg"] - fuel
    rmse = math.sqrt(
        sum(row["error_predicted_minus_observed_kg"] ** 2 for row in intervals)
        / len(intervals)
    )
    anchor_record = records[-1]
    anchor_state = FlightState(
        anchor_record["altitude_ft"], anchor_record["mach"], anchor_record["sat_c"]
    )
    anchor_flow = model.flow(zfw + anchor_record["fuel_kg"], anchor_state)
    return {
        "intervals": intervals,
        "observed_total_burn_kg": observed_total,
        "predicted_total_burn_kg": predicted_total,
        "total_error_predicted_minus_observed_kg": predicted_total - observed_total,
        "interval_rmse_kg": rmse,
        "predicted_ending_fuel_kg": fuel,
        "anchor_flow": anchor_flow.__dict__,
    }


def recreate_official_post_acars(
    model: PublicPerformanceModel,
    acars: dict[str, Any],
    official: dict[str, Any],
) -> dict[str, Any]:
    validate_official_anchor(acars)
    zfw = acars["zero_fuel_weight"]["value"]
    fuel = acars["required_anchor"]["fuel_kg"]
    initial_fuel = fuel
    pounds_to_kg = model.p("pounds_to_kg")
    segments = []
    elapsed_s = 0.0
    for row in official["segments"]:
        duration_s = row["duration_h"] * model.p("seconds_per_hour")
        simulation = model.simulate_constant_segment(
            altitude_ft=row["flight_level"] * model.p("feet_per_flight_level"),
            mach=row["mach"],
            duration_s=duration_s,
            zero_fuel_weight_kg=zfw,
            start_fuel_kg=fuel,
        )
        fuel = simulation["ending_fuel_kg"]
        elapsed_s += duration_s
        official_end = row["official_ending_fuel_lb"] * pounds_to_kg
        segments.append(
            {
                "segment": row["segment"],
                "duration_s": duration_s,
                "elapsed_s": elapsed_s,
                "predicted_ending_fuel_kg": fuel,
                "official_ending_fuel_kg": official_end,
                "predicted_minus_official_ending_fuel_kg": fuel - official_end,
            }
        )
    official_end = official["official_arc1_ending_fuel_lb"] * pounds_to_kg
    return {
        "segments": segments,
        "printed_duration_s": elapsed_s,
        "official_arc1_offset_s": (
            parse_utc(official["official_arc1_utc"])
            - parse_utc(acars["required_anchor"]["utc"])
        ).total_seconds(),
        "predicted_burn_kg": initial_fuel - fuel,
        "official_calculated_burn_kg": initial_fuel - official_end,
        "predicted_ending_fuel_kg": fuel,
        "official_calculated_ending_fuel_kg": official_end,
        "overburn_vs_official_calculation_kg": official_end - fuel,
    }


def recreate_stress_family(
    model: PublicPerformanceModel,
    acars: dict[str, Any],
    stress: dict[str, Any],
) -> dict[str, Any]:
    validate_official_anchor(acars)
    zfw = acars["zero_fuel_weight"]["value"]
    results = []
    for profile in stress["profiles"]:
        fuel = acars["required_anchor"]["fuel_kg"]
        for start_row, end_row in zip(profile["waypoints"], profile["waypoints"][1:]):
            duration = end_row["offset_s"] - start_row["offset_s"]
            start_isa = model.standard_atmosphere(start_row["altitude_ft"])["isa_temperature_k"]
            end_isa = model.standard_atmosphere(end_row["altitude_ft"])["isa_temperature_k"]
            start = FlightState(
                start_row["altitude_ft"],
                start_row["mach"],
                start_isa - model.p("celsius_zero_kelvin") + stress["isa_temperature_offset_c"],
            )
            end = FlightState(
                end_row["altitude_ft"],
                end_row["mach"],
                end_isa - model.p("celsius_zero_kelvin") + stress["isa_temperature_offset_c"],
            )
            simulation = model.simulate_linear_interval(start, end, duration, zfw, fuel)
            fuel = simulation["ending_fuel_kg"]
        results.append(
            {
                "profile_id": profile["id"],
                "ending_fuel_kg": fuel,
                "burn_kg": acars["required_anchor"]["fuel_kg"] - fuel,
                "likelihood_weight": stress["likelihood_weight"],
                "initializer_eligible": stress["initializer_eligible"],
            }
        )
    return {
        "family_id": stress["family_id"],
        "epistemic_role": "unweighted-stress-only",
        "profiles": results,
    }


def convergence_check(
    model: PublicPerformanceModel,
    acars: dict[str, Any],
    steps_s: Iterable[float],
) -> list[dict[str, float]]:
    records = acars["records"]
    zfw = acars["zero_fuel_weight"]["value"]
    output = []
    for step in steps_s:
        fuel = records[0]["fuel_kg"]
        for start_record, end_record in zip(records, records[1:]):
            duration = (parse_utc(end_record["utc"]) - parse_utc(start_record["utc"])).total_seconds()
            result = model.simulate_linear_interval(
                FlightState(start_record["altitude_ft"], start_record["mach"], start_record["sat_c"]),
                FlightState(end_record["altitude_ft"], end_record["mach"], end_record["sat_c"]),
                duration,
                zfw,
                fuel,
                step_s=step,
            )
            fuel = result["ending_fuel_kg"]
        output.append({"step_s": step, "predicted_total_burn_kg": records[0]["fuel_kg"] - fuel})
    return output
