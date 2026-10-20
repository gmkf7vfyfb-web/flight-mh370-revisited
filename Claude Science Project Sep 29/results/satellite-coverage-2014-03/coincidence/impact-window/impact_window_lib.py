"""Track B (impact window) helpers, satellite-coverage module, 20 Oct 2026. Provisional.
- cross_fast: same rule as coincide.crossings (first ahead->behind sign change of the along-track coordinate, linear
  interpolation, z > 0.5 guard) solved by bisection for ~2M static targets; validated against coincide.crossings on
  5 passes x 20,000 targets: identical NaN pattern, max |dt| = 0.0 s, max |d offset| = 0.0 km.
- xarc: signed distance (NM, + = east/outside) from the shared sea-level 7th arc polyline (arcs-sea-level.csv,
  densified to 0.002 deg latitude), nearest point on the unit sphere (R = 6371 km).
- Weights: rebuild_seed.py (exec of option_table_0019.seed_terms, final reduction replaced by 'return cells, f4, g');
  within-seed multinomial draws, then seeds pooled by evidence (multinomial over seed ln Z), as option_table_0019.
"""
import numpy as np, coincide
NM = 1.852
def cross_fast(t_s, lat, lon, U):
    n, u, r = coincide.sat_frames(lat, lon); K = len(t_s)
    a0 = U @ u[0]; a1 = U @ u[-1]; ok = (a0 > 0) & (a1 <= 0)
    lo = np.zeros(len(U), int); hi = np.full(len(U), K - 1)
    for _ in range(int(np.ceil(np.log2(K))) + 1):
        mid = (lo + hi) // 2; pos = (U * u[mid]).sum(1) > 0
        lo = np.where(pos, mid, lo); hi = np.where(pos, hi, mid)
        if (hi - lo <= 1).all(): break
    k = lo; A0 = (U * u[k]).sum(1); A1 = (U * u[k + 1]).sum(1); f = A0 / (A0 - A1 + 1e-30)
    tc = t_s[k] + f * (t_s[k + 1] - t_s[k])
    c = (U * r[k]).sum(1) + f * ((U * r[k + 1]).sum(1) - (U * r[k]).sum(1)); z = (U * n[k]).sum(1) + f * ((U * n[k + 1]).sum(1) - (U * n[k]).sum(1))
    off = coincide.R * np.arctan2(c, z); good = ok & (z > 0.5)
    return np.where(good, tc, np.nan), np.where(good, off, np.nan)
def make_xarc(arcs):
    from scipy.spatial import cKDTree
    a7 = arcs.dropna(subset=['lon_arc7']).sort_values('lat'); LATD = np.arange(a7.lat.min(), a7.lat.max() + 1e-9, 0.002)
    T = cKDTree(coincide.unit(LATD, np.interp(LATD, a7.lat, a7.lon_arc7)))
    def xarc(lat, lon):
        d, _ = T.query(coincide.unit(lat, lon)); dist = 2 * np.arcsin(np.clip(d / 2, 0, 1)) * 6371.0 / NM
        return np.where(lon > np.interp(lat, a7.lat, a7.lon_arc7), 1, -1) * dist
    return xarc
def sun_jdfr(t_after_0000Z_8mar):
    jd = 2451545.0 + (1394236800.0 + t_after_0000Z_8mar - 946728000.0) / 86400.0
    return np.floor(jd), jd - np.floor(jd)
