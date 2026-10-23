mkdir -p leg/out; cat > leg/geometry_windows.py <<'EOF'
"""Predicted 95 % arrival windows for sources on the corrected Kadri locality (18 Oct 2026, hydroacoustic leg).
Source time is inferred from the H01W reception, so  t_X = t_H01W + (d_X - d_H01W)/c  (work-order 13 Oct budget, re-used).
Sigma per point: group-speed term |d_X - d_H01W| * 0.015 / 1.48^2 and a 5 s pick allowance, in quadrature; 95 % = 1.96 sigma.
Bearing (core 0.5 deg, wide 1.0 deg) and BTO (+/-63 us) enter by RE-SOLVING the source point; the reported window is the
union over the source set. Source sets: crossing (core/wide), Kadri eq.-4 strip (v 0-250 m/s), full locality strip
(R7-60 to R7+250 km, bearing +/-1 deg), Haixun 01 (fixed point).  Usage: python geometry_windows.py OUTDIR"""
import sys, json, pathlib
import numpy as np, pandas as pd
from geographiclib.geodesic import Geodesic
G = Geodesic.WGS84
OUT = pathlib.Path(sys.argv[1]); OUT.mkdir(parents=True, exist_ok=True)
C, DC, PICK = 1.48, 0.015, 5.0
H01W = (-34.8903, 114.1426); AZ = 306.18; HX = (-25.975, 101.461)
R7 = {"bto": 1591.3, "bto_lo": 1578.9, "bto_hi": 1603.7}          # kadri_geom_output.txt (sea level, m0019a)
R7_AZ = {305.18: 1585.7, 305.68: 1588.4, 306.18: 1591.3, 306.68: 1594.3, 307.18: 1597.5}   # same file
def dm(a): d, m = a; return d + m / 60.0
ST = {  # name: (lat, lon, source, note)
 "PerthCanyon_3376": (-dm((31, 50.530)), dm((115, 0.824)), "IMOS deployment metadata (mem c85d94)", "seabed logger"),
 "PerthCanyon_3315": (-dm((31, 52.033)), dm((115, 0.068)), "IMOS deployment metadata", "seabed logger"),
 "H08S": (np.mean([-7.645348, -7.645545, -7.627407]), np.mean([72.474438, 72.493307, 72.483879]), "Royer 2016 Table 1 (triad centroid)", "IMS triad"),
 "H08N": (-6.337533, 71.002077, "module request_ims.json", "IMS triad"),
 "Portland_3274": (-dm((38, 32.218)), dm((141, 14.854)), "IMOS metadata", "shelf logger"),
 "ScottReef_3250": (-dm((15, 29.002)), dm((121, 15.060)), "IMOS metadata", "shelf logger"),
 "OHAS_NCRO": (-dm((41, 14.93)), dm((53, 5.05)), "Royer 2016 Table 1", "OHASISBIO, recorded"),
 "OHAS_WKER": (-dm((46, 37.07)), dm((60, 34.20)), "Royer 2016 Table 1", "OHASISBIO, recorded"),
 "OHAS_SWAMS1": (-dm((43, 2.62)), dm((74, 36.30)), "Royer 2016 Table 1 (printed 'E' for latitude read as S)", "OHASISBIO, recorded; clock drift not determined"),
 "OHAS_SWAMS2": (-dm((42, 58.53)), dm((74, 31.49)), "Royer 2016 Table 1", "OHASISBIO, recorded"),
 "OHAS_SWAMS3": (-dm((42, 57.53)), dm((74, 37.77)), "Royer 2016 Table 1", "OHASISBIO, recorded"),
 "OHAS_SSEIR": (-dm((33, 30.98)), dm((70, 52.57)), "Royer 2016 Table 1", "OHASISBIO, recorded"),
 "OHAS_MAD": (-dm((26, 4.99)), dm((58, 8.40)), "Royer 2016 Table 1", "OHASISBIO, recorded; clock drift not determined"),
 "OHAS_NEAMS": (-dm((31, 34.12)), dm((83, 11.36)), "Royer 2016 Table 1", "OHASISBIO, LOST on recovery: no data"),
}
T_RX = {"T": 52 * 60 + 3, "C": 54 * 60 + 30}     # seconds after 00:00 UTC 8 Mar 2014, at H01W
T7 = 19 * 60 + 29
hms = lambda s: f"{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:04.1f}"
def pos(az, r): p = G.Direct(H01W[0], H01W[1], az, r * 1e3); return p["lat2"], p["lon2"]
def dist(a, b): return G.Inverse(a[0], a[1], b[0], b[1])["s12"] / 1e3
def r7_of_az(az): k = np.array(sorted(R7_AZ)); return float(np.interp(az, k, [R7_AZ[x] for x in k]))
def source_sets(branch):
    dt = (T_RX[branch] - T7) - R7["bto"] / C
    v = np.linspace(0, 250, 26); dT = dt / (1 + v / 1000 / C); dr_eq4 = v / 1000 * dT
    S = {}
    S["crossing_core"] = [(a, r7_of_az(a) + db) for a in (AZ - 0.5, AZ, AZ + 0.5) for db in (R7["bto_lo"] - R7["bto"], 0, R7["bto_hi"] - R7["bto"])]
    S["crossing_wide"] = [(a, r7_of_az(a) + db) for a in (AZ - 1, AZ - 0.5, AZ, AZ + 0.5, AZ + 1) for db in (R7["bto_lo"] - R7["bto"], 0, R7["bto_hi"] - R7["bto"])]
    S["eq4_strip_core"] = [(a, r7_of_az(a) + d) for a in (AZ - 0.5, AZ, AZ + 0.5) for d in dr_eq4]
    S["locality_strip_wide"] = [(a, R7["bto"] + d) for a in np.linspace(AZ - 1, AZ + 1, 9) for d in np.arange(-60, 251, 5)]
    S["haixun"] = [(None, None)]
    return S, float(dr_eq4.max())
