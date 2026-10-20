#!/usr/bin/env python3
"""Generate the publication controls without inventing an MH370 spatial posterior.

The valid controls are intentionally kept separate:

* truth-separated MH371 BTO+BFO inference, with and without the conditional
  no-gain-precompensation likelihood; and
* early-MH370 received-power forward prediction, calibrated at 16:42 and
  evaluated at the later 16:55 and 17:07 bursts.

The primary blocked gain comparison is also stratified by flight.  Events are
the replicate unit; raw reports are never treated as independent replicates.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import platform
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


BUNDLE = Path(__file__).resolve().parents[1]
REPO = BUNDLE.parents[1]
OUTPUT = BUNDLE / "outputs"
EARLY_CONTROL = BUNDLE / "data" / "early-mh370-forward-power-control.csv"
BLOCKED_EVENTS = OUTPUT / "blocked_event_scores.csv"
BLOCKED_PREDICTIONS = OUTPUT / "blocked_predictions.csv"
HYPOTHESIS_COMPARISON = OUTPUT / "hypothesis_comparison.csv"
MH371_BASELINE = REPO / "runs" / "mh371" / "final-analog-medium-assessment" / "score-summary.json"
MH371_ANTENNA = REPO / "runs" / "mh371" / "conditional-antenna-no-precomp-medium-assessment" / "score-summary.json"
MH371_FULL_PRECOMP = REPO / "runs" / "mh371" / "conditional-antenna-full-precomp-medium-assessment" / "score-summary.json"
SEED = 20260826

EXPECTED_INPUT_HASHES = {
    EARLY_CONTROL: "948bc874e6c144e021d43acd88378983f17baf8a348b2ce7215e706afbb3174d",
    MH371_BASELINE: "c0d9f3ef01febee69ed390a824197c446cd6b9f5c143db36a4bd5844cb9480d1",
    MH371_ANTENNA: "80db54e515a33a4eab4ee253f3a9bfe5571e34f55887e8cc75aa49ec1432ec54",
    BLOCKED_EVENTS: "9c8780d0cd8ff1e2efd19542f6308ede7a014c08c3aee48f89a4442b3a0d6140",
}

REFERENCE = "BTO+BFO / full gain precompensation"
ANTENNA = "BTO+BFO + no gain precompensation"
FULL = "full_gain_precompensation"
NONE = "no_gain_precompensation"
PRIMARY = "gaussian_ou_purge30_primary"

BLUE = "#4C72B0"
PURPLE = "#8C6BB1"
ORANGE = "#D17A43"
GREEN = "#4F9D78"
DARK = "#303030"
LIGHT_GRID = "#E6E8EB"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_frozen_inputs() -> None:
    for path, expected in EXPECTED_INPUT_HASHES.items():
        if not path.is_file():
            raise RuntimeError(f"missing frozen input: {path}")
        actual = sha256(path)
        if actual != expected:
            raise RuntimeError(f"frozen input changed: {path}: {actual}")


def circular_error_deg(left: float, right: float) -> float:
    return abs((left - right + 180.0) % 360.0 - 180.0)


def exact_signflip_p(values: np.ndarray) -> float:
    observed = abs(float(np.mean(values)))
    randomized = (
        abs(float(np.mean(values * np.asarray(signs, dtype=float))))
        for signs in itertools.product((-1.0, 1.0), repeat=len(values))
    )
    return float(
        sum(value >= observed - 1e-14 for value in randomized)
        / (2 ** len(values))
    )


def bootstrap_mean_interval(values: np.ndarray, seed_offset: int) -> tuple[float, float]:
    rng = np.random.default_rng(SEED + seed_offset)
    samples = rng.integers(0, len(values), size=(200_000, len(values)))
    distribution = np.mean(values[samples], axis=1)
    lower, upper = np.quantile(distribution, (0.025, 0.975))
    return float(lower), float(upper)


def load_score(path: Path) -> dict[str, object]:
    package = json.loads(path.read_text(encoding="utf-8"))
    if package.get("schema_version") != "mh370-known-flight-assessment-v2":
        raise RuntimeError(f"unexpected score schema: {path}")
    if package.get("numerically_valid") is not True:
        raise RuntimeError(f"invalid score package: {path}")
    return package


def mh371_comparison() -> pd.DataFrame:
    baseline = load_score(MH371_BASELINE)
    antenna = load_score(MH371_ANTENNA)
    full = load_score(MH371_FULL_PRECOMP)
    for field in ("seeds", "particle_count_per_seed", "truth_sha256"):
        if baseline[field] != antenna[field] or baseline[field] != full[field]:
            raise RuntimeError(f"MH371 endpoint mismatch in {field}")

    identity_fields = (
        "posterior_mean_latitude_deg",
        "posterior_mean_longitude_deg",
        "posterior_mean_error_nm",
        "posterior_mean_ground_track_deg",
        "mass_within_100_nm",
        "truth_hpd_mass",
    )
    baseline_by_key = {
        (row["seed"], row["checkpoint_index"]): row
        for row in baseline["checkpoints"]
    }
    for row in full["checkpoints"]:
        reference = baseline_by_key[(row["seed"], row["checkpoint_index"])]
        for field in identity_fields:
            if not math.isclose(float(row[field]), float(reference[field]), abs_tol=1e-12):
                raise RuntimeError("full-precompensation endpoint is not posterior-identical to baseline")

    rows: list[dict[str, object]] = []
    for label, package in ((REFERENCE, baseline), (ANTENNA, antenna)):
        for item in package["checkpoints"]:
            if int(item["checkpoint_index"]) == 0:
                continue
            rows.append(
                {
                    "model": label,
                    "seed": int(item["seed"]),
                    "checkpoint_index": int(item["checkpoint_index"]),
                    "epoch": str(item["epoch_id"]).replace("mh371_", ""),
                    "position_error_nm": float(item["posterior_mean_error_nm"]),
                    "mass_within_100_nm": float(item["mass_within_100_nm"]),
                    "truth_hpd_mass": float(item["truth_hpd_mass"]),
                    "ground_track_error_deg": circular_error_deg(
                        float(item["posterior_mean_ground_track_deg"]),
                        float(item["truth_ground_track_deg"]),
                    ),
                }
            )
    frame = pd.DataFrame(rows)
    if len(frame) != 24 or frame["seed"].nunique() != 2:
        raise RuntimeError("unexpected MH371 comparison dimensions")
    return frame


def mh371_long_table(frame: pd.DataFrame) -> pd.DataFrame:
    metrics = (
        ("position_error_nm", "lower is better"),
        ("mass_within_100_nm", "higher is better"),
        ("truth_hpd_mass", "lower is better; cumulative mass at truth density"),
        ("ground_track_error_deg", "lower is better; heading-aware ground-track metric"),
    )
    rows: list[dict[str, object]] = []
    for checkpoint, subset in frame.groupby("checkpoint_index", sort=True):
        epoch = str(subset["epoch"].iloc[0])
        for metric, interpretation in metrics:
            values = {
                model: group[metric].to_numpy(float)
                for model, group in subset.groupby("model")
            }
            reference = values[REFERENCE]
            antenna = values[ANTENNA]
            rows.append(
                {
                    "flight": "MH371",
                    "control_kind": "truth-separated spatial posterior",
                    "epoch": epoch,
                    "metric": metric,
                    "paired_seeds": len(reference),
                    "reference_mean": float(reference.mean()),
                    "reference_seed_min": float(reference.min()),
                    "reference_seed_max": float(reference.max()),
                    "no_precomp_mean": float(antenna.mean()),
                    "no_precomp_seed_min": float(antenna.min()),
                    "no_precomp_seed_max": float(antenna.max()),
                    "no_precomp_minus_reference": float(antenna.mean() - reference.mean()),
                    "interpretation": interpretation,
                }
            )
    return pd.DataFrame(rows)


def early_mh370_burst_summary() -> tuple[pd.DataFrame, pd.DataFrame]:
    frame = pd.read_csv(EARLY_CONTROL)
    if len(frame) != 18 or set(frame["burst"]) != {"MH370-1642", "MH370-1656", "MH370-1707"}:
        raise RuntimeError("unexpected early-MH370 control dimensions")
    calibration = frame.loc[frame["calibration_role"].str.contains("calibration")]
    holdout = frame.loc[frame["calibration_role"] == "MH370 forward holdout"].copy()
    if len(calibration) != 6 or len(holdout) != 12:
        raise RuntimeError("early-MH370 chronology changed")

    rows: list[dict[str, object]] = []
    for burst, group in holdout.groupby("burst", sort=True):
        values: dict[str, float | int | str] = {
            "flight": "early MH370",
            "control_kind": "received-power forward holdout; not spatial inference",
            "burst": str(burst).replace("MH370-", ""),
            "channel_event_points": len(group),
            "raw_reports_aggregated": int(group["record_count"].sum()),
        }
        for endpoint, column in (
            ("no_precomp", "residual_no_gain_compensation_db"),
            ("full_precomp", "residual_complete_gain_cancellation_db"),
        ):
            residual = group[column].to_numpy(float)
            values[f"{endpoint}_rmse_db"] = float(np.sqrt(np.mean(np.square(residual))))
            values[f"{endpoint}_mae_db"] = float(np.mean(np.abs(residual)))
            values[f"{endpoint}_mean_residual_db"] = float(np.mean(residual))
        values["rmse_no_minus_full_db"] = float(
            values["no_precomp_rmse_db"] - values["full_precomp_rmse_db"]
        )
        rows.append(values)

    residual_no = holdout["residual_no_gain_compensation_db"].to_numpy(float)
    residual_full = holdout["residual_complete_gain_cancellation_db"].to_numpy(float)
    rows.append(
        {
            "flight": "early MH370",
            "control_kind": "received-power forward holdout; not spatial inference",
            "burst": "pooled_1656_1707",
            "channel_event_points": len(holdout),
            "raw_reports_aggregated": int(holdout["record_count"].sum()),
            "no_precomp_rmse_db": float(np.sqrt(np.mean(np.square(residual_no)))),
            "no_precomp_mae_db": float(np.mean(np.abs(residual_no))),
            "no_precomp_mean_residual_db": float(np.mean(residual_no)),
            "full_precomp_rmse_db": float(np.sqrt(np.mean(np.square(residual_full)))),
            "full_precomp_mae_db": float(np.mean(np.abs(residual_full))),
            "full_precomp_mean_residual_db": float(np.mean(residual_full)),
            "rmse_no_minus_full_db": float(
                np.sqrt(np.mean(np.square(residual_no)))
                - np.sqrt(np.mean(np.square(residual_full)))
            ),
        }
    )
    return frame, pd.DataFrame(rows)


def gain_by_flight() -> tuple[pd.DataFrame, pd.DataFrame]:
    events = pd.read_csv(BLOCKED_EVENTS)
    subset = events.loc[events["configuration"] == PRIMARY].copy()
    pivot = subset.pivot(
        index="held_event",
        columns="hypothesis",
        values=["event_time_utc", "test_points", "log_predictive_density_per_point", "mse_db2"],
    ).dropna()
    rows: list[dict[str, object]] = []
    for event, item in pivot.iterrows():
        event = int(event)
        flight = "MH371" if event <= 12 else "early MH370"
        timestamp = str(item[("event_time_utc", FULL)])
        if event <= 12 and timestamp[11:13] >= "09":
            raise RuntimeError("MH371 event-to-flight chronology mismatch")
        if event >= 13 and timestamp[11:16] not in {"15:59", "16:06", "17:06"}:
            raise RuntimeError("early-MH370 event-to-flight chronology mismatch")
        points = int(float(item[("test_points", FULL)]))
        if points != int(float(item[("test_points", NONE)])):
            raise RuntimeError("endpoint test-point mismatch")
        rows.append(
            {
                "flight": flight,
                "event": event,
                "event_time_utc": timestamp,
                "channel_event_points": points,
                "delta_log_density_per_point_no_minus_full": float(
                    item[("log_predictive_density_per_point", NONE)]
                    - item[("log_predictive_density_per_point", FULL)]
                ),
                "mse_no_precomp_db2": float(item[("mse_db2", NONE)]),
                "mse_full_precomp_db2": float(item[("mse_db2", FULL)]),
            }
        )
    event_frame = pd.DataFrame(rows).sort_values("event")
    if list(event_frame.groupby("flight", sort=False).size()) != [13, 3]:
        raise RuntimeError("unexpected flight-stratified event counts")

    summaries: list[dict[str, object]] = []
    for offset, (flight, group) in enumerate(event_frame.groupby("flight", sort=False), 1):
        delta = group["delta_log_density_per_point_no_minus_full"].to_numpy(float)
        points = group["channel_event_points"].to_numpy(float)
        lower, upper = bootstrap_mean_interval(delta, 100 + offset)
        summaries.append(
            {
                "flight": flight,
                "events": len(group),
                "channel_event_points": int(points.sum()),
                "mean_event_log_density_difference_per_point_no_minus_full": float(delta.mean()),
                "bootstrap_95_lower": lower,
                "bootstrap_95_upper": upper,
                "descriptive_exact_signflip_p": exact_signflip_p(delta),
                "events_favor_no_precomp": int(np.count_nonzero(delta > 0)),
                "events_favor_full_precomp": int(np.count_nonzero(delta < 0)),
                "pooled_point_rmse_no_precomp_db": float(
                    np.sqrt(np.sum(group["mse_no_precomp_db2"] * points) / points.sum())
                ),
                "pooled_point_rmse_full_precomp_db": float(
                    np.sqrt(np.sum(group["mse_full_precomp_db2"] * points) / points.sum())
                ),
            }
        )

    combined = pd.read_csv(HYPOTHESIS_COMPARISON)
    combined = combined.loc[combined["configuration"] == PRIMARY].iloc[0]
    summaries.append(
        {
            "flight": "combined (descriptive only)",
            "events": int(combined["paired_events"]),
            "channel_event_points": int(combined["test_points_per_hypothesis"]),
            "mean_event_log_density_difference_per_point_no_minus_full": float(combined["mean_event_lpd_no_minus_full"]),
            "bootstrap_95_lower": float(combined["lpd_bootstrap_95_lower"]),
            "bootstrap_95_upper": float(combined["lpd_bootstrap_95_upper"]),
            "descriptive_exact_signflip_p": float(combined["lpd_exact_signflip_two_sided_p"]),
            "events_favor_no_precomp": int(combined["events_lpd_favor_no"]),
            "events_favor_full_precomp": int(combined["events_lpd_favor_full"]),
            "pooled_point_rmse_no_precomp_db": float(combined["point_rmse_no_db"]),
            "pooled_point_rmse_full_precomp_db": float(combined["point_rmse_full_db"]),
        }
    )
    return event_frame, pd.DataFrame(summaries)


def style_axis(ax: plt.Axes) -> None:
    ax.grid(axis="y", color=LIGHT_GRID, linewidth=0.7)
    ax.spines[["top", "right"]].set_visible(False)
    ax.tick_params(labelsize=8.5)


def save_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(OUTPUT / f"{stem}.png", dpi=300, facecolor="white")
    fig.savefig(
        OUTPUT / f"{stem}.pdf",
        facecolor="white",
        metadata={"Creator": "MH370 publication control generator", "CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def make_mh371_figure(frame: pd.DataFrame) -> None:
    means = frame.groupby(["model", "checkpoint_index", "epoch"], as_index=False).mean(numeric_only=True)
    metrics = (
        ("position_error_nm", "Posterior-mean position error (NM)", "lower is better"),
        ("mass_within_100_nm", "Posterior mass within 100 NM", "higher is better"),
        ("truth_hpd_mass", "Truth HPD mass", "lower is better"),
        ("ground_track_error_deg", "Posterior-mean ground-track error (°)", "lower is better"),
    )
    fig, axes = plt.subplots(2, 2, figsize=(10.4, 7.0), sharex=True)
    for ax, (metric, ylabel, direction) in zip(axes.flat, metrics):
        for model, color, marker in ((REFERENCE, DARK, "o"), (ANTENNA, PURPLE, "s")):
            group = means.loc[means["model"] == model].sort_values("checkpoint_index")
            ax.plot(group["epoch"], group[metric], color=color, marker=marker, linewidth=1.6, markersize=4.5, label=model)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.text(0.98, 0.95, direction, transform=ax.transAxes, ha="right", va="top", fontsize=7.8, color="#666666")
        style_axis(ax)
    position_values = means["position_error_nm"].to_numpy(dtype=float)
    position_span = float(position_values.max() - position_values.min())
    axes[0, 0].set_ylim(0.0, float(position_values.max()) + max(1.0, 0.30 * position_span))
    axes[0, 0].legend(frameon=True, facecolor="white", framealpha=1.0, edgecolor="none", fontsize=8, loc="upper left")
    for ax in axes[1, :]:
        ax.set_xlabel("Held-back MH371 epoch (UTC)", fontsize=9)
    fig.suptitle("MH371 truth-separated posterior: medium-BFO baseline versus conditional antenna endpoint", x=0.06, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.06, 0.93, "Means across two frozen 12,000-particle seeds; all non-antenna settings fixed. Ground track is the available heading-aware posterior metric.", fontsize=8.5)
    fig.text(0.06, 0.015, "Held-back ACARS states enter scoring only. Seed spread is deterministic numerical sensitivity, not an independent-flight confidence interval.", fontsize=7.5, color="#555555")
    fig.tight_layout(rect=(0.04, 0.05, 0.99, 0.91))
    save_figure(fig, "figure_4_mh371_spatial_endpoint_comparison")


def make_early_figure(raw: pd.DataFrame, summary: pd.DataFrame) -> None:
    holdout = summary.loc[summary["burst"] != "pooled_1656_1707"].copy()
    holdout["label"] = holdout["burst"].map({"1656": "16:55–16:56", "1707": "17:07"})
    x = np.arange(len(holdout))
    width = 0.34
    fig, (ax, note) = plt.subplots(1, 2, figsize=(10.4, 4.8), gridspec_kw={"width_ratios": [1.55, 1.0]})
    ax.bar(x - width / 2, holdout["full_precomp_rmse_db"], width, color="#B8BDC7", label="Full gain precompensation")
    ax.bar(x + width / 2, holdout["no_precomp_rmse_db"], width, color=PURPLE, label="No gain precompensation")
    ax.set_xticks(x, holdout["label"])
    ax.set_ylabel("Received-power RMSE across channel-event points (dB)", fontsize=9)
    ax.set_xlabel("Forward-held burst (UTC)")
    style_axis(ax)
    pooled = summary.loc[summary["burst"] == "pooled_1656_1707"].iloc[0]
    ax.text(0.02, 0.97, f"Pooled 12 channel-event points\nno-precomp {pooled['no_precomp_rmse_db']:.3f} dB\nfull-precomp {pooled['full_precomp_rmse_db']:.3f} dB", transform=ax.transAxes, va="top", fontsize=8.2, bbox={"facecolor": "white", "edgecolor": "#CCCCCC", "alpha": 0.9})
    ax.legend(frameon=False, fontsize=8, loc="lower right")

    note.axis("off")
    note.text(0.0, 0.96, "Chronology", fontsize=11, fontweight="bold")
    note.text(0.0, 0.78, "16:42", fontsize=10, color=DARK, fontweight="bold")
    note.text(0.24, 0.78, "6 channel-event points set one\nflight-wide offset for each endpoint", fontsize=8.2, va="center")
    note.annotate("", xy=(0.10, 0.51), xytext=(0.10, 0.68), arrowprops={"arrowstyle": "->", "color": "#777777"})
    note.text(0.0, 0.42, "16:55 and 17:07", fontsize=10, color=PURPLE, fontweight="bold")
    note.text(0.0, 0.29, "12 later channel-event points are forward holdouts.\nKnown position and ground track are used only for\nreceived-power prediction, not localization.", fontsize=8.1, va="top")
    note.text(0.0, 0.02, "Two bursts are the replicate units; repeated raw reports\nare aggregated. Ground track substitutes for true heading.", fontsize=7.5, color="#555555")
    fig.suptitle("Early-MH370 received-power control: calibration then forward holdout", x=0.06, y=0.98, ha="left", fontsize=12.5, fontweight="bold")
    fig.text(0.06, 0.91, "Closest valid alternative to a spatial posterior; this figure does not estimate position.", fontsize=8.5)
    fig.subplots_adjust(left=0.11, right=0.98, bottom=0.16, top=0.77, wspace=0.16)
    save_figure(fig, "figure_5_early_mh370_forward_power_control")


def make_gain_figure(events: pd.DataFrame, summary: pd.DataFrame) -> None:
    fig = plt.figure(figsize=(10.4, 7.0))
    grid = fig.add_gridspec(2, 2, height_ratios=(1.55, 1.0))
    axes = [fig.add_subplot(grid[0, 0]), fig.add_subplot(grid[0, 1])]
    for ax, flight in zip(axes, ("MH371", "early MH370")):
        group = events.loc[events["flight"] == flight].copy()
        values = group["delta_log_density_per_point_no_minus_full"].to_numpy(float)
        colors = np.where(values >= 0, BLUE, ORANGE)
        ax.bar(np.arange(len(group)), values, color=colors, width=0.72)
        ax.axhline(0, color=DARK, linewidth=0.8)
        labels = pd.to_datetime(group["event_time_utc"]).dt.strftime("%H:%M")
        ax.set_xticks(np.arange(len(group)), labels, rotation=50, ha="right")
        ax.set_title(f"{flight}: {len(group)} held-out events", loc="left", fontsize=10.5, fontweight="bold")
        ax.set_ylabel("Log-density difference per channel-event point\nno precomp − full precomp", fontsize=8.5)
        style_axis(ax)

    forest = fig.add_subplot(grid[1, :])
    ordered = summary.set_index("flight").loc[["MH371", "early MH370", "combined (descriptive only)"]].reset_index()
    y = np.arange(len(ordered))[::-1]
    mean = ordered["mean_event_log_density_difference_per_point_no_minus_full"].to_numpy(float)
    lower = mean - ordered["bootstrap_95_lower"].to_numpy(float)
    upper = ordered["bootstrap_95_upper"].to_numpy(float) - mean
    forest.errorbar(mean, y, xerr=np.vstack((lower, upper)), fmt="o", color=DARK, ecolor="#777777", capsize=4)
    forest.axvline(0, color=DARK, linewidth=0.8)
    labels = [f"{row.flight}  (n={int(row.events)} events; p={row.descriptive_exact_signflip_p:.3f})" for row in ordered.itertuples()]
    forest.set_yticks(y, labels)
    forest.set_xlabel("Mean held-out log-density difference per point (event-bootstrap interval)\nnegative favors full precompensation; positive favors no precompensation")
    forest.grid(axis="x", color=LIGHT_GRID, linewidth=0.7)
    forest.spines[["top", "right", "left"]].set_visible(False)
    fig.suptitle("Gain-hypothesis prediction is not stable between known-flight controls", x=0.06, ha="left", fontsize=13, fontweight="bold")
    fig.text(0.06, 0.93, "Gaussian OU whole-event holdout with 30-minute purge; events/bursts, not raw reports, are the replicate unit.", fontsize=8.7)
    fig.text(0.98, 0.015, "Per-flight p-values are descriptive: epochs and overlapping training sets are dependent.", ha="right", fontsize=7.6, color="#555555")
    fig.tight_layout(rect=(0.04, 0.06, 0.99, 0.91))
    save_figure(fig, "figure_6_gain_hypothesis_by_flight")


def write_summary(mh371: pd.DataFrame, early: pd.DataFrame, gain: pd.DataFrame) -> None:
    terminal = mh371.loc[mh371["checkpoint_index"] == mh371["checkpoint_index"].max()]
    terminal_means = terminal.groupby("model").mean(numeric_only=True)
    pooled = early.loc[early["burst"] == "pooled_1656_1707"].iloc[0]
    combined = gain.loc[gain["flight"] == "combined (descriptive only)"].iloc[0]
    by_flight = gain.set_index("flight")
    text = f"""# Publication controls for the antenna-gain hypothesis

