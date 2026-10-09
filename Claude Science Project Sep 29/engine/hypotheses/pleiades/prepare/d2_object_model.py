"""Deliverable 2 (part): object clusters at a declared linkage threshold, with sensitivity. PROVISIONAL.

Inputs: data/ga-rec2017-13-objects.csv (all 70 GA objects; PHR_2 object 12 transposition corrected).

Declared configuration (reported with every result, brief section 5):
  linkage            single linkage on great-circle distance
  threshold_km       3.0 default; swept over THRESHOLDS_KM
  object-rating      arms: rating 5 only; rating 5 + rating 4 with weight rho4 (swept)
  cluster position   unweighted mean of member positions (matches the brief's table)
  cluster weight w_c two declared forms, both reported:
                       'equal'  - each cluster equally likely to be the 9M-MRO one, scaled by the
                                  highest rating weight among its members
                       'count'  - proportional to the rating-weighted member count
                     Neither uses shape or size as identity evidence; there is none (brief section 3).
  background q_c     NOT computed here. GA gives each scene as about 25 km x 20 km, heavily cloud and
                     glint affected; footprints are not assembled (brief section 13).

Matching-space size for the two-epoch enumeration: injective partial assignments of the 4 COSMO-SkyMed
contacts to n targets, sum_k C(4,k) n!/(n-k)!  (1,045 for n = 6; 18,001 for n = 12).

Usage: python d2_object_model.py <module dir> <outdir>  (also rewrites <module dir>/data/targets-3km.csv)
"""

import sys
from math import comb, perm
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

THRESHOLDS_KM = [0.5, 1, 2, 3, 5, 10, 20, 50, 100, 200]
DEFAULT_KM = 3.0
RHO4 = [0.0, 0.25, 0.5, 1.0]
N_COSMO = 4
EARTH_KM = 6371.0088


def gc_km(lat, lon):
    p, l = np.radians(lat), np.radians(lon)
    a = np.sin((p[:, None] - p[None, :]) / 2) ** 2 + np.cos(p)[:, None] * np.cos(p)[None, :] * np.sin((l[:, None] - l[None, :]) / 2) ** 2
    return 2 * EARTH_KM * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def matchings(n, m=N_COSMO):
    return sum(comb(m, k) * perm(n, k) for k in range(min(m, n) + 1))


def cluster(objs, threshold_km):
    if len(objs) == 1:
        return np.array([1])
    d = gc_km(objs.latitude.to_numpy(), objs.longitude.to_numpy())
    np.fill_diagonal(d, 0)
    return fcluster(linkage(squareform(d, checks=False), "single"), t=threshold_km, criterion="distance")


def cluster_table(objs, labels, rho4):
    rho = objs.rating.map({5: 1.0, 4: rho4}).to_numpy()
    o = objs.assign(cluster=labels, rho=rho)
    g = o.groupby("cluster")
    t = pd.DataFrame({
        "scenes": g.scene.agg(lambda s: "+".join(sorted(set(s)))),
        "objects": g.apply(lambda d: ",".join(f"{s}:{k}" for s, k in zip(d.scene, d.object)), include_groups=False),
        "n": g.size(), "n_rating5": g.rating.agg(lambda r: int((r == 5).sum())), "n_rating4": g.rating.agg(lambda r: int((r == 4).sum())),
        "mean_lat": g.latitude.mean(), "mean_lon": g.longitude.mean(), "area_m2": g.area_m2.sum(),
        "max_rho": g.rho.max(), "sum_rho": g.rho.sum(),
    }).reset_index()
    t = t[t.max_rho > 0].copy()  # a cluster of rating-4 objects carried at rho4 = 0 does not exist
    t["w_equal"] = t.max_rho / t.max_rho.sum()
    t["w_count"] = t.sum_rho / t.sum_rho.sum()
    return t.sort_values(["mean_lat"], ascending=False).reset_index(drop=True)


def run(module_dir: Path, out: Path):
    objs = pd.read_csv(module_dir / "data/ga-rec2017-13-objects.csv")
    arms = {"rating5": objs[objs.rating == 5].reset_index(drop=True),
            "rating45": objs[objs.rating >= 4].reset_index(drop=True)}
    sens = []
    for arm, o in arms.items():
        for th in THRESHOLDS_KM:
            n = int(len(set(cluster(o, th))))
            sens.append({"arm": arm, "threshold_km": th, "objects": len(o), "clusters": n,
                         "cosmo_matchings_clusters": matchings(n), "cosmo_matchings_objects": matchings(len(o))})
    sens = pd.DataFrame(sens)
    tables = []
    for arm, o in arms.items():
        lab = cluster(o, DEFAULT_KM)
        for rho4 in (RHO4 if arm == "rating45" else [0.0]):
            tables.append(cluster_table(o, lab, rho4).assign(arm=arm, rho4=rho4, threshold_km=DEFAULT_KM))
    clusters = pd.concat(tables, ignore_index=True)
    out.mkdir(parents=True, exist_ok=True)
    sens.to_csv(out / "d2-cluster-sensitivity.csv", index=False)
    clusters.to_csv(out / "d2-clusters-3km.csv", index=False)
    # the hook's input (data/targets-3km.csv): one row per (arm, rho4, cluster), no quoted fields
    tg = clusters[["arm", "rho4", "scenes", "mean_lon", "mean_lat", "w_equal", "w_count", "n", "n_rating5", "n_rating4"]]
    tg = tg.rename(columns={"scenes": "scene", "mean_lon": "lon", "mean_lat": "lat"})
    tg.to_csv(module_dir / "data/targets-3km.csv", index=False, float_format="%.6f")
    return sens, clusters


if __name__ == "__main__":
    assert matchings(6) == 1045 and matchings(12) == 18001
    run(Path(sys.argv[1]), Path(sys.argv[2]))
