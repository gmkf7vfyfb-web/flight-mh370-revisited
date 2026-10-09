"""One command: section 11 and deliverables 1 and 4 on a reference run's PER-PARTICLE positions.

    python rerun_reference.py <reference run dir> <module dir> <repository root> <outdir> [label]

Re-runs unchanged on a new reference (architecture, 9 Oct ~04:15 UTC). Every output row carries
`label` (default "295.66 deg prior; superseded on re-run") and the run directory.

Inputs
  <run>/summary.json, run.json, bto-bfo/seed-*/final.npy   the reference's 00:19:37 particles; pooled
      exactly as crates/mh370/src/summary.rs does (row weight x pool_factors[replicate][stratum]);
      each replicate alone uses its stored weights (its own mode mixture). Checked against the run's
      own 0.25 deg map.
  <module>/../../runs/pleiades/likelihood-surface.{f32,toml}   ln L(s|H) exported by THIS module's hook
      (lib.rs test pleiades_export_likelihood_surface), every object-rating x cluster-weight option.
  prior-work H grid (withdrawn share, model-averaged-impact-density.csv), kept for continuity with
      the 8 Oct section 11 and D1 numbers; its crossNm column also defines "inside the arc".

Descent (end of flight owns it; nothing here is a descent model):
  disk-R     uniform disk of declared reach R NM about each 00:19:37 position (the 8 Oct sweep)
  eof-2f     PROVISIONAL-OVERNIGHT: built from end of flight's two published fractions (6.6 % of
             weight >= 30 NM and 3.4 % >= 50 NM north-west of the 00:19:37 position; 9 Oct ruling):
             (1 - 0.066) uniform disk 15 NM + 0.032 uniform on the NW quadrant annulus 30-50 NM
             + 0.034 uniform on the NW quadrant annulus 50-103.4 NM. The 15 NM core and the quadrant
             are assumptions; replace with end of flight's 2-D displacement histogram when it exists.

Outputs (per descent kernel, per H field and option, pooled and per replicate):
  s11: share of H x flight mass in the lobe (H 90 % HDR and >= 30 / >= 50 NM inside the arc; 35S 91E box)
  D1/D4 (always paired): ln R (Bayes ratio vs flat prior over the field's domain, with its volume),
      ln S (suspiciousness, Handley & Lemos 2019 eqs. 9-10), two-way 90 % HDR overlap, HDR areas,
      mode and mean displacement (NM), and for the module's own likelihood the absolute
      BF(H : not-H) = E_flight[L_H] over the domain and the mass outside it.
"""

import json
import os
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.signal import fftconvolve

KM_PER_DEG = 6371.0088 * math.pi / 180.0
NM_KM = 1.852
STEP = 0.05
LON_EDGE0, LAT_EDGE0, N = 85.0, -43.0, 280  # fine grid 85-99 E, 43-29 S
R_NM = [7.5, 15.0, 30.0, 45.0, 60.0, 80.0, 103.4]
EOF_P30, EOF_P50 = 0.066, 0.034
DEFAULT_LABEL = "295.66 deg prior; superseded on re-run"
PRIOR_GRID = ("Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/"
              "pleiades-bran2016-forward-inversion/outputs/model-averaged-impact-density.csv")


def centres():
    lon = LON_EDGE0 + STEP * (np.arange(N) + 0.5)
    lat = LAT_EDGE0 + STEP * (np.arange(N) + 0.5)
    return lon, lat


def cell_area_km2(lat):
    return (STEP * KM_PER_DEG) ** 2 * np.cos(np.radians(lat))


