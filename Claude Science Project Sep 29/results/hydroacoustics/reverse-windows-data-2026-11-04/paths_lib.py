"""Geodesic paths (WGS84) and a geometric line-of-sight screen on GEBCO 2026 (15 arc-s).

The screen re-implements the rule of the hydro_data.sqlite `arc_path` table (README, 23 Oct 2026):
  blocked            : land, or water shallower than min(receiver depth, 200 m), more than 20 km from the receiver
  large attenuation  : >= 10 km of path shallower than 1,000 m, more than 100 km from the receiver
  ridge (partial)    : deep receivers only, >= 10 km of path shallower than the hydrophone
  clear              : none of these
It is a geometric screen, not a transmission-loss result. Validated against the DB table in validate_blocking.py.
"""
from __future__ import annotations
import numpy as np
from pyproj import Geod

GEOD = Geod(ellps='WGS84')
GEBCO = '/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026_elevation.i16'
_LON0, _LAT0, _ST = 40.00208333333333, -59.99791666666667, 1 / 240
_G = np.memmap(GEBCO, dtype='<i2', mode='r', shape=(21600, 33600))   # rows south->north, cols west->east


def elev(lat, lon):
    i = np.rint((np.asarray(lat) - _LAT0) / _ST).astype(int)
    j = np.rint((np.asarray(lon) - _LON0) / _ST).astype(int)
    return _G[np.clip(i, 0, 21599), np.clip(j, 0, 33599)].astype(float)


def path(src_lat, src_lon, rcv_lat, rcv_lon, step_km=1.0):
    """Samples along the geodesic source->receiver; returns (dist_from_src_km, lat, lon, total_km)."""
    az, baz, d = GEOD.inv(src_lon, src_lat, rcv_lon, rcv_lat)
    n = max(int(d / 1000 / step_km) - 1, 1)
    pts = np.array(GEOD.npts(src_lon, src_lat, rcv_lon, rcv_lat, n))
    lon = np.r_[src_lon, pts[:, 0], rcv_lon]
    lat = np.r_[src_lat, pts[:, 1], rcv_lat]
    s = np.r_[0, (np.arange(1, n + 1)) * d / (n + 1), d] / 1000
    return s, lat, lon, d / 1000, az, baz


def screen(src_lat, src_lon, rcv_lat, rcv_lon, rcv_depth_m, deep_receiver=None, step_km=1.0):
    s, lat, lon, L, az, baz = path(src_lat, src_lon, rcv_lat, rcv_lon, step_km)
    z = elev(lat, lon)                       # m, positive up
    ds = L / (len(s) - 1)
    from_rcv = L - s
    depth = -z
    blk_lim = min(rcv_depth_m, 200.0)
    blocked = ((z >= 0) | (depth < blk_lim)) & (from_rcv > 20)
    land = (z >= 0) & (from_rcv > 20)
    shallow1000 = (depth < 1000) & (from_rcv > 100)
    if deep_receiver is None:
        deep_receiver = rcv_depth_m >= 900
    above_rcv = (depth < rcv_depth_m) & deep_receiver
    km_block = blocked.sum() * ds
    km_1000 = shallow1000.sum() * ds
    km_above = above_rcv.sum() * ds
    if km_block > 0:
        cls = 'blocked'
    elif km_1000 >= 10:
        cls = 'large attenuation'
    elif km_above >= 10:
        cls = 'ridge (partial)'
    else:
        cls = 'clear'
    # extent of the blocked stretch (for the mixed-path sensitivity): from first to last blocked sample
    if km_block > 0:
        ib = np.where(blocked)[0]
        span_block = (s[ib[-1]] - s[ib[0]]) + ds
        block_to_rcv = L - s[ib[0]]
    else:
        span_block = 0.0
        block_to_rcv = 0.0
    k = np.argmin(np.where(from_rcv > 20, z * -1, np.inf))   # shallowest point > 20 km from receiver
    return dict(dist_km=L, az_src_deg=az, baz_rcv_deg=baz % 360, land_km=land.sum() * ds, blocking_km=km_block,
                km_shallower_1000m=km_1000, km_shallower_receiver=km_above, shallowest_m=float(depth[k]),
                shallowest_lat=float(lat[k]), shallowest_lon=float(lon[k]), block_span_km=span_block,
                block_start_to_rcv_km=block_to_rcv, cls=cls)
