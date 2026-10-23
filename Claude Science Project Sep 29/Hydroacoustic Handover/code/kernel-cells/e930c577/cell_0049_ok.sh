cd leg; cat > blockage.py <<'EOF'
"""GEBCO_2026 path blockage from locality source points to every receiver (geodesic, 1 km sampling).
Declared rule (this leg, not pre-registered): exclude the last 50 km before the receiver (its own slope/shelf).
BLOCKED: any land, or > 10 km shallower than 200 m;  PARTIAL: minimum depth shallower than 1,500 m (the path meets the
SOFAR-axis band, ~1,000-1,300 m here);  OPEN: otherwise."""
import sys, json; sys.path.insert(0, "."); import numpy as np, pandas as pd
import gebco as G; from geometry_windows import ST, pos, AZ, R7, HX
SRC = {"crossing": pos(AZ, R7["bto"]), "haixun": HX, "strip_R7-60": pos(AZ, R7["bto"] - 60), "strip_R7+100": pos(AZ, R7["bto"] + 100),
       "strip_R7+250": pos(AZ, R7["bto"] + 250), "strip_R7+250_az-1": pos(AZ - 1, R7["bto"] + 250), "strip_R7+250_az+1": pos(AZ + 1, R7["bto"] + 250)}
SRC["H01W_check"] = None
rows = []
for sn, s in SRC.items():
    if s is None: continue
    for stn, (la, lo, *_ ) in list(ST.items()) + [("H01W", (-34.8903, 114.1426, "", ""))]:
        if stn == "H01W": la, lo = -34.8903, 114.1426
        km, pla, plo, z = G.profile(s, (la, lo)); m = km <= km[-1] - 50
        zz = z[m]; land = float((zz > 0).sum()); sh200 = float((zz > -200).sum()); sh1000 = float((zz > -1000).sum()); mind = float(-np.nanmax(zz))
        k = int(np.nanargmax(zz)); cls = "BLOCKED" if (land > 0 or sh200 > 10) else ("PARTIAL" if mind < 1500 else "OPEN")
        rows.append(dict(source=sn, station=stn, range_km=round(km[-1], 1), land_km=land, km_shallower_200m=sh200, km_shallower_1000m=sh1000,
                         min_depth_m=round(mind), min_depth_at=f"{pla[m][k]:.2f},{plo[m][k]:.2f}", min_depth_km_from_source=round(km[m][k]), verdict=cls))
B = pd.DataFrame(rows); B.to_csv(sys.argv[1], index=False)
print(B.pivot(index="station", columns="source", values="verdict").to_string())
print(B[B.source.isin(["crossing", "haixun"])][["source", "station", "range_km", "land_km", "km_shallower_200m", "km_shallower_1000m", "min_depth_m", "min_depth_at", "verdict"]].to_string(index=False))
EOF
python blockage.py out/path_blockage.csv 2>&1 | grep -v -i proj