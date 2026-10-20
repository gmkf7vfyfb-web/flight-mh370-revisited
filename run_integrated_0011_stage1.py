#!/usr/bin/env python3
"""MH370 integrated Bayesian stage-1 estimator, observations through 00:11 UTC.

This program augments the existing refined BTO+BFO+received-power SMC posterior
with explicit controlled-flight performance families at 00:11, propagates each
airborne state through a marginalized terminal-flight kernel, and model-averages
two deliberately weak debris-drift likelihoods.  The 00:19 measurements are not
used.  All numerical assumptions are emitted to CSV for audit and sensitivity
analysis.

The refined posterior is reconstructed from its published summary because the
particle checkpoint is not present in the project files.  This is therefore a
stage-1 integrated estimate, not a replacement for a future full particle-level
rerun from 18:01:49 with numerical ACCESS-G fields.
"""

from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.special import ndtr


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "mh370_stage1_0011"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 3700011
N_AIR = 900_000
N_IMPACT = 1_200_000
R_EARTH_NM = 3440.065
SUBSAT_LAT = 0.0
SUBSAT_LON = 64.5
T_RADAR_TO_0011_H = (5 * 60 + 49 - 11 / 60) / 60  # 18:22 to 00:11
RADAR_1822_LAT = 6.8320131402
RADAR_1822_LON = 96.5051958747


@dataclass(frozen=True)
class Case:
    name: str
    family_prior: tuple[float, float, float]
    bfo_sigma_hz: float
    bfo_vertical_hz_per_fpm: float
    drift_davey_weight: float
    forward_glide_probability: float


PRIMARY = Case(
    "Primary equal-control priors",
    (1 / 3, 1 / 3, 1 / 3),
    12.0,
    0.009,
    0.5,
    0.70,
)

SENSITIVITY_CASES = [
    PRIMARY,
    Case("Cruise-heavy prior", (0.60, 0.20, 0.20), 12.0, 0.009, 0.5, 0.70),
    Case("Descent-open prior", (0.25, 0.35, 0.40), 12.0, 0.009, 0.5, 0.70),
    Case("Tighter vertical-BFO model", (1 / 3, 1 / 3, 1 / 3), 8.0, 0.009, 0.5, 0.70),
    Case("Looser vertical-BFO model", (1 / 3, 1 / 3, 1 / 3), 18.0, 0.009, 0.5, 0.70),
    Case("Davey-drift weighted", (1 / 3, 1 / 3, 1 / 3), 12.0, 0.009, 0.75, 0.70),
    Case("Meta-drift weighted", (1 / 3, 1 / 3, 1 / 3), 12.0, 0.009, 0.25, 0.70),
]


def normal_pdf(x: np.ndarray, mean: float, sd: float) -> np.ndarray:
    return np.exp(-0.5 * ((x - mean) / sd) ** 2) / (sd * math.sqrt(2 * math.pi))


def wrap180(deg: np.ndarray | float) -> np.ndarray:
    return (np.asarray(deg) + 180.0) % 360.0 - 180.0


def initial_bearing(lat1, lon1, lat2, lon2):
    p1 = np.radians(lat1)
    p2 = np.radians(lat2)
    dl = np.radians(np.asarray(lon2) - np.asarray(lon1))
    y = np.sin(dl) * np.cos(p2)
    x = np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(dl)
    return (np.degrees(np.arctan2(y, x)) + 360.0) % 360.0


def great_circle_nm(lat1, lon1, lat2, lon2):
    p1 = np.radians(lat1)
    p2 = np.radians(lat2)
    dp = p2 - p1
    dl = np.radians(np.asarray(lon2) - np.asarray(lon1))
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return R_EARTH_NM * 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def destination(lat, lon, bearing_deg, distance_nm):
    p1 = np.radians(lat)
    l1 = np.radians(lon)
    b = np.radians(bearing_deg)
    d = np.asarray(distance_nm) / R_EARTH_NM
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(b))
    l2 = l1 + np.arctan2(
        np.sin(b) * np.sin(d) * np.cos(p1),
        np.cos(d) - np.sin(p1) * np.sin(p2),
    )
    return np.degrees(p2), (np.degrees(l2) + 540.0) % 360.0 - 180.0


def weighted_quantile(x, w, probs=(0.025, 0.5, 0.975)):
    order = np.argsort(x)
    xs = np.asarray(x)[order]
    ws = np.asarray(w)[order]
    cs = np.cumsum(ws)
    cs /= cs[-1]
    return np.interp(probs, cs, xs)


