"""Shortest all-water route from a source to a receiver over GEBCO_2026, for a set of minimum-depth thresholds.

Grid: GEBCO 15-arc-s cells aggregated into blocks of `agg` x `agg` cells (agg=12 -> 0.05 deg). A block's depth is the
DEEPEST cell in the block (permissive: narrow straits stay open; this can only make a water path look easier).
Graph: 8-neighbour, edge length = haversine distance between block centres (R = 6371.0 km; spherical, <0.5 % vs WGS84).
A block is passable if depth >= threshold. The source and receiver blocks are always passable (source sits in shallow water).
Output per threshold: route length (km) or None if no route; for the route: length in water shallower than 50/200/1000 m
(using the same block depths) and the shallowest block on the route (bottleneck depth).
"""
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra

R = 6371.0

def hav(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    dphi = p2 - p1; dl = np.radians(lo2 - lo1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

def block_depth(gb, lat0, lat1, lon0, lon1, agg=12):
    la, lo, z = gb.box(lat0, lat1, lon0, lon1)
    ni, nj = z.shape[0] // agg, z.shape[1] // agg
    z = z[:ni * agg, :nj * agg].reshape(ni, agg, nj, agg)
    depth = -z.min(axis=(1, 3))       # deepest cell (most negative elevation) -> largest depth
    lat_c = la[:ni * agg].reshape(ni, agg).mean(1); lon_c = lo[:nj * agg].reshape(nj, agg).mean(1)
    return lat_c, lon_c, depth

def route(lat_c, lon_c, depth, src, rcv, thresholds=(1, 20, 30, 50, 100, 200, 500, 1000)):
    ni, nj = depth.shape
    LA, LO = np.meshgrid(lat_c, lon_c, indexing="ij")
    idx = np.arange(ni * nj).reshape(ni, nj)
    si = (np.abs(lat_c - src[0]).argmin(), np.abs(lon_c - src[1]).argmin())
    ri = (np.abs(lat_c - rcv[0]).argmin(), np.abs(lon_c - rcv[1]).argmin())
    out = {}
    for th in thresholds:
        ok = depth >= th
        ok[si] = True; ok[ri] = True
        rows, cols, w = [], [], []
        for di, dj in [(0, 1), (1, 0), (1, 1), (1, -1)]:
            ja = slice(0, nj - 1) if dj == 1 else (slice(1, nj) if dj == -1 else slice(0, nj))
            jb = slice(1, nj) if dj == 1 else (slice(0, nj - 1) if dj == -1 else slice(0, nj))
            a = idx[0:ni - di, ja]
            b = idx[di:ni, jb]
            m = ok.ravel()[a.ravel()] & ok.ravel()[b.ravel()]
            aa, bb = a.ravel()[m], b.ravel()[m]
            d = hav(LA.ravel()[aa], LO.ravel()[aa], LA.ravel()[bb], LO.ravel()[bb])
            rows += [aa, bb]; cols += [bb, aa]; w += [d, d]
        g = coo_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))), shape=(ni * nj, ni * nj)).tocsr()
        dist, pred = dijkstra(g, indices=idx[si], return_predecessors=True)
        L = dist[idx[ri]]
        if not np.isfinite(L):
            out[th] = None; continue
        path = [idx[ri]]
        while path[-1] != idx[si]:
            path.append(pred[path[-1]])
        path = np.array(path[::-1]); pd_ = depth.ravel()[path]
        seg = hav(LA.ravel()[path[:-1]], LO.ravel()[path[:-1]], LA.ravel()[path[1:]], LO.ravel()[path[1:]])
        dmid = np.minimum(pd_[:-1], pd_[1:])
        out[th] = dict(length_km=float(L), shallower_50m_km=float(seg[dmid < 50].sum()), shallower_200m_km=float(seg[dmid < 200].sum()),
                       shallower_1000m_km=float(seg[dmid < 1000].sum()), bottleneck_depth_m=float(pd_[1:-1].min()) if len(pd_) > 2 else None,
                       lats=LA.ravel()[path], lons=LO.ravel()[path], depths=pd_)
    return out
