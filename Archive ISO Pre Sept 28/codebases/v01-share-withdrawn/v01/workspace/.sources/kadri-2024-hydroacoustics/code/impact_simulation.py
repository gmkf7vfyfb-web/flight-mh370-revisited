#!/usr/bin/env python3
"""Family-conditional impact-to-SOFAR Monte Carlo sensitivity.

This is a reduced-order energy and pressure-proxy experiment.  Impact families
and coupling priors remain explicit alternatives; the output is not an MH370
impact posterior or a station detection model.
"""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
CONFIG_PATH = DATA / "impact-simulation-config.json"
TNT_SPECIFIC_ENERGY_J_KG = 4.184e6
PDF_METADATA = {"CreationDate": None, "ModDate": None}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sample_vertical_speed(rng: np.random.Generator, family: dict, count: int) -> np.ndarray:
    values = family["vertical_speed_m_s"]
    distribution = family["vertical_speed_distribution"]
    if distribution == "fixed":
        return np.full(count, values[0], dtype=float)
    if distribution == "triangular":
        return rng.triangular(values[0], values[1], values[2], size=count)
    if distribution == "loguniform":
        return 10.0 ** rng.uniform(np.log10(values[0]), np.log10(values[1]), size=count)
    raise ValueError(f"unknown vertical-speed distribution: {distribution}")


def sample_coupling(rng: np.random.Generator, prior: dict, count: int) -> np.ndarray:
    distribution = prior["distribution"]
    low = np.log10(prior["minimum"])
    high = np.log10(prior["maximum"])
    if distribution == "loguniform":
        return 10.0 ** rng.uniform(low, high, size=count)
    if distribution == "truncated_normal_log10":
        result = np.empty(count, dtype=float)
        filled = 0
        while filled < count:
            draw = rng.normal(prior["log10_mean"], prior["log10_sd"], size=(count - filled) * 2)
            accepted = draw[(draw >= low) & (draw <= high)]
            take = min(accepted.size, count - filled)
            result[filled : filled + take] = 10.0 ** accepted[:take]
            filled += take
        return result
    raise ValueError(f"unknown coupling distribution: {distribution}")


def pressure_from_coupled_energy(coupled_energy_j: np.ndarray, range_km: float) -> np.ndarray:
    effective_yield_kg_tnt = coupled_energy_j / TNT_SPECIFIC_ENERGY_J_KG
    scaled_range_m = range_km * 1000.0 / np.cbrt(effective_yield_kg_tnt)
    return 52.4e6 * scaled_range_m ** -1.13