def effective_sample_size(w):
    p = np.asarray(w) / np.sum(w)
    return 1.0 / np.sum(p * p)


def systematic_resample(rng, w, n):
    p = np.asarray(w, dtype=float)
    p /= p.sum()
    u = (rng.random() + np.arange(n)) / n
    return np.searchsorted(np.cumsum(p), u, side="right")


def reconstruct_airborne_proposal(rng: np.random.Generator, n: int):
    """Reconstruct the refined v3 00:11 posterior from its reported mixture."""
    # Fitted to the reported median, 95% interval, tail masses, and peak ratios.
    means = np.array([-37.47, -36.458390177, -34.22, -33.11])
    sds = np.array([0.17551636, 0.66377073, 0.50503654, 1.01111127])
    weights = np.array([0.07470034, 0.72436317, 0.13711707, 0.06381942])
    comp = rng.choice(4, size=n, p=weights)
    lat = rng.normal(means[comp], sds[comp])
    # Arc ridge calibrated to the reported joint medians; the local slope is
    # digitized from the refined heat map.  Cross-arc scatter represents BTO SD.
    dl = lat + 36.312238135
    lon = 89.60393358 + 1.48 * dl - 0.030 * dl * dl + rng.normal(0, 0.085, n)
    heading = (rng.normal(186.083, 4.0, n) + 360.0) % 360.0
    mach = np.clip(rng.normal(0.78792, 0.018, n), 0.70, 0.84)
    return lat, lon, heading, mach, comp


def sample_control_families(rng, n):
    """Draw equal numbers from three open controlled-flight families."""
    fam = rng.integers(0, 3, n)
    altitude = np.empty(n)
    vspd = np.empty(n)
    slow_minutes = np.zeros(n)
    low_phase_speed = np.empty(n)

    hi = fam == 0
    altitude[hi] = rng.uniform(25_000, 43_000, hi.sum())
    vspd[hi] = rng.normal(0, 120, hi.sum())
    low_phase_speed[hi] = np.nan

    low = fam == 1
    altitude[low] = rng.triangular(3_000, 12_000, 25_000, low.sum())
    vspd[low] = rng.normal(0, 180, low.sum())
    # Completed descent is deliberately limited to the terminal 90 minutes;
    # longer low-level exposure is allowed in sensitivity via the broad tail.
    slow_minutes[low] = np.clip(rng.gamma(2.2, 19.0, low.sum()), 5, 120)
    low_phase_speed[low] = np.clip(
        255 + 0.0048 * altitude[low] + rng.normal(0, 18, low.sum()), 260, 410
    )

    desc = fam == 2
    descent_minutes = rng.uniform(2, 45, desc.sum())
    descent_rate = -rng.uniform(300, 2_500, desc.sum())
    start_alt = rng.uniform(28_000, 43_000, desc.sum())
    end_alt = np.maximum(2_000, start_alt + descent_rate * descent_minutes)
    # Recompute duration when the sampled descent reaches the 2,000-ft floor.
    descent_minutes = np.minimum(descent_minutes, (start_alt - 2_000) / (-descent_rate))
    altitude[desc] = end_alt
    vspd[desc] = descent_rate
    slow_minutes[desc] = descent_minutes
    low_phase_speed[desc] = np.clip(
        300 + 0.0032 * (start_alt + end_alt) / 2 + rng.normal(0, 15, desc.sum()),
        300,
        445,
    )
    return fam, altitude, vspd, slow_minutes, low_phase_speed


def bto_altitude_shift(lat, lon, altitude_ft):
    """Move alternate-altitude states along the local BTO normal.

    The baseline proposal is referenced to 35,000 ft.  The first-order slant
    range correction is tan(elevation)*delta-height along the bearing to the
    satellite subpoint.  This is only a few nautical miles.
    """
    # GEO elevation using spherical Earth geometry.
    central = great_circle_nm(lat, lon, SUBSAT_LAT, SUBSAT_LON) / R_EARTH_NM
    re_over_rs = 6371.0 / 42164.0
    elev = np.arctan2(np.cos(central) - re_over_rs, np.sin(central))
    delta_h_nm = (35_000.0 - altitude_ft) / 6076.12
    shift_nm = np.tan(elev) * delta_h_nm
    bearing = initial_bearing(lat, lon, SUBSAT_LAT, SUBSAT_LON)
    return destination(lat, lon, bearing, shift_nm)


