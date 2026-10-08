"""Deliverable 1: two-dimensional tension between H and the unconditional posterior. PROVISIONAL.

Reported together, always (brief section 2):
  1. evidence ratio  R = P(D_H | flight posterior) / P(D_H | flat impact prior over the source grid)
                       = A * sum_s p_core(s) * dens_H(s)          (Bayes ratio; A = grid area)
     R < 1: the flight posterior puts impacts where the Pleiades positions are LESS compatible than
     a flat prior would. It depends on the declared prior volume A and is quoted with it.
  2. two-way 90% HDR overlap: unconditional mass inside the conditional's HDR, and conditional mass
     inside the unconditional's HDR (two numbers; not symmetric).
  3. mode displacement (NM), plus mean-position displacement as a steadier companion.
  Also: suspiciousness ln S = ln R - ln I (Handley & Lemos 2019, PRD 100 023512), with
  ln I = D_KL(uncond) + D_KL(H) - D_KL(cond) against the same flat prior. ln S is designed to cancel
  the prior volume that R depends on; ln S < 0 indicates tension. No p-value is attached: its
  Gaussian calibration does not hold for these truncated, non-Gaussian fields.

Unconditional = core posterior at 00:19:37 (no-exhaustion-prior pooled 0.25 deg map, which FAILS
split-half 0.9020 vs 0.924) spread by a declared descent reach R (uniform disk; end of flight owns the
real kernel). Each 0.25 deg core cell is subsampled n x n before the disk is applied so the kernel
does not inherit the histogram's blockiness; n = 1 is run as a check.
H = the prior work's equal-prior three-family mixture grid (unnormalised 10 km kernel, brief section
9; only the mixture's per-cell values were archived). Conditional = unconditional x H, on the grid.
Both are truncated to the grid (+-100 NM, along-arc span of the grid); the core mass outside it is
reported.

Usage: python d1_tension.py <csp29 dir> <archive outputs dir> <outdir>
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from s11_western_reach import NM_KM, haversine_nm, load  # noqa: E402

R_NM = [7.5, 15.0, 30.0, 60.0, 103.4]
SUB = 5


def subsample(core, n):
    if n == 1:
        return core
    off = (np.arange(n) + 0.5) / n - 0.5
    dy, dx = np.meshgrid(off * 0.25, off * 0.25, indexing="ij")
    lat = (core.lat.to_numpy()[:, None] + dy.ravel()[None, :]).ravel()
    lon = (core.lon.to_numpy()[:, None] + dx.ravel()[None, :]).ravel()
    mass = np.repeat(core.mass.to_numpy() / n**2, n**2)
    return pd.DataFrame({"lat": lat, "lon": lon, "mass": mass})


def hdr_mask(dens, mass, level=0.9):
    order = np.argsort(-dens)
    cum = np.cumsum(mass[order])
    k = np.searchsorted(cum, level * mass.sum()) + 1
    m = np.zeros(len(dens), bool)
    m[order[:k]] = True
    return m


def core_on_grid(core, t, r, chunk=4000):
    """Core impact probability per grid cell, uniform disk of radius r NM around each core point."""
    disk_km2 = np.pi * (r * NM_KM) ** 2
    glat, glon = t.latitude.to_numpy(), t.longitude.to_numpy()
    f = np.zeros(len(t))
    for i in range(0, len(core), chunk):
        c = core.iloc[i:i + chunk]
        d = haversine_nm(glat, glon, c.lat.to_numpy(), c.lon.to_numpy())
        f += ((d <= r) * c.mass.to_numpy()[None, :]).sum(1)
    return f / disk_km2 * t.cellAreaKm2.to_numpy()  # probability per cell


def pos(t, w):
    """Mass-weighted mean position (lat, lon) - adequate over a few degrees."""
    w = w / w.sum()
    return float((t.latitude * w).sum()), float((t.longitude * w).sum())


def dist(a, b):
    return float(haversine_nm(np.array([a[0]]), np.array([a[1]]), np.array([b[0]]), np.array([b[1]]))[0, 0])


def run(csp29: Path, archive_outputs: Path, out: Path, sub=SUB):
    _, core0, t = load(csp29, archive_outputs)
    core = subsample(core0, sub)
    area = t.cellAreaKm2.to_numpy()
    A = float(area.sum())
    pH = t.probabilityMass.to_numpy()
    dH = t.densityPerKm2.to_numpy()
    hdrH = hdr_mask(dH, pH)
    modeH = (float(t.latitude[np.argmax(dH)]), float(t.longitude[np.argmax(dH)]))
    rows, fields = [], {}
    for r in R_NM:
        pc_raw = core_on_grid(core, t, r)
        in_grid = float(pc_raw.sum())
        pc = pc_raw / in_grid
        dc = pc / area
        pj = pc * dH
        bayes_ratio = A * float(pj.sum())
        pj = pj / pj.sum()
        dj = pj / area
        hdrC, hdrJ = hdr_mask(dc, pc), hdr_mask(dj, pj)
        modeC = (float(t.latitude[np.argmax(dc)]), float(t.longitude[np.argmax(dc)]))
        modeJ = (float(t.latitude[np.argmax(dj)]), float(t.longitude[np.argmax(dj)]))
        meanC, meanJ, meanH = pos(t, pc), pos(t, pj), pos(t, pH)
        fields[r] = (pc, pj, hdrC, hdrJ)
        rows.append({
            "descent_reach_nm": r, "core_subsample": sub,
            "core_mass_inside_grid": in_grid,
            "bayes_ratio_R": bayes_ratio, "ln_R": float(np.log(bayes_ratio)),
            "prior_volume_km2": A,
            "uncond_mass_in_cond_hdr90": float(pc[hdrJ].sum()),
            "cond_mass_in_uncond_hdr90": float(pj[hdrC].sum()),
            "uncond_mass_in_Honly_hdr90": float(pc[hdrH].sum()),
            "Honly_mass_in_uncond_hdr90": float(pH[hdrC].sum()),
            "uncond_hdr90_km2": float(area[hdrC].sum()), "cond_hdr90_km2": float(area[hdrJ].sum()),
            "Honly_hdr90_km2": float(area[hdrH].sum()),
            "uncond_mode_lat": modeC[0], "uncond_mode_lon": modeC[1],
            "cond_mode_lat": modeJ[0], "cond_mode_lon": modeJ[1],
            "mode_displacement_nm": dist(modeC, modeJ),
            "mean_displacement_nm": dist(meanC, meanJ),
            "Honly_vs_uncond_mode_displacement_nm": dist(modeC, modeH),
            "Honly_vs_uncond_mean_displacement_nm": dist(meanC, meanH),
            "cond_mean_lat": meanJ[0], "cond_mean_lon": meanJ[1],
            "uncond_mean_lat": meanC[0], "uncond_mean_lon": meanC[1],
        })
    res = pd.DataFrame(rows)
    q = area / A

    def kl(p):
        k = p > 0
        return float((p[k] * np.log(p[k] / q[k])).sum())
    res["D_KL_uncond"] = [kl(fields[r][0]) for r in R_NM]
    res["D_KL_Honly"] = kl(pH)
    res["D_KL_cond"] = [kl(fields[r][1]) for r in R_NM]
    res["ln_I"] = res.D_KL_uncond + res.D_KL_Honly - res.D_KL_cond
    res["ln_S"] = res.ln_R - res.ln_I
    out.mkdir(parents=True, exist_ok=True)
    res.to_csv(out / f"d1-tension-sub{sub}.csv", index=False)
    return res, t, fields, core


if __name__ == "__main__":
    for n in (1, SUB):
        run(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sub=n)