def load_particles(run: Path):
    summ = json.loads((run / "summary.json").read_text())
    rj = json.loads((run / "run.json").read_text())
    case = summ["cases"][0]
    cols = rj["final_columns"]
    ci = {c: cols.index(c) for c in ("weight", "latitude_deg", "longitude_deg", "stratum")}
    seeds = case.get("seeds") or [r["seed"] for r in rj["replicates"]]
    factors = np.array(case["pool_factors"])
    hists, outside = [], []
    pooled = np.zeros((N, N))
    pooled_out = 0.0
    map25 = {}
    for i, s in enumerate(seeds):
        a = np.load(run / case["case"] / f"seed-{s}" / "final.npy", mmap_mode="r")
        w = np.asarray(a[:, ci["weight"]], float)
        lat = np.asarray(a[:, ci["latitude_deg"]], float)
        lon = np.asarray(a[:, ci["longitude_deg"]], float)
        st = np.asarray(a[:, ci["stratum"]], int)
        wp = w * factors[i][st]
        jx = np.floor((lon - LON_EDGE0) / STEP).astype(int)
        jy = np.floor((lat - LAT_EDGE0) / STEP).astype(int)
        inside = (jx >= 0) & (jx < N) & (jy >= 0) & (jy < N)
        h = np.zeros((N, N))
        np.add.at(h, (jy[inside], jx[inside]), w[inside])
        hp = np.zeros((N, N))
        np.add.at(hp, (jy[inside], jx[inside]), wp[inside])
        hists.append(h / w.sum())
        outside.append(float(w[~inside].sum() / w.sum()))
        pooled += hp
        pooled_out += float(wp[~inside].sum())
        # the run's own 0.25 deg map, for the check
        ky = np.floor((lat + 50.0) / 0.25).astype(int)
        kx = np.floor((lon - 55.0) / 0.25).astype(int)
        for key, v in pd.Series(wp).groupby([ky, kx]).sum().items():
            map25[key] = map25.get(key, 0.0) + v
        del a
    tot = pooled.sum() + pooled_out
    m = np.array(case["map"], float)
    mine = np.array([map25.get((int(y), int(x)), 0.0) for y, x, _ in m]) / tot / 0.0625
    check = float(np.max(np.abs(mine - m[:, 2])))
    return dict(seeds=seeds, hists=hists, outside=outside, pooled=pooled / tot, pooled_outside=pooled_out / tot,
                map_check_max_abs=check, n_particles=int(case["particles"]))


def kernel(kind, R_nm=None):
    lat_ref = -36.0
    dx = STEP * KM_PER_DEG * math.cos(math.radians(lat_ref))
    dy = STEP * KM_PER_DEG
    rmax = (103.4 if kind == "eof-2f" else R_nm) * NM_KM
    nx, ny = int(math.ceil(rmax / dx)) + 1, int(math.ceil(rmax / dy)) + 1
    X, Y = np.meshgrid(np.arange(-nx, nx + 1) * dx, np.arange(-ny, ny + 1) * dy)
    r = np.hypot(X, Y)
    if kind == "disk":
        k = (r <= R_nm * NM_KM).astype(float)
        return k / k.sum()
    nw = (X <= 0) & (Y >= 0)  # north-west quadrant
    core = (r <= 15 * NM_KM).astype(float)
    a1 = (nw & (r >= 30 * NM_KM) & (r < 50 * NM_KM)).astype(float)
    a2 = (nw & (r >= 50 * NM_KM) & (r <= 103.4 * NM_KM)).astype(float)
    return (1 - EOF_P30) * core / core.sum() + (EOF_P30 - EOF_P50) * a1 / a1.sum() + EOF_P50 * a2 / a2.sum()


def hdr_mask(dens, mass, level=0.9):
    order = np.argsort(-dens, axis=None)
    cum = np.cumsum(mass.ravel()[order])
    k = np.searchsorted(cum, level * mass.sum()) + 1
    m = np.zeros(dens.size, bool)
    m[order[:k]] = True
    return m.reshape(dens.shape)