def family_loglikelihood(
    lat, lon, mach, fam, altitude, vspd, slow_minutes, slow_speed, case: Case
):
    # BFO vertical component: conservative effective uncertainty includes
    # fast error, correlated bias, satellite-state, and horizontal-state error.
    delta_bfo = case.bfo_vertical_hz_per_fpm * vspd
    log_bfo = -0.5 * (delta_bfo / case.bfo_sigma_hz) ** 2

    # Performance likelihood: compare loss during descent/low flight with the
    # remaining Mach margin below M0.84.  The baseline high-altitude SMC state is
    # taken as feasible by construction, avoiding double-counting its dynamics.
    speed_sound_35k = 574.0
    cruise_tas = mach * speed_sound_35k
    loss_nm = np.where(
        fam == 0,
        0.0,
        np.maximum(cruise_tas - slow_speed, 0) * slow_minutes / 60.0,
    )
    extra_mach = loss_nm / (speed_sound_35k * T_RADAR_TO_0011_H)
    # Probability that an operational Mach draw can supply the lost distance.
    perf = (1 - ndtr((mach + extra_mach - 0.805) / 0.022))
    perf0 = (1 - ndtr((mach - 0.805) / 0.022))
    perf_ratio = np.clip(perf / np.maximum(perf0, 1e-9), 1e-6, 1.0)

    # Straight-line required speed is an independent hard-envelope diagnostic.
    # It only suppresses states that exceed M0.84 plus a 15-kt tailwind.
    req_gs = great_circle_nm(RADAR_1822_LAT, RADAR_1822_LON, lat, lon) / T_RADAR_TO_0011_H
    max_gs = 0.84 * speed_sound_35k + 15.0 - loss_nm / T_RADAR_TO_0011_H
    hard = 1.0 / (1.0 + np.exp((req_gs - max_gs) / 4.0))

    prior = np.asarray(case.family_prior)[fam]
    return np.log(prior) + log_bfo + np.log(perf_ratio) + np.log(np.clip(hard, 1e-9, 1)), {
        "delta_bfo": delta_bfo,
        "loss_nm": loss_nm,
        "req_gs": req_gs,
        "max_gs": max_gs,
        "bfo_like": np.exp(log_bfo),
        "performance_like": perf_ratio * hard,
    }


