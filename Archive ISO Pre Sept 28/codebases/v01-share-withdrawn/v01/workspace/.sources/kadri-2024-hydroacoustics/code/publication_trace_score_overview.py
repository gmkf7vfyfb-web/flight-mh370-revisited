#!/usr/bin/env python3
"""Catalogue noted events and plot full-window publication-trace energy scores.

The pressure inputs are vectors extracted from Kadri Figure 9, not raw CTBTO
channels. H08S panels are filtered with the held-out-control-selected rank-8
low-rank method. Impact times are conditional summaries under the independent
integrated spatial PDF and a declared uniform celerity sensitivity.
"""

from __future__ import annotations

import copy
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from scipy.signal import find_peaks

import event_pair_analysis as base
import filter_sensitivity as airgun


HERE = Path(__file__).resolve().parents[1]
DATA = HERE / "data"
OUTPUT = HERE / "outputs"
EVENT_CONFIG_PATH = DATA / "event-pair-analysis-config.json"
FILTER_CONFIG_PATH = DATA / "filter-sensitivity-config.json"
PDF_METADATA = {"CreationDate": None, "ModDate": None}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"No rows for {path}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def candidate_peaks(
    score: np.ndarray,
    screen: dict,
) -> tuple[np.ndarray, float]:
    dt = float(screen["regular_grid_dt_s"])
    separation = int(round(float(screen["candidate_minimum_separation_s"]) / dt))
    guard = int(round(float(screen["panel_edge_guard_s"]) / dt))
    peaks, _ = find_peaks(score, distance=separation)
    peaks = peaks[(peaks >= guard) & (peaks < score.size - guard)]
    threshold = float(
        np.quantile(score[peaks], float(screen["candidate_score_quantile_per_panel"]))
    )
    return peaks, threshold


def load_h08_panel(panel_name: str, configuration: dict) -> airgun.TracePanel:
    metadata = json.loads(base.METADATA_PATH.read_text(encoding="utf-8"))
    record = next(
        row
        for row in metadata["figure9_vector_traces"]
        if row["station"] == "H08S" and row["panel"] == panel_name
    )
    with (base.TRACE_ROOT / record["file"]).open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    source_time = np.asarray([float(row["plotted_time_s"]) for row in rows])
    source_pressure = np.asarray([float(row["pressure_pa"]) for row in rows])
    order = np.argsort(source_time)
    unique_time, unique_index = np.unique(source_time[order], return_index=True)
    source_pressure = source_pressure[order][unique_index]
    dt = float(configuration["regular_grid_dt_s"])
    time_s = np.arange(0.0, 600.0, dt)
    pressure = np.interp(time_s, unique_time, source_pressure)
    pressure -= np.median(pressure)
    start = base.parse_utc(record["start_utc"]).timestamp()
    return airgun.TracePanel(
        panel=panel_name,
        start_epoch_s=start,
        time_s=time_s,
        epoch_s=start + time_s,
        pressure_pa=pressure,
    )


def analyse_h08_panel(
    panel_name: str,
    event_utc: str,
    filter_configuration: dict,
    screen: dict,
    fixed_method: str | None,
) -> dict:
    local_configuration = copy.deepcopy(filter_configuration)
    local_configuration["event_utc"] = event_utc
    panel = load_h08_panel(panel_name, local_configuration)
    geometry = airgun.fit_shot_geometry(panel, local_configuration)
    cycles = airgun.extract_and_align_cycles(panel, geometry, local_configuration)
    methods = airgun.evaluate_methods(cycles, geometry, local_configuration)
    control_selected = min(
        methods, key=lambda row: row["control_median_rms_retained_fraction"]
    )
    selected = (
        control_selected
        if fixed_method is None
        else next(row for row in methods if row["method"] == fixed_method)
    )
    residual = airgun.build_full_trace(
        panel, geometry, cycles, selected["_residuals"]
    )
    score = base.score_signal(residual, screen)
    peaks, threshold = candidate_peaks(score, screen)
    return {
        "panel": panel,
        "geometry": geometry,
        "cycles": cycles,
        "selected": selected,
        "control_selected": control_selected,
        "residual": residual,
        "score": score,
        "peaks": peaks,
        "threshold": threshold,
        "event_utc": event_utc,
    }


