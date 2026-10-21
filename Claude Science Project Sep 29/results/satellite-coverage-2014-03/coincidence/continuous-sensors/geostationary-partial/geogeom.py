"""Geostationary view geometry for an aircraft at altitude: view zenith angle, effective pixel size,
scan-line crossing time, parallax-displaced (apparent) position, sun elevation.

Frames: WGS84 ECEF. Satellite ECEF from SGP4 (TEME -> ECEF by GMST rotation, as in satgeom.py).
Scan-line coordinate: CGMS normalised geostationary projection line angle, y = asin(-(z_t - z_s)/|d|) in deg,
(north negative), measured from the satellite's actual position (so orbit inclination is included).
A full-disc scan is modelled as linear in y between y_first and y_last over duration D (seconds).
"""
import numpy as np, pandas as pd

A_WGS = 6378.137; F_WGS = 1/298.257223563; E2 = F_WGS*(2-F_WGS)


def geodetic_to_ecef(lat, lon, h_km):
    la, lo = np.radians(lat), np.radians(lon)
    N = A_WGS/np.sqrt(1-E2*np.sin(la)**2)
    return np.stack([(N+h_km)*np.cos(la)*np.cos(lo), (N+h_km)*np.cos(la)*np.sin(lo),
                     (N*(1-E2)+h_km)*np.sin(la)], -1)


def up_vector(lat, lon):
    la, lo = np.radians(lat), np.radians(lon)
    return np.stack([np.cos(la)*np.cos(lo), np.cos(la)*np.sin(lo), np.sin(la)], -1)


def ecef_to_geodetic(r):
    x, y, z = r[..., 0], r[..., 1], r[..., 2]
    lon = np.degrees(np.arctan2(y, x)); p = np.hypot(x, y)
    lat = np.arctan2(z, p*(1-E2))
    for _ in range(6):
        N = A_WGS/np.sqrt(1-E2*np.sin(lat)**2); h = p/np.cos(lat) - N
        lat = np.arctan2(z, p*(1-E2*N/(N+h)))
    N = A_WGS/np.sqrt(1-E2*np.sin(lat)**2); h = p/np.cos(lat) - N
    return np.degrees(lat), lon, h


def view(sat_ecef, lat, lon, h_km):
    """sat_ecef (...,3) broadcastable with target arrays. Returns vza_deg, slant_km, line_angle_deg (CGMS y)."""
    t = geodetic_to_ecef(lat, lon, h_km)
    d = sat_ecef - t
    rng = np.linalg.norm(d, axis=-1)
    cosz = (d*up_vector(lat, lon)).sum(-1)/rng
    vza = np.degrees(np.arccos(np.clip(cosz, -1, 1)))
    los = t - sat_ecef  # satellite -> target
    y = np.degrees(np.arcsin(-los[..., 2]/rng))
    return vza, rng, y


def pixel_size(s0_km, slant_km, vza_deg, nadir_range_km=35786.0):
    """Nadir sampling s0 scaled to the aircraft: minor axis (perpendicular to the line of sight azimuth) and
    major axis (along it, divided by cos VZA), and the area-equivalent size sqrt(minor*major)."""
    minor = s0_km*slant_km/nadir_range_km
    major = minor/np.cos(np.radians(vza_deg))
    return minor, major, np.sqrt(minor*major)


def apparent_position(sat_ecef, lat, lon, h_km):
    """Where the line of sight from the satellite through the aircraft meets the ellipsoid surface
    (the position at which a geolocated image shows a feature at altitude h). Returns lat, lon, shift_km."""
    t = geodetic_to_ecef(lat, lon, h_km)
    s = np.broadcast_to(sat_ecef, t.shape)
    u = t - s; u = u/np.linalg.norm(u, axis=-1, keepdims=True)
    # solve |s + k u| on ellipsoid: scale z by 1/sqrt(1-E2)
    sc = np.array([1, 1, 1/np.sqrt(1-E2)])
    S = s*sc; U = u*sc
    a = (U*U).sum(-1); b = 2*(S*U).sum(-1); c = (S*S).sum(-1) - A_WGS**2
    k = (-b - np.sqrt(np.maximum(b*b-4*a*c, 0)))/(2*a)
    g = s + k[..., None]*u
    la, lo, _ = ecef_to_geodetic(g)
    g0 = geodetic_to_ecef(lat, lon, 0*np.asarray(h_km))
    return la, lo, np.linalg.norm(g - g0, axis=-1)


def sat_ecef_series(sg, satrec, times):
    """satrec: sgp4 Satrec; times: DatetimeIndex (UTC). Returns (K,3) ECEF km."""
    jd, fr = sg.jd_from_times(times)
    e, r, v = satrec.sgp4_array(jd, fr)
    r = np.asarray(r); g = sg.gmst_rad(jd, fr)
    x = np.cos(g)*r[:, 0] + np.sin(g)*r[:, 1]
    y = -np.sin(g)*r[:, 0] + np.cos(g)*r[:, 1]
    return np.stack([x, y, r[:, 2]], -1)


def weighted_quantile(values, weights, qs, axis=0):
    """Weighted quantiles along axis 0 of a (N, ...) array."""
    v = np.moveaxis(values, axis, 0); idx = np.argsort(v, axis=0)
    vs = np.take_along_axis(v, idx, 0)
    w = np.broadcast_to(weights.reshape((-1,)+(1,)*(v.ndim-1)), v.shape)
    ws = np.take_along_axis(w, idx, 0)
    cw = np.cumsum(ws, 0); cw = cw/cw[-1]
    out = []
    for q in qs:
        k = (cw < q).sum(0)
        k = np.minimum(k, v.shape[0]-1)
        out.append(np.take_along_axis(vs, k[None], 0)[0])
    return np.array(out)
