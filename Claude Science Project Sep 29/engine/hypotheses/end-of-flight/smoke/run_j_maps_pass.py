"""One streaming pass over an end-of-flight production set for the standard map products (Pete, 17 Oct 2026).

    python run_j_maps_pass.py EOF_ROOT CORE_ROOT TABLE_JSON OUT_DIR PART NPARTS
    python run_j_maps_pass.py --combine OUT_DIR NPARTS

For every 00:19 treatment D0..D5 (competing-causes total, q = 1/3, C2 silent, survival factor; the same per-row log mass
as run_i_maps.cell_logmass and option_table_0019.seed_terms) and for each family (A1 = code 1, A2 = code 2, B = codes 3+6)
it accumulates a 0.02 deg impact-location histogram on [-42,-15] x [80,110], scaled by exp(-ln Z_cell) from TABLE_JSON so
each treatment's histogram sums to ~1 (a built-in check against the production table). It also keeps a mass-preserving
systematic resample of 10,000 rows per seed per treatment (impact location, family, stratum, peak radiated power and
energy transferred from the tau90_v1 sidecar, flight-path angle, speed) for the scatter maps. Strata mixed with core run
J's P(family); seeds pooled with weight P/K (as option_table_0019.py). PART/NPARTS splits the seed list for parallel workers.
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from compact_impacts import load
from run_i_maps import cell_logmass

STRATA = {"run-j-waypoints": 0.9982, "run-j-free": 0.0013, "run-j-repro-radar": 0.0003, "run-j-descent-climb": 0.0002}
LAT0, LAT1, LON0, LON1, G = -42.0, -15.0, 80.0, 110.0, 0.02
NLAT, NLON = int(round((LAT1 - LAT0) / G)), int(round((LON1 - LON0) / G))
CELLS = ("D0", "D1", "D2", "D3", "D4", "D5")
FAMS = {"A1": (1,), "A2": (2,), "B": (3, 6)}
NRS = 10_000


def seed_list(eof_root):
    out = []
    for st, P in STRATA.items():
        seeds = sorted((p for p in (pathlib.Path(eof_root) / st).glob("seed-*") if p.is_dir()), key=lambda p: int(p.name[5:]))
        out += [(st, P, len(seeds), sd) for sd in seeds]
    return out


def part(eof_root, core_root, table, out, k, n):
    tab = json.load(open(table))["cells"]
    lnz = {d: tab[f"{d} total q=0.333 (C2 silent)"]["ln_Z"] for d in CELLS}
    H = {(d, f): np.zeros(NLAT * NLON) for d in CELLS for f in ("all",) + tuple(FAMS)}
    L1 = {(d, f): [] for d in CELLS for f in ("all",) + tuple(FAMS)}; L2 = {key: [] for key in L1}
    RS = {d: [] for d in CELLS}
    todo = seed_list(eof_root)[k::n]
    for st, P, K, sd in todo:
        meta, g = load(sd)
        lm = cell_logmass(g, meta, pathlib.Path(core_root) / st / "bto-bfo" / sd.name / "handoff-m0011" / "handoff.npy")
        lat = g("latitude_deg"); lon = g("longitude_deg"); f4 = g("family4_code")
        tz = np.load(sd / "tau90_v1.npz"); pk = tz["peak_rate_w"].astype(np.float64); en = tz["energy_transferred_j"].astype(np.float64)
        assert len(pk) == len(lat), (sd, len(pk), len(lat))
        fpa = g("flight_path_angle_deg")
        spd = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
        i = np.floor((lat - LAT0) / G).astype(np.int64); j = np.floor((lon - LON0) / G).astype(np.int64)
        ok = (i >= 0) & (i < NLAT) & (j >= 0) & (j < NLON); ij = (i * NLON + j)[ok]
        c = np.log(P / K)
        fm = {f: np.isin(f4, v) for f, v in FAMS.items()}
        for d, a in lm.items():
            fin = np.isfinite(a)
            m = np.zeros(len(a)); m[fin] = np.exp(c + a[fin] - lnz[d])
            for f in ("all",) + tuple(FAMS):
                mf = m if f == "all" else m * fm[f]
                s = mf.sum()
                L1[(d, f)].append(np.log(s) if s > 0 else -np.inf); L2[(d, f)].append(np.log((mf * mf).sum()) if s > 0 else -np.inf)
                H[(d, f)] += np.bincount(ij, weights=mf[ok], minlength=NLAT * NLON)
            if m.sum() > 0:
                cs = np.cumsum(m); s_ = np.minimum(np.searchsorted(cs, (np.arange(NRS) + 0.5) / NRS * cs[-1]), len(m) - 1)
                RS[d].append(np.column_stack([np.full(NRS, cs[-1] / NRS), lat[s_], lon[s_], f4[s_], np.full(NRS, list(STRATA).index(st)),
                                              pk[s_], en[s_], fpa[s_], spd[s_]]).astype(np.float64))
        print(f"part {k}: {st} {sd.name} nan_peak={np.isnan(pk).mean():.4f}", flush=True)
    sv = {}
    for (d, f), h in H.items():
        sv[f"H_{d}_{f}"] = h.astype(np.float64); sv[f"L1_{d}_{f}"] = np.array(L1[(d, f)]); sv[f"L2_{d}_{f}"] = np.array(L2[(d, f)])
    for d in CELLS:
        sv[f"RS_{d}"] = np.concatenate(RS[d]) if RS[d] else np.zeros((0, 9))
    sv["seeds"] = np.array([f"{st}/{sd.name}" for st, _, _, sd in todo])
    np.savez(pathlib.Path(out) / f"part-{k}-of-{n}.npz", **sv)


def combine(out, n):
    out = pathlib.Path(out); Z = [np.load(out / f"part-{k}-of-{n}.npz") for k in range(n)]
    res = {"grid": dict(lat0=LAT0, lat1=LAT1, lon0=LON0, lon1=LON1, step=G), "strata": STRATA, "cells": {}}
    sv = dict(lat0=LAT0, lon0=LON0, grid=G, nlat=NLAT, nlon=NLON)
    for d in CELLS:
        for f in ("all",) + tuple(FAMS):
            h = sum(z[f"H_{d}_{f}"] for z in Z)
            l1 = np.concatenate([z[f"L1_{d}_{f}"] for z in Z]); l2 = np.concatenate([z[f"L2_{d}_{f}"] for z in Z])
            s1 = logsumexp(l1); s2 = logsumexp(l2)
            res["cells"][f"{d}/{f}"] = {"mass_rel_table": float(np.exp(s1)), "eff_impacts": float(np.exp(2 * s1 - s2)) if np.isfinite(s2) else 0.0,
                                        "mass_in_grid": float(h.sum())}
            sv[f"H_{d}_{f}"] = h.reshape(NLAT, NLON).astype(np.float32)
        sv[f"RS_{d}"] = np.concatenate([z[f"RS_{d}"] for z in Z]).astype(np.float32)
    res["n_seeds"] = int(sum(len(z["seeds"]) for z in Z))
    np.savez_compressed(out / "run-j-maps-accumulators.npz", **sv)
    json.dump(res, open(out / "run-j-maps-accumulators.json", "w"), indent=1)
    print(json.dumps({k: (round(v["mass_rel_table"], 4), round(v["eff_impacts"])) for k, v in res["cells"].items()}))


if __name__ == "__main__":
    if sys.argv[1] == "--combine":
        combine(sys.argv[2], int(sys.argv[3]))
    else:
        part(*sys.argv[1:5], int(sys.argv[5]), int(sys.argv[6]))
