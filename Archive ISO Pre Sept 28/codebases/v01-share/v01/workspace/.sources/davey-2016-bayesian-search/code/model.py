"""Vectorised geometry and stochastic-model primitives for the Davey reconstruction."""

from __future__ import annotations

import math
from typing import Iterable

import numpy as np


WGS84_A_KM = 6378.137
WGS84_E2 = 6.69437999014e-3
KM_PER_NM = 1.852
KT_TO_KM_S = KM_PER_NM / 3600.0
FT_TO_KM = 0.0003048
FPM_TO_KM_S = FT_TO_KM / 60.0
G_M_S2 = 9.80665


def wrap360(angle):
    return np.mod(angle, 360.0)


def angle_difference(target, current):
    return np.mod(target - current + 180.0, 360.0) - 180.0


def lla_to_ecef(lat_deg, lon_deg, altitude_km=0.0):
    lat = np.radians(np.asarray(lat_deg, dtype=float))
    lon = np.radians(np.asarray(lon_deg, dtype=float))
    alt = np.asarray(altitude_km, dtype=float)
    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)
    radius = WGS84_A_KM / np.sqrt(1.0 - WGS84_E2 * sin_lat * sin_lat)
    x = (radius + alt) * cos_lat * np.cos(lon)
    y = (radius + alt) * cos_lat * np.sin(lon)
    z = (radius * (1.0 - WGS84_E2) + alt) * sin_lat
    return np.stack(np.broadcast_arrays(x, y, z), axis=-1)


def local_basis(lat_deg, lon_deg):
    lat = np.radians(np.asarray(lat_deg, dtype=float))
    lon = np.radians(np.asarray(lon_deg, dtype=float))
    sin_lat, cos_lat = np.sin(lat), np.cos(lat)
    sin_lon, cos_lon = np.sin(lon), np.cos(lon)
    north = np.stack(np.broadcast_arrays(-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat), axis=-1)
    east = np.stack(np.broadcast_arrays(-sin_lon, cos_lon, np.zeros_like(lat)), axis=-1)
    up = np.stack(np.broadcast_arrays(cos_lat * cos_lon, cos_lat * sin_lon, sin_lat), axis=-1)
    return north, east, up


def destination(lat_deg, lon_deg, bearing_deg, distance_nm):
    radius_nm = 3440.065
    lat1 = np.radians(np.asarray(lat_deg, dtype=float))
    lon1 = np.radians(np.asarray(lon_deg, dtype=float))
    bearing = np.radians(np.asarray(bearing_deg, dtype=float))
    angular = np.asarray(distance_nm, dtype=float) / radius_nm
    sin_lat2 = np.sin(lat1) * np.cos(angular) + np.cos(lat1) * np.sin(angular) * np.cos(bearing)
    lat2 = np.arcsin(np.clip(sin_lat2, -1.0, 1.0))
    lon2 = lon1 + np.arctan2(
        np.sin(bearing) * np.sin(angular) * np.cos(lat1),
        np.cos(angular) - np.sin(lat1) * np.sin(lat2),
    )
    return np.degrees(lat2), np.mod(np.degrees(lon2) + 180.0, 360.0) - 180.0


def final_bearing(lat1_deg, lon1_deg, lat2_deg, lon2_deg):
    lat1 = np.radians(np.asarray(lat1_deg, dtype=float))
    lat2 = np.radians(np.asarray(lat2_deg, dtype=float))
    delta_lon = np.radians(np.asarray(lon2_deg, dtype=float) - np.asarray(lon1_deg, dtype=float))
    y = np.sin(delta_lon) * np.cos(lat2)
    x = -np.sin(lat1) * np.cos(lat2) + np.cos(lat1) * np.sin(lat2) * np.cos(delta_lon)
    return wrap360(np.degrees(np.arctan2(y, x)) + 180.0)


def isa_temperature_kelvin(altitude_ft):
    altitude_m = np.asarray(altitude_ft, dtype=float) * 0.3048
    return np.where(altitude_m < 11000.0, 288.15 - 0.0065 * altitude_m, 216.65)


def speed_of_sound_knots(temperature_kelvin):
    return np.sqrt(1.4 * 287.05287 * np.asarray(temperature_kelvin, dtype=float)) / 0.5144444444444445


