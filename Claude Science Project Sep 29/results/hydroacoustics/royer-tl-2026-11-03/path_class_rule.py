"""Path-type rule (recovered 3 Nov 2026 from path-sections-index.csv, exact on the index).
shallow_inner_m = shallowest seabed depth along the section, excluding 50 km at each end.
axis_m = median along the section of the sound-channel axis depth (minimum sound speed, nodes to 3,000 m).
blocked: path crosses land, or shallow_inner_m < 200 m
ridge above the channel axis: shallow_inner_m < axis_m
ridge near the channel axis: axis_m <= shallow_inner_m < axis_m + 1000
clear deep path: shallow_inner_m >= axis_m + 1000"""
import sys, numpy as np
sys.path.insert(0, "tlchain/tl-chain-2026-10-27")
from tlchain import paths as P
def classify(sec):
    rr = sec["range_km"]; d = sec["depth_native"]; L = rr[-1]; inner = (rr > 50) & (rr < L - 50)
    si = float(np.min(d[inner])) if inner.any() else float(np.min(d))
    zs, rn, Cm = P.node_matrix(sec, zmax=3000.0); ax = float(np.median(zs[np.argmin(Cm, axis=0)]))
    land = bool((d[1:-1] <= 0).any())
    if land or si < 200: c = "blocked"
    elif si < ax: c = "ridge above the channel axis"
    elif si < ax + 1000: c = "ridge near the channel axis"
    else: c = "clear deep path"
    return dict(path_class=c, shallow_inner_m=si, axis_m=ax, land=land)
