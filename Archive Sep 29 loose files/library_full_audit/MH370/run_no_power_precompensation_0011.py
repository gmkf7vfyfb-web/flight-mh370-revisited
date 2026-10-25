#!/usr/bin/env python3
"""Conditional no-power-precompensation reconstruction for MH370 at 00:11 UTC.

The refined-v3 particle checkpoint is absent, so the exact conditional density
p(x_0011 | beta=1) cannot be recovered by ordinary particle reweighting.  This
program recovers the empirical received-power latitude likelihood from the
matched BTO+BFO and BTO+BFO+power curves produced by the original integrated
run, then changes its contrast from the refined posterior mean beta=0.67664 to
beta=1.  The primary correction assumes that spatial log-likelihood contrast
scales linearly with beta.  A beta-squared contrast is retained as a deliberately
strong sensitivity case for the Gaussian RF residual term.

The Pleiades/BRAN likelihood is evaluated at sampled impact states and smoothed
backward through the existing controlled terminal-flight kernel.  No 00:19 BTO,
BFO, received-power, or log-on observation is used.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-mh370-no-precomp")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from PIL import Image
from scipy.ndimage import gaussian_filter1d

from run_integrated_0011_stage1 import (
    Case,
    bto_altitude_shift,
    density_grid,
    family_loglikelihood,
    grid_mode,
    hpd_levels,
    reconstruct_airborne_proposal,
    sample_control_families,
    summarize,
    systematic_resample,
    terminal_kernel,
)
from run_pleiades_bran_fl400_expanded import (
    GRID_LATS,
    GRID_LONS,
    bilinear_grid_lookup,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "mh370_no_power_precomp_0011"
OUT.mkdir(parents=True, exist_ok=True)

SOURCE_PDF_PLOT = ROOT / "downloads" / "MH370" / "mh370_integrated_0011_final_latitude_pdf.png"
ORIGIN_GRID_CSV = ROOT / "outputs" / "mh370_pleiades_bran_fl400_expanded" / "expanded_origin_grid.csv"

SEED = 3701001
N_AIR = 1_000_000
N_TERMINAL = 1_500_000
EXTENT = (84.0, 98.0, -40.0, -28.0)
BETA_REFERENCE = 0.6766419224079634

CASES = {
    "Marginalized beta (reference)": 1.0,
    "Beta=1, linear RF-contrast reconstruction": 1.0 / BETA_REFERENCE,
    "Beta=1, quadratic RF-contrast sensitivity": 1.0 / (BETA_REFERENCE * BETA_REFERENCE),
}

COMPONENT_NAMES = ["37.47S", "36.46S", "34.22S", "33.11S"]


def normalize_logweights(logw):
    shifted = np.asarray(logw, dtype=float) - np.max(logw)
    w = np.exp(shifted)
    return w / w.sum()


def digitize_curve(image_rgb, color, x_pixels):
    """Trace a Matplotlib line from its exact/antialiased RGB pixels."""
    target = np.asarray(color, dtype=int)
    distance = np.max(np.abs(image_rgb.astype(int) - target), axis=2)
    y_curve = np.full(len(x_pixels), np.nan)
    for k, x in enumerate(x_pixels):
        lo = max(0, x - 1)
        hi = min(image_rgb.shape[1], x + 2)
        y = np.where(np.any(distance[:, lo:hi] < 12, axis=1))[0]
        y = y[(y >= 80) & (y <= 1175)]
        if len(y) == 0:
            continue
        clusters = np.split(y, np.where(np.diff(y) > 3)[0] + 1)
        # The actual posterior line is below legend samples in the affected
        # longitude range, hence select the lowest-on-page cluster.
        cluster = max(clusters, key=lambda values: float(np.mean(values)))
        value = float(np.median(cluster))
        if x > 1000 and value < 250:
            continue
        y_curve[k] = value

    valid = np.isfinite(y_curve)
    y_curve = np.interp(x_pixels, x_pixels[valid], y_curve[valid])
    # Plot calibration: density=0 at y=1170 and 0.1 per 175.5 pixels.
    density = np.clip((1170.0 - y_curve) / 1755.0, 0.0, None)
    return gaussian_filter1d(density, 2.0)


def empirical_rf_likelihood():
    """Recover L_RF(latitude) from matched plotted posterior densities."""
    image = np.asarray(Image.open(SOURCE_PDF_PLOT).convert("RGB"))
    x_pixels = np.arange(213, 1900)
    latitude = -40.0 + (x_pixels - 207.0) / 134.0
    bto_bfo = digitize_curve(image, (31, 119, 180), x_pixels)
    integrated = digitize_curve(image, (255, 127, 14), x_pixels)
    bto_bfo /= np.trapezoid(bto_bfo, latitude)
    integrated /= np.trapezoid(integrated, latitude)

    raw_log_bf = np.log(np.clip(integrated, 1e-5, None)) - np.log(
        np.clip(bto_bfo, 1e-5, None)
    )
    log_bf = gaussian_filter1d(raw_log_bf, 10.0)
    # Keep extrapolation outside the well-resolved plotting interval flat.
    resolved = (latitude >= -38.4) & (latitude <= -31.2)
    left = float(log_bf[np.where(resolved)[0][0]])
    right = float(log_bf[np.where(resolved)[0][-1]])
    log_bf = np.where(latitude < -38.4, left, log_bf)
    log_bf = np.where(latitude > -31.2, right, log_bf)
    # An arbitrary additive constant cancels in every posterior update.
    reference = float(np.interp(-36.458390177, latitude, log_bf))
    log_bf -= reference
    return latitude, bto_bfo, integrated, log_bf


def load_pleiades_grid():
    frame = pd.read_csv(ORIGIN_GRID_CSV)
    grid = np.zeros((len(GRID_LATS), len(GRID_LONS)), dtype=float)
    iy = np.rint((frame.seed_lat_deg.to_numpy() - GRID_LATS[0]) / (GRID_LATS[1] - GRID_LATS[0])).astype(int)
    ix = np.rint((frame.seed_lon_deg_E.to_numpy() - GRID_LONS[0]) / (GRID_LONS[1] - GRID_LONS[0])).astype(int)
    grid[iy, ix] = frame.relative_likelihood.to_numpy(float)
    return grid


def component_rows(case_name, conditioning, component, weights):
    total = float(weights.sum())
    return [
        {
            "power_model": case_name,
            "imagery_conditioning": conditioning,
            "component": name,
            "posterior_probability": float(weights[component == code].sum() / total),
        }
        for code, name in enumerate(COMPONENT_NAMES)
    ]


def plot_heatmap_comparison(grids, output):
    entries = [
        ("Marginalized beta (reference)", "Without Pleiades", "Marginalized beta\nPleiades excluded"),
        ("Beta=1, linear RF-contrast reconstruction", "Without Pleiades", "No precompensation (beta=1)\nPleiades excluded"),
        ("Marginalized beta (reference)", "With Pleiades/BRAN", "Marginalized beta\nPleiades objects assumed MH370"),
        ("Beta=1, linear RF-contrast reconstruction", "With Pleiades/BRAN", "No precompensation (beta=1)\nPleiades objects assumed MH370"),
    ]
    fig, axes = plt.subplots(2, 2, figsize=(14.2, 11.2), sharex=True, sharey=True)
    im = None
    for ax, (case_name, conditioning, title) in zip(axes.ravel(), entries):
        xc, yc, d = grids[(case_name, conditioning)]
        im = ax.imshow(
            d / d.max(),
            origin="lower",
            extent=(xc[0], xc[-1], yc[0], yc[-1]),
            cmap="viridis",
            vmin=0,
            vmax=1,
            aspect="auto",
        )
        levels = sorted(hpd_levels(d, (0.90, 0.50)))
        ax.contour(xc, yc, d, levels=levels, colors=["white", "#ffcc33"], linewidths=[1.0, 1.6])
        mode_lat, mode_lon = grid_mode(xc, yc, d)
        ax.plot(mode_lon, mode_lat, "*", ms=11, mec="black", mfc="white")
        ax.set_title(title, fontsize=13)
        ax.grid(color="white", alpha=0.14, linewidth=0.6)
        ax.set_xlim(EXTENT[0], EXTENT[1])
        ax.set_ylim(EXTENT[2], EXTENT[3])
    axes[1, 0].set_xlabel("Longitude (deg E)")
    axes[1, 1].set_xlabel("Longitude (deg E)")
    axes[0, 0].set_ylabel("Latitude (deg; south negative)")
    axes[1, 0].set_ylabel("Latitude (deg; south negative)")
    cax = fig.add_axes([0.92, 0.18, 0.015, 0.63])
    fig.colorbar(im, cax=cax, label="Relative posterior density")
    fig.suptitle("MH370 00:11 UTC posterior: effect of assuming no AES power precompensation", fontsize=17, y=0.975)
    fig.text(
        0.5,
        0.025,
        "Primary beta=1 reconstruction uses linear RF-contrast scaling; imagery likelihood is applied at impact and smoothed backward. No 00:19 likelihood.",
        ha="center",
        fontsize=10,
    )
    fig.subplots_adjust(left=0.07, right=0.90, bottom=0.08, top=0.90, hspace=0.18, wspace=0.10)
    fig.savefig(output, dpi=210, bbox_inches="tight")
    plt.close(fig)


def plot_latitude_marginals(curves, output):
    fig, axes = plt.subplots(1, 2, figsize=(14.2, 5.7), sharey=True)
    colors = ["#4c78a8", "#f58518", "#b279a2"]
    styles = ["-", "-", "--"]
    for ax, conditioning in zip(axes, ["Without Pleiades", "With Pleiades/BRAN"]):
        for (case_name, color, style) in zip(CASES, colors, styles):
            lat, density = curves[(case_name, conditioning)]
            ax.plot(lat, density, color=color, linestyle=style, linewidth=2.5, label=case_name)
        ax.set_title(conditioning)
        ax.set_xlabel("Latitude at 00:11 UTC (deg; south negative)")
        ax.grid(alpha=0.25)
        ax.set_xlim(-39, -31)
    axes[0].set_ylabel("Posterior density")
    axes[1].legend(fontsize=8.5, loc="upper right")
    fig.suptitle("Latitude marginal under fixed beta=1 received-power contrast", fontsize=16, y=0.98)
    fig.text(0.5, 0.025, "Solid orange is the primary reconstruction; dashed purple is the stronger beta-squared sensitivity.", ha="center", fontsize=10)
    fig.subplots_adjust(left=0.07, right=0.98, bottom=0.15, top=0.84, wspace=0.10)
    fig.savefig(output, dpi=210, bbox_inches="tight")
    plt.close(fig)


def latitude_curve(lat, weights, bins=np.linspace(-40, -28, 481)):
    hist, edges = np.histogram(lat, bins=bins, weights=weights, density=False)
    centers = (edges[:-1] + edges[1:]) / 2
    hist = gaussian_filter1d(hist.astype(float), 2.0)
    hist /= np.trapezoid(hist, centers)
    return centers, hist


def main():
    rf_lat, comparator_pdf, integrated_pdf, rf_log_bf = empirical_rf_likelihood()
    pd.DataFrame(
        {
            "latitude_deg": rf_lat,
            "bto_bfo_density_digitized": comparator_pdf,
            "integrated_density_digitized": integrated_pdf,
            "empirical_log_RF_Bayes_factor_relative": rf_log_bf,
        }
    ).to_csv(OUT / "empirical_received_power_likelihood.csv", index=False)

    case = Case(
        name="Refined random BFO noise",
        family_prior=(1 / 3, 1 / 3, 1 / 3),
        bfo_sigma_hz=0.9953793624482928,
        bfo_vertical_hz_per_fpm=0.009,
        drift_davey_weight=0.5,
        forward_glide_probability=0.70,
    )
    rng = np.random.default_rng(SEED)
    lat0, lon0, heading, mach, component = reconstruct_airborne_proposal(rng, N_AIR)
    family, altitude, vspd, slow_minutes, slow_speed = sample_control_families(rng, N_AIR)
    air_lat, air_lon = bto_altitude_shift(lat0, lon0, altitude)
    performance_logw, _ = family_loglikelihood(
        air_lat,
        air_lon,
        mach,
        family,
        altitude,
        vspd,
        slow_minutes,
        slow_speed,
        case,
    )
    empirical_log_rf = np.interp(air_lat, rf_lat, rf_log_bf)

    air_weights = {}
    for case_name, contrast_scale in CASES.items():
        air_weights[case_name] = normalize_logweights(
            performance_logw + (contrast_scale - 1.0) * empirical_log_rf
        )

    # Draw the terminal ensemble from the reference posterior once.  Fixed-beta
    # cases are then exact importance reweightings within this reconstructed
    # marginal model, and share identical terminal random numbers.
    terminal_rng = np.random.default_rng(SEED + 711)
    reference_weights = air_weights["Marginalized beta (reference)"]
    ancestor = systematic_resample(terminal_rng, reference_weights, N_TERMINAL)
    scenario = terminal_rng.integers(0, 3, N_TERMINAL)
    impact_lat, impact_lon, _ = terminal_kernel(
        terminal_rng,
        air_lat[ancestor],
        air_lon[ancestor],
        heading[ancestor],
        altitude[ancestor],
        vspd[ancestor],
        scenario,
        case.forward_glide_probability,
    )
    pleiades_grid = load_pleiades_grid()
    inside = (
        (impact_lat >= GRID_LATS[0])
        & (impact_lat <= GRID_LATS[-1])
        & (impact_lon >= GRID_LONS[0])
        & (impact_lon <= GRID_LONS[-1])
    )
    imagery_like = np.full(N_TERMINAL, 1e-300)
    imagery_like[inside] = np.clip(
        bilinear_grid_lookup(pleiades_grid, impact_lat[inside], impact_lon[inside]),
        1e-300,
        None,
    )

    summary_rows = []
    component_summary = []
    grids = {}
    curves = {}
    curve_frame = None
    for case_name, contrast_scale in CASES.items():
        w = air_weights[case_name]
        grid_no = density_grid(air_lat, air_lon, w, extent=EXTENT, nx=600, ny=520, sigma=2.0)
        grids[(case_name, "Without Pleiades")] = grid_no
        row = summarize(f"{case_name} — without Pleiades", air_lat, air_lon, w, grid_no)
        row.update(
            {
                "power_model": case_name,
                "imagery_conditioning": "Without Pleiades",
                "RF_contrast_scale": contrast_scale,
                "uses_0019_observation_likelihood": False,
            }
        )
        summary_rows.append(row)
        component_summary.extend(component_rows(case_name, "Without Pleiades", component, w))
        curves[(case_name, "Without Pleiades")] = latitude_curve(air_lat, w)

        # Importance ratio from reference air posterior to this fixed-beta case.
        ratio = np.exp((contrast_scale - 1.0) * empirical_log_rf[ancestor])
        post_w = ratio * imagery_like
        post_w /= post_w.sum()
        post_lat = air_lat[ancestor]
        post_lon = air_lon[ancestor]
        grid_yes = density_grid(post_lat, post_lon, post_w, extent=EXTENT, nx=600, ny=520, sigma=2.0)
        grids[(case_name, "With Pleiades/BRAN")] = grid_yes
        row = summarize(f"{case_name} — with Pleiades/BRAN", post_lat, post_lon, post_w, grid_yes)
        row.update(
            {
                "power_model": case_name,
                "imagery_conditioning": "With Pleiades/BRAN",
                "RF_contrast_scale": contrast_scale,
                "uses_0019_observation_likelihood": False,
            }
        )
        summary_rows.append(row)
        component_summary.extend(
            component_rows(case_name, "With Pleiades/BRAN", component[ancestor], post_w)
        )
        curves[(case_name, "With Pleiades/BRAN")] = latitude_curve(post_lat, post_w)

    pd.DataFrame(summary_rows).to_csv(OUT / "no_precompensation_summary.csv", index=False)
    pd.DataFrame(component_summary).to_csv(OUT / "no_precompensation_component_masses.csv", index=False)

    curve_rows = []
    for (case_name, conditioning), (latitude, density) in curves.items():
        curve_rows.extend(
            {
                "power_model": case_name,
                "imagery_conditioning": conditioning,
                "latitude_deg": float(la),
                "posterior_density": float(de),
            }
            for la, de in zip(latitude, density)
        )
    pd.DataFrame(curve_rows).to_csv(OUT / "latitude_marginal_curves.csv", index=False)

    plot_heatmap_comparison(grids, OUT / "mh370_no_precompensation_heatmap_comparison.png")
    plot_latitude_marginals(curves, OUT / "mh370_no_precompensation_latitude_marginals.png")

    manifest = {
        "analysis": "00:11 fixed beta=1 no-power-precompensation conditional reconstruction",
        "beta_definition": "beta=0 complete AES gain precompensation; beta=1 no precompensation",
        "reference_beta_posterior_mean": BETA_REFERENCE,
        "primary_RF_contrast_scale": CASES["Beta=1, linear RF-contrast reconstruction"],
        "quadratic_sensitivity_RF_contrast_scale": CASES["Beta=1, quadratic RF-contrast sensitivity"],
        "empirical_RF_surface": "digitized ratio of matched BTO+BFO+power and BTO+BFO-only latitude PDFs from the first integrated run",
        "checkpoint_limitation": "The refined-v3 particle checkpoint is unavailable; exact beta/location/gain/heading correlations cannot be restored. Primary and quadratic contrast scalings bracket the missing conditional decomposition.",
        "pleiades_conditioning": "BRAN2015/2016 expanded FL400-glide origin likelihood evaluated at impact and backward-smoothed through marginalized controlled terminal flight",
        "n_airborne_particles": N_AIR,
        "n_terminal_continuations": N_TERMINAL,
        "seed": SEED,
        "uses_0019_bto_bfo_power_or_logon_likelihood": False,
        "interpretation": "The Pleiades-conditioned result is conditional on at least some class-4/5 image objects being MH370 debris; it is not a probability that the objects are debris.",
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(pd.DataFrame(summary_rows).to_string(index=False))
    print(pd.DataFrame(component_summary).to_string(index=False))


if __name__ == "__main__":
    main()
