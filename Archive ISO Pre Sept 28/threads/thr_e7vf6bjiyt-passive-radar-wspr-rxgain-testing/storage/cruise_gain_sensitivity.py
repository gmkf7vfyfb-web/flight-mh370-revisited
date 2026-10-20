#!/usr/bin/env python3
"""Level-flight sensitivity for the archived received-power analyses.

This is a read-only post-analysis: it imports the frozen D-0058 machinery and
subsets its input events.  It also summarizes the already-computed D-0045
known-arc metrics over matching flight-state subsets.
"""

from __future__ import annotations

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd


LEGACY = Path(
    "/jackbox/home/.iso/thread-storage/"
    "MH370-legacy-pre-refactor-20260824/analyses"
)
HERE = Path(__file__).resolve().parent
D0058 = LEGACY / "D-0058-explicit-target-eirp-control"
D0045 = LEGACY / "D-0045-known-arc-harp-admission"


def import_d0058():
    source = D0058 / "src/run_blocked_analysis.py"
    spec = importlib.util.spec_from_file_location("d0058_blocked", source)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {source}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


# Event classifications are based on the archived ACARS/ADS-B state audit.
# "Level altitude" permits the 03:29--03:36 heading maneuver; the strict sets
# remove it because bank angle is not observed and was not used in the gain
# lookup.  High cruise additionally removes the level FL276 event at 01:55.
D0058_SETS = {
    "level_altitude_including_turn": [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15],
    "straight_and_level": [0, 4, 5, 6, 7, 8, 9, 10, 15],
    "high_cruise_straight_and_level": [4, 5, 6, 7, 8, 9, 10, 15],
}

D0058_CLASSIFICATION = [
    (0, "MH371", "01:55", 27599.8, -0.6, "include", "level at FL276"),
    (1, "MH371", "03:20", 28517.0, 559.6, "exclude", "climb"),
    (2, "MH371", "03:29", 36094.0, 0.6, "turn_only", "level altitude but turning; state sources conflict"),
    (3, "MH371", "03:35", 36097.0, 0.2, "turn_only", "level altitude but turning"),
    (4, "MH371", "03:59", 38102.0, -0.4, "include", "straight-and-level high cruise"),
    (5, "MH371", "04:29", 39999.0, 1.2, "include", "straight-and-level high cruise"),
    (6, "MH371", "04:55", 39998.0, 0.4, "include", "straight-and-level high cruise"),
    (7, "MH371", "05:10", 39999.0, -0.6, "include", "straight-and-level high cruise"),
    (8, "MH371", "05:29", 40001.0, -0.2, "include", "straight-and-level high cruise"),
    (9, "MH371", "06:09", 39998.0, 0.6, "include", "straight-and-level high cruise"),
    (10, "MH371", "06:48", 40000.0, 0.0, "include", "straight-and-level high cruise"),
    (11, "MH371", "07:58", np.nan, np.nan, "exclude", "post-cruise/descent or ground"),
    (12, "MH371", "08:01", np.nan, np.nan, "exclude", "post-cruise/descent or ground"),
    (13, "MH370", "15:59", 0.0, 0.0, "exclude", "ground/preflight"),
    (14, "MH370", "16:06", 0.0, 0.0, "exclude", "ground/preflight"),
    (15, "MH370", "17:06", 37375.0, 0.0, "include", "level high cruise"),
]

D0045_SETS = {
    "level_altitude_including_turn": [2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 18],
    "straight_and_level": [2, 6, 7, 8, 9, 10, 11, 12, 13, 18],
    "high_cruise_straight_and_level": [6, 7, 8, 9, 10, 11, 12, 13, 18],
}


def exact_one_sided_sign_p(successes: int, trials: int) -> float:
    return sum(math.comb(trials, k) for k in range(successes, trials + 1)) / 2**trials


