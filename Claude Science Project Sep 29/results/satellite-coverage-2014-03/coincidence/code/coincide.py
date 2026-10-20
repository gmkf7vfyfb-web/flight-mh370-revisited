
"""Space-time coincidence between satellite passes and moving or static targets.

A pass 'covers' a target when the satellite's zero-Doppler line (the plane through the sub-satellite point normal to the
ground-track direction) sweeps over the target, and at that instant the target's signed cross-track ground offset lies
inside the sensor's access band. Optical: |offset| <= ground offset at max off-nadir + half swath. SAR: near <= |offset|
<= far on an allowed look side. Earth is spherical (R = 6371 km) for the offset; ground track direction from consecutive
sub-satellite points in Earth-fixed coordinates, so Earth rotation is included.
"""
import numpy as np
R = 6371.0

def unit(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)], -1)

def sat_frames(lat, lon):
    """n (up), u (along-track), r (right of track) unit vectors at each step (arrays of shape (K,3))."""
    n = unit(lat, lon)
    d = np.gradient(n, axis=0)
    u = d - (d*n).sum(-1, keepdims=True)*n
    u /= np.linalg.norm(u, axis=-1, keepdims=True)
    r = np.cross(u, n)
    return n, u, r

def crossings(t_s, lat, lon, tgt):
    """t_s: (K,) seconds; lat, lon: (K,) sub-satellite points of ONE contiguous pass segment.
    tgt: (M, K, 3) target unit vectors at the same K times (static targets: broadcast).
    Returns per target: crossing time (s, NaN if none), signed cross-track ground offset km (+ = right of track),
    along-track sign check. Uses the first sign change of along-track coordinate within the segment."""
    n, u, r = sat_frames(lat, lon)
    a = (tgt * u[None]).sum(-1)              # along-track sine
    c = (tgt * r[None]).sum(-1)
    z = (tgt * n[None]).sum(-1)
    s = np.sign(a)
    ch = (s[:, :-1] > 0) & (s[:, 1:] <= 0)    # target passes from ahead to behind
    has = ch.any(1)
    k = np.where(has, ch.argmax(1), 0)
    M = tgt.shape[0]; idx = np.arange(M)
    a0, a1 = a[idx, k], a[idx, k+1]
    f = np.where(has, a0/(a0 - a1 + 1e-30), np.nan)
    tc = t_s[k] + f*(t_s[k+1]-t_s[k])
    cc = c[idx, k] + f*(c[idx, k+1]-c[idx, k]); zz = z[idx, k] + f*(z[idx, k+1]-z[idx, k])
    off = R*np.arctan2(cc, zz)
    tc = np.where(has & (zz > 0.5), tc, np.nan)
    off = np.where(np.isfinite(tc), off, np.nan)
    return tc, off

def in_band(off_km, g, near_km, far_km):
    """g: dict from geometry_params; near/far for this pass (scalars)."""
    a = np.abs(off_km)
    if g["is_sar"]:
        side_ok = np.zeros_like(a, dtype=bool)
        if "right" in g["sides"]: side_ok |= off_km > 0
        if "left" in g["sides"]: side_ok |= off_km < 0
        return side_ok & (a >= near_km) & (a <= far_km)
    return a <= far_km
