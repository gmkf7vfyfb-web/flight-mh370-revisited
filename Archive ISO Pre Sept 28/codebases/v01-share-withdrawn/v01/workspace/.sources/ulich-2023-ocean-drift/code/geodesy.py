"""Small dependency-free WGS84 inverse/direct geodesic implementation.

Vincenty's ellipsoidal formulae are adequate here because all constructed
offsets are at most 100 NM and none of the inverse fixtures are antipodal.
Angles are degrees, distances are nautical miles, and longitudes are east
positive in [-180, 180).
"""

from __future__ import annotations

import math


WGS84_A_M = 6_378_137.0
WGS84_F = 1.0 / 298.257223563
WGS84_B_M = (1.0 - WGS84_F) * WGS84_A_M
METRES_PER_NM = 1852.0


def wrap180(value: float) -> float:
    return (value + 180.0) % 360.0 - 180.0


def angular_difference(left_deg: float, right_deg: float) -> float:
    return abs(wrap180(left_deg - right_deg))


def inverse(
    latitude_1_deg: float,
    longitude_1_deg: float,
    latitude_2_deg: float,
    longitude_2_deg: float,
    *,
    tolerance: float = 1e-12,
    maximum_iterations: int = 200,
) -> tuple[float, float, float]:
    """Return ellipsoidal distance NM and forward/reverse bearings degrees."""
    if latitude_1_deg == latitude_2_deg and longitude_1_deg == longitude_2_deg:
        return 0.0, 0.0, 180.0
    phi_1 = math.radians(latitude_1_deg)
    phi_2 = math.radians(latitude_2_deg)
    reduced_1 = math.atan((1.0 - WGS84_F) * math.tan(phi_1))
    reduced_2 = math.atan((1.0 - WGS84_F) * math.tan(phi_2))
    sin_u1, cos_u1 = math.sin(reduced_1), math.cos(reduced_1)
    sin_u2, cos_u2 = math.sin(reduced_2), math.cos(reduced_2)
    longitude_difference = math.radians(wrap180(longitude_2_deg - longitude_1_deg))
    lam = longitude_difference
    for _ in range(maximum_iterations):
        sin_lam, cos_lam = math.sin(lam), math.cos(lam)
        sin_sigma = math.sqrt(
            (cos_u2 * sin_lam) ** 2
            + (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lam) ** 2
        )
        if sin_sigma == 0.0:
            return 0.0, 0.0, 180.0
        cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lam
        sigma = math.atan2(sin_sigma, cos_sigma)
        sin_alpha = cos_u1 * cos_u2 * sin_lam / sin_sigma
        cos_sq_alpha = 1.0 - sin_alpha * sin_alpha
        cos_2_sigma_m = (
            cos_sigma - 2.0 * sin_u1 * sin_u2 / cos_sq_alpha
            if cos_sq_alpha > 1e-15
            else 0.0
        )
        coefficient = WGS84_F / 16.0 * cos_sq_alpha * (
            4.0 + WGS84_F * (4.0 - 3.0 * cos_sq_alpha)
        )
        next_lam = longitude_difference + (1.0 - coefficient) * WGS84_F * sin_alpha * (
            sigma
            + coefficient
            * sin_sigma
            * (cos_2_sigma_m + coefficient * cos_sigma * (-1.0 + 2.0 * cos_2_sigma_m**2))
        )
        if abs(next_lam - lam) <= tolerance:
            lam = next_lam
            break
        lam = next_lam
    else:
        raise RuntimeError("Vincenty inverse failed to converge")
    u_sq = cos_sq_alpha * (WGS84_A_M**2 - WGS84_B_M**2) / WGS84_B_M**2
    a_coeff = 1.0 + u_sq / 16384.0 * (
        4096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq))
    )
    b_coeff = u_sq / 1024.0 * (
        256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq))
    )
    delta_sigma = b_coeff * sin_sigma * (
        cos_2_sigma_m
        + b_coeff
        / 4.0
        * (
            cos_sigma * (-1.0 + 2.0 * cos_2_sigma_m**2)
            - b_coeff
            / 6.0
            * cos_2_sigma_m
            * (-3.0 + 4.0 * sin_sigma**2)
            * (-3.0 + 4.0 * cos_2_sigma_m**2)
        )
    )
    distance_m = WGS84_B_M * a_coeff * (sigma - delta_sigma)
    forward = math.degrees(
        math.atan2(
            cos_u2 * math.sin(lam),
            cos_u1 * sin_u2 - sin_u1 * cos_u2 * math.cos(lam),
        )
    ) % 360.0
    reverse = math.degrees(
        math.atan2(
            cos_u1 * math.sin(lam),
            -sin_u1 * cos_u2 + cos_u1 * sin_u2 * math.cos(lam),
        )
    ) % 360.0
    return distance_m / METRES_PER_NM, forward, reverse