def quantile_columns(values: np.ndarray, quantiles: list[float], prefix: str) -> dict:
    return {
        f"{prefix}_q{quantile:g}": f"{value:.9g}"
        for quantile, value in zip(quantiles, np.quantile(values, quantiles))
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def style() -> tuple[dict[str, str], dict[str, str]]:
    colours = {
        "controlled_ditching_class": "#4477AA",
        "us1549_observed_contact": "#228833",
        "partially_arrested_bridge": "#CCBB44",
        "holland_unarrested_bound": "#CC6677",
    }
    return colours, {
        "controlled_ditching_class": "Controlled ditching class",
        "us1549_observed_contact": "Flight 1549 contact rate",
        "partially_arrested_bridge": "Partially arrested bridge",
        "holland_unarrested_bound": "Unarrested high-rate descent",
    }


def make_density_plot(samples: dict, configuration: dict) -> None:
    colours, labels = style()
    fig, axes = plt.subplots(1, 3, figsize=(17.0, 5.7))
    bins_energy = np.linspace(3.5, 9.5, 150)
    bins_transfer = np.linspace(-5.0, 8.5, 180)
    bins_pressure = np.linspace(-6.0, 1.5, 170)
    for family_id in configuration["impact_families"]:
        values = samples[(family_id, "f35_centred")]
        axes[0].hist(
            np.log10(values["normal_energy_j"]), bins=bins_energy, density=True,
            histtype="step", linewidth=2.0, color=colours[family_id], label=labels[family_id],
        )
        axes[1].hist(
            np.log10(values["coupled_energy_j"]), bins=bins_transfer, density=True,
            histtype="step", linewidth=2.0, color=colours[family_id],
        )
        axes[2].hist(
            np.log10(values["pressure_H01W_pa"]), bins=bins_pressure, density=True,
            histtype="step", linewidth=2.0, color=colours[family_id],
        )
    axes[0].set_xlabel(r"$\log_{10}$ normal kinetic energy (J)")
    axes[1].set_xlabel(r"$\log_{10}$ effective energy transferred to SOFAR (J)")
    axes[2].set_xlabel(r"$\log_{10}$ H01W peak-pressure proxy (Pa)")
    axes[0].set_ylabel(r"Density per $\log_{10}$ unit")
    for axis in axes:
        axis.grid(alpha=0.18)
    axes[0].legend(frameon=False, fontsize=8.4)
    fig.suptitle(
        "Impact-family transfer sensitivity under the F-35-centred coupling prior\n"
        "Family-conditional Monte Carlo; not an empirical event posterior",
        fontsize=14.2,
    )
    fig.tight_layout(rect=[0.0, 0.01, 1.0, 0.91])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"impact-family-transfer-density.{suffix}", dpi=280 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
    plt.close(fig)


def make_station_pressure_plot(rows: list[dict], configuration: dict) -> None:
    colours, labels = style()
    selected = {
        row["impact_family"]: row for row in rows if row["coupling_prior"] == "f35_centred"
    }
    fig, axes = plt.subplots(1, 2, figsize=(14.5, 5.8), sharey=True)
    family_ids = list(configuration["impact_families"])
    y = np.arange(len(family_ids))
    for axis, (station_id, station) in zip(axes, configuration["stations"].items()):
        medians = np.asarray([
            float(selected[family_id][f"pressure_{station_id}_pa_q0.5"])
            for family_id in family_ids
        ])
        lower = np.asarray([
            float(selected[family_id][f"pressure_{station_id}_pa_q0.05"])
            for family_id in family_ids
        ])
        upper = np.asarray([
            float(selected[family_id][f"pressure_{station_id}_pa_q0.95"])
            for family_id in family_ids
        ])
        for index, family_id in enumerate(family_ids):
            axis.errorbar(
                medians[index], y[index],
                xerr=[[medians[index] - lower[index]], [upper[index] - medians[index]]],
                fmt="o", color=colours[family_id], ecolor=colours[family_id],
                elinewidth=5.5, alpha=0.92, capsize=0, markersize=6.5,
            )
            axis.annotate(
                f"{medians[index]:.3g} Pa", (medians[index], y[index]),
                xytext=(5, 5), textcoords="offset points", fontsize=8.0,
            )
        axis.set_xscale("log")
        axis.set_yticks(y, [labels[family_id] for family_id in family_ids])
        axis.set_xlabel("Peak-pressure proxy (Pa); median and 5–95% interval")
        axis.set_title(f"{station_id} — {station['name']}\nrepresentative range {station['range_km']:,.0f} km")
        axis.grid(axis="x", which="both", alpha=0.20)
    axes[0].invert_yaxis()
    fig.suptitle(
        "Conditional received-pressure scale by impact family\n"
        "F-35-centred effective-coupling sensitivity prior; intervals are not detection probabilities",
        fontsize=14.0,
    )
    fig.tight_layout(rect=[0.0, 0.01, 1.0, 0.90])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"impact-pressure-by-station.{suffix}", dpi=280 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
    plt.close(fig)


def make_coupling_control(samples: dict, configuration: dict) -> None:
    colours, labels = style()
    bins = np.linspace(-5.0, 8.5, 180)
    fig, axes = plt.subplots(1, 2, figsize=(13.8, 5.6), sharey=True)
    for axis, prior_id in zip(axes, configuration["coupling_priors"]):
        for family_id in configuration["impact_families"]:
            axis.hist(
                np.log10(samples[(family_id, prior_id)]["coupled_energy_j"]),
                bins=bins, density=True, histtype="step", linewidth=1.9,
                color=colours[family_id], label=labels[family_id],
            )
        axis.set_title(configuration["coupling_priors"][prior_id]["label"])
        axis.set_xlabel(r"$\log_{10}$ effective SOFAR energy (J)")
        axis.grid(alpha=0.18)
    axes[0].set_ylabel(r"Density per $\log_{10}$ unit")
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="lower center", ncol=4, frameon=False, fontsize=8.3)
    fig.suptitle("Coupling-prior control: family ordering persists; absolute scale does not", fontsize=14.0)
    fig.tight_layout(rect=[0.0, 0.12, 1.0, 0.92])
    for suffix in ("png", "pdf"):
        fig.savefig(OUTPUT / f"impact-coupling-prior-control.{suffix}", dpi=280 if suffix == "png" else None, metadata=PDF_METADATA if suffix == "pdf" else None)
    plt.close(fig)