def local_event_score(
    epoch_s: np.ndarray,
    score: np.ndarray,
    event_epoch_s: float,
    half_width_s: float = 2.0,
) -> tuple[float, float]:
    indices = np.flatnonzero(np.abs(epoch_s - event_epoch_s) <= half_width_s)
    if indices.size == 0:
        raise ValueError("Event lies outside its declared panel")
    index = int(indices[np.argmax(score[indices])])
    return float(score[index]), float(epoch_s[index])


def impact_time_catalogue(
    configuration: dict,
    spatial: dict,
    traces: dict[str, base.Trace],
    h08_results: dict[str, dict],
) -> list[dict]:
    timing = configuration["impact_time_monte_carlo"]
    count = int(timing["sample_count"])
    rng = np.random.default_rng(int(timing["random_seed"]))
    probability = spatial["probability"].ravel()
    probability = probability / np.sum(probability)
    selected_cells = rng.choice(
        probability.size, size=count, replace=True, p=probability
    )
    celerity = rng.uniform(
        *map(float, configuration["acoustic_celerity_km_s"]), size=count
    )
    control_low, control_high = [
        base.parse_utc(value).timestamp()
        for value in configuration["impact_time_control_utc"]
    ]
    rows = []
    for event in configuration["noted_events"]:
        station = event["station"]
        arrival_epoch = base.parse_utc(event["arrival_utc"]).timestamp()
        distance_key = "distance_h01" if station == "H01W" else "distance_h08"
        distance = spatial[distance_key].ravel()[selected_cells]
        impact_epoch = arrival_epoch - distance / celerity
        quantiles = np.quantile(
            impact_epoch, np.asarray(timing["quantiles"], dtype=float)
        )
        after_final = (quantiles - control_low) / 60.0
        within = float(
            np.mean((impact_epoch >= control_low) & (impact_epoch <= control_high))
        )

        if station == "H01W":
            trace = traces[event["panel"]]
            score = trace.score
            epoch_s = trace.epoch_s
            threshold = trace.threshold
            score_basis = "original extracted publication trace"
        else:
            result = h08_results[event["panel"]]
            score = result["score"]
            epoch_s = result["panel"].epoch_s
            threshold = result["threshold"]
            score_basis = (
                "rank-8 low-rank residual selected on panel-d held-out controls"
            )
        local_score, local_peak_epoch = local_event_score(
            epoch_s, score, arrival_epoch
        )

        bearing = event["bearing_deg"]
        bearing_mass = ""
        if bearing is not None and station == "H01W":
            difference = np.abs(
                base.angular_difference_deg(
                    spatial["bearing_h01"], float(bearing)
                )
            )
            formal = float(configuration["bearing_half_widths_deg"]["formal"])
            bearing_mass = f"{np.sum(spatial['probability'][difference <= formal]):.9g}"

        rows.append(
            {
                "event_id": event["id"],
                "station": station,
                "panel": event["panel"],
                "arrival_utc": event["arrival_utc"],
                "category": event["category"],
                "bearing_deg": "" if bearing is None else f"{float(bearing):.2f}",
                "integrated_pdf_mass_within_formal_bearing": bearing_mass,
                "local_energy_score_basis": score_basis,
                "local_energy_score_within_2s": f"{local_score:.9g}",
                "local_energy_peak_utc_within_2s": base.iso_utc(local_peak_epoch),
                "panel_q99_threshold": f"{threshold:.9g}",
                "above_panel_q99_within_2s": bool(local_score >= threshold),
                "implied_impact_q2p5_utc": base.iso_utc(quantiles[0]),
                "implied_impact_median_utc": base.iso_utc(quantiles[1]),
                "implied_impact_q97p5_utc": base.iso_utc(quantiles[2]),
                "implied_flight_after_001937_q2p5_min": f"{after_final[0]:.4f}",
                "implied_flight_after_001937_median_min": f"{after_final[1]:.4f}",
                "implied_flight_after_001937_q97p5_min": f"{after_final[2]:.4f}",
                "monte_carlo_mass_within_001937_to_004937": f"{within:.9g}",
                "timing_model": (
                    "integrated PDF and uniform 1.43–1.57 km/s celerity; "
                    "500,000 deterministic draws"
                ),
                "status": event["status"],
            }
        )
    return rows


