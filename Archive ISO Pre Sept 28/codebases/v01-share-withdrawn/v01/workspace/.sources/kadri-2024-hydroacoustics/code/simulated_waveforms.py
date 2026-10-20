#!/usr/bin/env python3
"""Render illustrative pressure traces and spectrograms from current impact draws.

The pulse shape and coloured noise are display controls. They are not a
hydrodynamic Boeing 777 source waveform, a CTBTO observation, or a detector
model. Only the peak-pressure scale comes from the reduced-order impact
sensitivity experiment.
"""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, sosfiltfilt, spectrogram


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
CONFIG_PATH = DATA / "impact-simulation-config.json"
QUANTILES_PATH = OUTPUT / "impact-family-quantiles.csv"
PDF_METADATA = {"CreationDate": None, "ModDate": None}


def parse_utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def make_pulse(time_s: np.ndarray) -> np.ndarray:
    """Generic two-part 5–15 Hz pulse retained from the earlier illustration."""
    pulse = np.sin(2.0 * np.pi * 8.0 * time_s) * np.exp(-0.5 * (time_s / 1.25) ** 2)
    pulse += (
        0.34
        * np.sin(2.0 * np.pi * 6.2 * (time_s - 2.0))
        * np.exp(-0.5 * ((time_s - 2.0) / 2.8) ** 2)
    )
    return pulse / np.max(np.abs(pulse))


def load_pressure_rows(configuration: dict) -> list[dict]:
    with QUANTILES_PATH.open(newline="", encoding="utf-8") as handle:
        rows = [
            row
            for row in csv.DictReader(handle)
            if row["coupling_prior"] == "f35_centred"
        ]
    by_family = {row["impact_family"]: row for row in rows}
    return [by_family[family_id] for family_id in configuration["impact_families"]]


def generate_panels(configuration: dict, rows: list[dict]) -> tuple[dict, dict]:
    sample_rate_hz = 50.0
    relative_s = np.arange(-45.0, 45.0, 1.0 / sample_rate_hz)
    pulse = make_pulse(relative_s)
    bandpass = butter(4, [5.0, 15.0], btype="bandpass", fs=sample_rate_hz, output="sos")
    rng = np.random.default_rng(int(configuration["random_seed"]) + 1)
    waveforms: dict[tuple[str, str], dict] = {}
    spectra: dict[tuple[str, str], dict] = {}
    for station_id, station in configuration["stations"].items():
        raw = rng.normal(size=relative_s.size)
        noise = sosfiltfilt(bandpass, raw)
        noise *= 0.3 / np.sqrt(np.mean(noise**2))
        centre = parse_utc(station["representative_high_rate_reception_utc"])
        utc = np.asarray([centre + timedelta(seconds=float(value)) for value in relative_s])
        for row in rows:
            family_id = row["impact_family"]
            amplitude = float(row[f"pressure_{station_id}_pa_q0.5"])
            signal = amplitude * pulse
            combined = noise + signal
            frequency_hz, spec_time_s, power = spectrogram(
                combined,
                fs=sample_rate_hz,
                window="hann",
                nperseg=256,
                noverlap=224,
                detrend=False,
                scaling="density",
                mode="psd",
            )
            waveforms[(station_id, family_id)] = {
                "utc": utc,
                "relative_s": relative_s,
                "combined": combined,
                "signal": signal,
                "centre": centre,
                "amplitude": amplitude,
            }
            spectra[(station_id, family_id)] = {
                "frequency_hz": frequency_hz,
                "relative_s": spec_time_s - 45.0,
                "db_pa2_hz": 10.0 * np.log10(np.maximum(power, 1e-14)),
            }
    return waveforms, spectra


def save_figure(fig: plt.Figure, stem: str) -> list[Path]:
    paths = []
    for suffix in ("png", "pdf"):
        path = OUTPUT / f"{stem}.{suffix}"
        fig.savefig(
            path,
            dpi=280 if suffix == "png" else None,
            metadata=PDF_METADATA if suffix == "pdf" else None,
        )
        paths.append(path)
    plt.close(fig)
    return paths


def plot_pressure(configuration: dict, rows: list[dict], waveforms: dict) -> list[Path]:
    family_ids = list(configuration["impact_families"])
    fig, axes = plt.subplots(2, 4, figsize=(17.4, 7.5), sharey=True)
    for station_index, (station_id, station) in enumerate(configuration["stations"].items()):
        for family_index, family_id in enumerate(family_ids):
            panel = waveforms[(station_id, family_id)]
            axis = axes[station_index, family_index]
            axis.plot(panel["utc"], panel["combined"], color="#4477AA", linewidth=0.52, rasterized=True)
            axis.plot(panel["utc"], panel["signal"], color="#CC3311", linewidth=1.0)
            axis.axvline(panel["centre"], color="#222222", linewidth=0.7, linestyle=":")
            axis.set_ylim(-2.0, 2.0)
            axis.grid(alpha=0.16)
            axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S", tz=timezone.utc))
            axis.tick_params(axis="x", rotation=25, labelsize=7.5)
            if station_index == 0:
                label = configuration["impact_families"][family_id]["label"]
                axis.set_title(f"{label}\nmedian proxy {panel['amplitude']:.3g} Pa", fontsize=9.3)
            if family_index == 0:
                axis.set_ylabel(f"{station_id} — {station['name']}\npressure (Pa)")
            if station_index == 1:
                axis.set_xlabel("UTC on 8 March 2014", fontsize=8.8)
    fig.suptitle(
        "Illustrative station-domain pressure traces from the current impact sensitivity draws\n"
        "blue: generic 0.3 Pa RMS 5–15 Hz noise + pulse; red: pulse only; F-35-centred coupling-prior medians",
        fontsize=13.5,
    )
    fig.text(
        0.5,
        0.012,
        "Only the amplitude scale is model-derived. Pulse shape, noise, and placement are illustrative—not predicted aircraft-impact signatures or CTBTO data.",
        ha="center",
        fontsize=8.6,
    )
    fig.tight_layout(rect=[0.01, 0.05, 0.995, 0.90])
    return save_figure(fig, "simulated-pressure-time-series")


