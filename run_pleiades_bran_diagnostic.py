#!/usr/bin/env python3
"""Diagnostic Pleiades/BRAN update of the MH370 00:11 airborne posterior.

This is not a rerun of the gridded BRAN2015/2016 ocean models.  It uses the
along-arc best-match origin reported from the public 86,400-track
BRAN2015 experiment (35.4 S, 92.8 E), the nearly identical CSIRO common-model
origin (35.6 S, 92.8 E), and the CSIRO statement that origins within about
50 km along the arc remain plausible.  The resulting likelihood is deliberately
broader than a point constraint and is evaluated at impact, then smoothed back
to the 00:11 airborne ancestor.  No 00:19 observation is used.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-mh370-pleiades-bran")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from run_integrated_0011_stage1 import (
    Case,
    bto_altitude_shift,
    density_grid,
    family_loglikelihood,
    grid_mode,
    great_circle_nm,
    hpd_levels,
    reconstruct_airborne_proposal,
    sample_control_families,
    summarize,
    systematic_resample,
    terminal_kernel,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "mh370_pleiades_bran_diagnostic"
OUT.mkdir(parents=True, exist_ok=True)

SEED = 3702314
N_AIR = 1_200_000
N_TERMINAL = 1_800_000
SIGMA_BFO_HZ = 0.9953793624482928
EXTENT = (84.0, 98.0, -40.0, -28.0)


def normalize_logweights(logw):
    logw = logw - np.max(logw)
    w = np.exp(logw)
    return w / w.sum()


def bran_primary_likelihood(lat, lon, sigma_nm=35.0):
    """Broad published along-arc BRAN anchor, without applying a search mask."""
    # Midpoint of the CSIRO common-model solution (35.6S) and later full-arc
    # BRAN2015 closest-drifter solution (35.4S), both at 92.8E.
    distance = great_circle_nm(lat, lon, -35.5, 92.8)
    return np.exp(-0.5 * (distance / sigma_nm) ** 2)


def bran_published_candidate_mixture(lat, lon):
    """Sensitivity likelihood including the two lower-confidence CSIRO origins."""
    centers = [(-35.5, 92.8, 0.60, 35.0), (-34.7, 92.6, 0.20, 30.0), (-35.3, 91.8, 0.20, 30.0)]
    likelihood = np.zeros_like(lat, dtype=float)
    for clat, clon, weight, sigma_nm in centers:
        distance = great_circle_nm(lat, lon, clat, clon)
        likelihood += weight * np.exp(-0.5 * (distance / sigma_nm) ** 2)
    return likelihood


def plot_comparison(prior_grid, post_grid, output):
    fig, axes = plt.subplots(1, 2, figsize=(14.6, 6.5))
    for ax, grid, title, overlay in [
        (axes[0], prior_grid, "Before Pleiades/BRAN hypothesis", None),
        (axes[1], post_grid, "Assuming Pleiades objects are MH370\nBRAN likelihood backward-smoothed", prior_grid),
    ]:
        xc, yc, density = grid
        im = ax.imshow(
            density / density.max(),
            origin="lower",
            extent=(xc[0], xc[-1], yc[0], yc[-1]),
            aspect="auto",
            cmap="viridis",
            vmin=0,
            vmax=1,
        )
        levels = sorted(hpd_levels(density, (0.9, 0.5)))
        ax.contour(xc, yc, density, levels=levels, colors=["white", "#ffcc33"], linewidths=[1.2, 1.8])
        if overlay is not None:
            ox, oy, od = overlay
            ax.contour(
                ox,
                oy,
                od,
                levels=[hpd_levels(od, (0.5,))[0]],
                colors=["#53d8fb"],
                linestyles=["--"],
                linewidths=[1.6],
            )
        mode_lat, mode_lon = grid_mode(xc, yc, density)
        ax.plot(mode_lon, mode_lat, "*", ms=12, mec="black", mfc="white")
        ax.set_title(title, fontsize=14)
        ax.set_xlabel("Longitude (°E)")
        ax.set_xlim(EXTENT[0], EXTENT[1])
        ax.set_ylim(EXTENT[2], EXTENT[3])
        ax.grid(color="white", alpha=0.16, linewidth=0.6)
    axes[0].set_ylabel("Latitude (°; south negative)")
    fig.subplots_adjust(left=0.065, right=0.90, bottom=0.15, top=0.81, wspace=0.15)
    cax = fig.add_axes([0.92, 0.20, 0.017, 0.55])
    cb = fig.colorbar(im, cax=cax)
    cb.set_label("Relative posterior density")
    fig.suptitle("MH370 airborne position at 00:11 UTC — Pleiades/BRAN diagnostic", fontsize=17, y=0.97)
    fig.text(
        0.5,
        0.045,
        "Published along-arc BRAN anchor diagnostic; no search-area mask and no 00:19 observation.",
        ha="center",
        fontsize=10,
    )
    fig.savefig(output, dpi=210, bbox_inches="tight")
    plt.close(fig)


def main():
    case = Case(
        name="Refined random BFO noise",
        family_prior=(1 / 3, 1 / 3, 1 / 3),
        bfo_sigma_hz=SIGMA_BFO_HZ,
        bfo_vertical_hz_per_fpm=0.009,
        drift_davey_weight=0.5,
        forward_glide_probability=0.70,
    )
    rng = np.random.default_rng(SEED)
    base = reconstruct_airborne_proposal(rng, N_AIR)
    controls = sample_control_families(rng, N_AIR)
    lat0, lon0, heading, mach, _ = base
    family, altitude, vspd, slow_minutes, slow_speed = controls
    air_lat, air_lon = bto_altitude_shift(lat0, lon0, altitude)
    logw, _ = family_loglikelihood(
        air_lat, air_lon, mach, family, altitude, vspd, slow_minutes, slow_speed, case
    )
    air_w = normalize_logweights(logw)
    prior_grid = density_grid(air_lat, air_lon, air_w, extent=EXTENT, nx=600, ny=520, sigma=2.0)

    trng = np.random.default_rng(SEED + 711)
    ancestor = systematic_resample(trng, air_w, N_TERMINAL)
    scenario = trng.integers(0, 3, N_TERMINAL)
    impact_lat, impact_lon, terminal_diag = terminal_kernel(
        trng,
        air_lat[ancestor],
        air_lon[ancestor],
        heading[ancestor],
        altitude[ancestor],
        vspd[ancestor],
        scenario,
        case.forward_glide_probability,
    )

    like_primary = bran_primary_likelihood(impact_lat, impact_lon)
    post_w = like_primary / like_primary.sum()
    post_grid = density_grid(
        air_lat[ancestor], air_lon[ancestor], post_w, extent=EXTENT, nx=600, ny=520, sigma=2.0
    )

    like_mixture = bran_published_candidate_mixture(impact_lat, impact_lon)
    mixture_w = like_mixture / like_mixture.sum()
    mixture_grid = density_grid(
        air_lat[ancestor], air_lon[ancestor], mixture_w, extent=EXTENT, nx=600, ny=520, sigma=2.0
    )

    rows = [
        summarize("Before Pleiades/BRAN hypothesis", air_lat, air_lon, air_w, prior_grid),
        summarize(
            "Pleiades assumed MH370; published along-arc BRAN anchor diagnostic",
            air_lat[ancestor],
            air_lon[ancestor],
            post_w,
            post_grid,
        ),
        summarize(
            "Pleiades assumed MH370; published three-origin BRAN sensitivity",
            air_lat[ancestor],
            air_lon[ancestor],
            mixture_w,
            mixture_grid,
        ),
    ]
    for row in rows:
        row["uses_0019_observation"] = False
    pd.DataFrame(rows).to_csv(OUT / "pleiades_bran_airborne_0011_summary.csv", index=False)

    # Retain impact-state diagnostics to distinguish the BRAN origin from the
    # backward-smoothed airborne sixth-arc state.
    impact_rows = [
        summarize("Impact prior", impact_lat, impact_lon, np.ones_like(impact_lat)),
        summarize("Impact after primary Pleiades/BRAN likelihood", impact_lat, impact_lon, post_w),
        summarize("Impact after three-origin sensitivity likelihood", impact_lat, impact_lon, mixture_w),
    ]
    pd.DataFrame(impact_rows).to_csv(OUT / "pleiades_bran_impact_summary.csv", index=False)

    terminal_rows = []
    scenario_names = [
        "Controlled descent/ditch (power if available)",
        "Fuel exhaustion + controlled glide",
        "Fuel exhaustion + short uncontrolled descent",
    ]
    for code, name in enumerate(scenario_names):
        mask = scenario == code
        sw = post_w[mask]
        distances = terminal_diag["terminal_distance_nm"][mask]
        order = np.argsort(distances)
        cumulative = np.cumsum(sw[order]) / sw.sum()
        quantiles = np.interp([0.5, 0.95], cumulative, distances[order])
        terminal_rows.append(
            {
                "terminal_scenario": name,
                "posterior_probability": float(sw.sum()),
                "median_terminal_distance_nm": quantiles[0],
                "q95_terminal_distance_nm": quantiles[1],
                "probability_terminal_distance_over_100nm": float(
                    sw[distances > 100].sum() / sw.sum()
                ),
            }
        )
    all_distances = terminal_diag["terminal_distance_nm"]
    all_order = np.argsort(all_distances)
    all_cumulative = np.cumsum(post_w[all_order])
    all_quantiles = np.interp([0.5, 0.95], all_cumulative, all_distances[all_order])
    terminal_rows.append(
        {
            "terminal_scenario": "All terminal scenarios",
            "posterior_probability": 1.0,
            "median_terminal_distance_nm": all_quantiles[0],
            "q95_terminal_distance_nm": all_quantiles[1],
            "probability_terminal_distance_over_100nm": float(
                post_w[all_distances > 100].sum()
            ),
        }
    )
    pd.DataFrame(terminal_rows).to_csv(OUT / "pleiades_bran_terminal_diagnostics.csv", index=False)

    plot_comparison(prior_grid, post_grid, OUT / "mh370_0011_pleiades_bran_diagnostic.png")

    manifest = {
        "status": "published along-arc BRAN-anchor diagnostic, not a full 2-D BRAN grid rerun",
        "primary_origin": {"lat_deg": -35.5, "lon_deg_E": 92.8, "sigma_nm": 35.0},
        "origin_basis": "midpoint of CSIRO common-model 35.6S result and later 86,400-drifter along-arc BRAN2015 35.4S result",
        "search_area_mask": False,
        "uses_0019_observations": False,
        "likelihood_location": "impact state, backward-smoothed to the 00:11 ancestor",
        "n_airborne": N_AIR,
        "n_terminal": N_TERMINAL,
        "seed": SEED,
        "important_limitation": "The public MATLAB track links are no longer live and two-dimensional BRAN2015/2016 trajectories are unavailable locally; the diagnostic cannot discover off-arc modes that a source grid extending 150-200 NM either side of the seventh arc might contain.",
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(pd.DataFrame(rows).to_string(index=False))
    print("\nImpact summaries")
    print(pd.DataFrame(impact_rows).to_string(index=False))
    print("\nTerminal diagnostics")
    print(pd.DataFrame(terminal_rows).to_string(index=False))


if __name__ == "__main__":
    main()