## Outcome

No scientifically defensible early-MH370 spatial posterior can be generated
from the present inputs. The requested 16:42 state is in climb at about 1,700
ft; the canonical known-flight dynamics and weather fixtures do not cover that
climb regime or 16–17 UTC, and the retained ADS-B control supplies ground track
rather than true heading. The known positions also cannot be used both to
construct per-arc candidate clouds and to claim a truth-separated trajectory
test. No 18:25 state is treated as observed truth.

The closest honest early-MH370 control is therefore the generated forward
received-power holdout: six channel-event points at 16:42 calibrate one common
offset per endpoint, then twelve channel-event points in the 16:55 and 17:07
bursts are predicted. Its pooled RMSE is {pooled['no_precomp_rmse_db']:.3f} dB
for no precompensation and {pooled['full_precomp_rmse_db']:.3f} dB for full
precompensation. The two bursts, not the repeated reports, are the replicate
units. This is not spatial inference.

The valid MH371 truth-separated spatial control keeps the medium-BFO model and
all non-antenna settings fixed. At the terminal 06:48 checkpoint, the
two-seed mean posterior-position error changes from
{terminal_means.loc[REFERENCE, 'position_error_nm']:.2f} NM to
{terminal_means.loc[ANTENNA, 'position_error_nm']:.2f} NM; mean mass within
100 NM changes from {terminal_means.loc[REFERENCE, 'mass_within_100_nm']:.4f}
to {terminal_means.loc[ANTENNA, 'mass_within_100_nm']:.4f}; and mean truth HPD
mass changes from {terminal_means.loc[REFERENCE, 'truth_hpd_mass']:.4f} to
{terminal_means.loc[ANTENNA, 'truth_hpd_mass']:.4f}. Lower truth HPD mass is
better; the endpoint does not improve that terminal calibration metric.

