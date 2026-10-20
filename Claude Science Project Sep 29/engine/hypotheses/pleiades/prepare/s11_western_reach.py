"""Brief section 11: is the western lobe of the Pleiades-conditioned source region flight-reachable?

PROVISIONAL. Inputs and their limits:

* Core posterior: the pooled 0.25 deg map in results/no-exhaustion-prior-summary.json. It is the
  particle position at the run's stop epoch m0019b (00:19:37), NOT the impact. The run fails
  split-half (0.9020 against the 0.924 floor), and per-replicate final.npy files are not
  available, so no replicate spread is computed here.
* Descent: not modelled. This module does not own it. A declared descent reach R is swept and a
  uniform-disk kernel of radius R stands in for end-of-flight's impact distribution. 103.4 NM is
  the still-air energy-height best-glide bound from 35,000 ft quoted in the end-of-flight brief; it
  is a support bound, not a distribution.
* H transport compatibility: the prior work's equal-prior three-family mixture grid
  (model-averaged-impact-density.csv), 5,289 release cells, released 00:19 on 8 Mar, observed
  23 Mar. Built with an unnormalised 10 km kernel (brief section 9). It locates the lobe; it is not
  this module's likelihood. Per-family cell values are not archived, only the mixture.
* Searched areas are NOT applied (searched-areas module owns them).

Usage: python s11_western_reach.py <path to 'Claude Science Project Sep 29'> <path to archive outputs dir> <outdir>
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

R_NM = [7.5, 15.0, 30.0, 45.0, 60.0, 80.0, 103.4]  # 7.5 NM ~ half a map cell: "on the arc"
NM_KM = 1.852
EARTH_R_NM = 6371.0088 / NM_KM
MAP_STEP = 0.25
MAP_LAT0, MAP_LON0 = -50.0, 55.0  # summary.rs: cell = floor((x - x0) / step)
def _hdr90(t):
    return t.in_hpd90.astype(str).str.lower().eq("true").to_numpy()


# The lobe is defined inside the H 90% HDR only: a bare longitude cut also captures the arc itself
# south of ~36.5 S, where most core mass lies, and so does not isolate the lobe.
REGIONS = {
    "all_grid": lambda t: np.ones(len(t), bool),
    "H_hdr90": _hdr90,
    "lobe_hdr90_inside_30nm": lambda t: _hdr90(t) & (t.crossNm.to_numpy() <= -30),  # >= 30 NM inside (NW of) the arc
    "lobe_hdr90_inside_50nm": lambda t: _hdr90(t) & (t.crossNm.to_numpy() <= -50),
    "lobe_hdr90_west_of_91p5E": lambda t: _hdr90(t) & (t.longitude.to_numpy() < 91.5),
    "box_91E_35S": lambda t: (np.abs(t.longitude.to_numpy() - 91.0) <= 0.5) & (np.abs(t.latitude.to_numpy() + 35.0) <= 0.5),
}


def haversine_nm(lat1, lon1, lat2, lon2):
    p1, p2 = np.radians(lat1)[:, None], np.radians(lat2)[None, :]
    dphi = p2 - p1
    dlmb = np.radians(lon2)[None, :] - np.radians(lon1)[:, None]
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlmb / 2) ** 2
    return 2 * EARTH_R_NM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def load(csp29: Path, archive_outputs: Path):
    s = json.loads((csp29 / "results/no-exhaustion-prior-summary.json").read_text())
    case = s["cases"][0]
    assert s["map"]["step"] == MAP_STEP and s["map"]["lat"][0] == MAP_LAT0 and s["map"]["lon"][0] == MAP_LON0
    m = np.asarray(case["map"], float)
    core = pd.DataFrame({
        "lat": MAP_LAT0 + (m[:, 0] + 0.5) * MAP_STEP,
        "lon": MAP_LON0 + (m[:, 1] + 0.5) * MAP_STEP,
        "mass": m[:, 2] * MAP_STEP**2,
    })
    assert abs(core.mass.sum() - 1) < 1e-6, core.mass.sum()
    t = pd.read_csv(archive_outputs / "model-averaged-impact-density.csv")
    assert len(t) == 5289 and abs(t.probabilityMass.sum() - 1) < 1e-9
    return case, core, t


def run(csp29: Path, archive_outputs: Path, out: Path):
    case, core, t = load(csp29, archive_outputs)
    d = haversine_nm(t.latitude.to_numpy(), t.longitude.to_numpy(), core.lat.to_numpy(), core.lon.to_numpy())
    area = t.cellAreaKm2.to_numpy()
    h_mass = t.probabilityMass.to_numpy()
    h_dens = t.densityPerKm2.to_numpy()
    rows, cells = [], {}
    for r in R_NM:
        reach = d <= r
        disk_km2 = np.pi * (r * NM_KM) ** 2
        f = (reach * core.mass.to_numpy()[None, :]).sum(1) / disk_km2  # core impact density /km2
        p_core = f * area  # core impact probability per release cell
        joint = f * h_dens * area
        z = joint.sum()
        w = joint / z if z > 0 else np.zeros_like(joint)
        cells[r] = (p_core, w)
        for name, sel in REGIONS.items():
            k = sel(t)
            rows.append({
                "descent_reach_nm": r,
                "region": name,
                "cells": int(k.sum()),
                "H_transport_mass": float(h_mass[k].sum()),
                "H_mass_unreachable": float(h_mass[k & (f == 0)].sum()),
                "core_impact_mass_in_region": float(p_core[k].sum()),
                "joint_mass_in_region": float(w[k].sum()),
            })
        rows.append({"descent_reach_nm": r, "region": "_core_mass_inside_grid",
                     "core_impact_mass_in_region": float(p_core.sum()),
                     "joint_normaliser_relative": float(z)})
    res = pd.DataFrame(rows)

    # context numbers
    i_box = np.argmin(np.hypot(t.latitude - (-35.0), (t.longitude - 91.0) * np.cos(np.radians(35))))
    lat = core.lat.to_numpy()
    ctx = {
        "core_epoch": "m0019b 00:19:37 (stop epoch; no descent applied)",
        "core_particles_per_replicate": case["particles"],
        "core_split_half_verdict": "FAILS: 0.9020 vs floor 0.924 (results/no-exhaustion-prior-datasheet.md section 3)",
        "core_mass_lat_-36_to_-34": float(core.mass[(lat >= -36) & (lat < -34)].sum()),
        "core_mass_north_of_-35.5": float(core.mass[lat >= -35.5].sum()),
        "core_mass_north_of_-35": float(core.mass[lat >= -35.0].sum()),
        "grid_cell_nearest_35S_91E": {k: (float(v) if isinstance(v, (float, np.floating, int, np.integer)) else str(v))
                                      for k, v in t.iloc[i_box][["id", "latitude", "longitude", "alongNm", "crossNm"]].items()},
        "H_mixture_mode": {"lat": float(t.latitude[t.densityPerKm2.idxmax()]), "lon": float(t.longitude[t.densityPerKm2.idxmax()]),
                           "crossNm": float(t.crossNm[t.densityPerKm2.idxmax()])},
    }
    d_box = haversine_nm(np.array([-35.0]), np.array([91.0]), core.lat.to_numpy(), core.lon.to_numpy())[0]
    ctx["core_0019_mass_within_d_of_35S_91E"] = {f"{dd:g}nm": float(core.mass[d_box <= dd].sum()) for dd in [30, 45, 60, 65, 75, 90, 105, 120]}
    sig = core.mass.to_numpy() >= 1e-4
    ctx["nearest_core_cell_mass_ge_1e-4_to_35S_91E_nm"] = float(d_box[sig].min())
    box = REGIONS["box_91E_35S"](t)
    ctx["box_91E_35S_crossNm_range"] = [float(t.crossNm[box].min()), float(t.crossNm[box].max())]
    for r in R_NM:
        p_core, w = cells[r]
        if w.sum() > 0:
            j = int(np.argmax(w / area))
            ctx[f"joint_mode_R{r}"] = {"lat": float(t.latitude[j]), "lon": float(t.longitude[j]), "crossNm": float(t.crossNm[j])}
    out.mkdir(parents=True, exist_ok=True)
    res.to_csv(out / "s11-western-reach.csv", index=False)
    (out / "s11-western-reach-context.json").write_text(json.dumps(ctx, indent=1))
    return res, ctx, core, t, cells


if __name__ == "__main__":
    run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