def make_pressure_prior_comparison(rows: list[dict], configuration: dict) -> None:
    """Show how the station-pressure scale changes with coupling-prior choice."""
    _colours, labels = style()
    selected = {
        (row["impact_family"], row["coupling_prior"]): row
        for row in rows
    }
    prior_style = {
        "f35_centred": ("#6B4C9A", "F-35-centred sensitivity prior"),
        "loguniform_control": ("#D55E00", "Log-uniform coupling control"),
    }
    family_ids = list(configuration["impact_families"])
    y = np.arange(len(family_ids), dtype=float)
    fig, axes = plt.subplots(1, 2, figsize=(15.2, 6.1), sharey=True)
    for axis, (station_id, station) in zip(axes, configuration["stations"].items()):
        for prior_index, (prior_id, (colour, label)) in enumerate(prior_style.items()):
            offset = -0.11 if prior_index == 0 else 0.11
            medians = np.asarray([
                float(selected[(family_id, prior_id)][f"pressure_{station_id}_pa_q0.5"])
                for family_id in family_ids
            ])
            lower = np.asarray([
                float(selected[(family_id, prior_id)][f"pressure_{station_id}_pa_q0.05"])
                for family_id in family_ids
            ])
            upper = np.asarray([
                float(selected[(family_id, prior_id)][f"pressure_{station_id}_pa_q0.95"])
                for family_id in family_ids
            ])
            axis.errorbar(
                medians,
                y + offset,
                xerr=[medians - lower, upper - medians],
                fmt="o",
                color=colour,
                ecolor=colour,
                elinewidth=3.8,
                capsize=0,
                markersize=5.2,
                alpha=0.92,
                label=label,
            )
        axis.set_xscale("log")
        axis.set_yticks(y, [labels[family_id] for family_id in family_ids])
        axis.set_xlabel("Peak-pressure proxy (Pa); median and 5–95% interval")
        axis.set_title(
            f"{station_id} — {station['name']}\n"
            f"representative range {station['range_km']:,.0f} km"
        )
        axis.grid(axis="x", which="both", alpha=0.20)
    axes[0].invert_yaxis()
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="lower center", ncol=2, frameon=False)
    fig.suptitle(
        "Station-pressure sensitivity to the coupling prior\n"
        "The impact-family draws are identical; only the surface-to-SOFAR coupling distribution changes",
        fontsize=14.0,
    )
    fig.tight_layout(rect=[0.0, 0.10, 1.0, 0.90])
    for suffix in ("png", "pdf"):
        fig.savefig(
            OUTPUT / f"impact-pressure-prior-comparison.{suffix}",
            dpi=280 if suffix == "png" else None,
            metadata=PDF_METADATA if suffix == "pdf" else None,
        )
    plt.close(fig)