def terminal_kernel(rng, lat, lon, heading, altitude, vspd, scenario, forward_prob):
    n = len(lat)
    out_lat = np.empty(n)
    out_lon = np.empty(n)
    impact_minutes = np.empty(n)
    terminal_distance = np.empty(n)
    eof_minutes = np.full(n, np.nan)
    glide_max = np.zeros(n)

    # 0: controlled descent/ditching sequence.  Engines remain available only
    # until the same broad EOF prior used in the other scenarios.  If the sea is
    # not reached by then, the remaining altitude is converted into a controlled
    # glide; this avoids silently granting unlimited powered endurance.
    m = scenario == 0
    descent = rng.uniform(700, 2_500, m.sum())
    eof = np.clip(rng.normal(8.0, 4.5, m.sum()), 0, 25)
    t_to_sea = np.clip(altitude[m] / descent, 0.5, 65.0)
    powered_minutes = np.minimum(t_to_sea, eof)
    remaining_alt = np.maximum(0, altitude[m] - descent * powered_minutes)
    speed = np.clip(250 + 0.0045 * altitude[m] + rng.normal(0, 18, m.sum()), 230, 430)
    powered_dist = speed * powered_minutes / 60.0
    ld = rng.uniform(12, 18, m.sum())
    gmax = ld * remaining_alt / 6076.12
    glide = rng.beta(1.8, 1.3, m.sum()) * gmax
    glide_speed = np.clip(rng.normal(230, 25, m.sum()), 175, 290)
    glide_time_h = glide / glide_speed
    forward = rng.random(m.sum()) < 0.75
    bearing = np.where(
        forward,
        heading[m] + rng.normal(0, 25, m.sum()),
        rng.uniform(0, 360, m.sum()),
    )
    p_lat, p_lon = destination(lat[m], lon[m], heading[m] + rng.normal(0, 10, m.sum()), powered_dist)
    out_lat[m], out_lon[m] = destination(p_lat, p_lon, bearing, glide)
    impact_minutes[m] = powered_minutes + 60 * glide_time_h
    terminal_distance[m] = powered_dist + glide
    eof_minutes[m] = eof
    glide_max[m] = gmax

    # 1: fuel exhaustion followed by a human-controlled glide.  The endurance
    # prior is independent of 00:19 and is intentionally broad.
    m = scenario == 1
    eof = np.clip(rng.normal(8.0, 4.5, m.sum()), 0, 25)
    alt_eof = np.maximum(1_000, altitude[m] + np.minimum(vspd[m], 0) * eof)
    powered_speed = np.clip(285 + 0.0045 * altitude[m], 260, 455)
    powered_dist = powered_speed * eof / 60
    ld = rng.uniform(12, 18, m.sum())
    gmax = ld * (alt_eof / 6076.12)
    # A broad utilization prior includes immediate ditching through near-max glide.
    utilization = rng.beta(1.6, 1.4, m.sum())
    glide = utilization * gmax
    wind_along = rng.normal(0, 12, m.sum())
    glide_speed = np.clip(rng.normal(235, 25, m.sum()), 180, 290)
    glide_time_h = glide / glide_speed
    glide = np.maximum(0, glide + wind_along * glide_time_h)
    forward = rng.random(m.sum()) < forward_prob
    bearing = np.where(
        forward,
        heading[m] + rng.normal(0, 28, m.sum()),
        rng.uniform(0, 360, m.sum()),
    )
    # Combine powered and glide legs sequentially.
    p_lat, p_lon = destination(lat[m], lon[m], heading[m] + rng.normal(0, 8, m.sum()), powered_dist)
    out_lat[m], out_lon[m] = destination(p_lat, p_lon, bearing, glide)
    impact_minutes[m] = eof + 60 * glide_time_h
    terminal_distance[m] = powered_dist + glide
    eof_minutes[m] = eof
    glide_max[m] = gmax

    # 2: fuel exhaustion and short unpowered/uncontrolled descent.
    m = scenario == 2
    eof = np.clip(rng.normal(8.0, 4.5, m.sum()), 0, 25)
    powered_speed = np.clip(285 + 0.0045 * altitude[m], 260, 455)
    powered_dist = powered_speed * eof / 60
    descent_dist = np.clip(rng.normal(8, 5, m.sum()), 0, 25)
    p_lat, p_lon = destination(lat[m], lon[m], heading[m] + rng.normal(0, 8, m.sum()), powered_dist)
    out_lat[m], out_lon[m] = destination(
        p_lat, p_lon, heading[m] + rng.normal(0, 20, m.sum()), descent_dist
    )
    impact_minutes[m] = eof + np.clip(rng.normal(2.0, 0.8, m.sum()), 0.5, 5.0)
    terminal_distance[m] = powered_dist + descent_dist
    eof_minutes[m] = eof

    return out_lat, out_lon, {
        "impact_minutes": impact_minutes,
        "terminal_distance_nm": terminal_distance,
        "eof_minutes": eof_minutes,
        "glide_max_nm": glide_max,
    }


def davey_drift_likelihood(lat, lon):
    """Smooth digitized approximation to Davey Fig. 11.2 (relative scale)."""
    base = 0.48 + 0.040 * (lat + 40.0) + 0.014 * (lon - 85.0)
    hotspot = 0.70 * np.exp(-0.5 * (((lat + 33.4) / 1.35) ** 2 + ((lon - 96.8) / 1.6) ** 2))
    return np.clip(base + hotspot, 0.12, None)


def meta_drift_likelihood(lat, lon):
    """Latitude likelihood from the 12-study ocean-drift meta-analysis."""
    # Reported mean 30.2 S and imputed 95% range 12 S to 38 S -> SD 6.63 deg.
    return normal_pdf(lat, -30.2, 6.63)


def normalize_model_likelihood(like):
    # Unit mean makes explicit model weights comparable before averaging.
    return like / np.mean(like)


def density_grid(lat, lon, weights, extent=(84, 98, -40, -28), nx=560, ny=480, sigma=2.0):
    xmin, xmax, ymin, ymax = extent
    h, ye, xe = np.histogram2d(lat, lon, bins=(ny, nx), range=((ymin, ymax), (xmin, xmax)), weights=weights)
    h = gaussian_filter(h, sigma=sigma)
    # Convert cell mass to relative density; normalization is sufficient for plotting/HPD.
    h /= h.sum()
    xc = (xe[:-1] + xe[1:]) / 2
    yc = (ye[:-1] + ye[1:]) / 2
    return xc, yc, h


