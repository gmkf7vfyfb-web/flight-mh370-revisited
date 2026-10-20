#!/usr/bin/env python3
"""Build a family-specific ocean-drift likelihood admission handoff.

The handoff removes the source-cell prior, keeps current families separate,
and documents one nearest-cell query contract with explicit out-of-support
behavior. Admission is derived from configured scientific diagnostics; this
script never averages families or converts a failed diagnostic into evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


TERMINATION_REASONS = (
    "missing_field_coverage",
    "outside_spatial_support",
    "land_encounter",
    "beaching",
    "outside_time_support",
    "numerical_failure",
)
OUT_OF_SUPPORT_REASONS = (
    "missing_field_coverage",
    "outside_spatial_support",
    "outside_time_support",
)
CONTOUR_LEVELS = (0.90, 0.95, 0.99)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(repo: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else repo / path


def display_path(repo: Path, path: Path) -> str:
    try:
        return str(path.resolve().relative_to(repo.resolve()))
    except ValueError:
        return str(path.resolve())


def normalized(values: list[float]) -> list[float]:
    total = sum(values)
    if not math.isfinite(total) or total <= 0.0:
        raise ValueError("weights do not have positive finite mass")
    return [value / total for value in values]


def median(values: list[float]) -> float:
    if not values:
        raise ValueError("cannot calculate the median of an empty sequence")
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[middle]
    return 0.5 * (ordered[middle - 1] + ordered[middle])


def weighted_quantile(values: list[float], weights: list[float], probability: float) -> float:
    cumulative = 0.0
    for value, weight in sorted(zip(values, normalized(weights)), key=lambda item: item[0]):
        cumulative += weight
        if cumulative >= probability:
            return value
    return max(values)


def equal_tail(values: list[float], weights: list[float], level: float) -> list[float]:
    tail = 0.5 * (1.0 - level)
    return [
        weighted_quantile(values, weights, tail),
        weighted_quantile(values, weights, 1.0 - tail),
    ]


def recovery_map(cell: dict) -> dict[str, dict]:
    return {
        str(item["event_id"]): item
        for item in cell.get("recoveries", [])
        if "event_id" in item
    }


def non_recovery_ids(cell: dict) -> set[str]:
    return {
        str(item["observation_id"])
        for item in cell.get("non_recoveries", [])
        if "observation_id" in item
    }


def summarize_validation(path: Path, family: str, thresholds: dict) -> dict:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = [row for row in csv.DictReader(stream) if row["family"] == family]
    if not rows:
        return {
            "matched": False,
            "passed": False,
            "reason": f"no predictive-validation rows match {family}",
            "source": {"path": str(path), "sha256": sha256(path)},
        }
    complete = [float(row["complete_fraction"]) for row in rows]
    error_ratios = [
        float(row["median_current_terminal_hold_error_km"])
        / float(row["median_persistence_error_km"])
        for row in rows
    ]
    better = [float(row["current_better_than_persistence_fraction"]) for row in rows]
    passed = (
        min(complete) >= thresholds["minimum_validation_complete_fraction"]
        and median(error_ratios) <= thresholds["maximum_median_error_ratio_to_persistence"]
        and median(better) >= thresholds["minimum_median_fraction_better_than_persistence"]
    )
    return {
        "matched": True,
        "passed": passed,
        "family": family,
        "row_count": len(rows),
        "attempted_paths": sum(int(row["attempts"]) for row in rows),
        "minimum_complete_fraction": min(complete),
        "median_error_ratio_to_persistence": median(error_ratios),
        "median_fraction_better_than_persistence": median(better),
        "failed_paths_scored_by_terminal_hold": True,
        "assimilation_or_climatology_leakage_limitation": True,
        "source": {"path": str(path), "sha256": sha256(path)},
    }


def summarize_stability(
    repo: Path, path: Path | None, source_path: Path, thresholds: dict
) -> dict:
    if path is None or not path.exists():
        return {
            "matched": False,
            "passed": False,
            "reason": "no matched seed-and-particle replication artifact",
        }
    document = json.loads(path.read_text(encoding="utf-8"))
    source_resolved = source_path.resolve()
    matches = []
    for run in document.get("runs", []):
        candidate = resolve(repo, run["output"]) / "source-area.json"
        if candidate.resolve() == source_resolved:
            matches.append(run)
    if len(matches) != 1:
        return {
            "matched": False,
            "passed": False,
            "reason": "stability artifact does not contain this exact source result",
            "source": {"path": display_path(repo, path), "sha256": sha256(path)},
        }
    run = matches[0]
    comparisons = [
        item
        for item in document.get("pairwise_comparisons", [])
        if run["name"] in (item["first"], item["second"])
    ]
    if not comparisons:
        return {
            "matched": True,
            "passed": False,
            "reason": "matched run has no seed-or-particle comparison",
            "run": run["name"],
            "source": {"path": display_path(repo, path), "sha256": sha256(path)},
        }
    maximum_tv = max(item["weight_total_variation"] for item in comparisons)
    maximum_endpoint_shift = max(
        contour["equal_tail_endpoint_maximum_shift_cells"]
        for item in comparisons
        for contour in item["contours"]
        if contour["level"] in CONTOUR_LEVELS
    )
    minimum_jaccard = min(
        contour["highest_weight_set_jaccard"]
        for item in comparisons
        for contour in item["contours"]
        if contour["level"] in CONTOUR_LEVELS
    )
    passed = (
        maximum_tv <= thresholds["maximum_replication_total_variation"]
        and maximum_endpoint_shift
        <= thresholds["maximum_contour_endpoint_shift_cells"]
        and minimum_jaccard >= thresholds["minimum_contour_set_jaccard"]
    )
    return {
        "matched": True,
        "passed": passed,
        "run": run["name"],
        "comparison_count": len(comparisons),
        "maximum_total_variation": maximum_tv,
        "maximum_90_95_99_endpoint_shift_cells": maximum_endpoint_shift,
        "minimum_90_95_99_highest_weight_set_jaccard": minimum_jaccard,
        "source": {"path": display_path(repo, path), "sha256": sha256(path)},
    }


def check(name: str, passed: bool, value, threshold, explanation: str) -> dict:
    return {
        "name": name,
        "passed": passed,
        "value": value,
        "threshold": threshold,
        "explanation": explanation,
    }


def summarize_family(repo: Path, specification: dict, thresholds: dict) -> dict:
    source_path = resolve(repo, specification["source_result"])
    source = json.loads(source_path.read_text(encoding="utf-8"))
    cells = source["cells"]
    if not cells:
        raise ValueError(f"source result has no cells: {source_path}")

    evidence_log = []
    for cell in cells:
        combined = cell.get("combined_log_weight")
        if combined is None:
            evidence_log.append(-math.inf)
        else:
            evidence_log.append(float(combined) - math.log(float(cell["prior_weight"])))
    finite = [value for value in evidence_log if math.isfinite(value)]
    if not finite:
        raise ValueError(f"source result has no finite likelihood: {source_path}")
    maximum = max(finite)
    relative = [math.exp(value - maximum) if math.isfinite(value) else 0.0 for value in evidence_log]
    surface_mass = normalized(relative)
    latitude_s = [-float(cell["position"]["latitude"]) for cell in cells]

    event_maps = [recovery_map(cell) for cell in cells]
    actual_events = sorted(set().union(*(set(items) for items in event_maps)))
    actual_non_recoveries = sorted(
        set().union(*(non_recovery_ids(cell) for cell in cells))
    )
    expected_events = sorted(specification["expected_recovery_events"])
    expected_non_recoveries = sorted(specification["expected_non_recoveries"])

    minimum_event_ess = []
    for items in event_maps:
        if set(items) == set(expected_events) and items:
            minimum_event_ess.append(
                min(float(items[event]["effective_sample_size"]) for event in expected_events)
            )
        else:
            minimum_event_ess.append(0.0)
    ess_mass = sum(
        weight
        for weight, value in zip(surface_mass, minimum_event_ess, strict=True)
        if value >= thresholds["minimum_event_arrival_ess"]
    )

    weighted_termination = {
        reason: sum(
            weight * float(cell.get("termination_reason_fractions", {}).get(reason, 0.0))
            for weight, cell in zip(surface_mass, cells, strict=True)
        )
        for reason in TERMINATION_REASONS
    }
    out_of_support = sum(weighted_termination[reason] for reason in OUT_OF_SUPPORT_REASONS)

    isotope_items = [cell.get("isotope") for cell in cells if cell.get("isotope")]
    isotope_counts = {
        "compatible": sum(int(item.get("compatible_paths", 0)) for item in isotope_items),
        "marginal": sum(int(item.get("marginal_paths", 0)) for item in isotope_items),
        "rejected": sum(int(item.get("rejected_paths", 0)) for item in isotope_items),
        "missing_coverage": sum(
            int(item.get("missing_coverage_paths", 0)) for item in isotope_items
        ),
    }
    isotope_log = [
        float(cell["conditional_isotope_log_compatibility"])
        for cell in cells
        if cell.get("conditional_isotope_log_compatibility") is not None
    ]
    isotope_nonpositive = bool(isotope_log) and max(isotope_log) <= 1e-12

    stability_path = specification.get("stability_summary")
    stability = summarize_stability(
        repo,
        resolve(repo, stability_path) if stability_path else None,
        source_path,
        thresholds,
    )
    validation_path = resolve(repo, specification["trajectory_validation_csv"])
    validation = summarize_validation(
        validation_path, specification["trajectory_validation_family"], thresholds
    )

    checks = [
        check(
            "complete_evidence_scope",
            actual_events == expected_events
            and actual_non_recoveries == expected_non_recoveries,
            {
                "recoveries": actual_events,
                "non_recoveries": actual_non_recoveries,
            },
            {
                "recoveries": expected_events,
                "non_recoveries": expected_non_recoveries,
            },
            "Every selected recovery and Australian non-recovery population must be represented.",
        ),
        check(
            "out_of_support_termination",
            out_of_support <= thresholds["maximum_out_of_support_fraction"],
            out_of_support,
            thresholds["maximum_out_of_support_fraction"],
            "Missing, outside-spatial, and outside-time support are failures, never zero current.",
        ),
        check(
            "eventwise_arrival_ess",
            ess_mass >= thresholds["minimum_surface_mass_with_event_ess"],
            ess_mass,
            thresholds["minimum_surface_mass_with_event_ess"],
            "Supported source mass must have hundreds-scale effective arrivals for every recovery.",
        ),
        check(
            "seed_and_particle_stability",
            stability["passed"],
            stability,
            {
                "maximum_total_variation": thresholds[
                    "maximum_replication_total_variation"
                ],
                "maximum_contour_endpoint_shift_cells": thresholds[
                    "maximum_contour_endpoint_shift_cells"
                ],
                "minimum_contour_set_jaccard": thresholds[
                    "minimum_contour_set_jaccard"
                ],
            },
            "The exact surface must be stable when the seed changes and particle count doubles.",
        ),
        check(
            "predictive_drifter_validation",
            validation["passed"],
            validation,
            {
                "minimum_complete_fraction": thresholds[
                    "minimum_validation_complete_fraction"
                ],
                "maximum_median_error_ratio_to_persistence": thresholds[
                    "maximum_median_error_ratio_to_persistence"
                ],
                "minimum_median_fraction_better_than_persistence": thresholds[
                    "minimum_median_fraction_better_than_persistence"
                ],
            },
            "All attempts, including terminated paths, are scored against persistence.",
        ),
        check(
            "conservative_isotope_screen",
            bool(source.get("isotope_enabled")) and isotope_nonpositive,
            {
                "enabled": bool(source.get("isotope_enabled")),
                "maximum_conditional_log_compatibility": max(isotope_log)
                if isotope_log
                else None,
                "path_classification_counts": isotope_counts,
            },
            "enabled and never positive",
            "Isotope is conditional on represented Reunion arrival and may only downweight.",
        ),
    ]
    admitted = all(item["passed"] for item in checks)

    event_diagnostics = []
    for event in actual_events:
        values = [
            float(items[event]["effective_sample_size"])
            for items in event_maps
            if event in items
        ]
        mass = sum(
            weight
            for weight, items in zip(surface_mass, event_maps, strict=True)
            if event in items
            and float(items[event]["effective_sample_size"])
            >= thresholds["minimum_event_arrival_ess"]
        )
        event_diagnostics.append(
            {
                "event_id": event,
                "maximum_effective_sample_size": max(values),
                "median_effective_sample_size": median(values),
                "surface_mass_at_or_above_threshold": mass,
            }
        )

    peak_index = max(range(len(cells)), key=lambda index: relative[index])
    manifest_path = source_path.parent / "run-manifest.json"
    runtime_path = source_path.parent / "runtime-receipt.json"
    manifest = (
        json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest_path.exists()
        else None
    )
    runtime = (
        json.loads(runtime_path.read_text(encoding="utf-8"))
        if runtime_path.exists()
        else None
    )
    cell_records = []
    for index, (cell, log_value, rel, mass_value, event_items) in enumerate(
        zip(cells, evidence_log, relative, surface_mass, event_maps, strict=True)
    ):
        cell_records.append(
            {
                "id": str(cell["id"]),
                "latitude_deg": float(cell["position"]["latitude"]),
                "longitude_deg": float(cell["position"]["longitude"]),
                "evidence_log_likelihood": log_value if math.isfinite(log_value) else None,
                "relative_log_likelihood": log_value - maximum
                if math.isfinite(log_value)
                else None,
                "relative_likelihood": rel,
                "diagnostic_uniform_cell_mass": mass_value,
                "source_prior_weight_removed": float(cell["prior_weight"]),
                "status": cell.get("status", "supported"),
                "termination_reason_fractions": {
                    reason: float(
                        cell.get("termination_reason_fractions", {}).get(reason, 0.0)
                    )
                    for reason in TERMINATION_REASONS
                },
                "event_effective_sample_size": {
                    event: float(item["effective_sample_size"])
                    for event, item in sorted(event_items.items())
                },
                "conditional_isotope_log_compatibility": cell.get(
                    "conditional_isotope_log_compatibility"
                ),
            }
        )

    return {
        "id": specification["id"],
        "label": specification["label"],
        "color": specification["color"],
        "current_family": source["family"],
        "role": specification["role"],
        "decision": "admissible_conditional_likelihood" if admitted else "diagnostic_only",
        "admitted": admitted,
        "failed_checks": [item["name"] for item in checks if not item["passed"]],
        "conditions": specification["conditions"],
        "limitations": specification["limitations"],
        "source_result": {
            "path": display_path(repo, source_path),
            "sha256": sha256(source_path),
            "seed": int(source["seed"]),
            "particles_per_cell": int(source["particles_per_cell"]),
            "isotope_enabled": bool(source["isotope_enabled"]),
            "run_manifest": {
                "path": display_path(repo, manifest_path),
                "sha256": sha256(manifest_path),
                "executable_sha256": manifest.get("executable_sha256"),
                "config_sha256": manifest.get("config_sha256"),
                "input_sha256": manifest.get("input_sha256", {}),
            }
            if manifest
            else None,
            "runtime": {
                "path": display_path(repo, runtime_path),
                "sha256": sha256(runtime_path),
                "elapsed_seconds": runtime.get("elapsed_seconds"),
                "peak_memory_kib": runtime.get("peak_memory_kib"),
                "simulated_paths": runtime.get("simulated_paths"),
            }
            if runtime
            else None,
        },
        "surface_summary": {
            "cell_count": len(cells),
            "peak_cell_id": str(cells[peak_index]["id"]),
            "peak_latitude_s": latitude_s[peak_index],
            "peak_longitude_e": float(cells[peak_index]["position"]["longitude"]),
            "latitude_s_equal_tail_intervals": {
                str(int(level * 100)): equal_tail(latitude_s, surface_mass, level)
                for level in CONTOUR_LEVELS
            },
        },
        "evidence_scope": {
            "expected_recovery_events": expected_events,
            "represented_recovery_events": actual_events,
            "expected_non_recoveries": expected_non_recoveries,
            "represented_non_recoveries": actual_non_recoveries,
        },
        "diagnostics": {
            "checks": checks,
            "surface_weighted_termination_reason_fractions": weighted_termination,
            "surface_weighted_out_of_support_fraction": out_of_support,
            "surface_mass_with_every_recovery_ess_at_least_threshold": ess_mass,
            "event_arrival_effective_sample_size": event_diagnostics,
            "isotope_path_classification_counts": isotope_counts,
            "stability": stability,
            "predictive_validation": validation,
        },
        "cells": cell_records,
    }


def write_plot(output: Path, families: list[dict]) -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 9,
            "axes.titlesize": 10,
            "axes.labelsize": 9,
            "svg.hashsalt": "mh370-ocean-drift-family-likelihood-handoff",
        }
    )
    figure, axes = plt.subplots(
        len(families), 1, figsize=(8.0, 2.9 * len(families)), sharex=True,
        constrained_layout=True,
    )
    if len(families) == 1:
        axes = [axes]
    for axis, family in zip(axes, families, strict=True):
        ordered = sorted(family["cells"], key=lambda item: -item["latitude_deg"])
        latitude_s = [-item["latitude_deg"] for item in ordered]
        likelihood = [item["relative_likelihood"] for item in ordered]
        out_support = [
            sum(item["termination_reason_fractions"][reason] for reason in OUT_OF_SUPPORT_REASONS)
            for item in ordered
        ]
        axis.plot(latitude_s, likelihood, color=family["color"], linewidth=1.8)
        axis.fill_between(latitude_s, likelihood, color=family["color"], alpha=0.16)
        axis.set_ylim(0.0, 1.05)
        axis.set_ylabel("Relative likelihood", labelpad=11)
        axis.grid(True, color="#D8DEE8", linewidth=0.6, alpha=0.8)
        status = family["decision"].replace("_", " ").upper()
        axis.set_title(f"{family['label']}  ·  {status}", loc="left", fontweight="bold")
        secondary = axis.twinx()
        secondary.plot(
            latitude_s,
            out_support,
            color="#6B7280",
            linewidth=1.0,
            linestyle="--",
            label="out-of-support termination",
        )
        secondary.set_ylim(0.0, 1.05)
        secondary.set_ylabel("Out-of-support fraction", color="#4B5563", labelpad=11)
        secondary.tick_params(axis="y", colors="#4B5563")
        peak = family["surface_summary"]["peak_latitude_s"]
        axis.axvline(peak, color=family["color"], linewidth=0.8, linestyle=":")
        axis.text(
            0.99,
            0.92,
            "No family pooling",
            transform=axis.transAxes,
            ha="right",
            va="top",
            color="#6B7280",
            fontsize=8,
        )
    axes[-1].set_xlabel("Seventh-arc source latitude (°S)", labelpad=8)
    figure.suptitle(
        "MH370 ocean-drift family likelihoods and field-support diagnostics",
        fontsize=12,
        fontweight="bold",
    )
    figure.savefig(
        output.with_suffix(".png"),
        dpi=240,
        metadata={"Software": "MH370 ocean-drift likelihood handoff"},
    )
    figure.savefig(output.with_suffix(".svg"), metadata={"Date": None})
    with PdfPages(
        output.with_suffix(".pdf"),
        metadata={
            "Title": "MH370 family-specific ocean-drift likelihood diagnostics",
            "Creator": "MH370 ocean-drift likelihood handoff",
            "CreationDate": None,
            "ModDate": None,
        },
    ) as pdf:
        pdf.savefig(figure)
    plt.close(figure)


def write_csv(path: Path, families: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(
            stream,
            fieldnames=(
                "family_id",
                "decision",
                "cell_id",
                "latitude_deg",
                "longitude_deg",
                "evidence_log_likelihood",
                "relative_log_likelihood",
                "relative_likelihood",
                "diagnostic_uniform_cell_mass",
            ),
        )
        writer.writeheader()
        for family in families:
            for cell in family["cells"]:
                writer.writerow(
                    {
                        "family_id": family["id"],
                        "decision": family["decision"],
                        "cell_id": cell["id"],
                        "latitude_deg": cell["latitude_deg"],
                        "longitude_deg": cell["longitude_deg"],
                        "evidence_log_likelihood": cell["evidence_log_likelihood"],
                        "relative_log_likelihood": cell["relative_log_likelihood"],
                        "relative_likelihood": cell["relative_likelihood"],
                        "diagnostic_uniform_cell_mass": cell[
                            "diagnostic_uniform_cell_mass"
                        ],
                    }
                )


def write_html(path: Path, handoff: dict, svg_path: Path) -> None:
    embedded = json.dumps(handoff, separators=(",", ":")).replace("</", "<\\/")
    rows = "".join(
        "<tr>"
        f"<td><span class='swatch' style='background:{family['color']}'></span>{family['label']}</td>"
        f"<td class='decision'>{family['decision'].replace('_', ' ')}</td>"
        f"<td>{', '.join(family['failed_checks']) or 'none'}</td>"
        f"<td>{family['surface_summary']['peak_latitude_s']:.2f}°S</td>"
        "</tr>"
        for family in handoff["families"]
    )
    svg = svg_path.read_text(encoding="utf-8")
    svg = svg[svg.index("<svg") :]
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MH370 ocean-drift family handoff</title>
<style>
:root {{ color-scheme: light; --navy:#17365d; --ink:#172033; --muted:#5b6474; --line:#d7dee9; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; font-family:Inter,ui-sans-serif,system-ui,-apple-system,sans-serif; color:var(--ink); background:#f5f7fa; }}
main {{ max-width:1120px; margin:0 auto; padding:22px; }}
h1 {{ color:var(--navy); font-size:24px; margin:0 0 7px; }}
p {{ color:var(--muted); line-height:1.5; }}
.notice {{ background:#fff4dd; border-left:5px solid #d97706; padding:12px 15px; border-radius:5px; color:#6b4500; }}
.card {{ background:white; border:1px solid var(--line); border-radius:10px; margin:16px 0; padding:17px; box-shadow:0 2px 7px #20304a0d; }}
table {{ width:100%; border-collapse:collapse; font-size:14px; }}
th,td {{ padding:9px 8px; border-bottom:1px solid var(--line); text-align:left; vertical-align:top; }}
th {{ color:var(--navy); }}
.swatch {{ display:inline-block; width:11px; height:11px; border-radius:50%; margin-right:7px; }}
.decision {{ font-weight:700; text-transform:uppercase; }}
.plot svg {{ width:100%; height:auto; }}
.query-grid {{ display:grid; grid-template-columns:1.5fr 1fr 1fr auto; gap:9px; align-items:end; }}
label {{ display:block; color:var(--muted); font-size:12px; margin-bottom:4px; }}
select,input,button {{ width:100%; padding:9px; border:1px solid #b7c0ce; border-radius:6px; background:white; }}
button {{ background:var(--navy); color:white; border-color:var(--navy); cursor:pointer; }}
#query-result {{ margin-top:12px; padding:12px; background:#f5f7fa; border-radius:6px; min-height:46px; }}
code {{ font-family:ui-monospace,SFMono-Regular,Menlo,monospace; font-size:12px; }}
@media (max-width:700px) {{ .query-grid {{ grid-template-columns:1fr; }} main {{ padding:12px; }} }}
</style>
</head>
<body><main>
<h1>Ocean-drift likelihood admission handoff</h1>
<p>Family-specific seventh-arc likelihoods. Source priors are removed before query; current families are never averaged.</p>
<div class="notice"><strong>Admission status:</strong> A diagnostic-only surface must not update the integrated flight posterior.</div>
<section class="card"><table><thead><tr><th>Family</th><th>Decision</th><th>Failed checks</th><th>Diagnostic peak</th></tr></thead><tbody>{rows}</tbody></table></section>
<section class="card plot">{svg}</section>
<section class="card">
<h2>Common query interface</h2>
<p>Nearest WGS84 great-circle source cell, maximum {handoff['query_contract']['maximum_nearest_cell_distance_nm']:.1f} NM. Beyond that distance the result is <code>out_of_support</code>, never zero or neutral evidence.</p>
<div class="query-grid">
<div><label for="family">Family</label><select id="family"></select></div>
<div><label for="latitude">Latitude (°)</label><input id="latitude" type="number" step="0.01" value="-34"></div>
<div><label for="longitude">Longitude (°E)</label><input id="longitude" type="number" step="0.01" value="94"></div>
<div><button id="query">Query</button></div>
</div>
<div id="query-result">Choose a family and position.</div>
</section>
</main>
<script>
const handoff={embedded};
const familySelect=document.getElementById('family');
for(const family of handoff.families){{const option=document.createElement('option');option.value=family.id;option.textContent=family.label;familySelect.appendChild(option);}}
function haversineNm(a,b,c,d){{const r=3440.065,rad=Math.PI/180;const p1=a*rad,p2=c*rad,dp=(c-a)*rad,dl=(d-b)*rad;const h=Math.sin(dp/2)**2+Math.cos(p1)*Math.cos(p2)*Math.sin(dl/2)**2;return 2*r*Math.asin(Math.sqrt(Math.min(1,h)));}}
document.getElementById('query').addEventListener('click',()=>{{
 const family=handoff.families.find(item=>item.id===familySelect.value);
 const latitude=Number(document.getElementById('latitude').value),longitude=Number(document.getElementById('longitude').value);
 let best=null,distance=Infinity;for(const cell of family.cells){{const value=haversineNm(latitude,longitude,cell.latitude_deg,cell.longitude_deg);if(value<distance){{distance=value;best=cell;}}}}
 const target=document.getElementById('query-result');
 if(!Number.isFinite(latitude)||!Number.isFinite(longitude)){{target.textContent='Enter finite coordinates.';return;}}
 if(distance>handoff.query_contract.maximum_nearest_cell_distance_nm){{target.innerHTML=`<strong>out_of_support</strong> · nearest cell ${{best.id}} is ${{distance.toFixed(1)}} NM away · no likelihood returned`;return;}}
 target.innerHTML=`<strong>${{family.decision}}</strong> · cell ${{best.id}} · ${{distance.toFixed(1)}} NM · relative likelihood ${{best.relative_likelihood.toPrecision(5)}} · relative log-likelihood ${{best.relative_log_likelihood.toFixed(4)}}`;
}});
</script></body></html>"""
    path.write_text(html, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--specification", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    repo = Path(__file__).resolve().parents[3]
    specification_path = arguments.specification.resolve()
    specification = json.loads(specification_path.read_text(encoding="utf-8"))
    thresholds = specification["admission_thresholds"]
    families = [
        summarize_family(repo, family, thresholds)
        for family in specification["families"]
    ]

    output = arguments.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    handoff = {
        "schema": "mh370-ocean-drift-family-likelihood-handoff-v1",
        "title": specification["title"],
        "family_combination": "prohibited_without_out_of_sample_estimated_model_weights",
        "query_contract": {
            "coordinate_reference": "WGS84 latitude/longitude degrees",
            "algorithm": "nearest source cell by great-circle distance",
            "maximum_nearest_cell_distance_nm": thresholds[
                "maximum_query_distance_nm"
            ],
            "source_prior_removed": True,
            "returned_fields": [
                "evidence_log_likelihood",
                "relative_log_likelihood",
                "relative_likelihood",
            ],
            "out_of_support": {
                "status": "out_of_support",
                "likelihood": None,
                "required_behavior": "error; do not extrapolate and do not treat as zero or neutral current",
            },
            "admission_rule": "Only admissible_conditional_likelihood families may update the integrated estimator.",
        },
        "admission_thresholds": thresholds,
        "specification": {
            "path": display_path(repo, specification_path),
            "sha256": sha256(specification_path),
        },
        "families": families,
    }

    json_path = output / "ocean-drift-family-likelihoods.json"
    csv_path = output / "ocean-drift-family-likelihoods.csv"
    plot_base = output / "ocean-drift-family-likelihoods"
    json_path.write_text(json.dumps(handoff, indent=2) + "\n", encoding="utf-8")
    write_csv(csv_path, families)
    write_plot(plot_base, families)
    write_html(output / "index.html", handoff, plot_base.with_suffix(".svg"))

    artifacts = [
        json_path,
        csv_path,
        plot_base.with_suffix(".png"),
        plot_base.with_suffix(".svg"),
        plot_base.with_suffix(".pdf"),
        output / "index.html",
    ]
    hashes = {
        display_path(repo, path): sha256(path)
        for path in artifacts
    }
    (output / "artifact-sha256.json").write_text(
        json.dumps(
            {
                "schema": "mh370-artifact-sha256-v1",
                "artifacts": hashes,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
