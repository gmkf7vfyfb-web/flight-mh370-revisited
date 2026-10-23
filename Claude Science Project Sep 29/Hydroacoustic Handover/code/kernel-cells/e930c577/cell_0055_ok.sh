cd leg; cat > royer_recombination.py <<'EOF'
"""EXPLORATORY, not pre-registered (post hoc after seeing that Royer's SSEIR 01:11:10-01:11:21 and MAD 01:25:20 picks fall in
the branch-C windows). Free inversion of (lat, lon, origin time) from H01W arrival time + Kadri bearing + SSEIR + MAD picks,
with c = 1.48 km/s; sigma_i = hypot(5 s, d_i*0.015/1.48^2); bearing sigma 0.5 deg. Grid 32-18 S, 92-108 E, 0.02 deg.
Also the chance probability that >= k of the five recording OHASISBIO sites have a Royer pick inside the L windows."""
import sys, json, itertools; sys.path.insert(0, "."); import numpy as np, pandas as pd
from pyproj import Geod; Gp = Geod(ellps="WGS84")
from geometry_windows import H01W, ST, AZ, HX, T_RX
s = lambda x: sum(float(a) * m for a, m in zip(x.split(":"), (3600, 60, 1)))
la = np.arange(-32, -18 + 1e-9, 0.02); lo = np.arange(92, 108 + 1e-9, 0.02); LA, LO = np.meshgrid(la, lo, indexing="ij")
def d_az(st):
    az, _, d = Gp.inv(np.full(LA.shape, st[1]), np.full(LA.shape, st[0]), LO, LA); return d / 1e3, az % 360
dH, azH = d_az(H01W); dS, _ = d_az(ST["OHAS_SSEIR"][:2]); dM, _ = d_az(ST["OHAS_MAD"][:2])
cases = {"C: Kadri caption 00:54:30 + SSEIR (event 8/7/12/11 picks, mean 01:11:15.9) + MAD 01:25:20.44":
             dict(h=T_RX["C"], sse=np.mean([s("01:11:10.16"), s("01:11:15.87"), s("01:11:16.83"), s("01:11:20.83")]), mad=s("01:25:20.44")),
         "C': Royer H01W 00:54:10.43 + 16 s + SSEIR + MAD": dict(h=s("00:54:10.43") + 16, sse=np.mean([s("01:11:10.16"), s("01:11:15.87"), s("01:11:16.83"), s("01:11:20.83")]), mad=s("01:25:20.44")),
         "C'': Royer H01W 00:54:10.43 as printed + SSEIR + MAD": dict(h=s("00:54:10.43"), sse=np.mean([s("01:11:10.16"), s("01:11:15.87"), s("01:11:16.83"), s("01:11:20.83")]), mad=s("01:25:20.44"))}
out = {}
for k, c in cases.items():
    D = np.stack([dH, dS, dM]); T = np.array([c["h"], c["sse"], c["mad"]])[:, None, None]
    sig = np.hypot(5.0, D * 0.015 / 1.48 ** 2); wgt = 1 / sig ** 2
    t0 = ((T - D / 1.48) * wgt).sum(0) / wgt.sum(0); r = (T - D / 1.48 - t0) / sig
    dz = ((azH - AZ + 180) % 360 - 180) / 0.5; chi = (r ** 2).sum(0) + dz ** 2
    i = np.unravel_index(np.argmin(chi), chi.shape); m = chi <= chi[i] + 5.99
    out[k] = dict(best_lat=round(float(LA[i]), 3), best_lon=round(float(LO[i]), 3), chi2_min=round(float(chi[i]), 2), dof=1,
                  origin_utc=f"00:{int(t0[i]%3600//60):02d}:{t0[i]%60:04.1f}", residuals_s=[round(float(x * y), 1) for x, y in zip(r[:, i[0], i[1]], sig[:, i[0], i[1]])],
                  bearing_resid_deg=round(float(dz[i] * 0.5), 2), km_to_crossing=round(float(Gp.inv(101.369, -25.732, LO[i], LA[i])[2] / 1e3), 1),
                  km_to_haixun=round(float(Gp.inv(HX[1], HX[0], LO[i], LA[i])[2] / 1e3), 1),
                  region_95_lat=[round(float(LA[m].min()), 2), round(float(LA[m].max()), 2)], region_95_lon=[round(float(LO[m].min()), 2), round(float(LO[m].max()), 2)])
# chance: Poisson-binomial over 5 sites, windows of each source set
CH = pd.read_csv("out/royer_chance_rates.csv"); pk = {}
for (br, ss), g in CH.groupby(["branch", "source_set"]):
    p = g.p_at_least_one.values; dist = np.zeros(len(p) + 1); dist[0] = 1
    for q in p: dist[1:] = dist[1:] * (1 - q) + dist[:-1] * q; dist[0] *= (1 - q)
    obs = int(g.observed_hit.sum()); pk[f"{br}|{ss}"] = dict(observed_sites_hit=obs, p_ge_observed=round(float(dist[obs:].sum()), 4), p_ge_2=round(float(dist[2:].sum()), 4))
json.dump(dict(inversions=out, chance=pk), open("out/royer_recombination.json", "w"), indent=1)
print(json.dumps(out, indent=1)); print(json.dumps(pk, indent=1))
EOF
python royer_recombination.py 2>&1 | grep -v -i proj