def summarize_d0045() -> pd.DataFrame:
    metrics = pd.read_csv(D0045 / "outputs/known_arc_model_metrics.csv")
    rows: list[dict[str, object]] = []
    for sample, sequences in D0045_SETS.items():
        subset = metrics.loc[metrics["sequence"].isin(sequences)].copy()
        base = subset.loc[subset["model"] == "bfo_only"].set_index("sequence")
        for model, model_frame in subset.groupby("model"):
            model_frame = model_frame.set_index("sequence").sort_index()
            delta = (
                model_frame["joint_mass_within_100nm_20deg"]
                - base["joint_mass_within_100nm_20deg"]
            )
            nonzero = delta.loc[np.abs(delta) > 1e-15]
            improved = int((nonzero > 0).sum())
            worsened = int((nonzero < 0).sum())
            rows.append(
                {
                    "sample": sample,
                    "model": model,
                    "events": len(model_frame),
                    "map_successes": int(model_frame["joint_map_success_100nm_20deg"].sum()),
                    "mean_position_truth_mass": float(model_frame["position_mass_within_100nm"].mean()),
                    "mean_joint_truth_mass": float(model_frame["joint_mass_within_100nm_20deg"].mean()),
                    "improved_vs_bfo": improved,
                    "worsened_vs_bfo": worsened,
                    "one_sided_sign_p_if_improved": (
                        exact_one_sided_sign_p(improved, len(nonzero))
                        if model != "bfo_only" and len(nonzero)
                        else np.nan
                    ),
                }
            )
    return pd.DataFrame(rows)


def main() -> None:
    module = import_d0058()
    frame = module.load_data()
    selected_configs = [
        config
        for config in module.CONFIGS
        if config.name
        in {
            "gaussian_ou_purge30_primary",
            "gaussian_independent_event_purge30",
            "gaussian_no_time_purge30",
        }
    ]
    comparison_frames: list[pd.DataFrame] = []
    paired_frames: list[pd.DataFrame] = []
    beta_rows: list[dict[str, object]] = []
    sample_rows: list[dict[str, object]] = []
    for sample, events in D0058_SETS.items():
        subset = frame.loc[frame["event"].isin(events)].copy()
        sample_rows.append(
            {
                "sample": sample,
                "events": subset["event"].nunique(),
                "channel_event_means": len(subset),
                "raw_reports": int(subset["raw_rows"].sum()),
                "event_ids": ",".join(str(event) for event in events),
            }
        )
        observation_frames = []
        event_frames = []
        for config in selected_configs:
            for beta in (0.0, 1.0):
                observations, event_results = module.run_blocked_predictions(
                    subset, beta, config
                )
                observation_frames.append(observations)
                event_frames.append(event_results)
        all_observations = pd.concat(observation_frames, ignore_index=True)
        all_events = pd.concat(event_frames, ignore_index=True)
        comparison, paired = module.compare_hypotheses(all_observations, all_events)
        comparison.insert(0, "sample", sample)
        paired.insert(0, "sample", sample)
        comparison_frames.append(comparison)
        paired_frames.append(paired)

        beta_summary, _ = module.fit_continuous_beta(
            subset, module.PRIMARY_CONFIG
        )
        beta_rows.append({"sample": sample, **beta_summary})

    comparisons = pd.concat(comparison_frames, ignore_index=True)
    paired = pd.concat(paired_frames, ignore_index=True)
    beta = pd.DataFrame(beta_rows)
    samples = pd.DataFrame(sample_rows)
    classification = pd.DataFrame(
        D0058_CLASSIFICATION,
        columns=[
            "event",
            "flight",
            "time_utc",
            "altitude_ft",
            "vertical_speed_fpm",
            "classification",
            "reason",
        ],
    )
    arc_summary = summarize_d0045()

    outputs = {
        "cruise_sample_audit.csv": samples,
        "event_flight_state_audit.csv": classification,
        "cruise_blocked_comparison.csv": comparisons,
        "cruise_event_paired_results.csv": paired,
        "cruise_continuous_beta.csv": beta,
        "cruise_known_arc_truth_summary.csv": arc_summary,
    }
    for filename, result in outputs.items():
        result.to_csv(HERE / filename, index=False)

    primary = comparisons.loc[
        comparisons["configuration"] == module.PRIMARY_CONFIG
    ].copy()
    report = {
        "samples": samples.to_dict(orient="records"),
        "primary_blocked_comparison": primary.to_dict(orient="records"),
        "continuous_beta": beta.to_dict(orient="records"),
        "known_arc_truth": arc_summary.to_dict(orient="records"),
    }
    (HERE / "cruise_gain_sensitivity.json").write_text(
        json.dumps(report, indent=2, allow_nan=True), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