def hpd_levels(grid, masses=(0.5, 0.9)):
    flat = np.sort(grid.ravel())[::-1]
    cs = np.cumsum(flat) / flat.sum()
    return [flat[min(np.searchsorted(cs, m), len(flat) - 1)] for m in masses]


def grid_mode(xc, yc, grid):
    iy, ix = np.unravel_index(np.argmax(grid), grid.shape)
    return yc[iy], xc[ix]


def summarize(label, lat, lon, w, grid=None):
    qlat = weighted_quantile(lat, w)
    qlon = weighted_quantile(lon, w)
    if grid is None:
        xc, yc, g = density_grid(lat, lon, w)
    else:
        xc, yc, g = grid
    mlat, mlon = grid_mode(xc, yc, g)
    return {
        "estimate": label,
        "mode_lat_deg": mlat,
        "mode_lon_deg_E": mlon,
        "median_lat_deg": qlat[1],
        "median_lon_deg_E": qlon[1],
        "lat_95_low": qlat[0],
        "lat_95_high": qlat[2],
        "lon_95_low": qlon[0],
        "lon_95_high": qlon[2],
        "prob_south_of_34S": float(np.sum(w[lat < -34]) / np.sum(w)),
        "prob_south_of_36S": float(np.sum(w[lat < -36]) / np.sum(w)),
        "ESS": effective_sample_size(w),
    }


def plot_main(air_grid, impact_prior_grid, impact_post_grid, output):
    fig, axes = plt.subplots(1, 3, figsize=(16, 6.2))
    entries = [
        (air_grid, "00:11 airborne state\nBTO + BFO + power + performance"),
        (impact_prior_grid, "Impact before debris drift\nterminal flight marginalized"),
        (impact_post_grid, "Integrated impact posterior\ndrift models averaged"),
    ]
    for ax, ((xc, yc, g), title) in zip(axes, entries):
        rel = g / g.max()
        im = ax.imshow(
            rel,
            origin="lower",
            extent=(xc[0], xc[-1], yc[0], yc[-1]),
            aspect="auto",
            cmap="viridis",
            vmin=0,
            vmax=1,
        )
        lev = sorted(hpd_levels(g, (0.9, 0.5)))
        ax.contour(xc, yc, g, levels=lev, colors=["white", "#ffcc33"], linewidths=[1.1, 1.6])
        ax.set_title(title, fontsize=14)
        ax.set_xlabel("Longitude (°E)")
        ax.set_xlim(84, 98)
        ax.set_ylim(-40, -28)
        ax.grid(color="white", alpha=0.16, linewidth=0.6)
    axes[0].set_ylabel("Latitude (°)")
    cb = fig.colorbar(im, ax=axes, shrink=0.82, pad=0.015)
    cb.set_label("Relative posterior density")
    fig.suptitle("MH370 stage-1 integrated Bayesian estimate — data through 00:11 UTC only", fontsize=18, y=0.975)
    fig.text(
        0.5,
        0.035,
        "Contours: 50% (yellow) and 90% (white) HPD.  No 00:19 BTO/BFO/log-on likelihood used.",
        ha="center",
        fontsize=10,
    )
    fig.subplots_adjust(left=0.055, right=0.94, bottom=0.14, top=0.83, wspace=0.16)
    fig.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(fig)


