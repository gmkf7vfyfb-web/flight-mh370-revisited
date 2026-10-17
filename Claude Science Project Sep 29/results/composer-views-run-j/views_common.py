"""Shared definitions for the composer views on run J (numpy implementation).

Equal-area grid: as the composer's proposed summary.rs extension (results/composer-summary-rs.patch): cells uniform in longitude
(0.25 deg) and in the WGS-84 authalic function q(latitude); q step = q(0.25 deg) - q(0), so every cell has the same area
(0.5 a^2 dlon dq, about 769 km^2). Extent here 50-6 S, 78-116 E (run J impacts reach 46.6-10.4 S, 82.9-111.5 E).
Sub-bins: the union of 0.01 deg latitude edges and equal-area row edges, so that 1-D latitude products at 0.01 deg and
row-wise (arc-uniform) reweighting are both exact sums of sub-bins.
"""
import numpy as np
A_KM = 6378.137; E2 = 0.00669437999014; E = np.sqrt(E2)
STEP = 0.25; LAT0, LAT1 = -50.0, -6.0; LON0, LON1 = 78.0, 116.0

def authalic_q(lat):
    s = np.sin(np.radians(lat))
    return (1 - E2) * (s / (1 - E2 * s * s) - np.log((1 - E * s) / (1 + E * s)) / (2 * E))

QSTEP = authalic_q(STEP) - authalic_q(0.0)
CELL_KM2 = 0.5 * A_KM * A_KM * np.radians(STEP) * QSTEP
Q0 = authalic_q(LAT0)
NY = int(np.ceil((authalic_q(LAT1) - Q0) / QSTEP)); NX = int(round((LON1 - LON0) / STEP))

def _inv_q(q):
    lo, hi = np.full_like(q, -90.0), np.full_like(q, 90.0)
    for _ in range(80):
        mid = 0.5 * (lo + hi); up = authalic_q(mid) < q; lo = np.where(up, mid, lo); hi = np.where(up, hi, mid)
    return 0.5 * (lo + hi)

ROW_EDGES = _inv_q(Q0 + np.arange(NY + 1) * QSTEP)          # latitude edges of the equal-area rows (last one >= LAT1)
L01_EDGES = np.round(np.arange(LAT0, LAT1 + 1e-9, 0.01), 2)  # 0.01 deg edges
SUB_EDGES = np.unique(np.concatenate([L01_EDGES, ROW_EDGES[ROW_EDGES < LAT1]]))
NSUB = len(SUB_EDGES) - 1
_mid = 0.5 * (SUB_EDGES[1:] + SUB_EDGES[:-1])
SUB_ROW = np.clip(np.searchsorted(ROW_EDGES, _mid, side='right') - 1, 0, NY - 1)
SUB_L01 = np.clip(np.searchsorted(L01_EDGES, _mid, side='right') - 1, 0, len(L01_EDGES) - 2)
L01_MID = 0.5 * (L01_EDGES[1:] + L01_EDGES[:-1]); ROW_MID = 0.5 * (ROW_EDGES[1:] + ROW_EDGES[:-1])

def sub_index(lat):
    """Sub-bin index; NSUB for rows outside [LAT0, LAT1)."""
    i = np.searchsorted(SUB_EDGES, lat, side='right') - 1
    return np.where((lat >= LAT0) & (lat < LAT1) & np.isfinite(lat), i, NSUB)

def cell_index(lat, lon):
    """Equal-area cell index y*NX+x; NY*NX outside the extent."""
    y = np.floor((authalic_q(np.where(np.isfinite(lat), lat, 0.0)) - Q0) / QSTEP).astype(np.int64)
    x = np.floor((lon - LON0) / STEP).astype(np.int64)
    ok = (lat >= LAT0) & (lat < LAT1) & (lon >= LON0) & (lon < LON1) & (y >= 0) & (y < NY) & (x >= 0) & (x < NX)
    return np.where(ok, y * NX + x, NY * NX)

