import os
"""Geometry and straight-path (geodesic) bathymetry check for each case x station.

Range/back-azimuth: WGS84 geodesic (pyproj) from the triad centroid (StationXML element positions for the event epoch)
to the impact point. Back-azimuth = azimuth from station toward source (degrees clockwise from N).
Path check: GEBCO_2026 15-arc-second grid sampled every 1 km along the geodesic (nearest cell).
Reported per path: min depth on path, length of land (elev >= 0), length shallower than 50 m, 200 m, 1000 m,
and the 'blocked' flag used in the module's arc_line_of_sight.py: land or water shallower than min(receiver depth, 200 m)
more than 20 km from the receiver.
"""
import numpy as np, netCDF4
from pyproj import Geod
G = Geod(ellps="WGS84")
GEBCO = os.path.join(os.environ.get("MH370_OCEAN_DATA", "mh370-ocean-data"), "gebco", "GEBCO_2026.nc")

class Gebco:
    def __init__(self, fn=GEBCO):
        self.nc = netCDF4.Dataset(fn)
        self.lat = self.nc.variables["lat"][:].data
        self.lon = self.nc.variables["lon"][:].data
        self.z = self.nc.variables["elevation"]
        self.dlat = self.lat[1] - self.lat[0]; self.dlon = self.lon[1] - self.lon[0]
    def sample(self, lats, lons):
        i = np.clip(np.round((np.asarray(lats) - self.lat[0]) / self.dlat).astype(int), 0, len(self.lat) - 1)
        j = np.clip(np.round(((np.asarray(lons) + 180) % 360 - 180 - self.lon[0]) / self.dlon).astype(int), 0, len(self.lon) - 1)
        out = np.empty(len(i), dtype=float)
        # read row by row in blocks to keep memory small
        order = np.argsort(i)
        for a in range(0, len(order), 2000):
            idx = order[a:a + 2000]
            i0, i1 = i[idx].min(), i[idx].max(); j0, j1 = j[idx].min(), j[idx].max()
            if (i1 - i0 + 1) * (j1 - j0 + 1) < 4e7:
                blk = self.z[i0:i1 + 1, j0:j1 + 1]
                out[idx] = blk[i[idx] - i0, j[idx] - j0]
            else:
                for q in idx: out[q] = self.z[i[q], j[q]]
        return out
    def box(self, lat0, lat1, lon0, lon1, step=1):
        i0 = int((lat0 - self.lat[0]) / self.dlat); i1 = int((lat1 - self.lat[0]) / self.dlat)
        j0 = int((lon0 - self.lon[0]) / self.dlon); j1 = int((lon1 - self.lon[0]) / self.dlon)
        return self.lat[i0:i1:step], self.lon[j0:j1:step], np.asarray(self.z[i0:i1:step, j0:j1:step], dtype=float)

def geodesic_profile(gb, src, rcv, step_km=1.0):
    """src, rcv = (lat, lon). Returns dist from receiver (km), lats, lons, elevation (m)."""
    az, baz, d = G.inv(rcv[1], rcv[0], src[1], src[0])
    n = max(int(d / 1000 / step_km), 2)
    pts = G.npts(rcv[1], rcv[0], src[1], src[0], n)
    lons = np.r_[rcv[1], [p[0] for p in pts], src[1]]; lats = np.r_[rcv[0], [p[1] for p in pts], src[0]]
    dist = np.linspace(0, d / 1000, len(lats))
    return dist, lats, lons, gb.sample(lats, lons), az % 360, d / 1000

def path_summary(dist, z, rcv_depth_m):
    dd = np.gradient(dist)
    far = dist > 20.0
    thr = min(rcv_depth_m, 200.0)
    blocked = bool(np.any(far & ((z >= 0) | (-z < thr))))
    return dict(min_depth_m=float(-z[1:-1].max()) if len(z) > 2 else float(-z.max()),
                land_km=float(dd[z >= 0].sum()), shallower_50m_km=float(dd[-z < 50].sum()),
                shallower_200m_km=float(dd[-z < 200].sum()), shallower_1000m_km=float(dd[-z < 1000].sum()),
                blocked_module_rule=blocked)