def plot_impact_posterior(air_grid, impact_post_grid, output):
    xc, yc, g = impact_post_grid
    axc, ayc, ag = air_grid
    fig, ax = plt.subplots(figsize=(9.2, 7.2))
    rel = g / g.max()
    im = ax.imshow(
        rel,
        origin="lower",
        extent=(xc[0], xc[-1], yc[0], yc[-1]),
        aspect="auto",
        cmap="viridis",
        vmin=0,
        vmax=1,
    )
    lev = sorted(hpd_levels(g, (0.9, 0.5)))
    ax.contour(xc, yc, g, levels=lev, colors=["white", "#ffcc33"], linewidths=[1.4, 2.0])
    air50 = hpd_levels(ag, (0.5,))[0]
    ax.contour(axc, ayc, ag, levels=[air50], colors=["#53d8fb"], linestyles=["--"], linewidths=[1.7])
    mlat, mlon = grid_mode(xc, yc, g)
    ax.plot(mlon, mlat, marker="*", markersize=13, markeredgecolor="black", markerfacecolor="white", label="2-D mode")
    ax.set_title("MH370 integrated impact posterior\nobservations through 00:11 UTC", fontsize=17)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°)")
    ax.set_xlim(84, 98)
    ax.set_ylim(-40, -28)
    ax.grid(color="white", alpha=0.16, linewidth=0.6)
    ax.plot([], [], color="#53d8fb", linestyle="--", lw=1.7, label="00:11 airborne 50% HPD")
    ax.plot([], [], color="#ffcc33", lw=2.0, label="Impact 50% HPD")
    ax.plot([], [], color="white", lw=1.4, label="Impact 90% HPD")
    ax.legend(loc="upper left", framealpha=0.82, fontsize=9)
    cb = fig.colorbar(im, ax=ax, shrink=0.84, pad=0.025)
    cb.set_label("Relative posterior density")
    fig.text(0.5, 0.028, "Terminal flight and debris drift marginalized; 00:19 data excluded.", ha="center", fontsize=10)
    fig.subplots_adjust(left=0.09, right=0.88, bottom=0.14, top=0.86)
    fig.savefig(output, dpi=210, bbox_inches="tight")
    plt.close(fig)


def plot_latitudes(curves, output):
    fig, ax = plt.subplots(figsize=(10.8, 6.4), constrained_layout=True)
    bins = np.linspace(-41, -27, 281)
    for lat, w, label, color in curves:
        h, e = np.histogram(lat, bins=bins, weights=w, density=True)
        h = gaussian_filter(h, 1.4)
        x = (e[:-1] + e[1:]) / 2
        ax.plot(x, h, lw=2.5, label=label, color=color)
    ax.set_xlabel("Latitude (°; south negative)")
    ax.set_ylabel("Posterior density")
    ax.set_title("Effect of terminal-flight and marginalized drift models")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)


def run_case(case: Case, base, controls, terminal_randoms=None, keep_arrays=False):
    lat0, lon0, heading, mach, comp = base
    fam, altitude, vspd, slow_minutes, slow_speed = controls
    lat, lon = bto_altitude_shift(lat0, lon0, altitude)
    logw, diag = family_loglikelihood(
        lat, lon, mach, fam, altitude, vspd, slow_minutes, slow_speed, case
    )
    logw -= np.max(logw)
    w = np.exp(logw)
    w /= w.sum()

    rng_terminal = np.random.default_rng(SEED + 711)
    idx = systematic_resample(rng_terminal, w, N_IMPACT)
    scenario = rng_terminal.integers(0, 3, N_IMPACT)
    ilat, ilon, tdiag = terminal_kernel(
        rng_terminal,
        lat[idx],
        lon[idx],
        heading[idx],
        altitude[idx],
        vspd[idx],
        scenario,
        case.forward_glide_probability,
    )
    wd = normalize_model_likelihood(davey_drift_likelihood(ilat, ilon))
    wm = normalize_model_likelihood(meta_drift_likelihood(ilat, ilon))
    drift = case.drift_davey_weight * wd + (1 - case.drift_davey_weight) * wm
    drift /= drift.sum()

    air_grid = density_grid(lat, lon, w, extent=(84, 98, -40, -28), sigma=1.9)
    ip_grid = density_grid(ilat, ilon, np.ones_like(ilat), extent=(84, 98, -40, -28), sigma=2.0)
    post_grid = density_grid(ilat, ilon, drift, extent=(84, 98, -40, -28), sigma=2.0)
    summary = [
        summarize("00:11 airborne", lat, lon, w, air_grid),
        summarize("Impact before drift", ilat, ilon, np.ones_like(ilat), ip_grid),
        summarize("Impact after model-averaged drift", ilat, ilon, drift, post_grid),
    ]

    # Family evidences/posteriors. Proposal families are uniform by construction;
    # logw already contains the requested prior probabilities.
    family_rows = []
    names = ["High-altitude/near-level", "Earlier descent completed/low-level", "Active controlled descent"]
    for j, name in enumerate(names):
        mask = fam == j
        posterior = w[mask].sum()
        prior = case.family_prior[j]
        family_rows.append(
            {
                "case": case.name,
                "family": name,
                "prior_probability": prior,
                "posterior_probability": posterior,
                "Bayes_factor_vs_complement": (posterior / (1 - posterior)) / (prior / (1 - prior)),
                "mean_altitude_ft_posterior": np.average(altitude[mask], weights=w[mask]),
                "mean_abs_vertical_rate_fpm_posterior": np.average(np.abs(vspd[mask]), weights=w[mask]),
            }
        )

    scenario_rows = []
    sc_names = ["Controlled descent/ditch (power if available)", "Fuel exhaustion + controlled glide", "Fuel exhaustion + short uncontrolled descent"]
    for j, name in enumerate(sc_names):
        m = scenario == j
        scenario_rows.append(
            {
                "case": case.name,
                "terminal_scenario": name,
                "prior_probability": 1 / 3,
                "posterior_probability_after_drift": float(drift[m].sum()),
                "median_terminal_distance_nm": float(np.median(tdiag["terminal_distance_nm"][m])),
                "q95_terminal_distance_nm": float(np.quantile(tdiag["terminal_distance_nm"][m], 0.95)),
                "median_impact_minutes_after_0011": float(np.median(tdiag["impact_minutes"][m])),
                "probability_airborne_at_0019_29": float(np.mean(tdiag["impact_minutes"][m] > 8.4833)),
            }
        )

    result = {
        "summary": summary,
        "family_rows": family_rows,
        "scenario_rows": scenario_rows,
        "air_grid": air_grid,
        "impact_prior_grid": ip_grid,
        "impact_post_grid": post_grid,
    }
    if keep_arrays:
        result["arrays"] = {
            "air_lat": lat,
            "air_lon": lon,
            "air_w": w,
            "family": fam,
            "altitude": altitude,
            "vspd": vspd,
            "impact_lat": ilat,
            "impact_lon": ilon,
            "impact_w": drift,
            "scenario": scenario,
            **tdiag,
        }
    return result


