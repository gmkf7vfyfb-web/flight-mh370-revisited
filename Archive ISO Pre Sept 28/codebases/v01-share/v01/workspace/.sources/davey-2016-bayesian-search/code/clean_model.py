#!/usr/bin/env python3
"""Independent physical and statistical primitives for a clean SATCOM reconstruction.

The module does not import the historical flight estimator or environmental model; all transformations are implemented here for independent comparison.  Frozen observations and environmental arrays may be
passed in as data, but all transformations below are implemented here so the
clean estimator can serve as an independent reconstruction.

Conventions
-----------
* latitude/longitude and bearings are degrees; longitude is wrapped to
  ``[-180, 180)``;
* altitude passed to SATCOM geometry is geometric/geopotential altitude in ft;
* east magnetic declination is positive and ``true = magnetic + declination``;
* north/east horizontal velocity is knots, vertical velocity is ft/min;
* OU ``noise_strength`` is the diffusion variance rate q in
  ``dX = beta * (setpoint - X) dt + sqrt(q) dW``.
"""

from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Callable, Iterable, Sequence

import numpy as np


WGS84_A_KM = 6378.137
WGS84_F = 1.0 / 298.257223563
WGS84_B_KM = WGS84_A_KM * (1.0 - WGS84_F)
WGS84_E2 = WGS84_F * (2.0 - WGS84_F)
LEGACY_SPHERE_RADIUS_NM = 3440.065
KM_PER_NM = 1.852
KT_TO_KM_S = KM_PER_NM / 3600.0
FT_TO_KM = 0.0003048
FPM_TO_KM_S = FT_TO_KM / 60.0
G0_M_S2 = 9.80665
M_S_TO_KT = 1.9438444924406048
M_TO_FT = 3.280839895013123

MODE_CONSTANT_TRUE_HEADING = 0
MODE_CONSTANT_MAGNETIC_HEADING = 1
MODE_CONSTANT_TRUE_TRACK = 2
MODE_CONSTANT_MAGNETIC_TRACK = 3
MODE_LATERAL_NAVIGATION = 4
MAGNETIC_MODES = (MODE_CONSTANT_MAGNETIC_HEADING, MODE_CONSTANT_MAGNETIC_TRACK)
HEADING_MODES = (MODE_CONSTANT_TRUE_HEADING, MODE_CONSTANT_MAGNETIC_HEADING)


class EnvironmentDomainError(ValueError):
    """A proposed state left the declared environmental-data domain."""


def _scalar_if_scalar(value, shape):
    array = np.asarray(value)
    return float(array) if shape == () else array


def wrap360(angle):
    return np.mod(angle, 360.0)


def wrap180(angle):
    return np.mod(np.asarray(angle) + 180.0, 360.0) - 180.0


def angle_difference(target, current):
    return wrap180(np.asarray(target) - np.asarray(current))


def magnetic_to_true(magnetic_deg, east_positive_declination_deg):
    """Convert magnetic direction to true direction with east-positive D."""

    return wrap360(np.asarray(magnetic_deg) + np.asarray(east_positive_declination_deg))


def control_to_true(control_deg, mode, east_positive_declination_deg):
    control, mode_values, declination = np.broadcast_arrays(
        np.asarray(control_deg, dtype=float),
        np.asarray(mode),
        np.asarray(east_positive_declination_deg, dtype=float),
    )
    result = control.copy()
    magnetic = (mode_values == MODE_CONSTANT_MAGNETIC_HEADING) | (
        mode_values == MODE_CONSTANT_MAGNETIC_TRACK
    )
    result[magnetic] += declination[magnetic]
    result = wrap360(result)
    return _scalar_if_scalar(result, result.shape)


def lla_to_ecef(lat_deg, lon_deg, altitude_km=0.0):
    """WGS-84 geodetic coordinates to Earth-centred Earth-fixed kilometres."""

    lat = np.radians(np.asarray(lat_deg, dtype=float))
    lon = np.radians(np.asarray(lon_deg, dtype=float))
    altitude = np.asarray(altitude_km, dtype=float)
    lat, lon, altitude = np.broadcast_arrays(lat, lon, altitude)
    sin_lat = np.sin(lat)
    cos_lat = np.cos(lat)
    prime_vertical = WGS84_A_KM / np.sqrt(1.0 - WGS84_E2 * sin_lat**2)
    x = (prime_vertical + altitude) * cos_lat * np.cos(lon)
    y = (prime_vertical + altitude) * cos_lat * np.sin(lon)
    z = (prime_vertical * (1.0 - WGS84_E2) + altitude) * sin_lat
    return np.stack((x, y, z), axis=-1)


def local_basis(lat_deg, lon_deg):
    """Return local geodetic north, east, up ECEF unit vectors."""

    lat = np.radians(np.asarray(lat_deg, dtype=float))
    lon = np.radians(np.asarray(lon_deg, dtype=float))
    lat, lon = np.broadcast_arrays(lat, lon)
    sin_lat, cos_lat = np.sin(lat), np.cos(lat)
    sin_lon, cos_lon = np.sin(lon), np.cos(lon)
    north = np.stack((-sin_lat * cos_lon, -sin_lat * sin_lon, cos_lat), axis=-1)
    east = np.stack((-sin_lon, cos_lon, np.zeros_like(lat)), axis=-1)
    up = np.stack((cos_lat * cos_lon, cos_lat * sin_lon, sin_lat), axis=-1)
    return north, east, up