def plot_spectrograms(configuration: dict, spectra: dict) -> list[Path]:
    family_ids = list(configuration["impact_families"])
    visible_values = []
    for panel in spectra.values():
        mask = (panel["frequency_hz"] >= 2.0) & (panel["frequency_hz"] <= 20.0)
        visible_values.append(panel["db_pa2_hz"][mask])
    stacked = np.concatenate([value.ravel() for value in visible_values])
    colour_min, colour_max = np.quantile(stacked, [0.01, 0.995])
    fig, axes = plt.subplots(2, 4, figsize=(17.4, 7.5), sharex=True, sharey=True)
    image = None
    for station_index, (station_id, station) in enumerate(configuration["stations"].items()):
        for family_index, family_id in enumerate(family_ids):
            panel = spectra[(station_id, family_id)]
            axis = axes[station_index, family_index]
            image = axis.pcolormesh(
                panel["relative_s"],
                panel["frequency_hz"],
                panel["db_pa2_hz"],
                shading="auto",
                cmap="magma",
                vmin=colour_min,
                vmax=colour_max,
                rasterized=True,
            )
            axis.axvline(0.0, color="white", linewidth=0.75, linestyle=":", alpha=0.9)
            axis.set_xlim(-30.0, 30.0)
            axis.set_ylim(2.0, 20.0)
            if station_index == 0:
                axis.set_title(configuration["impact_families"][family_id]["label"], fontsize=9.3)
            if family_index == 0:
                axis.set_ylabel(f"{station_id} — {station['name']}\nfrequency (Hz)")
            if station_index == 1:
                axis.set_xlabel("Seconds relative to illustrative arrival")
    colour_axis = fig.add_axes([0.925, 0.15, 0.012, 0.68])
    colour_bar = fig.colorbar(image, cax=colour_axis)
    colour_bar.set_label(r"PSD (dB re 1 Pa$^2$/Hz)")
    fig.suptitle(
        "Spectrograms of the illustrative pressure traces\n"
        "Common colour scale; appearance reflects a generic two-part pulse and declared coloured noise, not a 777 hydrodynamic waveform",
        fontsize=13.5,
    )
    fig.text(
        0.5,
        0.012,
        "These panels show how the amplitude proxies render under one display model; they do not test event detectability or reproduce Kadri's filtering chain.",
        ha="center",
        fontsize=8.6,
    )
    fig.tight_layout(rect=[0.01, 0.05, 0.91, 0.90])
    return save_figure(fig, "simulated-pressure-spectrograms")


def main() -> None:
    configuration = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    rows = load_pressure_rows(configuration)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    waveforms, spectra = generate_panels(configuration, rows)
    paths = [
        *plot_pressure(configuration, rows, waveforms),
        *plot_spectrograms(configuration, spectra),
    ]
    manifest = {
        "status": "ILLUSTRATIVE_PRESSURE_RENDERING_NOT_SOURCE_WAVEFORM_OR_DETECTOR",
        "inputs": {
            str(CONFIG_PATH.relative_to(HERE)): sha256(CONFIG_PATH),
            str(QUANTILES_PATH.relative_to(HERE)): sha256(QUANTILES_PATH),
        },
        "code": {str(Path(__file__).relative_to(HERE)): sha256(Path(__file__))},
        "display_model": {
            "coupling_prior": "f35_centred",
            "pressure_quantile": 0.5,
            "sample_rate_hz": 50.0,
            "noise_rms_pa": 0.3,
            "noise_band_hz": [5.0, 15.0],
            "pulse": "normalised 8 Hz Gaussian-windowed carrier plus delayed 6.2 Hz component",
            "placement": "representative high-rate receiver time from impact-simulation-config.json",
        },
        "outputs": {path.name: sha256(path) for path in paths},
        "limitations": [
            "only peak-pressure amplitude comes from the impact sensitivity calculation",
            "pulse shape and noise are generic display assumptions",
            "no 777 hydrodynamics, source spectrum, AGW dispersion, site response, CTBTO processing or detector is represented",
        ],
    }
    manifest_path = OUTPUT / "simulated-pressure-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
