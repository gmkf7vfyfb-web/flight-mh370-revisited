#!/usr/bin/env python3
from pathlib import Path
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl-mh370-pp-chart")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "mh370_pp_descent_climb_sensitivity"

eof = pd.read_csv(OUT / "eof_predictive_summary.csv")
direct = pd.read_csv(OUT / "direct_eof_time_shift.csv")
pp = pd.read_csv(OUT / "pp_manoeuvre_summary.csv")

fig, axes = plt.subplots(1, 2, figsize=(12.6, 5.0))
labels = ["No PP excursion", "PP descent/re-climb", "Full PP branch"]
keys = ["no_pp", "pp_only", "full_pp"]
colours = ["#3B82F6", "#D97706", "#B91C1C"]

med = [float(eof.loc[eof.scenario == k, "median_minutes_after_0011"].iloc[0]) for k in keys]
qlo = [float(eof.loc[eof.scenario == k, "q025_minutes_after_0011"].iloc[0]) for k in keys]
qhi = [float(eof.loc[eof.scenario == k, "q975_minutes_after_0011"].iloc[0]) for k in keys]
for i, colour in enumerate(colours):
    axes[0].errorbar(
        i,
        med[i],
        yerr=[[med[i] - qlo[i]], [qhi[i] - med[i]]],
        fmt="o",
        color=colour,
        elinewidth=4,
        capsize=7,
        ms=8,
        alpha=0.8,
    )
axes[0].axhspan(0, 8, color="#10B981", alpha=0.12, label="00:11–00:19 window")
axes[0].axhline(6.5, color="#111827", ls="--", lw=1.1, label="00:17:30 calibration")
axes[0].set_xticks(range(3), labels, rotation=12, ha="right")
axes[0].set_ylabel("EOF time relative to 00:11 (minutes)")
axes[0].set_title("Predictive timing is broad; centre shifts earlier")
axes[0].grid(axis="y", alpha=0.2)
axes[0].legend(frameon=False, fontsize=8)

fuel = pp[pp.variable == "delta_fuel_t"].set_index("scenario")
for i, (k, colour) in enumerate(zip(["pp_only", "full_pp"], colours[1:])):
    row = fuel.loc[k]
    axes[1].errorbar(i, row["median"], yerr=[[row["median"] - row["q025"]], [row["q975"] - row["median"]]], fmt="o", color=colour, capsize=7, lw=4, ms=8)
axes[1].axhline(0, color="#111827", lw=1)
axes[1].set_xticks([0, 1], ["PP descent/re-climb", "Full PP branch"], rotation=12, ha="right")
axes[1].set_ylabel("Fuel change versus FL340/M0.84 comparator (t)")
axes[1].set_title("Idle descent offsets much of re-climb burn")
axes[1].grid(axis="y", alpha=0.2)

fig.suptitle("Pulau Perak fuel and exhaustion-time sensitivity", fontsize=15)
fig.tight_layout(rect=(0, 0, 1, 0.93))
fig.savefig(OUT / "mh370_pp_fuel_and_eof_sensitivity.png", dpi=220, bbox_inches="tight")
plt.close(fig)