rows, pts = [], []
for br in ("T", "C"):
    S, drmax = source_sets(br)
    for sset, P in S.items():
        for stn, (la, lo, src, note) in ST.items():
            ts = []
            for a, r in P:
                if a is None: s = HX; dH = dist(H01W, HX)
                else: s = pos(a, r); dH = r
                dX = dist(s, (la, lo)); dd = dX - dH
                sig = np.hypot(abs(dd) * DC / C ** 2, PICK)
                t = T_RX[br] + dd / C
                ts.append((t - 1.96 * sig, t, t + 1.96 * sig, dX, dH, sig))
            ts = np.array(ts); i0 = int(np.argmin(np.abs(ts[:, 4] - (dist(H01W, HX) if sset == "haixun" else R7["bto"])) + 0 * ts[:, 0]))
            ctr = ts[len(ts) // 2] if sset != "haixun" else ts[0]
            rows.append(dict(branch=br, h01w_time=hms(T_RX[br]), source_set=sset, station=stn, station_source=src, note=note,
                             window_start=hms(ts[:, 0].min()), window_end=hms(ts[:, 2].max()), centre=hms(ctr[1]),
                             window_start_s=ts[:, 0].min(), window_end_s=ts[:, 2].max(), centre_s=ctr[1],
                             width_s=ts[:, 2].max() - ts[:, 0].min(), range_km_min=ts[:, 3].min(), range_km_max=ts[:, 3].max(),
                             dt_minus_h01w_s_min=(ts[:, 1].min() - T_RX[br]), dt_minus_h01w_s_max=(ts[:, 1].max() - T_RX[br]),
                             sigma_s_max=ts[:, 5].max(), eq4_dr_max_km=drmax))
W = pd.DataFrame(rows); W.to_csv(OUT / "arrival_windows.csv", index=False, float_format="%.2f")
# superseded geometry, same construction, for the before/after table
old = (-26.2, 101.9); dH = dist(H01W, old)
old_rows = []
for br in ("T", "C"):
    for stn, (la, lo, *_ ) in ST.items():
        dd = dist(old, (la, lo)) - dH; sig = np.hypot(abs(dd) * DC / C ** 2, PICK)
        old_rows.append(dict(branch=br, station=stn, old_centre=hms(T_RX[br] + dd / C), old_centre_s=T_RX[br] + dd / C, old_sigma_s=sig, old_range_km=dist(old, (la, lo))))
pd.DataFrame(old_rows).to_csv(OUT / "arrival_windows_superseded_26p2S.csv", index=False, float_format="%.2f")
xs = pos(AZ, R7["bto"])
json.dump(dict(crossing=xs, h01w_to_haixun_km=dist(H01W, HX), haixun_az=G.Inverse(*H01W, *HX)["azi1"] % 360,
               superseded_h01w_range_km=dH, c=C, dc=DC, pick_s=PICK), open(OUT / "geometry.json", "w"), indent=1)
print(W[W.source_set.isin(["crossing_core", "haixun"])][["branch", "source_set", "station", "window_start", "centre", "window_end", "range_km_min", "dt_minus_h01w_s_min"]].to_string(index=False))
EOF
cd leg && python geometry_windows.py out 2>&1 | grep -v -i proj