def destination_sphere(lat_deg, lon_deg, bearing_deg, distance_nm):
    """Legacy great-circle direct solution on the 3440.065-nm sphere."""

    latitude = np.radians(np.asarray(lat_deg, dtype=float))
    longitude = np.radians(np.asarray(lon_deg, dtype=float))
    bearing = np.radians(np.asarray(bearing_deg, dtype=float))
    angular = np.asarray(distance_nm, dtype=float) / LEGACY_SPHERE_RADIUS_NM
    latitude, longitude, bearing, angular = np.broadcast_arrays(
        latitude, longitude, bearing, angular
    )
    sin_latitude_2 = (
        np.sin(latitude) * np.cos(angular)
        + np.cos(latitude) * np.sin(angular) * np.cos(bearing)
    )
    latitude_2 = np.arcsin(np.clip(sin_latitude_2, -1.0, 1.0))
    longitude_2 = longitude + np.arctan2(
        np.sin(bearing) * np.sin(angular) * np.cos(latitude),
        np.cos(angular) - np.sin(latitude) * np.sin(latitude_2),
    )
    latitude_out = np.degrees(latitude_2)
    longitude_out = wrap180(np.degrees(longitude_2))
    return (
        _scalar_if_scalar(latitude_out, latitude_out.shape),
        _scalar_if_scalar(longitude_out, longitude_out.shape),
    )


def _vincenty_direct_scalar(lat_deg, lon_deg, bearing_deg, distance_km):
    """Vincenty's WGS-84 direct solution for one finite coordinate."""

    if distance_km == 0.0:
        return float(lat_deg), float(wrap180(lon_deg))
    if distance_km < 0.0:
        raise ValueError("geodesic distance must be non-negative")
    phi_1 = math.radians(lat_deg)
    alpha_1 = math.radians(bearing_deg)
    tangent_u_1 = (1.0 - WGS84_F) * math.tan(phi_1)
    cos_u_1 = 1.0 / math.sqrt(1.0 + tangent_u_1**2)
    sin_u_1 = tangent_u_1 * cos_u_1
    sigma_1 = math.atan2(tangent_u_1, math.cos(alpha_1))
    sin_alpha = cos_u_1 * math.sin(alpha_1)
    cos_sq_alpha = max(0.0, 1.0 - sin_alpha**2)
    u_sq = cos_sq_alpha * (
        WGS84_A_KM**2 - WGS84_B_KM**2
    ) / WGS84_B_KM**2
    coefficient_a = 1.0 + u_sq / 16384.0 * (
        4096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq))
    )
    coefficient_b = u_sq / 1024.0 * (
        256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq))
    )
    sigma = distance_km / (WGS84_B_KM * coefficient_a)
    for _ in range(100):
        two_sigma_m = 2.0 * sigma_1 + sigma
        sin_sigma = math.sin(sigma)
        cos_sigma = math.cos(sigma)
        cos_two_sigma_m = math.cos(two_sigma_m)
        delta_sigma = coefficient_b * sin_sigma * (
            cos_two_sigma_m
            + coefficient_b
            / 4.0
            * (
                cos_sigma * (-1.0 + 2.0 * cos_two_sigma_m**2)
                - coefficient_b
                / 6.0
                * cos_two_sigma_m
                * (-3.0 + 4.0 * sin_sigma**2)
                * (-3.0 + 4.0 * cos_two_sigma_m**2)
            )
        )
        updated = distance_km / (WGS84_B_KM * coefficient_a) + delta_sigma
        if abs(updated - sigma) <= 1e-13:
            sigma = updated
            break
        sigma = updated
    else:
        raise RuntimeError("Vincenty direct solution failed to converge")
    sin_sigma = math.sin(sigma)
    cos_sigma = math.cos(sigma)
    two_sigma_m = 2.0 * sigma_1 + sigma
    cos_two_sigma_m = math.cos(two_sigma_m)
    numerator = sin_u_1 * cos_sigma + cos_u_1 * sin_sigma * math.cos(alpha_1)
    denominator = (1.0 - WGS84_F) * math.sqrt(
        sin_alpha**2
        + (sin_u_1 * sin_sigma - cos_u_1 * cos_sigma * math.cos(alpha_1)) ** 2
    )
    phi_2 = math.atan2(numerator, denominator)
    lam = math.atan2(
        sin_sigma * math.sin(alpha_1),
        cos_u_1 * cos_sigma - sin_u_1 * sin_sigma * math.cos(alpha_1),
    )
    correction_c = WGS84_F / 16.0 * cos_sq_alpha * (
        4.0 + WGS84_F * (4.0 - 3.0 * cos_sq_alpha)
    )
    longitude_delta = lam - (
        (1.0 - correction_c)
        * WGS84_F
        * sin_alpha
        * (
            sigma
            + correction_c
            * sin_sigma
            * (
                cos_two_sigma_m
                + correction_c
                * cos_sigma
                * (-1.0 + 2.0 * cos_two_sigma_m**2)
            )
        )
    )
    return math.degrees(phi_2), float(wrap180(lon_deg + math.degrees(longitude_delta)))