## Detectability boundary

The primary blocked comparison remains {combined['mean_event_log_density_difference_per_point_no_minus_full']:+.4f}
log-density units per point, with 95% event-bootstrap interval
[{combined['bootstrap_95_lower']:+.4f}, {combined['bootstrap_95_upper']:+.4f}]
and descriptive sign-flip p={combined['descriptive_exact_signflip_p']:.4f}.
Separated by flight, MH371 gives
{by_flight.loc['MH371', 'mean_event_log_density_difference_per_point_no_minus_full']:+.4f}
over {int(by_flight.loc['MH371', 'events'])} events, whereas early MH370 gives
{by_flight.loc['early MH370', 'mean_event_log_density_difference_per_point_no_minus_full']:+.4f}
over only {int(by_flight.loc['early MH370', 'events'])} events. The early-MH370
forward construction reverses direction again. The effect is therefore not
stably or transportably detected in the available controls.

## Recommended placement

- Main paper: `figure_6_gain_hypothesis_by_flight` with its flight-stratified
  table. It directly supports the boundary that detectability is unstable.
- Supplement: `figure_4_mh371_spatial_endpoint_comparison` and the existing
  MH371 posterior density panels, plus their long-form metric table.
- Supplement or methods: `figure_5_early_mh370_forward_power_control`, clearly
  labelled as a forward power holdout and not a position estimate.