def bto_us(lat_deg, lon_deg, altitude_ft, satellite_position_km, ges_position_km, c_km_s, nominal_delay_us, channel_term_us):
    aircraft = lla_to_ecef(lat_deg, lon_deg, np.asarray(altitude_ft) * FT_TO_KM)
    satellite = np.asarray(satellite_position_km, dtype=float)
    ges = np.asarray(ges_position_km, dtype=float)
    sat_aircraft = np.linalg.norm(satellite - aircraft, axis=-1)
    sat_ges = np.linalg.norm(satellite - ges, axis=-1)
    propagation_us = 2.0 * (sat_aircraft + sat_ges) / c_km_s * 1e6
    return propagation_us - nominal_delay_us + channel_term_us


def bfo_components(
    lat_deg,
    lon_deg,
    altitude_ft,
    north_velocity_kt,
    east_velocity_kt,
    vertical_velocity_fpm,
    satellite_position_km,
    satellite_velocity_km_s,
    ges_position_km,
    satellite_afc_hz,
    uplink_hz,
    downlink_hz,
    c_km_s,
    nominal_satellite_longitude_deg,
    nominal_satellite_altitude_km,
):
    lat = np.asarray(lat_deg, dtype=float)
    lon = np.asarray(lon_deg, dtype=float)
    aircraft = lla_to_ecef(lat, lon, np.asarray(altitude_ft) * FT_TO_KM)
    surface_aircraft = lla_to_ecef(lat, lon, 0.0)
    north, east, up = local_basis(lat, lon)
    horizontal_velocity = (
        north * (np.asarray(north_velocity_kt) * KT_TO_KM_S)[..., None]
        + east * (np.asarray(east_velocity_kt) * KT_TO_KM_S)[..., None]
    )
    aircraft_velocity = horizontal_velocity + up * (np.asarray(vertical_velocity_fpm) * FPM_TO_KM_S)[..., None]
    satellite = np.asarray(satellite_position_km, dtype=float)
    satellite_velocity = np.asarray(satellite_velocity_km_s, dtype=float)
    ges = np.asarray(ges_position_km, dtype=float)

    aircraft_to_satellite = satellite - aircraft
    unit_up = aircraft_to_satellite / np.linalg.norm(aircraft_to_satellite, axis=-1)[..., None]
    # Physical Doppler sign: increasing propagation range lowers received frequency.
    uplink = -uplink_hz / c_km_s * np.sum((satellite_velocity - aircraft_velocity) * unit_up, axis=-1)

    ges_to_satellite = satellite - ges
    unit_down = ges_to_satellite / np.linalg.norm(ges_to_satellite, axis=-1)[..., None]
    downlink = -downlink_hz / c_km_s * np.sum(satellite_velocity * unit_down, axis=-1)

    nominal_satellite = lla_to_ecef(0.0, nominal_satellite_longitude_deg, nominal_satellite_altitude_km)
    nominal_to_aircraft = surface_aircraft - nominal_satellite
    unit_nominal_to_aircraft = nominal_to_aircraft / np.linalg.norm(nominal_to_aircraft, axis=-1)[..., None]
    compensation = uplink_hz / c_km_s * np.sum(horizontal_velocity * unit_nominal_to_aircraft, axis=-1)
    base = uplink + downlink + compensation + satellite_afc_hz
    return {
        "uplink_hz": uplink,
        "downlink_hz": downlink,
        "compensation_hz": compensation,
        "satellite_afc_hz": np.broadcast_to(satellite_afc_hz, np.shape(base)),
        "base_without_bias_hz": base,
    }


def ou_step(value, setpoint, beta, q, dt_seconds, rng):
    phi = math.exp(-beta * dt_seconds)
    variance = q / (2.0 * beta) * (1.0 - math.exp(-2.0 * beta * dt_seconds))
    return setpoint + phi * (value - setpoint) + rng.normal(0.0, math.sqrt(variance), np.shape(value))


def systematic_resample(weights, rng):
    cumulative = np.cumsum(weights)
    positions = (rng.random() + np.arange(len(weights))) / len(weights)
    return np.searchsorted(cumulative, positions, side="right")


def normal_logpdf(residual, sigma):
    return -0.5 * np.square(np.asarray(residual) / sigma) - math.log(sigma * math.sqrt(2.0 * math.pi))


def normalize_log_weights(log_weights):
    maximum = np.max(log_weights)
    weights = np.exp(log_weights - maximum)
    total = np.sum(weights)
    if not np.isfinite(total) or total <= 0.0:
        raise RuntimeError("all particle weights are zero or non-finite")
    return weights / total


def weighted_quantile(values, weights, probabilities: Iterable[float]):
    values = np.asarray(values)
    weights = np.asarray(weights)
    order = np.argsort(values)
    cumulative = np.cumsum(weights[order])
    cumulative /= cumulative[-1]
    return np.interp(tuple(probabilities), cumulative, values[order])