def peak_rows(
    station: str,
    panel_name: str,
    epoch_s: np.ndarray,
    score: np.ndarray,
    peaks: np.ndarray,
    threshold: float,
    geometry: airgun.ShotGeometry | None = None,
    panel_start_epoch_s: float | None = None,
    start_epoch_s: float | None = None,
    limit: int = 20,
) -> list[dict]:
    eligible = peaks
    if start_epoch_s is not None:
        eligible = eligible[epoch_s[eligible] >= start_epoch_s]
    ordered = sorted(eligible, key=lambda index: score[index], reverse=True)
    rows = []
    for rank, index in enumerate(ordered[:limit], start=1):
        shot_utc = ""
        shot_offset_s = ""
        if geometry is not None and panel_start_epoch_s is not None:
            shot_epochs = panel_start_epoch_s + geometry.observed_centres_s
            nearest = int(np.argmin(np.abs(shot_epochs - epoch_s[index])))
            shot_utc = base.iso_utc(shot_epochs[nearest])
            shot_offset_s = f"{epoch_s[index] - shot_epochs[nearest]:.3f}"
        rows.append(
            {
                "station": station,
                "panel": panel_name,
                "rank_within_panel": rank,
                "peak_utc": base.iso_utc(epoch_s[index]),
                "local_energy_score": f"{score[index]:.9g}",
                "panel_q99_threshold": f"{threshold:.9g}",
                "above_panel_q99": bool(score[index] >= threshold),
                "nearest_observed_airgun_peak_utc": shot_utc,
                "offset_from_observed_airgun_peak_s": shot_offset_s,
                "status": (
                    "FILTERED_PUBLICATION_TRACE_PEAK_NOT_EVENT_IDENTITY"
                    if station == "H08S"
                    else "PUBLICATION_TRACE_PEAK_NOT_EVENT_IDENTITY"
                ),
            }
        )
    return rows


def pressure_scale_rows(traces: dict[str, base.Trace]) -> list[dict]:
    metadata = json.loads(base.METADATA_PATH.read_text(encoding="utf-8"))
    records = {
        record["panel"]: record for record in metadata["figure9_vector_traces"]
    }
    rows = []
    for panel_name in ("a", "b", "c", "d", "e"):
        trace = traces[panel_name]
        values = trace.pressure_pa
        median = float(np.median(values))
        with (base.TRACE_ROOT / records[panel_name]["file"]).open(
            newline="", encoding="utf-8"
        ) as handle:
            vector_values = np.asarray(
                [float(row["pressure_pa"]) for row in csv.DictReader(handle)]
            )
        rows.append(
            {
                "panel": panel_name,
                "station": trace.station,
                "raw_vector_vertex_rms_pa": (
                    f"{np.sqrt(np.mean(vector_values**2)):.9g}"
                ),
                "raw_vector_vertex_mean_removed_rms_pa": (
                    f"{np.std(vector_values):.9g}"
                ),
                "analysis_trace_mean_removed_rms_pa": f"{np.std(values):.9g}",
                "analysis_trace_median_absolute_deviation_sigma_pa": (
                    f"{1.4826 * np.median(np.abs(values - median)):.9g}"
                ),
                "analysis_trace_q05_pa": f"{np.quantile(values, 0.05):.9g}",
                "analysis_trace_q95_pa": f"{np.quantile(values, 0.95):.9g}",
                "analysis_trace_maximum_absolute_pa": (
                    f"{np.max(np.abs(values)):.9g}"
                ),
                "status": (
                    "EXTRACTED_ALREADY_FILTERED_PUBLICATION_TRACE_NOT_RECEIVER_NOISE; "
                    "raw vertex RMS is sampling-density dependent"
                ),
            }
        )
    return rows