All figures are generated as 300-dpi PNG and vector PDF. Seed ranges in the
MH371 table are numerical-replication sensitivity, not independent-aircraft
confidence intervals. Event-bootstrap intervals and sign-flip p-values are
descriptive because training sets overlap and epoch exchangeability is not
established.
"""
    (OUTPUT / "PUBLICATION-CONTROLS.md").write_text(text, encoding="utf-8")


def write_manifest(output_names: list[str]) -> None:
    script_path = Path(__file__).resolve()
    manifest = {
        "schema_version": 1,
        "analysis": "known-flight antenna publication controls",
        "status": "complete_with_early_mh370_spatial_blocker",
        "seed": SEED,
        "software": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "matplotlib": matplotlib.__version__,
        },
        "code": {"path": str(script_path.relative_to(REPO)), "sha256": sha256(script_path)},
        "inputs": {
            str(path.relative_to(REPO)): sha256(path)
            for path in (
                EARLY_CONTROL,
                BLOCKED_EVENTS,
                BLOCKED_PREDICTIONS,
                HYPOTHESIS_COMPARISON,
                MH371_BASELINE,
                MH371_ANTENNA,
                MH371_FULL_PRECOMP,
            )
        },
        "outputs": {
            name: {"sha256": sha256(OUTPUT / name), "bytes": (OUTPUT / name).stat().st_size}
            for name in output_names
        },
        "scientific_boundary": [
            "early MH370 is a forward received-power holdout, not spatial inference",
            "events or bursts are replicate units; raw reports are aggregated",
            "no 18:25 state is treated as observed truth",
            "gain endpoint preference is not stable across flights or validation constructions",
        ],
    }
    (OUTPUT / "publication_controls_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    validate_frozen_inputs()
    mh371 = mh371_comparison()
    mh371_table = mh371_long_table(mh371)
    early_raw, early_summary = early_mh370_burst_summary()
    gain_events, gain_summary = gain_by_flight()

    mh371_table.to_csv(OUTPUT / "mh371_spatial_endpoint_comparison.csv", index=False)
    early_summary.to_csv(OUTPUT / "early_mh370_forward_power_burst_summary.csv", index=False)
    gain_events.to_csv(OUTPUT / "gain_hypothesis_event_differences_by_flight.csv", index=False)
    gain_summary.to_csv(OUTPUT / "gain_hypothesis_summary_by_flight.csv", index=False)
    make_mh371_figure(mh371)
    make_early_figure(early_raw, early_summary)
    make_gain_figure(gain_events, gain_summary)
    write_summary(mh371, early_summary, gain_summary)

    outputs = [
        "mh371_spatial_endpoint_comparison.csv",
        "early_mh370_forward_power_burst_summary.csv",
        "gain_hypothesis_event_differences_by_flight.csv",
        "gain_hypothesis_summary_by_flight.csv",
        "figure_4_mh371_spatial_endpoint_comparison.png",
        "figure_4_mh371_spatial_endpoint_comparison.pdf",
        "figure_5_early_mh370_forward_power_control.png",
        "figure_5_early_mh370_forward_power_control.pdf",
        "figure_6_gain_hypothesis_by_flight.png",
        "figure_6_gain_hypothesis_by_flight.pdf",
        "PUBLICATION-CONTROLS.md",
    ]
    write_manifest(outputs)


if __name__ == "__main__":
    main()