def destination_wgs84(lat_deg, lon_deg, bearing_deg, distance_nm):
    """Vector-friendly Vincenty direct solution on WGS-84."""

    inputs = np.broadcast_arrays(
        np.asarray(lat_deg, dtype=float),
        np.asarray(lon_deg, dtype=float),
        np.asarray(bearing_deg, dtype=float),
        np.asarray(distance_nm, dtype=float),
    )
    shape = inputs[0].shape
    latitude_out = np.empty(shape)
    longitude_out = np.empty(shape)
    iterator = np.ndindex(shape) if shape else [()]
    for index in iterator:
        latitude_out[index], longitude_out[index] = _vincenty_direct_scalar(
            float(inputs[0][index]),
            float(inputs[1][index]),
            float(inputs[2][index]),
            float(inputs[3][index]) * KM_PER_NM,
        )
    return (
        _scalar_if_scalar(latitude_out, shape),
        _scalar_if_scalar(longitude_out, shape),
    )


def isa_temperature_kelvin(pressure_altitude_ft):
    altitude_m = np.asarray(pressure_altitude_ft, dtype=float) * 0.3048
    result = np.where(altitude_m < 11_000.0, 288.15 - 0.0065 * altitude_m, 216.65)
    return _scalar_if_scalar(result, result.shape)


def speed_of_sound_knots(temperature_kelvin):
    result = np.sqrt(1.4 * 287.05287 * np.asarray(temperature_kelvin, dtype=float))
    result /= 0.5144444444444445
    return _scalar_if_scalar(result, result.shape)


def bto_us(
    lat_deg,
    lon_deg,
    altitude_ft,
    satellite_position_km,
    ges_position_km,
    speed_of_light_km_s,
    nominal_delay_us,
    channel_term_us,
):
    aircraft = lla_to_ecef(lat_deg, lon_deg, np.asarray(altitude_ft) * FT_TO_KM)
    satellite = np.asarray(satellite_position_km, dtype=float)
    ground_station = np.asarray(ges_position_km, dtype=float)
    satellite_aircraft_range = np.linalg.norm(satellite - aircraft, axis=-1)
    satellite_ground_range = np.linalg.norm(satellite - ground_station, axis=-1)
    propagation_us = 2.0 * (
        satellite_aircraft_range + satellite_ground_range
    ) / speed_of_light_km_s * 1e6
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
    speed_of_light_km_s,
    nominal_satellite_longitude_deg,
    nominal_satellite_altitude_km,
):
    latitude = np.asarray(lat_deg, dtype=float)
    longitude = np.asarray(lon_deg, dtype=float)
    aircraft = lla_to_ecef(latitude, longitude, np.asarray(altitude_ft) * FT_TO_KM)
    surface_aircraft = lla_to_ecef(latitude, longitude, 0.0)
    north_basis, east_basis, up_basis = local_basis(latitude, longitude)
    horizontal_velocity = (
        north_basis * (np.asarray(north_velocity_kt) * KT_TO_KM_S)[..., None]
        + east_basis * (np.asarray(east_velocity_kt) * KT_TO_KM_S)[..., None]
    )
    aircraft_velocity = horizontal_velocity + up_basis * (
        np.asarray(vertical_velocity_fpm) * FPM_TO_KM_S
    )[..., None]
    satellite = np.asarray(satellite_position_km, dtype=float)
    satellite_velocity = np.asarray(satellite_velocity_km_s, dtype=float)
    ground_station = np.asarray(ges_position_km, dtype=float)

    aircraft_to_satellite = satellite - aircraft
    aircraft_to_satellite /= np.linalg.norm(aircraft_to_satellite, axis=-1)[..., None]
    uplink = -uplink_hz / speed_of_light_km_s * np.sum(
        (satellite_velocity - aircraft_velocity) * aircraft_to_satellite, axis=-1
    )

    ground_to_satellite = satellite - ground_station
    ground_to_satellite /= np.linalg.norm(ground_to_satellite, axis=-1)[..., None]
    downlink = -downlink_hz / speed_of_light_km_s * np.sum(
        satellite_velocity * ground_to_satellite, axis=-1
    )

    nominal_satellite = lla_to_ecef(
        0.0, nominal_satellite_longitude_deg, nominal_satellite_altitude_km
    )
    nominal_to_aircraft = surface_aircraft - nominal_satellite
    nominal_to_aircraft /= np.linalg.norm(nominal_to_aircraft, axis=-1)[..., None]
    compensation = uplink_hz / speed_of_light_km_s * np.sum(
        horizontal_velocity * nominal_to_aircraft, axis=-1
    )
    base = uplink + downlink + compensation + satellite_afc_hz
    return {
        "uplink_hz": uplink,
        "downlink_hz": downlink,
        "compensation_hz": compensation,
        "satellite_afc_hz": np.broadcast_to(satellite_afc_hz, np.shape(base)),
        "base_without_bias_hz": base,
    }


def normal_log_density(residual, standard_deviation):
    residual = np.asarray(residual, dtype=float)
    standard_deviation = np.asarray(standard_deviation, dtype=float)
    return -0.5 * (residual / standard_deviation) ** 2 - np.log(
        standard_deviation * math.sqrt(2.0 * math.pi)
    )