def direct(
    latitude_deg: float,
    longitude_deg: float,
    bearing_deg: float,
    distance_nm: float,
    *,
    tolerance: float = 1e-12,
    maximum_iterations: int = 200,
) -> tuple[float, float, float]:
    """Project a point along a WGS84 geodesic; return lat, lon, final bearing."""
    if distance_nm < 0.0:
        raise ValueError("distance_nm must be non-negative")
    if distance_nm == 0.0:
        return latitude_deg, wrap180(longitude_deg), bearing_deg % 360.0
    alpha_1 = math.radians(bearing_deg)
    phi_1 = math.radians(latitude_deg)
    reduced_1 = math.atan((1.0 - WGS84_F) * math.tan(phi_1))
    sin_u1, cos_u1 = math.sin(reduced_1), math.cos(reduced_1)
    sigma_1 = math.atan2(math.tan(reduced_1), math.cos(alpha_1))
    sin_alpha = cos_u1 * math.sin(alpha_1)
    cos_sq_alpha = 1.0 - sin_alpha * sin_alpha
    u_sq = cos_sq_alpha * (WGS84_A_M**2 - WGS84_B_M**2) / WGS84_B_M**2
    a_coeff = 1.0 + u_sq / 16384.0 * (
        4096.0 + u_sq * (-768.0 + u_sq * (320.0 - 175.0 * u_sq))
    )
    b_coeff = u_sq / 1024.0 * (
        256.0 + u_sq * (-128.0 + u_sq * (74.0 - 47.0 * u_sq))
    )
    sigma = distance_nm * METRES_PER_NM / (WGS84_B_M * a_coeff)
    for _ in range(maximum_iterations):
        cos_2_sigma_m = math.cos(2.0 * sigma_1 + sigma)
        sin_sigma, cos_sigma = math.sin(sigma), math.cos(sigma)
        delta_sigma = b_coeff * sin_sigma * (
            cos_2_sigma_m
            + b_coeff
            / 4.0
            * (
                cos_sigma * (-1.0 + 2.0 * cos_2_sigma_m**2)
                - b_coeff
                / 6.0
                * cos_2_sigma_m
                * (-3.0 + 4.0 * sin_sigma**2)
                * (-3.0 + 4.0 * cos_2_sigma_m**2)
            )
        )
        next_sigma = distance_nm * METRES_PER_NM / (WGS84_B_M * a_coeff) + delta_sigma
        if abs(next_sigma - sigma) <= tolerance:
            sigma = next_sigma
            break
        sigma = next_sigma
    else:
        raise RuntimeError("Vincenty direct failed to converge")
    cos_2_sigma_m = math.cos(2.0 * sigma_1 + sigma)
    sin_sigma, cos_sigma = math.sin(sigma), math.cos(sigma)
    temporary = sin_u1 * sin_sigma - cos_u1 * cos_sigma * math.cos(alpha_1)
    phi_2 = math.atan2(
        sin_u1 * cos_sigma + cos_u1 * sin_sigma * math.cos(alpha_1),
        (1.0 - WGS84_F) * math.sqrt(sin_alpha**2 + temporary**2),
    )
    lam = math.atan2(
        sin_sigma * math.sin(alpha_1),
        cos_u1 * cos_sigma - sin_u1 * sin_sigma * math.cos(alpha_1),
    )
    coefficient = WGS84_F / 16.0 * cos_sq_alpha * (
        4.0 + WGS84_F * (4.0 - 3.0 * cos_sq_alpha)
    )
    longitude_correction = (1.0 - coefficient) * WGS84_F * sin_alpha * (
        sigma
        + coefficient
        * sin_sigma
        * (cos_2_sigma_m + coefficient * cos_sigma * (-1.0 + 2.0 * cos_2_sigma_m**2))
    )
    longitude_2 = math.radians(longitude_deg) + lam - longitude_correction
    final_bearing = math.degrees(math.atan2(sin_alpha, -temporary)) % 360.0
    return math.degrees(phi_2), wrap180(math.degrees(longitude_2)), final_bearing

