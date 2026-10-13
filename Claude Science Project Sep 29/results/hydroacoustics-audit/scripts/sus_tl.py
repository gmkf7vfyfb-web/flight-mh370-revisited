"""Audit: the hydroacoustics module's propagation (kraken_tl.tl_path + air9_tl_validation.build_profiles, imported
read-only from hypothesis/hydroacoustics @3412bc6) on the 2003 SUS paths of Blackman et al. (2004) Table 5
(printed p. 24), sites A6-A11, to H01W (H01W1, the only H01W element in 2003) and H08S (2002 triad centroid).

Same settings as the module's air9 validation: hard half-space bottom, Francois-Garrison, incoherent adiabatic
modes, 5 km profiles, third-octave centres 5-63 Hz, spherical-earth correction. Paths: audit builder (paths.py),
WOA23 95A4 for the month of the shot. Source depths 610 and 915 m (Table 5).

Usage: python sus_tl.py <module_prepare_dir> <at_bin_dir> <work_dir> <out_csv>
"""
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, sys.argv[1])
sys.path.insert(0, __file__.rsplit("/", 1)[0])
import air9_tl_validation as A  # noqa: E402
import kraken_tl as K  # noqa: E402
import paths  # noqa: E402

SITES = {  # Table 5 (printed p. 24) as transcribed in the module's blackman_2003_events.csv; month of the shot
    "A6": (-22.084817, 72.742150, 5), "A7": (-18.434083, 80.918183, 5), "A8": (-17.175917, 83.675100, 6),
    "A9": (-13.494550, 91.688600, 6), "A10": (-12.213317, 96.796650, 6), "A11": (-13.197967, 104.694350, 6)}
RX = {"H01W": (-34.892899, 114.153900, 1063.0), "H08S": (-7.639380, 72.483828, 1376.0)}
BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
SD = [610.0, 915.0]

if __name__ == "__main__":
    at_bin, work, out = sys.argv[2], sys.argv[3], sys.argv[4]
    rows = []
    for site, (la, lo, mon) in SITES.items():
        for st, (rla, rlo, rd) in RX.items():
            name = f"{site}_{st}"
            L, shallow = paths.build(name, (la, lo), (rla, rlo), "95A4", mon, f"{work}/paths")
            bathy = pd.read_csv(f"{work}/paths/bathy_{name}.csv"); ssp = pd.read_csv(f"{work}/paths/ssp_{name}.csv")
            rprof, profiles = A.build_profiles(bathy, ssp)
            t0 = time.time()
            for fc in BANDS:
                try:
                    r, tl, nm, dt = K.tl_path(f"{work}/k/{name}", f"f{fc:g}".replace(".", "p"), fc, profiles, rprof,
                                              np.array([rprof[-1]]), SD, [rd], A.BOTTOMS["hard"], at_bin, fg=A.FG)
                    s = K.read_shd(f"{work}/k/{name}/" + f"f{fc:g}".replace(".", "p") + ".shd")
                    x = s["rr_m"] / 1000.0 / 6371.0
                    sph = 10 * np.log10(x / np.sin(x))
                    for js, zs in enumerate(s["sz"]):
                        rows.append(dict(site=site, station=st, fc_hz=fc, src_depth_m=float(zs), range_km=L,
                                         shallowest_m=-shallow, tl_db=float(-20 * np.log10(np.abs(s["p"][0, js, 0, -1])) + sph[-1]),
                                         n_modes_first=nm[0] if nm else -1, n_modes_min=min(nm) if nm else -1))
                except Exception as e:  # noqa: BLE001
                    rows.append(dict(site=site, station=st, fc_hz=fc, src_depth_m=np.nan, range_km=L, shallowest_m=-shallow,
                                     tl_db=np.nan, n_modes_first=-1, n_modes_min=-1, error=str(e)[:200]))
            print(name, round(L, 1), "km, shallowest", -shallow, "m,", round(time.time() - t0, 1), "s", flush=True)
            pd.DataFrame(rows).to_csv(out, index=False)