@dataclass(frozen=True)
class BFOBiasState:
    mean_hz: float
    variance_hz2: float


def bfo_bias_predictive_update(
    state: BFOBiasState,
    observed_bfo_hz: float,
    base_without_bias_hz: float,
    measurement_sd_hz: float,
):
    """One exact Gaussian predictive likelihood and posterior bias update."""

    if state.variance_hz2 < 0.0 or measurement_sd_hz <= 0.0:
        raise ValueError("BFO variance must be non-negative and SD positive")
    innovation = observed_bfo_hz - base_without_bias_hz - state.mean_hz
    predictive_variance = state.variance_hz2 + measurement_sd_hz**2
    log_likelihood = -0.5 * (
        innovation**2 / predictive_variance
        + math.log(2.0 * math.pi * predictive_variance)
    )
    gain = state.variance_hz2 / predictive_variance
    updated = BFOBiasState(
        mean_hz=state.mean_hz + gain * innovation,
        variance_hz2=state.variance_hz2 * (1.0 - gain),
    )
    return float(log_likelihood), float(innovation), updated


def bfo_bias_sequence_log_likelihood(
    observed_bfo_hz: Sequence[float],
    base_without_bias_hz: Sequence[float],
    measurement_sd_hz: Sequence[float],
    prior_mean_hz: float,
    prior_sd_hz: float,
):
    state = BFOBiasState(float(prior_mean_hz), float(prior_sd_hz) ** 2)
    total = 0.0
    innovations = []
    for observed, base, sd in zip(
        observed_bfo_hz, base_without_bias_hz, measurement_sd_hz, strict=True
    ):
        increment, innovation, state = bfo_bias_predictive_update(
            state, float(observed), float(base), float(sd)
        )
        total += increment
        innovations.append(innovation)
    return total, np.asarray(innovations), state


@dataclass(frozen=True)
class OUTransitionMoments:
    mean: np.ndarray | float
    variance: float
    phi: float


@dataclass(frozen=True)
class OUIntegralMoments:
    state_mean: np.ndarray | float
    integral_mean: np.ndarray | float
    state_variance: float
    integral_variance: float
    covariance: float
    phi: float


def ou_transition_moments(value, setpoint, beta, noise_strength, dt_seconds):
    if beta < 0.0 or noise_strength < 0.0 or dt_seconds < 0.0:
        raise ValueError("OU beta, q, and dt must be non-negative")
    value = np.asarray(value, dtype=float)
    setpoint = np.asarray(setpoint, dtype=float)
    if beta == 0.0:
        phi = 1.0
        mean = value.copy()
        variance = noise_strength * dt_seconds
    else:
        phi = math.exp(-beta * dt_seconds)
        mean = setpoint + phi * (value - setpoint)
        variance = noise_strength / (2.0 * beta) * (1.0 - phi**2)
    return OUTransitionMoments(_scalar_if_scalar(mean, mean.shape), variance, phi)


def ou_state_and_integral_moments(value, setpoint, beta, noise_strength, dt_seconds):
    """Joint moments of X(t+dt) and integral X(s) ds for constant setpoint."""

    transition = ou_transition_moments(
        value, setpoint, beta, noise_strength, dt_seconds
    )
    value = np.asarray(value, dtype=float)
    setpoint = np.asarray(setpoint, dtype=float)
    if beta == 0.0:
        integral_mean = value * dt_seconds
        integral_variance = noise_strength * dt_seconds**3 / 3.0
        covariance = noise_strength * dt_seconds**2 / 2.0
    else:
        phi = transition.phi
        integral_mean = (
            setpoint * dt_seconds + (value - setpoint) * (1.0 - phi) / beta
        )
        integral_variance = noise_strength / beta**2 * (
            dt_seconds
            - 2.0 * (1.0 - phi) / beta
            + (1.0 - phi**2) / (2.0 * beta)
        )
        covariance = noise_strength * (1.0 - phi) ** 2 / (2.0 * beta**2)
    return OUIntegralMoments(
        transition.mean,
        _scalar_if_scalar(integral_mean, integral_mean.shape),
        transition.variance,
        integral_variance,
        covariance,
        transition.phi,
    )


def ou_exact_step(value, setpoint, beta, noise_strength, dt_seconds, rng):
    moments = ou_transition_moments(
        value, setpoint, beta, noise_strength, dt_seconds
    )
    value_shape = np.shape(np.broadcast_arrays(value, setpoint)[0])
    result = np.asarray(moments.mean) + rng.normal(
        0.0, math.sqrt(max(moments.variance, 0.0)), size=value_shape or None
    )
    return _scalar_if_scalar(result, result.shape)


@dataclass(frozen=True)
class PoissonEvent:
    time_s: float
    event_type: str
    target: float | int


def sample_poisson_event_skeleton(
    rng,
    start_s: float,
    end_s: float,
    rate_per_s: float,
    event_type: str,
    target_sampler: Callable,
):
    if end_s < start_s or rate_per_s < 0.0:
        raise ValueError("invalid Poisson interval or rate")
    duration = end_s - start_s
    count = int(rng.poisson(rate_per_s * duration))
    times = np.sort(rng.uniform(start_s, end_s, count)) if count else np.empty(0)
    return tuple(
        PoissonEvent(float(time_s), event_type, target_sampler(rng))
        for time_s in times
    )