# drift node grid (run A, 30 NM) and bilinear-in-L lookup normalised over evaluated corners (compose_drift_runj.corners)
DG = dict(lat0=-41.166666666666664, lon0=83.96226004720266, dlat=0.5, dlon=0.5856322967993869, nlat=41, nlon=38)
DNC = DG['nlat'] * DG['nlon']

def drift_corners(lat, lon):
    fi = (lat - DG['lat0']) / DG['dlat']; fj = (lon - DG['lon0']) / DG['dlon']
    inside = (fi >= 0) & (fj >= 0) & (fi <= DG['nlat'] - 1) & (fj <= DG['nlon'] - 1)
    i = np.minimum(np.floor(np.where(inside, fi, 0)).astype(int), DG['nlat'] - 2); j = np.minimum(np.floor(np.where(inside, fj, 0)).astype(int), DG['nlon'] - 2)
    ti, tj = fi - i, fj - j
    W = np.stack([(1 - ti) * (1 - tj), ti * (1 - tj), (1 - ti) * tj, ti * tj], 1)
    cid = i * DG['nlon'] + j; nid = np.stack([cid, cid + DG['nlon'], cid + 1, cid + DG['nlon'] + 1], 1)
    return inside, nid, W

def drift_lookup(inside, nid, W, nodeL):
    """L per row (linear interpolation in L over evaluated corners); NaN where no evaluated corner (not computed)."""
    good = inside[:, None] & np.isfinite(nodeL[nid]) & (W > 0); Wg = np.where(good, W, 0.0); sw = Wg.sum(1)
    v = (Wg * np.where(good, nodeL[nid], 0.0)).sum(1)
    return np.where(sw > 0, v / np.where(sw > 0, sw, 1.0), np.nan)

# ---- 7th arc as a small circle (arc_line.py fit to run J 00:19:29 positions with |BTO residual| < 20 us)
import pathlib as _pl
_ARC = _pl.Path('/Users/pete/Downloads/mh370-exchange/composer/run-j-views/arc-line.npz')
NM_R = 3440.065
if _ARC.exists():
    _a = np.load(_ARC); ARC_C = tuple(float(x) for x in _a['centre']); ARC_RAD = float(_a['radius_deg'])
else:
    ARC_C, ARC_RAD = (0.57, 64.252), 44.501
ARC_NM_PER_DEG = NM_R * np.radians(1.0) * np.sin(np.radians(ARC_RAD))   # NM of arc per degree of azimuth about the centre
SBIN_NM = 10.0; NSB = 400                                                # arc bins: 10 NM from the arc's southern tip

def arc_s(lat, lon):
    """Arc position (NM along the 7th arc, from its southern tip at azimuth 180 deg, increasing north along the eastern branch)
    of the projection of (lat, lon) onto the arc circle: azimuth of the point seen from the circle centre."""
    p1, l1 = np.radians(ARC_C[0]), np.radians(ARC_C[1]); p2, l2 = np.radians(lat), np.radians(lon)
    az = np.degrees(np.arctan2(np.sin(l2 - l1) * np.cos(p2), np.cos(p1) * np.sin(p2) - np.sin(p1) * np.cos(p2) * np.cos(l2 - l1)))
    az = np.mod(az, 360.0)
    return (180.0 - az) * ARC_NM_PER_DEG

def arc_point(s):
    """Latitude, longitude of the arc point at arc position s (NM)."""
    az = np.radians(180.0 - np.asarray(s, float) / ARC_NM_PER_DEG); d = np.radians(ARC_RAD); p1, l1 = np.radians(ARC_C[0]), np.radians(ARC_C[1])
    p2 = np.arcsin(np.sin(p1) * np.cos(d) + np.cos(p1) * np.sin(d) * np.cos(az))
    l2 = l1 + np.arctan2(np.sin(az) * np.sin(d) * np.cos(p1), np.cos(d) - np.sin(p1) * np.sin(p2))
    return np.degrees(p2), np.degrees(l2)

def sbin_index(s):
    i = np.floor(s / SBIN_NM).astype(np.int64)
    return np.where(np.isfinite(s) & (i >= 0) & (i < NSB), i, NSB)