def plot_h01_scores(
    configuration: dict,
    traces: dict[str, base.Trace],
    catalogue: list[dict],
) -> list[Path]:
    start_epoch = base.parse_utc("2014-03-08T00:39:23Z").timestamp()
    end_epoch = traces["c"].epoch_s[-1]
    figure, axis = plt.subplots(figsize=(16.5, 6.4))
    for panel_name, shade in (("b", "#F3EEF8"), ("c", "#ECE2F0")):
        trace = traces[panel_name]
        visible = (trace.epoch_s >= start_epoch) & (trace.epoch_s <= end_epoch)
        times = np.asarray(
            [datetime.fromtimestamp(value, timezone.utc) for value in trace.epoch_s]
        )
        axis.axvspan(
            times[visible][0],
            times[visible][-1],
            color=shade,
            alpha=0.46,
            zorder=0,
        )
        axis.plot(
            times[visible],
            trace.score[visible],
            color="#3F145D",
            linewidth=1.55,
            label="robust multi-window local-energy score"
            if panel_name == "b"
            else None,
        )
        axis.hlines(
            trace.threshold,
            times[visible][0],
            times[visible][-1],
            color="#B2182B",
            linewidth=1.15,
            linestyle="--",
            label="panel q99 candidate threshold"
            if panel_name == "b"
            else None,
        )
        q99 = [
            index
            for index in trace.candidate_indices
            if visible[index] and trace.score[index] >= trace.threshold
        ]
        for index in q99:
            axis.scatter(times[index], trace.score[index], s=55, color="#B2182B", zorder=6)
            axis.annotate(
                f"{times[index]:%H:%M:%S}\nscore {trace.score[index]:.2f}",
                (times[index], trace.score[index]),
                xytext=(6, 9),
                textcoords="offset points",
                fontsize=8.2,
                color="#6A0014",
            )

    colours = {
        "kadri_table_1_transient": "#2166AC",
        "kadri_figure9_major_signal": "#E08214",
        "kadri_figure9_preferred_signal": "#B2182B",
        "independently_screened_publication_trace": "#1B7837",
        "edge_affected_screen": "#777777",
    }
    levels = [0.98, 0.90, 0.82, 0.74]
    position = 0
    for event in configuration["noted_events"]:
        if event["station"] != "H01W":
            continue
        event_time = base.parse_utc(event["arrival_utc"])
        if event_time.timestamp() < start_epoch:
            continue
        colour = colours[event["category"]]
        axis.axvline(event_time, color=colour, linewidth=0.9, alpha=0.72)
        axis.text(
            event_time,
            levels[position % len(levels)],
            event_time.strftime("%H:%M:%S"),
            transform=axis.get_xaxis_transform(),
            rotation=90,
            va="top",
            ha="right",
            fontsize=7.1,
            color=colour,
        )
        position += 1

    axis.set_xlim(
        datetime.fromtimestamp(start_epoch, timezone.utc),
        datetime.fromtimestamp(end_epoch, timezone.utc),
    )
    axis.set_ylabel("Robust local-energy score (dimensionless)")
    axis.set_xlabel("UTC on 8 March 2014")
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    axis.grid(alpha=0.16)
    axis.legend(loc="upper left", frameon=False)
    axis.set_title(
        "Cape Leeuwin H01W local-energy score across the complete relevant Figure 9 window"
    )
    figure.text(
        0.5,
        0.018,
        "The score is normalised separately within each already-filtered publication panel; "
        "vertical event times are context, not detected associations.",
        ha="center",
        fontsize=8.6,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.96])
    paths = []
    for suffix in ("png", "pdf"):
        path = OUTPUT / f"h01w-full-window-local-energy.{suffix}"
        figure.savefig(
            path,
            dpi=280 if suffix == "png" else None,
            metadata=PDF_METADATA if suffix == "pdf" else None,
        )
        paths.append(path)
    plt.close(figure)
    return paths