def poisson_event_log_density(
    events: Sequence[PoissonEvent],
    start_s: float,
    end_s: float,
    rate_per_s: float,
    target_log_density: Callable[[float | int], float],
    event_type: str | None = None,
):
    """Joint ordered-time density of a homogeneous marked Poisson process."""

    if end_s < start_s or rate_per_s < 0.0:
        raise ValueError("invalid Poisson interval or rate")
    previous = start_s
    for event in events:
        if event.time_s < previous or event.time_s < start_s or event.time_s > end_s:
            return -math.inf
        if event_type is not None and event.event_type != event_type:
            return -math.inf
        previous = event.time_s
    if rate_per_s == 0.0:
        return 0.0 if not events else -math.inf
    result = -rate_per_s * (end_s - start_s) + len(events) * math.log(rate_per_s)
    result += sum(float(target_log_density(event.target)) for event in events)
    return result


def ground_velocity_from_control(
    true_airspeed_kt,
    control_deg,
    mode,
    wind_north_kt,
    wind_east_kt,
    east_positive_declination_deg=0.0,
):
    """Resolve heading- or track-controlled airspeed into ground velocity."""

    tas, control, mode_values, wind_north, wind_east, declination = np.broadcast_arrays(
        np.asarray(true_airspeed_kt, dtype=float),
        np.asarray(control_deg, dtype=float),
        np.asarray(mode),
        np.asarray(wind_north_kt, dtype=float),
        np.asarray(wind_east_kt, dtype=float),
        np.asarray(east_positive_declination_deg, dtype=float),
    )
    true_control = np.asarray(control_to_true(control, mode_values, declination))
    angle = np.radians(true_control)
    desired_north = np.cos(angle)
    desired_east = np.sin(angle)
    heading = (mode_values == MODE_CONSTANT_TRUE_HEADING) | (
        mode_values == MODE_CONSTANT_MAGNETIC_HEADING
    )
    north = np.empty_like(tas)
    east = np.empty_like(tas)
    north[heading] = tas[heading] * desired_north[heading] + wind_north[heading]
    east[heading] = tas[heading] * desired_east[heading] + wind_east[heading]
    track = ~heading
    if np.any(track):
        along = wind_north * desired_north + wind_east * desired_east
        cross = -wind_north * desired_east + wind_east * desired_north
        infeasible = np.abs(cross) > tas
        ground_speed = along + np.sqrt(np.maximum(tas**2 - cross**2, 0.0))
        north[track] = ground_speed[track] * desired_north[track]
        east[track] = ground_speed[track] * desired_east[track]
        north[track & infeasible] = np.nan
        east[track & infeasible] = np.nan
    speed = np.hypot(north, east)
    ground_track = wrap360(np.degrees(np.arctan2(east, north)))
    return {
        "north_kt": _scalar_if_scalar(north, north.shape),
        "east_kt": _scalar_if_scalar(east, east.shape),
        "speed_kt": _scalar_if_scalar(speed, speed.shape),
        "track_deg": _scalar_if_scalar(ground_track, ground_track.shape),
        "true_control_deg": _scalar_if_scalar(true_control, true_control.shape),
    }


def _validate_interpolation_axis(axis):
    axis = np.asarray(axis, dtype=float)
    if axis.ndim != 1 or len(axis) < 2 or np.any(np.diff(axis) <= 0.0):
        raise ValueError("interpolation axis must be one-dimensional and increasing")


def bracket(axis, values, assume_valid=False):
    """Return lower interpolation cell, fraction, and in-domain mask."""

    axis = np.asarray(axis, dtype=float)
    values = np.asarray(values, dtype=float)
    if not assume_valid:
        _validate_interpolation_axis(axis)
    valid = np.isfinite(values) & (values >= axis[0]) & (values <= axis[-1])
    clipped = np.clip(values, axis[0], axis[-1])
    upper = np.searchsorted(axis, clipped, side="right")
    upper = np.clip(upper, 1, len(axis) - 1)
    lower = upper - 1
    fraction = (clipped - axis[lower]) / (axis[upper] - axis[lower])
    return lower, fraction, valid


def multilinear_interpolate(
    field, axes: Sequence[np.ndarray], coordinates, assume_valid_axes=False
):
    """N-dimensional linear interpolation with an explicit validity mask."""

    field = np.asarray(field)
    if field.ndim != len(axes) or len(coordinates) != len(axes):
        raise ValueError("field, axes, and coordinates have inconsistent ranks")
    prepared = [
        bracket(axis, coordinate, assume_valid=assume_valid_axes)
        for axis, coordinate in zip(axes, coordinates)
    ]
    lower_indices = [item[0] for item in prepared]
    fractions = [item[1] for item in prepared]
    valid = np.logical_and.reduce([item[2] for item in prepared])
    shape = np.broadcast_shapes(*[np.shape(coordinate) for coordinate in coordinates])
    output = np.zeros(shape, dtype=float)
    for corner_bits in itertools.product((0, 1), repeat=len(axes)):
        corner = []
        weight = 1.0
        for lower, fraction, bit in zip(lower_indices, fractions, corner_bits):
            corner.append(lower + bit)
            weight = weight * (fraction if bit else 1.0 - fraction)
        output += weight * field[tuple(corner)]
    return output, valid