def main():
    os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-mh370")
    rng = np.random.default_rng(SEED)
    base = reconstruct_airborne_proposal(rng, N_AIR)
    controls = sample_control_families(rng, N_AIR)

    all_summary = []
    all_families = []
    all_scenarios = []
    sensitivity_rows = []
    primary_result = None
    for case in SENSITIVITY_CASES:
        result = run_case(case, base, controls, keep_arrays=case is PRIMARY)
        for row in result["summary"]:
            all_summary.append({"case": case.name, **row})
        all_families.extend(result["family_rows"])
        all_scenarios.extend(result["scenario_rows"])
        final = result["summary"][-1]
        sensitivity_rows.append(
            {
                "case": case.name,
                "impact_mode_lat_deg": final["mode_lat_deg"],
                "impact_mode_lon_deg_E": final["mode_lon_deg_E"],
                "impact_median_lat_deg": final["median_lat_deg"],
                "impact_lat_95_low": final["lat_95_low"],
                "impact_lat_95_high": final["lat_95_high"],
                "prob_south_of_36S": final["prob_south_of_36S"],
            }
        )
        if case is PRIMARY:
            primary_result = result

    assert primary_result is not None
    pd.DataFrame(all_summary).to_csv(OUT / "stage1_summary.csv", index=False)
    pd.DataFrame(all_families).to_csv(OUT / "control_family_hypothesis_tests.csv", index=False)
    pd.DataFrame(all_scenarios).to_csv(OUT / "terminal_scenario_summary.csv", index=False)
    pd.DataFrame(sensitivity_rows).to_csv(OUT / "sensitivity_summary.csv", index=False)

    arr = primary_result["arrays"]
    # A manageable weighted particle sample for reproducibility and downstream work.
    sample_rng = np.random.default_rng(SEED + 991)
    air_idx = systematic_resample(sample_rng, arr["air_w"], 50_000)
    impact_idx = systematic_resample(sample_rng, arr["impact_w"], 75_000)
    pd.DataFrame(
        {
            "lat_deg": arr["air_lat"][air_idx],
            "lon_deg_E": arr["air_lon"][air_idx],
            "altitude_ft": arr["altitude"][air_idx],
            "vertical_rate_fpm": arr["vspd"][air_idx],
            "control_family_code": arr["family"][air_idx],
        }
    ).to_csv(OUT / "airborne_0011_posterior_sample.csv", index=False)
    pd.DataFrame(
        {
            "lat_deg": arr["impact_lat"][impact_idx],
            "lon_deg_E": arr["impact_lon"][impact_idx],
            "terminal_scenario_code": arr["scenario"][impact_idx],
            "terminal_distance_nm": arr["terminal_distance_nm"][impact_idx],
            "impact_minutes_after_0011": arr["impact_minutes"][impact_idx],
        }
    ).to_csv(OUT / "impact_posterior_sample.csv", index=False)

    plot_main(
        primary_result["air_grid"],
        primary_result["impact_prior_grid"],
        primary_result["impact_post_grid"],
        OUT / "mh370_stage1_integrated_heatmaps.png",
    )
    plot_impact_posterior(
        primary_result["air_grid"],
        primary_result["impact_post_grid"],
        OUT / "mh370_stage1_integrated_impact_heatmap.png",
    )
    plot_latitudes(
        [
            (arr["air_lat"], arr["air_w"], "00:11 airborne", "#1f77b4"),
            (arr["impact_lat"], np.ones_like(arr["impact_lat"]), "Impact before drift", "#777777"),
            (arr["impact_lat"], arr["impact_w"], "Impact after drift mixture", "#d62728"),
        ],
        OUT / "mh370_stage1_latitude_marginals.png",
    )

    assumptions = [
        ("Observation cutoff", "00:11:00 UTC; no 00:19 measurement likelihood"),
        ("Satellite/RF proposal", "Refined v3 BTO+BFO+received-power/3-D-gain SMC summary reconstruction"),
        ("Gain precompensation", "Gain-survival coefficient already marginalized in proposal; posterior mean 0.677"),
        ("Control-family prior", "Equal 1/3: high-level, completed lower-level descent, active controlled descent"),
        ("BFO vertical coefficient", f"{PRIMARY.bfo_vertical_hz_per_fpm:.3f} Hz/fpm"),
        ("Effective vertical-BFO sigma", f"{PRIMARY.bfo_sigma_hz:.1f} Hz; sensitivity 8 and 18 Hz"),
        ("Low/descent duration", "5–120 min completed low phase; 2–45 min active descent"),
        ("Performance ceiling", "M0.84 plus 15 kt favorable-wind hard-envelope check"),
        ("Fuel-exhaustion time after 00:11", "Truncated Normal(8.0 min, 4.5 min), 0–25 min; not conditioned on 00:19"),
        ("Controlled glide", "L/D Uniform(12,18), altitude-scaled; 70% forward-biased, 30% any bearing"),
        ("Terminal-scenario prior", "Equal 1/3 powered controlled ditch, controlled glide, short uncontrolled descent"),
        ("Drift model average", "50% Davey Fig. 11.2 smooth digitization, 50% 12-study meta-analysis latitude model"),
        ("Davey drift use", "Relative likelihood, normalized to unit mean over impact prior"),
        ("Meta drift use", "Normal latitude mean 30.2°S, SD 6.63° from reported 12°S–38°S 95% range"),
        ("Monte Carlo", f"{N_AIR:,} airborne augmentations; {N_IMPACT:,} terminal propagations; seed {SEED}"),
    ]
    pd.DataFrame(assumptions, columns=["parameter", "primary_value_or_method"]).to_csv(
        OUT / "model_assumptions.csv", index=False
    )
    with open(OUT / "run_manifest.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "seed": SEED,
                "n_airborne": N_AIR,
                "n_impact": N_IMPACT,
                "observation_cutoff": "2014-03-08T00:11:00Z",
                "uses_0019_likelihood": False,
                "source_files": [
                    "mh370_0011_refined_v3_notes.txt",
                    "mh370_0011_refined_v3_summary.csv",
                    "mh370_post_radar_measurement_ledger_through_0011.csv",
                    "Bayesian_Methods_MH370_Search_3Dec2015.pdf",
                    "A META ANALYSIS OF GEOSPATIAL ESTIMATES IN THE CASE OF MALAYSIAN AIRLINES FLIGHT MH370.pdf",
                    "9M-MRO Fuel Model V5.X.xlsm",
                ],
            },
            f,
            indent=2,
        )

    print(pd.DataFrame(all_summary).query("case == @PRIMARY.name").to_string(index=False))
    print("\nControl-family hypothesis tests")
    print(pd.DataFrame(all_families).query("case == @PRIMARY.name").to_string(index=False))
    print("\nSensitivity")
    print(pd.DataFrame(sensitivity_rows).to_string(index=False))


if __name__ == "__main__":
    main()
