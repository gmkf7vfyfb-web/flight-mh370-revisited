"""Check the numpy BFO port against the engine on a use_bfo = true single-particle run (tempering off): the engine's predicted
BFO without bias is z - innovation - m_prev, with m from the scalar Kalman recursion (prior 150 Hz, 625 Hz^2, drift off).
Usage: validate_bfo.py RUN_DIR OBS_CSV EPH_CSV"""
import sys, glob, math, os, json
import numpy as np
from e2e_common import read_rows, sat_state, bfo_nobias
NAMES = ["LateralNavigation", "MagneticHeading", "MagneticTrack", "TrueHeading", "TrueTrack"]
run, obs, eph = sys.argv[1:4]; O = read_rows(obs); EP = read_rows(eph)
bfo_ep = [r for r in O if "bfo" in r["cruise"].split()]
diffs = []; level = []
for sd in sorted(glob.glob(f"{run}/prior/seed-*")):
    for name in NAMES:
        m, v = 150.0, 625.0; ok = True
        for r in bfo_ep:
            e = r["epoch_id"]; f = f"{sd}/residuals/{name}-{e}.npy"; fx = f"{sd}/residuals/{name}-x{e}.npy"
            if not (os.path.exists(f) and os.path.exists(fx)): ok = False; break
            s = np.load(f)[0].astype(float); x = np.load(fx)[0].astype(float)
            z = float(r["bfo_hz"]); sdv = float(r["bfo_sd_hz"]); innov = s[8]
            if not np.isfinite(innov): ok = False; break
            pe = z - innov - m
            xw = np.load(f"{sd}/residuals/{name}-w{e}.npy")[0].astype(float); fwd = (x[2] - s[2]) * 60.0; bwd = (s[2] - xw[2]) * 60.0
            vup = 0.0 if (abs(fwd) < 1 or abs(bwd) < 1) else (fwd if abs(fwd) >= abs(bwd) else bwd); sat, satv = sat_state(EP, e)
            pp = bfo_nobias(sat, satv, float(r["satellite_afc_hz"]), s[0], s[1], s[2], s[3] * math.cos(math.radians(s[4])), s[3] * math.sin(math.radians(s[4])), vup)
            diffs.append(pp - pe); level.append(abs(vup) < 1)
            g = v / (v + sdv ** 2); m += g * innov; v *= (1 - g)
d = np.array(diffs); L = np.array(level)
print(json.dumps({"n": int(d.size), "max_abs_hz": float(np.abs(d).max()), "median_abs_hz": float(np.median(np.abs(d))),
                  "max_abs_level_hz": float(np.abs(d[L]).max()) if L.any() else None, "n_level": int(L.sum()),
                  "max_abs_nonlevel_hz": float(np.abs(d[~L]).max()) if (~L).any() else None, "n_nonlevel": int((~L).sum())}))