def interpolate3(field, axes, coordinates, assume_valid_axes=False):
    if len(axes) != 3:
        raise ValueError("interpolate3 requires three axes")
    return multilinear_interpolate(field, axes, coordinates, assume_valid_axes)


def interpolate4(field, axes, coordinates, assume_valid_axes=False):
    if len(axes) != 4:
        raise ValueError("interpolate4 requires four axes")
    return multilinear_interpolate(field, axes, coordinates, assume_valid_axes)


class EnvironmentalFields:
    """Independent reader/interpolator for the frozen ERA5 and IGRF arrays."""

    def __init__(self, era5_path: Path, igrf_path: Path):
        with np.load(era5_path, allow_pickle=False) as source:
            self.time = source["time_unix_s"].astype(float)
            self.flight_level = source["flight_level_ft"].astype(float)
            era_latitude = source["latitude_deg"].astype(float)
            self.longitude = source["longitude_deg"].astype(float)
            reverse_era_lat = np.any(np.diff(era_latitude) < 0.0)
            self.latitude = era_latitude[::-1] if reverse_era_lat else era_latitude
            latitude_slice = slice(None, None, -1) if reverse_era_lat else slice(None)
            self.temperature = source["temperature_k"][
                :, :, latitude_slice, :
            ]
            self.wind_east = source["wind_east_m_s"][
                :, :, latitude_slice, :
            ]
            self.wind_north = source["wind_north_m_s"][
                :, :, latitude_slice, :
            ]
            self.geopotential = source["geopotential_m2_s2"][
                :, :, latitude_slice, :
            ]
        with np.load(igrf_path, allow_pickle=False) as source:
            magnetic_flight_level = source["flight_level_ft"].astype(float)
            magnetic_latitude = source["latitude_deg"].astype(float)
            magnetic_longitude = source["longitude_deg"].astype(float)
            reverse_magnetic_lat = np.any(np.diff(magnetic_latitude) < 0.0)
            magnetic_latitude = (
                magnetic_latitude[::-1] if reverse_magnetic_lat else magnetic_latitude
            )
            latitude_slice = (
                slice(None, None, -1) if reverse_magnetic_lat else slice(None)
            )
            self.declination = source["declination_deg"][
                :, latitude_slice, :
            ]
        if not np.array_equal(self.flight_level, magnetic_flight_level):
            raise ValueError("ERA5 and IGRF flight-level axes differ")
        if not np.array_equal(self.latitude, magnetic_latitude):
            raise ValueError("ERA5 and IGRF latitude axes differ")
        if not np.array_equal(self.longitude, magnetic_longitude):
            raise ValueError("ERA5 and IGRF longitude axes differ")
        for axis in (self.time, self.flight_level, self.latitude, self.longitude):
            _validate_interpolation_axis(axis)
        self.periodic_longitude = bool(
            len(self.longitude) >= 3
            and self.longitude[0] == 0.0
            and self.longitude[-1] == 360.0
        )
        if self.periodic_longitude:
            for name, field in (
                ("temperature", self.temperature), ("wind_east", self.wind_east),
                ("wind_north", self.wind_north), ("geopotential", self.geopotential),
                ("declination", self.declination),
            ):
                if not np.array_equal(field[..., 0], field[..., -1]):
                    raise ValueError(f"{name} periodic longitude seam differs")
        self.axes4 = (self.time, self.flight_level, self.latitude, self.longitude)
        self.axes3 = (self.flight_level, self.latitude, self.longitude)

    def _sample_scalar(self, time_unix_s, flight_level_ft, latitude_deg, longitude_deg):
        coordinates = (
            float(time_unix_s),
            float(flight_level_ft),
            float(latitude_deg),
            float(longitude_deg) % 360.0 if self.periodic_longitude else float(longitude_deg),
        )
        prepared = [
            bracket(axis, coordinate, assume_valid=True)
            for axis, coordinate in zip(self.axes4, coordinates)
        ]
        lower = [int(item[0]) for item in prepared]
        fraction = [float(item[1]) for item in prepared]
        in_bounds = all(bool(item[2]) for item in prepared)
        temperature = 0.0
        wind_east = 0.0
        wind_north = 0.0
        geopotential = 0.0
        for bits in itertools.product((0, 1), repeat=4):
            index = tuple(base + bit for base, bit in zip(lower, bits))
            weight = 1.0
            for part, bit in zip(fraction, bits):
                weight *= part if bit else 1.0 - part
            temperature += weight * float(self.temperature[index])
            wind_east += weight * float(self.wind_east[index])
            wind_north += weight * float(self.wind_north[index])
            geopotential += weight * float(self.geopotential[index])
        declination = 0.0
        for bits in itertools.product((0, 1), repeat=3):
            index = tuple(base + bit for base, bit in zip(lower[1:], bits))
            weight = 1.0
            for part, bit in zip(fraction[1:], bits):
                weight *= part if bit else 1.0 - part
            declination += weight * float(self.declination[index])
        return {
            "temperature_k": temperature,
            "wind_east_kt": wind_east * M_S_TO_KT,
            "wind_north_kt": wind_north * M_S_TO_KT,
            "geopotential_altitude_ft": geopotential / G0_M_S2 * M_TO_FT,
            "declination_deg": declination,
            "in_bounds": in_bounds,
        }

    def sample(self, time_unix_s, flight_level_ft, latitude_deg, longitude_deg):
        if all(
            np.ndim(value) == 0
            for value in (time_unix_s, flight_level_ft, latitude_deg, longitude_deg)
        ):
            return self._sample_scalar(
                time_unix_s, flight_level_ft, latitude_deg, longitude_deg
            )
        longitude_coordinate = np.asarray(longitude_deg, dtype=float)
        if self.periodic_longitude:
            longitude_coordinate = np.mod(longitude_coordinate, 360.0)
        coordinates4 = (
            time_unix_s, flight_level_ft, latitude_deg, longitude_coordinate
        )
        temperature, valid_temperature = interpolate4(
            self.temperature, self.axes4, coordinates4, True
        )
        wind_east, valid_east = interpolate4(self.wind_east, self.axes4, coordinates4, True)
        wind_north, valid_north = interpolate4(
            self.wind_north, self.axes4, coordinates4, True
        )
        geopotential, valid_geopotential = interpolate4(
            self.geopotential, self.axes4, coordinates4, True
        )
        declination, valid_declination = interpolate3(
            self.declination,
            self.axes3,
            (flight_level_ft, latitude_deg, longitude_coordinate),
            True,
        )
        in_bounds = (
            valid_temperature
            & valid_east
            & valid_north
            & valid_geopotential
            & valid_declination
        )
        return {
            "temperature_k": temperature,
            "wind_east_kt": wind_east * M_S_TO_KT,
            "wind_north_kt": wind_north * M_S_TO_KT,
            "geopotential_altitude_ft": geopotential / G0_M_S2 * M_TO_FT,
            "declination_deg": declination,
            "in_bounds": in_bounds,
        }


