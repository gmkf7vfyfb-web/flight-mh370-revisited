#!/usr/bin/env python3
"""Refined-noise MH370 airborne posterior at the 00:11 UTC sixth arc.

The random BFO measurement standard deviation is estimated from successive
differences within the 18:39 and 23:14 call clusters.  Differencing removes a
locally constant AES/satellite/model bias, so the estimate is not inflated by
the slow/intermittent bias process.  The estimate is then used in the explicit
00:11 vertical-rate likelihood that augments the reconstructed refined
BTO+BFO+received-power posterior and its controlled-flight performance model.

Two airborne posteriors are emitted:
  1. satellite/RF/performance evidence only, through 00:11; and
  2. the same 00:11 state after debris-drift evidence is smoothed backward
     through a marginalized terminal-flight kernel.

The debris likelihood is evaluated at a sampled impact state, never directly
at the sixth-arc airborne position.  No 00:19 observation is used.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-mh370-refined-bfo")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.ndimage import gaussian_filter
from scipy.stats import chi2

from run_integrated_0011_stage1 import (
    Case,
    bto_altitude_shift,
    davey_drift_likelihood,
    density_grid,
    family_loglikelihood,
    grid_mode,
    hpd_levels,
    meta_drift_likelihood,
    normalize_model_likelihood,
    reconstruct_airborne_proposal,
    sample_control_families,
    summarize,
    systematic_resample,
    terminal_kernel,
)


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "mh370_refined_bfo_0011_airborne"
OUT.mkdir(parents=True, exist_ok=True)

NOISE_DATA = (
    ROOT
    / "downloads_refined_bfo"
    / "MH370"
    / "mh370_bfo_short_interval_validation.csv"
)

SEED = 3700110
N_AIR = 1_200_000
N_TERMINAL = 1_800_000
EXTENT = (84.0, 98.0, -40.0, -28.0)
FAMILY_NAMES = [
    "High-altitude/near-level",
    "Earlier descent completed/low-level",
    "Active controlled descent",
]


def estimate_random_bfo_sigma(path: Path):
    """Pooled within-cluster successive-difference estimate and audit rows."""
    frame = pd.read_csv(path)
    centered_differences = []
    cluster_rows = []
    raw_numerator = 0.0
    raw_count = 0
    for cluster, group in frame.groupby("cluster", sort=False):
        values = group.sort_values("sample_number")["BFO_Hz"].to_numpy(float)
        differences = np.diff(values)
        centered = differences - differences.mean()
        centered_differences.append(centered)
        raw_numerator += float(np.sum(differences * differences))
        raw_count += len(differences)
        cluster_rows.append(
            {
                "basis": cluster,
                "N_BFO_samples": len(values),
                "N_successive_differences": len(differences),
                "raw_sample_SD_Hz": float(np.std(values, ddof=1)),
                "mean_successive_difference_Hz": float(differences.mean()),
                "successive_difference_SD_Hz": float(np.std(differences, ddof=1)),
                "sigma_random_Hz": float(np.std(differences, ddof=1) / math.sqrt(2.0)),
            }
        )

    # Two cluster-specific difference means are fitted, hence Ndiff-2 dof.
    pooled = np.concatenate(centered_differences)
    dof = len(pooled) - len(centered_differences)
    sigma2 = float(np.sum(pooled * pooled) / (2.0 * dof))
    sigma = math.sqrt(sigma2)
    ci_low = math.sqrt(dof * sigma2 / chi2.ppf(0.975, dof))
    ci_high = math.sqrt(dof * sigma2 / chi2.ppf(0.025, dof))
    raw_rms_sigma = math.sqrt(raw_numerator / (2.0 * raw_count))

    tests = []
    for null_sigma in [1.0, 1.5, 3.4, 7.0, 12.0]:
        q = dof * sigma2 / (null_sigma * null_sigma)
        lower = float(chi2.cdf(q, dof))
        upper = float(chi2.sf(q, dof))
        tests.append(
            {
                "null_sigma_Hz": null_sigma,
                "chi_square_statistic": q,
                "degrees_of_freedom": dof,
                "two_sided_p_value": min(1.0, 2.0 * min(lower, upper)),
                "note": "Gaussian independent-successive-difference reference test",
            }
        )

    cluster_rows.append(
        {
            "basis": "Pooled, cluster difference means removed",
            "N_BFO_samples": len(frame),
            "N_successive_differences": len(pooled),
            "raw_sample_SD_Hz": float(
                np.sqrt(
                    sum(
                        (len(g) - 1) * np.var(g["BFO_Hz"], ddof=1)
                        for _, g in frame.groupby("cluster", sort=False)
                    )
                    / (len(frame) - frame["cluster"].nunique())
                )
            ),
            "mean_successive_difference_Hz": float("nan"),
            "successive_difference_SD_Hz": sigma * math.sqrt(2.0),
            "sigma_random_Hz": sigma,
        }
    )
    return {
        "sigma_Hz": sigma,
        "sigma_95_low_Hz": ci_low,
        "sigma_95_high_Hz": ci_high,
        "dof": dof,
        "raw_successive_difference_RMS_sigma_Hz": raw_rms_sigma,
        "cluster_rows": cluster_rows,
        "test_rows": tests,
    }


def normalized_logweights(logw):
    shifted = logw - np.max(logw)
    weights = np.exp(shifted)
    return weights / weights.sum()


def family_posterior_rows(family, altitude, vspd, weights, state):
    rows = []
    total = float(np.sum(weights))
    for code, name in enumerate(FAMILY_NAMES):
        mask = family == code
        family_weight = weights[mask]
        rows.append(
            {
                "airborne_posterior": state,
                "control_family": name,
                "prior_probability": 1.0 / 3.0,
                "posterior_probability": float(family_weight.sum() / total),
                "posterior_mean_altitude_ft": float(
                    np.average(altitude[mask], weights=family_weight)
                ),
                "posterior_mean_abs_vertical_rate_fpm": float(
                    np.average(np.abs(vspd[mask]), weights=family_weight)
                ),
            }
        )
    return rows


def plot_heatmap(grid, output, title, subtitle, overlay_grid=None):
    xc, yc, density = grid
    fig, ax = plt.subplots(figsize=(9.2, 7.4))
    relative = density / density.max()
    im = ax.imshow(
        relative,
        origin="lower",
        extent=(xc[0], xc[-1], yc[0], yc[-1]),
        aspect="auto",
        cmap="viridis",
        vmin=0,
        vmax=1,
    )
    levels = sorted(hpd_levels(density, (0.90, 0.50)))
    ax.contour(
        xc,
        yc,
        density,
        levels=levels,
        colors=["white", "#ffcc33"],
        linewidths=[1.4, 2.0],
    )
    if overlay_grid is not None:
        ox, oy, od = overlay_grid
        level50 = hpd_levels(od, (0.50,))[0]
        ax.contour(
            ox,
            oy,
            od,
            levels=[level50],
            colors=["#53d8fb"],
            linestyles=["--"],
            linewidths=[1.8],
        )
    mode_lat, mode_lon = grid_mode(xc, yc, density)
    ax.plot(
        mode_lon,
        mode_lat,
        marker="*",
        markersize=14,
        markeredgecolor="black",
        markerfacecolor="white",
        label="2-D posterior mode",
    )
    ax.plot([], [], color="#ffcc33", linewidth=2.0, label="50% HPD")
    ax.plot([], [], color="white", linewidth=1.4, label="90% HPD")
    if overlay_grid is not None:
        ax.plot(
            [],
            [],
            color="#53d8fb",
            linestyle="--",
            linewidth=1.8,
            label="No-drift 50% HPD",
        )
    ax.set_title(title, fontsize=16, pad=13)
    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°; south negative)")
    ax.set_xlim(EXTENT[0], EXTENT[1])
    ax.set_ylim(EXTENT[2], EXTENT[3])
    ax.grid(color="white", alpha=0.16, linewidth=0.6)
    ax.legend(loc="upper left", framealpha=0.84, fontsize=9)
    colorbar = fig.colorbar(im, ax=ax, shrink=0.84, pad=0.025)
    colorbar.set_label("Relative posterior density")
    fig.text(0.5, 0.035, subtitle, ha="center", fontsize=10)
    fig.subplots_adjust(left=0.095, right=0.88, bottom=0.15, top=0.86)
    fig.savefig(output, dpi=220, bbox_inches="tight")
    plt.close(fig)


def plot_comparison(no_drift_grid, drift_grid, output, sigma):
    fig, axes = plt.subplots(1, 2, figsize=(14.6, 6.5))
    entries = [
        (no_drift_grid, "Without ocean-drift evidence", None),
        (drift_grid, "With drift evidence\n(backward-smoothed)", no_drift_grid),
    ]
    im = None
    for ax, (grid, title, overlay) in zip(axes, entries):
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
        levels = sorted(hpd_levels(density, (0.90, 0.50)))
        ax.contour(
            xc,
            yc,
            density,
            levels=levels,
            colors=["white", "#ffcc33"],
            linewidths=[1.2, 1.8],
        )
        if overlay is not None:
            ox, oy, od = overlay
            ax.contour(
                ox,
                oy,
                od,
                levels=[hpd_levels(od, (0.50,))[0]],
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
    fig.subplots_adjust(left=0.065, right=0.90, bottom=0.14, top=0.83, wspace=0.15)
    colorbar_axis = fig.add_axes([0.92, 0.20, 0.017, 0.57])
    colorbar = fig.colorbar(im, cax=colorbar_axis)
    colorbar.set_label("Relative posterior density")
    fig.suptitle(
        f"MH370 airborne position at the 00:11 UTC sixth arc — random BFO σ = {sigma:.2f} Hz",
        fontsize=17,
        y=0.975,
    )
    fig.text(
        0.5,
        0.035,
        "Yellow/white: 50%/90% HPD; cyan: no-drift 50% HPD. No 00:19 observations used.",
        ha="center",
        fontsize=10,
    )
    fig.savefig(output, dpi=210, bbox_inches="tight")
    plt.close(fig)


def main():
    noise = estimate_random_bfo_sigma(NOISE_DATA)
    sigma = noise["sigma_Hz"]
    case = Case(
        name="Refined random BFO noise",
        family_prior=(1 / 3, 1 / 3, 1 / 3),
        bfo_sigma_hz=sigma,
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
    logw, diagnostics = family_loglikelihood(
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
    no_drift_weights = normalized_logweights(logw)
    no_drift_grid = density_grid(
        air_lat, air_lon, no_drift_weights, extent=EXTENT, nx=600, ny=520, sigma=2.0
    )

    # Draw terminal continuations from the 00:11 posterior.  The displayed
    # coordinate remains the ancestor at 00:11; only the drift likelihood at
    # the corresponding impact state is transmitted back to that ancestor.
    terminal_rng = np.random.default_rng(SEED + 711)
    ancestor = systematic_resample(terminal_rng, no_drift_weights, N_TERMINAL)
    scenario = terminal_rng.integers(0, 3, N_TERMINAL)
    impact_lat, impact_lon, terminal_diag = terminal_kernel(
        terminal_rng,
        air_lat[ancestor],
        air_lon[ancestor],
        heading[ancestor],
        altitude[ancestor],
        vspd[ancestor],
        scenario,
        case.forward_glide_probability,
    )
    davey = normalize_model_likelihood(davey_drift_likelihood(impact_lat, impact_lon))
    meta = normalize_model_likelihood(meta_drift_likelihood(impact_lat, impact_lon))
    backward_weights = 0.5 * davey + 0.5 * meta
    backward_weights /= backward_weights.sum()
    drift_air_lat = air_lat[ancestor]
    drift_air_lon = air_lon[ancestor]
    drift_grid = density_grid(
        drift_air_lat,
        drift_air_lon,
        backward_weights,
        extent=EXTENT,
        nx=600,
        ny=520,
        sigma=2.0,
    )

    summary_rows = [
        summarize(
            "00:11 airborne — without ocean drift",
            air_lat,
            air_lon,
            no_drift_weights,
            no_drift_grid,
        ),
        summarize(
            "00:11 airborne — with drift backward-smoothed",
            drift_air_lat,
            drift_air_lon,
            backward_weights,
            drift_grid,
        ),
    ]
    for row in summary_rows:
        row["random_BFO_sigma_Hz"] = sigma
        row["uses_0019_observation"] = False

    family_rows = family_posterior_rows(
        family, altitude, vspd, no_drift_weights, "Without ocean drift"
    )
    family_rows.extend(
        family_posterior_rows(
            family[ancestor],
            altitude[ancestor],
            vspd[ancestor],
            backward_weights,
            "With drift backward-smoothed",
        )
    )

    # Propagate the statistical uncertainty in the random-noise estimate through
    # the 00:11 likelihood.  These rows do not add a separate bias variance.
    sigma_sensitivity_rows = []
    for label, sigma_value in [
        ("95% lower random-sigma bound", noise["sigma_95_low_Hz"]),
        ("point estimate", sigma),
        ("95% upper random-sigma bound", noise["sigma_95_high_Hz"]),
        ("previous fast-noise setting", 1.5),
    ]:
        sensitivity_case = Case(
            name=label,
            family_prior=(1 / 3, 1 / 3, 1 / 3),
            bfo_sigma_hz=sigma_value,
            bfo_vertical_hz_per_fpm=0.009,
            drift_davey_weight=0.5,
            forward_glide_probability=0.70,
        )
        sensitivity_logw, _ = family_loglikelihood(
            air_lat,
            air_lon,
            mach,
            family,
            altitude,
            vspd,
            slow_minutes,
            slow_speed,
            sensitivity_case,
        )
        sensitivity_w = normalized_logweights(sensitivity_logw)
        sensitivity_summary = summarize(
            label,
            air_lat,
            air_lon,
            sensitivity_w,
        )
        sigma_sensitivity_rows.append(
            {
                "case": label,
                "random_BFO_sigma_Hz": sigma_value,
                "median_lat_deg": sensitivity_summary["median_lat_deg"],
                "lat_95_low": sensitivity_summary["lat_95_low"],
                "lat_95_high": sensitivity_summary["lat_95_high"],
                "prob_active_controlled_descent": float(sensitivity_w[family == 2].sum()),
                "prob_earlier_descent_completed_low_level": float(
                    sensitivity_w[family == 1].sum()
                ),
            }
        )

    scenario_rows = []
    scenario_names = [
        "Controlled descent/ditch (power if available)",
        "Fuel exhaustion + controlled glide",
        "Fuel exhaustion + short uncontrolled descent",
    ]
    for code, name in enumerate(scenario_names):
        mask = scenario == code
        scenario_rows.append(
            {
                "terminal_scenario": name,
                "prior_probability": 1 / 3,
                "posterior_probability_given_drift": float(backward_weights[mask].sum()),
                "median_terminal_distance_nm": float(
                    np.median(terminal_diag["terminal_distance_nm"][mask])
                ),
                "q95_terminal_distance_nm": float(
                    np.quantile(terminal_diag["terminal_distance_nm"][mask], 0.95)
                ),
            }
        )

    pd.DataFrame(noise["cluster_rows"]).to_csv(
        OUT / "bfo_random_noise_estimate.csv", index=False
    )
    pd.DataFrame(noise["test_rows"]).to_csv(
        OUT / "bfo_sigma_reference_tests.csv", index=False
    )
    pd.DataFrame(summary_rows).to_csv(OUT / "airborne_0011_summary.csv", index=False)
    pd.DataFrame(family_rows).to_csv(OUT / "control_family_posteriors.csv", index=False)
    pd.DataFrame(scenario_rows).to_csv(OUT / "terminal_scenario_drift_weights.csv", index=False)
    pd.DataFrame(sigma_sensitivity_rows).to_csv(
        OUT / "random_bfo_sigma_sensitivity.csv", index=False
    )

    sample_rng = np.random.default_rng(SEED + 991)
    no_idx = systematic_resample(sample_rng, no_drift_weights, 60_000)
    drift_idx = systematic_resample(sample_rng, backward_weights, 60_000)
    no_sample = pd.DataFrame(
        {
            "posterior": "without_ocean_drift",
            "lat_deg": air_lat[no_idx],
            "lon_deg_E": air_lon[no_idx],
            "altitude_ft": altitude[no_idx],
            "vertical_rate_fpm": vspd[no_idx],
            "control_family_code": family[no_idx],
        }
    )
    drift_sample = pd.DataFrame(
        {
            "posterior": "with_drift_backward_smoothed",
            "lat_deg": drift_air_lat[drift_idx],
            "lon_deg_E": drift_air_lon[drift_idx],
            "altitude_ft": altitude[ancestor][drift_idx],
            "vertical_rate_fpm": vspd[ancestor][drift_idx],
            "control_family_code": family[ancestor][drift_idx],
        }
    )
    pd.concat([no_sample, drift_sample], ignore_index=True).to_csv(
        OUT / "airborne_0011_posterior_samples.csv", index=False
    )

    plot_heatmap(
        no_drift_grid,
        OUT / "mh370_0011_airborne_refined_bfo_no_drift.png",
        f"MH370 airborne position at 00:11 UTC\nrefined random BFO σ = {sigma:.2f} Hz — no drift evidence",
        "BTO + BFO + received power + controlled-flight performance; 00:19 excluded.",
    )
    plot_heatmap(
        drift_grid,
        OUT / "mh370_0011_airborne_refined_bfo_with_drift.png",
        f"MH370 airborne position at 00:11 UTC\nrefined random BFO σ = {sigma:.2f} Hz — drift-smoothed",
        "Debris likelihood evaluated at impact and smoothed backward; no 00:19 observations used.",
        overlay_grid=no_drift_grid,
    )
    plot_comparison(
        no_drift_grid,
        drift_grid,
        OUT / "mh370_0011_airborne_refined_bfo_comparison.png",
        sigma,
    )

    manifest = {
        "random_BFO_sigma_Hz": sigma,
        "random_BFO_sigma_95_interval_Hz": [
            noise["sigma_95_low_Hz"],
            noise["sigma_95_high_Hz"],
        ],
        "sigma_estimator": "pooled within-cluster successive differences, cluster difference means removed",
        "bias_handling": "slow/intermittent bias excluded from the random-noise variance estimate; no bias variance added in quadrature in the 00:11 vertical-rate likelihood",
        "n_airborne_augmentations": N_AIR,
        "n_terminal_continuations": N_TERMINAL,
        "seed": SEED,
        "observation_cutoff": "2014-03-08T00:11:00Z",
        "uses_0019_observations": False,
        "drift_conditioning": "impact-state likelihood smoothed backward to the 00:11 ancestor through a marginalized terminal kernel",
        "drift_model_average": "50% normalized Davey smooth digitization + 50% normalized 12-study meta-analysis latitude likelihood",
        "proposal_limitation": "refined v3 particle checkpoint unavailable; the reported multimodal satellite/RF posterior is reconstructed from its published summary, so exact location/Mach/heading/gain/BFO-bias correlations are unavailable",
        "source_data": str(NOISE_DATA.relative_to(ROOT)),
    }
    (OUT / "run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print("Random BFO sigma estimate")
    print(json.dumps(manifest, indent=2))
    print("\nAirborne summaries")
    print(pd.DataFrame(summary_rows).to_string(index=False))
    print("\nControl-family posteriors")
    print(pd.DataFrame(family_rows).to_string(index=False))
    print("\nReference sigma tests")
    print(pd.DataFrame(noise["test_rows"]).to_string(index=False))
    print("\nRandom-sigma sensitivity")
    print(pd.DataFrame(sigma_sensitivity_rows).to_string(index=False))


if __name__ == "__main__":
    main()