def main() -> None:
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    count = int(configuration["sample_count_per_family_and_coupling_prior"])
    quantiles = configuration["quantiles"]
    mass_kg = float(configuration["aircraft_mass_kg"])
    rng = np.random.default_rng(configuration["random_seed"])
    samples: dict[tuple[str, str], dict[str, np.ndarray]] = {}
    rows: list[dict] = []

    for family_id, family in configuration["impact_families"].items():
        vertical_speed = sample_vertical_speed(rng, family, count)
        normal_energy = 0.5 * mass_kg * vertical_speed**2
        for prior_id, prior in configuration["coupling_priors"].items():
            coupling = sample_coupling(rng, prior, count)
            coupled_energy = normal_energy * coupling
            pressure = {
                station_id: pressure_from_coupled_energy(coupled_energy, station["range_km"])
                for station_id, station in configuration["stations"].items()
            }
            samples[(family_id, prior_id)] = {
                "normal_energy_j": normal_energy,
                "coupled_energy_j": coupled_energy,
                **{f"pressure_{station_id}_pa": value for station_id, value in pressure.items()},
            }
            row = {
                "impact_family": family_id,
                "coupling_prior": prior_id,
                "sample_count": count,
                "family_status": family["status"],
                "coupling_status": prior["status"],
                **quantile_columns(vertical_speed, quantiles, "vertical_speed_m_s"),
                **quantile_columns(normal_energy, quantiles, "normal_energy_j"),
                **quantile_columns(coupling, quantiles, "coupling"),
                **quantile_columns(coupled_energy, quantiles, "transferred_energy_j"),
            }
            for station_id, values in pressure.items():
                row.update(quantile_columns(values, quantiles, f"pressure_{station_id}_pa"))
            rows.append(row)

    quantile_path = OUTPUT / "impact-family-quantiles.csv"
    write_csv(quantile_path, rows)
    make_density_plot(samples, configuration)
    make_station_pressure_plot(rows, configuration)
    make_coupling_control(samples, configuration)
    make_pressure_prior_comparison(rows, configuration)

    f35_model_pressure = float(pressure_from_coupled_energy(np.asarray([900e6 * 1e-4]), 3300.0)[0])
    summary = {
        "status": "FAMILY_CONDITIONAL_REDUCED_ORDER_SENSITIVITY_NOT_IMPACT_OR_DETECTION_POSTERIOR",
        "sample_count_per_family_and_coupling_prior": count,
        "random_seed": configuration["random_seed"],
        "aircraft_mass_kg": mass_kg,
        "aircraft_mass_basis": configuration["aircraft_mass_basis"],
        "normal_energy_only": True,
        "empirical_relation_check": {
            "f35_reported_pressure_pa": 0.7,
            "model_pressure_pa": f35_model_pressure,
            "model_to_reported_ratio": f35_model_pressure / 0.7,
        },
        "interpretive_limits": [
            "coupling distributions are sensitivity priors, not measured MH370 coupling probabilities",
            "only the normal kinetic-energy component enters the explosion-equivalent pressure relation",
            "horizontal hydrodynamics, breakup, cavitation, ventilation, sea state and fuel are omitted",
            "Flight 1549 is a cross-aircraft contact-rate analogue; all energies use the declared 777 mass",
            "the partially arrested family is a logarithmic bridge, not a physically inferred probability density",
            "no weights across impact families are supplied and pressure is not converted to detection probability",
        ],
    }
    summary_path = OUTPUT / "impact-simulation-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    output_paths = [
        quantile_path,
        summary_path,
        *[OUTPUT / f"{stem}.{suffix}" for stem in (
            "impact-family-transfer-density", "impact-pressure-by-station", "impact-coupling-prior-control",
            "impact-pressure-prior-comparison",
        ) for suffix in ("png", "pdf")],
    ]
    manifest = {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {str(CONFIG_PATH.relative_to(HERE)): sha256(CONFIG_PATH)},
        "code": {str(Path(__file__).relative_to(HERE)): sha256(Path(__file__))},
        "outputs": {path.name: sha256(path) for path in output_paths},
    }
    (OUTPUT / "impact-simulation-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