@dataclass(frozen=True)
class EnvironmentSample:
    temperature_k: float
    nominal_wind_north_kt: float = 0.0
    nominal_wind_east_kt: float = 0.0
    geopotential_altitude_ft: float | None = None
    declination_deg: float = 0.0
    in_bounds: bool = True


@dataclass(frozen=True)
class DynamicsParameters:
    mach_reversion_rate_s: float
    mach_noise_strength_per_s: float
    angle_reversion_rate_s: float
    angle_noise_strength_rad2_per_s: float
    wind_reversion_rate_s: float
    wind_noise_strength_kt2_per_s: float
    bank_angle_deg: float = 15.0
    mach_change_rate_per_min: float = 0.1
    altitude_change_rate_ft_per_min: float = 4000.0


@dataclass(frozen=True)
class FlightState:
    time_s: float
    latitude_deg: float
    longitude_deg: float
    pressure_altitude_ft: float
    geopotential_altitude_ft: float
    altitude_target_ft: float
    vertical_speed_fpm: float
    mach: float
    mach_set: float
    mach_target: float
    control_deg: float
    control_set_deg: float
    control_target_deg: float
    mode: int
    wind_error_north_kt: float = 0.0
    wind_error_east_kt: float = 0.0
    declination_deg: float = 0.0


def _apply_segment_event(state: FlightState, event: PoissonEvent):
    if event.event_type == "turn_delta_deg":
        return replace(
            state,
            control_target_deg=float(state.control_set_deg + float(event.target)),
        )
    if event.event_type == "speed_mach":
        return replace(state, mach_target=float(event.target))
    if event.event_type == "altitude_ft":
        return replace(state, altitude_target_ft=float(event.target))
    if event.event_type == "mode":
        new_mode = int(event.target)
        control = state.control_deg
        control_set = state.control_set_deg
        control_target = state.control_target_deg
        if state.mode not in MAGNETIC_MODES and new_mode in MAGNETIC_MODES:
            control -= state.declination_deg
            control_set -= state.declination_deg
            control_target -= state.declination_deg
        elif state.mode in MAGNETIC_MODES and new_mode not in MAGNETIC_MODES:
            control += state.declination_deg
            control_set += state.declination_deg
            control_target += state.declination_deg
        return replace(
            state,
            mode=new_mode,
            control_deg=float(wrap360(control)),
            control_set_deg=float(wrap360(control_set)),
            control_target_deg=float(wrap360(control_target)),
        )
    raise ValueError(f"unsupported event type: {event.event_type}")