def plot_h08_scores(
    configuration: dict,
    results: dict[str, dict],
) -> list[Path]:
    figure, axis = plt.subplots(figsize=(16.5, 6.4))
    for panel_name, shade in (("d", "#EFF6FB"), ("e", "#E5F0F7")):
        result = results[panel_name]
        panel = result["panel"]
        times = np.asarray(
            [datetime.fromtimestamp(value, timezone.utc) for value in panel.epoch_s]
        )
        axis.axvspan(times[0], times[-1], color=shade, alpha=0.50, zorder=0)
        for centre in result["geometry"].observed_centres_s:
            axis.axvline(
                datetime.fromtimestamp(panel.start_epoch_s + centre, timezone.utc),
                color="#67A9CF",
                linewidth=0.35,
                alpha=0.22,
                zorder=1,
            )
        axis.plot(
            times,
            result["score"],
            color="#3F145D",
            linewidth=1.5,
            label="local-energy score after selected rank-8 residual"
            if panel_name == "d"
            else None,
        )
        axis.hlines(
            result["threshold"],
            times[0],
            times[-1],
            color="#B2182B",
            linewidth=1.15,
            linestyle="--",
            label="panel q99 residual-score threshold"
            if panel_name == "d"
            else None,
        )
        q99 = [
            index
            for index in result["peaks"]
            if result["score"][index] >= result["threshold"]
        ]
        for index in q99:
            axis.scatter(
                times[index], result["score"][index], s=55, color="#B2182B", zorder=6
            )
            axis.annotate(
                f"{times[index]:%H:%M:%S}\nscore {result['score'][index]:.2f}",
                (times[index], result["score"][index]),
                xytext=(6, 9),
                textcoords="offset points",
                fontsize=8.2,
                color="#6A0014",
            )

    for event in configuration["noted_events"]:
        if event["station"] != "H08S":
            continue
        event_time = base.parse_utc(event["arrival_utc"])
        axis.axvline(event_time, color="#1B7837", linewidth=1.25)
        axis.text(
            event_time,
            0.96,
            event_time.strftime("%H:%M:%S"),
            transform=axis.get_xaxis_transform(),
            rotation=90,
            va="top",
            ha="right",
            fontsize=7.5,
            color="#1B7837",
        )

    first = results["d"]["panel"].epoch_s[0]
    last = results["e"]["panel"].epoch_s[-1]
    axis.set_xlim(
        datetime.fromtimestamp(first, timezone.utc),
        datetime.fromtimestamp(last, timezone.utc),
    )
    axis.set_ylabel("Residual local-energy score (dimensionless)")
    axis.set_xlabel("UTC on 8 March 2014")
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=timezone.utc))
    axis.grid(alpha=0.16)
    axis.legend(
        handles=[
            Line2D([0], [0], color="#3F145D", linewidth=1.5, label="rank-8 residual local-energy score"),
            Line2D([0], [0], color="#B2182B", linestyle="--", label="panel q99 threshold"),
            Line2D([0], [0], color="#67A9CF", linewidth=1.0, label="observed periodic-shot centres"),
            Line2D([0], [0], color="#1B7837", linewidth=1.2, label="noted screened time"),
        ],
        loc="upper left",
        frameon=False,
        ncol=2,
    )
    axis.set_title(
        "Diego Garcia H08S local-energy score after the held-out-control-selected airgun filter"
    )
    figure.text(
        0.5,
        0.018,
        "Rank 8 with ±0.30 s alignment was selected on panel d without using the target; "
        "the same method is transferred to panel e. Residual peaks remain periodic-context features.",
        ha="center",
        fontsize=8.5,
    )
    figure.tight_layout(rect=[0.0, 0.045, 1.0, 0.96])
    paths = []
    for suffix in ("png", "pdf"):
        path = OUTPUT / f"h08s-selected-filter-full-window-local-energy.{suffix}"
        figure.savefig(
            path,
            dpi=280 if suffix == "png" else None,
            metadata=PDF_METADATA if suffix == "pdf" else None,
        )
        paths.append(path)
    plt.close(figure)
    return paths


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    configuration = json.loads(EVENT_CONFIG_PATH.read_text(encoding="utf-8"))
    filter_configuration = json.loads(FILTER_CONFIG_PATH.read_text(encoding="utf-8"))
    traces = base.load_traces(configuration)
    spatial = base.load_spatial(configuration)
    screen = configuration["trace_screen"]

    h08_events = {
        event["panel"]: event["arrival_utc"]
        for event in configuration["noted_events"]
        if event["station"] == "H08S"
    }
    result_d = analyse_h08_panel(
        "d", h08_events["d"], filter_configuration, screen, fixed_method=None
    )
    selected_method = result_d["selected"]["method"]
    result_e = analyse_h08_panel(
        "e",
        h08_events["e"],
        filter_configuration,
        screen,
        fixed_method=selected_method,
    )
    h08_results = {"d": result_d, "e": result_e}

    catalogue = impact_time_catalogue(
        configuration, spatial, traces, h08_results
    )
    catalogue_path = OUTPUT / "noted-event-impact-time-catalogue.csv"
    write_csv(catalogue_path, catalogue)

    h01_peak_output = []
    h01_start = base.parse_utc("2014-03-08T00:39:23Z").timestamp()
    for panel_name in ("b", "c"):
        trace = traces[panel_name]
        h01_peak_output.extend(
            peak_rows(
                "H01W",
                panel_name,
                trace.epoch_s,
                trace.score,
                trace.candidate_indices,
                trace.threshold,
                start_epoch_s=h01_start,
            )
        )
    h01_peaks_path = OUTPUT / "h01w-local-energy-peaks.csv"
    write_csv(h01_peaks_path, h01_peak_output)

    h08_peak_output = []
    for panel_name in ("d", "e"):
        result = h08_results[panel_name]
        h08_peak_output.extend(
            peak_rows(
                "H08S",
                panel_name,
                result["panel"].epoch_s,
                result["score"],
                result["peaks"],
                result["threshold"],
                geometry=result["geometry"],
                panel_start_epoch_s=result["panel"].start_epoch_s,
            )
        )
    h08_peaks_path = OUTPUT / "h08s-selected-filter-local-energy-peaks.csv"
    write_csv(h08_peaks_path, h08_peak_output)

    pressure_path = OUTPUT / "publication-trace-pressure-scales.csv"
    write_csv(pressure_path, pressure_scale_rows(traces))

    paths = [
        catalogue_path,
        h01_peaks_path,
        h08_peaks_path,
        pressure_path,
        *plot_h01_scores(configuration, traces, catalogue),
        *plot_h08_scores(configuration, h08_results),
    ]
    summary = {
        "status": "PUBLICATION_TRACE_SCORE_AND_CONDITIONAL_TIMING_SUMMARY_NOT_EVENT_ASSOCIATION",
        "h01w_q99_peaks": [
            row for row in h01_peak_output if row["above_panel_q99"]
        ],
        "h08s_selected_filter": {
            "method_selected_on_panel_d": selected_method,
            "panel_e_control_selected_method": result_e["control_selected"]["method"],
            "panel_d_q99_peaks": [
                row
                for row in h08_peak_output
                if row["panel"] == "d" and row["above_panel_q99"]
            ],
            "panel_e_q99_peaks": [
                row
                for row in h08_peak_output
                if row["panel"] == "e" and row["above_panel_q99"]
            ],
        },
        "impact_time_model": configuration["impact_time_monte_carlo"],
        "limits": [
            "scores operate on already-filtered publication vectors, not raw CTBTO channels",
            "q99 is a within-panel screen, not a calibrated false-alarm probability",
            "H08S residual filtering can remove or retain coincident signal energy depending on subspace overlap",
            "impact-time intervals assume the independent integrated PDF and uniform celerity; they are not association posteriors",
        ],
    }
    summary_path = OUTPUT / "publication-score-overview-summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    paths.append(summary_path)

    manifest = {
        "status": "REPRODUCIBLE_OUTPUT_HASHES",
        "inputs": {
            str(EVENT_CONFIG_PATH.relative_to(HERE)): sha256(EVENT_CONFIG_PATH),
            str(FILTER_CONFIG_PATH.relative_to(HERE)): sha256(FILTER_CONFIG_PATH),
            "data/kadri-figure-extraction/metadata.json": sha256(base.METADATA_PATH),
            "data/posterior_grids.npz": sha256(base.GRID_PATH),
        },
        "code": {
            str(Path(__file__).relative_to(HERE)): sha256(Path(__file__)),
            "code/event_pair_analysis.py": sha256(Path(base.__file__)),
            "code/filter_sensitivity.py": sha256(Path(airgun.__file__)),
        },
        "outputs": {path.name: sha256(path) for path in paths},
    }
    (OUTPUT / "publication-score-overview-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
