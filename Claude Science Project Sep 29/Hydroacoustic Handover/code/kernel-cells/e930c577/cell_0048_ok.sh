cd leg; cat > gebco.py <<'EOF'
import json, numpy as np
from geographiclib.geodesic import Geodesic
D = "/Users/pete/Downloads/mh370-ocean-data/gebco/grid/"
M = json.load(open(D + "gebco_2026.json"))
Z = np.memmap(D + M["elevation_file"], dtype="<i2", mode="r", shape=(M["nlat"], M["nlon"]))
def elev(lat, lon):
    i = np.rint((np.asarray(lat) - M["lat0"]) / M["step_deg"]).astype(int); j = np.rint((np.asarray(lon) - M["lon0"]) / M["step_deg"]).astype(int)
    ok = (i >= 0) & (i < M["nlat"]) & (j >= 0) & (j < M["nlon"])
    out = np.full(np.shape(i), np.nan); out[ok] = Z[i[ok], j[ok]]; return out
def profile(a, b, step_km=1.0):
    l = Geodesic.WGS84.InverseLine(a[0], a[1], b[0], b[1]); n = int(l.s13 / 1e3 / step_km) + 1
    s = np.linspace(0, l.s13, n); P = [l.Position(x, Geodesic.LATITUDE | Geodesic.LONGITUDE) for x in s]
    la = np.array([p["lat2"] for p in P]); lo = np.array([p["lon2"] for p in P]); return s / 1e3, la, lo, elev(la, lo)
EOF
python -c "
import sys; sys.path.insert(0,'.'); import gebco as g
print(g.elev([-31.95,-30,-25.732,-25.975,-34.8903,-7.64],[115.86,100,101.369,101.461,114.1426,72.48]))"