def propagate_event_driven_segment(
    initial_state: FlightState,
    end_s: float,
    events: Sequence[PoissonEvent],
    rng,
    dynamics: DynamicsParameters,
    environment_sampler: Callable[[FlightState], EnvironmentSample],
    maximum_step_s: float = 60.0,
    geodesic: str = "wgs84",
):
    """Scalar event-driven segment and exact ledger for clean-model fixtures.

    This is a usable baseline propagator, but it deliberately does not invent an
    unavailable LNAV waypoint law: mode 4 follows its commanded true track like
    a track mode.  A later estimator must either declare a waypoint prior or
    retain that limitation as an explicit branch.
    """

    if end_s < initial_state.time_s or maximum_step_s <= 0.0:
        raise ValueError("invalid propagation interval or step")
    ordered = tuple(sorted(events, key=lambda event: event.time_s))
    if any(event.time_s < initial_state.time_s or event.time_s > end_s for event in ordered):
        raise ValueError("event is outside propagation interval")
    state = replace(initial_state)
    ledger = []
    event_index = 0
    while state.time_s < end_s - 1e-12:
        while event_index < len(ordered) and ordered[event_index].time_s <= state.time_s + 1e-12:
            state = _apply_segment_event(state, ordered[event_index])
            ledger.append(ordered[event_index])
            event_index += 1
        next_event_s = ordered[event_index].time_s if event_index < len(ordered) else math.inf
        next_s = min(end_s, state.time_s + maximum_step_s, next_event_s)
        dt_seconds = next_s - state.time_s
        if dt_seconds <= 1e-12:
            continue
        environment = environment_sampler(state)
        if not environment.in_bounds:
            raise EnvironmentDomainError("environment sample is outside its declared domain")
        temperature = float(environment.temperature_k)
        declination = float(environment.declination_deg)
        tas_m_s = state.mach * float(speed_of_sound_knots(temperature)) * 0.5144444444444445
        maximum_turn = math.degrees(
            math.tan(math.radians(dynamics.bank_angle_deg))
            * G0_M_S2
            / max(tas_m_s, 1.0)
        ) * dt_seconds
        control_set = state.control_set_deg + float(
            np.clip(
                angle_difference(state.control_target_deg, state.control_set_deg),
                -maximum_turn,
                maximum_turn,
            )
        )
        mach_set = state.mach_set + float(
            np.clip(
                state.mach_target - state.mach_set,
                -dynamics.mach_change_rate_per_min * dt_seconds / 60.0,
                dynamics.mach_change_rate_per_min * dt_seconds / 60.0,
            )
        )
        altitude_step = float(
            np.clip(
                state.altitude_target_ft - state.pressure_altitude_ft,
                -dynamics.altitude_change_rate_ft_per_min * dt_seconds / 60.0,
                dynamics.altitude_change_rate_ft_per_min * dt_seconds / 60.0,
            )
        )
        pressure_altitude = state.pressure_altitude_ft + altitude_step
        vertical_speed = altitude_step / dt_seconds * 60.0
        mach = float(
            ou_exact_step(
                state.mach,
                mach_set,
                dynamics.mach_reversion_rate_s,
                dynamics.mach_noise_strength_per_s,
                dt_seconds,
                rng,
            )
        )
        angle_q_deg2 = dynamics.angle_noise_strength_rad2_per_s * (180.0 / math.pi) ** 2
        control = float(
            ou_exact_step(
                state.control_deg,
                control_set,
                dynamics.angle_reversion_rate_s,
                angle_q_deg2,
                dt_seconds,
                rng,
            )
        )
        wind_error_north = float(
            ou_exact_step(
                state.wind_error_north_kt,
                0.0,
                dynamics.wind_reversion_rate_s,
                dynamics.wind_noise_strength_kt2_per_s,
                dt_seconds,
                rng,
            )
        )
        wind_error_east = float(
            ou_exact_step(
                state.wind_error_east_kt,
                0.0,
                dynamics.wind_reversion_rate_s,
                dynamics.wind_noise_strength_kt2_per_s,
                dt_seconds,
                rng,
            )
        )
        tas = mach * float(speed_of_sound_knots(temperature))
        velocity = ground_velocity_from_control(
            tas,
            control,
            state.mode,
            environment.nominal_wind_north_kt + wind_error_north,
            environment.nominal_wind_east_kt + wind_error_east,
            declination,
        )
        destination = destination_wgs84 if geodesic == "wgs84" else destination_sphere
        if geodesic not in ("wgs84", "sphere"):
            raise ValueError("geodesic must be 'wgs84' or 'sphere'")
        latitude, longitude = destination(
            state.latitude_deg,
            state.longitude_deg,
            velocity["track_deg"],
            velocity["speed_kt"] * dt_seconds / 3600.0,
        )
        geopotential_altitude = (
            pressure_altitude
            if environment.geopotential_altitude_ft is None
            else float(environment.geopotential_altitude_ft)
        )
        state = FlightState(
            time_s=next_s,
            latitude_deg=float(latitude),
            longitude_deg=float(longitude),
            pressure_altitude_ft=pressure_altitude,
            geopotential_altitude_ft=geopotential_altitude,
            altitude_target_ft=state.altitude_target_ft,
            vertical_speed_fpm=vertical_speed,
            mach=mach,
            mach_set=mach_set,
            mach_target=state.mach_target,
            control_deg=float(wrap360(control)),
            control_set_deg=float(wrap360(control_set)),
            control_target_deg=float(wrap360(state.control_target_deg)),
            mode=state.mode,
            wind_error_north_kt=wind_error_north,
            wind_error_east_kt=wind_error_east,
            declination_deg=declination,
        )
    while event_index < len(ordered) and ordered[event_index].time_s <= end_s + 1e-12:
        state = _apply_segment_event(state, ordered[event_index])
        ledger.append(ordered[event_index])
        event_index += 1
    return state, tuple(ledger)