def dist_nm(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    h = math.sin((p2 - p1) / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(math.radians(b[1] - a[1]) / 2) ** 2
    return 2 * 6371.0088 * math.asin(math.sqrt(min(1, h))) / NM_KM


def tension(pc, L, area, lat, lon, inside30, inside50, box):
    """pc: unconditional impact mass per cell (domain, sums <= 1); L: likelihood (any scale); area km2."""
    in_dom = pc.sum()
    pcn = pc / in_dom
    A = area.sum()
    dH = L / (L * area).sum()
    pH = dH * area
    j = pcn * L
    bf_rel = j.sum() / ((L * area).sum() / A)
    pj = j / j.sum()
    dc, dj = pcn / area, pj / area
    hC, hJ, hH = hdr_mask(dc, pcn), hdr_mask(dj, pj), hdr_mask(dH, pH)
    q = area / A

    def kl(p):
        k = p > 0
        return float((p[k] * np.log(p[k] / q[k])).sum())
    lnI = kl(pcn) + kl(pH) - kl(pj)

    def bmd(p):
        # Bayesian model dimensionality, Handley & Lemos 2019 (PRD 100, 043504) eq. 3: d/2 = Var_P[log P/pi]
        k = p > 0
        info = np.log(p[k] / q[k])
        return float(2.0 * ((p[k] * info**2).sum() - (p[k] * info).sum() ** 2))
    dA, dB, dAB = bmd(pcn), bmd(pH), bmd(pj)
    d_shared = dA + dB - dAB  # Proposition 2: dimensionality of the shared constrained parameters
    lnS = float(np.log(bf_rel) - lnI)
    from scipy.stats import chi2
    p_t = float(chi2.sf(d_shared - 2.0 * lnS, d_shared)) if d_shared > 0 else float("nan")  # eq. 25
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    iu, ij = np.unravel_index(np.argmax(dc), dc.shape), np.unravel_index(np.argmax(dj), dj.shape)
    mu = (float((pcn * LAT).sum()), float((pcn * LON).sum()))
    mj = (float((pj * LAT).sum()), float((pj * LON).sum()))
    return dict(uncond_mass_in_domain=float(in_dom), ln_R=float(np.log(bf_rel)), prior_volume_km2=float(A),
                ln_I=lnI, ln_S=lnS, d_A=dA, d_B=dB, d_AB=dAB, d_shared=d_shared, tension_p=p_t,
                uncond_in_cond_hdr90=float(pcn[hJ].sum()), cond_in_uncond_hdr90=float(pj[hC].sum()),
                uncond_hdr90_km2=float(area[hC].sum()), cond_hdr90_km2=float(area[hJ].sum()), Honly_hdr90_km2=float(area[hH].sum()),
                uncond_mode=(float(LAT[iu]), float(LON[iu])), cond_mode=(float(LAT[ij]), float(LON[ij])),
                mode_shift_nm=dist_nm((LAT[iu], LON[iu]), (LAT[ij], LON[ij])), mean_shift_nm=dist_nm(mu, mj),
                lobe30=float(pj[hH & inside30].sum()), lobe50=float(pj[hH & inside50].sum()), box_35S_91E=float(pj[box].sum()),
                lobe30_H_alone=float(pH[hH & inside30].sum()), lobe50_H_alone=float(pH[hH & inside50].sum()))


def run(run_dir, module_dir, csp29, out, label=DEFAULT_LABEL):
    run_dir, module_dir, csp29, out = Path(run_dir), Path(module_dir), Path(csp29), Path(out)
    P = load_particles(run_dir)
    lon, lat = centres()
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    area = cell_area_km2(LAT)
    # own likelihood surface
    surf_dir = Path(os.environ.get("PLEIADES_SURFACE_DIR", module_dir / "../../runs/pleiades"))
    meta = {}
    for line in (surf_dir / "likelihood-surface.toml").read_text().splitlines():
        k, v = line.split(" = ", 1)
        meta[k] = json.loads(v) if v.startswith("[") else (v.strip('"') if v.startswith('"') else float(v))
    nlat, nlon = int(meta["nlat"]), int(meta["nlon"])
    models = meta["ocean_model"] if isinstance(meta["ocean_model"], list) else [meta["ocean_model"]]
    S = np.fromfile(surf_dir / "likelihood-surface.f32", dtype="<f4").reshape(len(models), len(meta["object_rating"]), 2, nlat, nlon).astype(float)
    # composer marginal over `ocean-model` at equal prior weight: L = mean_m L_m
    fields = [(m, np.exp(S[i])) for i, m in enumerate(models)]
    if len(models) > 1:
        fields.append(("marginal: " + " | ".join(models), np.mean([f for _, f in fields], axis=0)))
    oy = int(round((meta["lat0"] - lat[0]) / STEP))
    ox = int(round((meta["lon0"] - lon[0]) / STEP))
    sl = (slice(oy, oy + nlat), slice(ox, ox + nlon))
    assert abs(lat[oy] - meta["lat0"]) < 1e-9 and abs(lon[ox] - meta["lon0"]) < 1e-9
    # prior-work grid: H field and the "inside the arc" coordinate
    T = pd.read_csv(csp29 / PRIOR_GRID)
    from scipy.spatial import cKDTree
    tree = cKDTree(np.c_[T.latitude, T.longitude * math.cos(math.radians(36))])
    d, idx = tree.query(np.c_[LAT.ravel(), LON.ravel() * math.cos(math.radians(36))])
    near = (d < 0.06).reshape(LAT.shape)  # within about one prior-grid cell (5 NM)
    cross = np.where(near, T.crossNm.to_numpy()[idx].reshape(LAT.shape), np.nan)
    Hprior = np.where(near, T.densityPerKm2.to_numpy()[idx].reshape(LAT.shape), np.nan)
    inside30, inside50 = (cross <= -30), (cross <= -50)
    box = (np.abs(LON - 91.0) <= 0.5) & (np.abs(LAT + 35.0) <= 0.5)
    kernels = [("disk", R) for R in R_NM] + [("eof-2f", None)]
    rows = []
    reps = [("pooled", P["pooled"])] + [(f"seed-{s}", h) for s, h in zip(P["seeds"], P["hists"])]
    for kind, R in kernels:
        K = kernel(kind, R)
        kname = f"disk-{R:g}nm" if kind == "disk" else "eof-2f PROVISIONAL-OVERNIGHT"
        for rep, h in reps:
            imp = fftconvolve(h, K, mode="same")
            imp = np.clip(imp, 0, None)
            # (a) prior-work H field, its own domain
            dom = near
            r = tension(np.where(dom, imp, 0), np.where(dom, Hprior, 0), np.where(dom, area, 1e-30),
                        lat, lon, inside30 & dom, inside50 & dom, box & dom)
            rows.append(dict(label=label, run=str(run_dir), kernel=kname, replicate=rep, field="prior-work mixture grid",
                             object_rating="rating5", cluster_weight="equal", **r))
            # (b) the module's own likelihood, every option
            pc = imp[sl]
            for fl, F in fields:
                for ri, rl in enumerate(meta["object_rating"]):
                    for wi, wl in enumerate(meta["cluster_weight"]):
                        Ls = F[ri, wi]
                        r = tension(pc, Ls, area[sl], lat[sl[0]], lon[sl[1]], inside30[sl], inside50[sl], box[sl])
                        r["bf_H_vs_notH_domain"] = float((pc / pc.sum() * Ls).sum())
                        rows.append(dict(label=label, run=str(run_dir), kernel=kname, replicate=rep,
                                         field=f"module D3 ({fl})", object_rating=rl, cluster_weight=wl, **r))
        if kind == "eof-2f":
            # pooled fields for the figure (prepare/d4_figure.py); gitignored run tree only
            pooled = np.clip(fftconvolve(P["pooled"], K, mode="same"), 0, None)[sl]
            out.mkdir(parents=True, exist_ok=True)
            np.savez_compressed(out / "fields-eof2f.npz", lat=lat[sl[0]], lon=lon[sl[1]], area=area[sl], uncond=pooled,
                                cross=cross[sl], labels=np.array([f for f, _ in fields]),
                                L=np.stack([F[0, 0] for _, F in fields]))  # rho4-0, equal
    d = pd.DataFrame(rows)
    for c in ("uncond_mode", "cond_mode"):
        d[c + "_lat"] = d[c].map(lambda x: x[0])
        d[c + "_lon"] = d[c].map(lambda x: x[1])
        d = d.drop(columns=c)
    out.mkdir(parents=True, exist_ok=True)
    d.to_csv(out / "rerun-reference.csv", index=False)
    info = dict(label=label, run=str(run_dir), seeds=P["seeds"], particles_per_replicate=P["n_particles"],
                map_check_max_abs_density=P["map_check_max_abs"], pooled_mass_outside_fine_grid=P["pooled_outside"],
                replicate_mass_outside_fine_grid=P["outside"], surface=meta)
    (out / "rerun-reference.json").write_text(json.dumps(info, indent=1))
    return d, info


if __name__ == "__main__":
    run(*sys.argv[1:5], *(sys.argv[5:6] or []))
