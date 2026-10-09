"""Convert shared ocean transport path exports (engine/crates/ocean examples/ocean_paths.rs; ruling H5) into
the column schema the module's propagation scripts read (the retired stub's schema), so air9/air8 and the
IMOS paths run on the SHARED environment with no change to the propagation code.

  bathymetry: range_km = s_m/1000, elevation_m = -depth_m, tid, corridor_max_elevation_m, lat, lon
  sound speed: node, range_km, lat, lon, depth_m, c_m_s = c_mean_m_s (and c_sd_m_s kept), plus
               sp_psu and t_insitu_c recovered EXACTLY from the exported SA and CT with gsw
               (SP_from_SA, t_from_CT), because the deep extension holds SA and CT via SP and t.
Levels the shared API leaves NaN stay NaN (never filled here); the propagation scripts extend below
the deepest valid level as before.
Usage: python shared_paths.py <export_dir> <out_dir> <name> [<name> ...]   (e.g. air9-H01W)
"""
import sys
from pathlib import Path

import gsw
import numpy as np
import pandas as pd


def convert(exp, out, name):
    b = pd.read_csv(exp / f"{name}_bathymetry.csv")
    s = pd.read_csv(exp / f"{name}_soundspeed.csv")
    src, st = name.split("-")
    pd.DataFrame(dict(range_km=b.s_m / 1000, lat=b.lat, lon=b.lon, elevation_m=-b.depth_m, tid=b.tid,
                      corridor_max_elevation_m=b.corridor_max_elevation_m)).to_csv(out / f"bathy_{src}_{st}.csv", index=False)
    sp = gsw.SP_from_SA(s.sa_g_kg, s.pressure_dbar, s.lon, s.lat)
    t = gsw.t_from_CT(s.sa_g_kg, s.ct_c, s.pressure_dbar)
    pd.DataFrame(dict(node=s.node, range_km=s.s_m / 1000, lat=s.lat, lon=s.lon, depth_m=s.depth_m, t_insitu_c=t, sp_psu=sp,
                      c_m_s=s.c_mean_m_s, c_sd_m_s=s.c_sd_m_s)).to_csv(out / f"ssp_{src}_{st}.csv", index=False)
    return len(b), int(np.isfinite(s.c_mean_m_s).sum())


if __name__ == "__main__":
    exp, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    for n in sys.argv[3:]:
        print(n, convert(exp, out, n))
