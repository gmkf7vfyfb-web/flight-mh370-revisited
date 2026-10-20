
"""Propagate March 2014 element sets with SGP4 and derive ground tracks, sun elevation and across-track access limits.
TEME -> ECEF uses GMST (IAU 1982) only; polar motion and nutation are neglected (sub-km on the ground).
"""
import numpy as np, pandas as pd
from sgp4.api import Satrec, SatrecArray, jday

R_E = 6378.137; F = 1/298.257223563; E2 = F*(2-F)

def jd_from_times(times):
    t = pd.DatetimeIndex(times)
    jd = np.full(len(t), 2451545.0) + (t.tz_convert(None) - pd.Timestamp("2000-01-01T12:00:00")).total_seconds().values/86400.0
    fr = jd - np.floor(jd); return np.floor(jd), fr

def gmst_rad(jd, fr):
    T = (jd + fr - 2451545.0)/36525.0
    g = 67310.54841 + (876600.0*3600 + 8640184.812866)*T + 0.093104*T**2 - 6.2e-6*T**3  # seconds
    return np.radians((g % 86400.0)/240.0)

def teme_to_geodetic(r_teme, jd, fr):
    g = gmst_rad(jd, fr)
    x = np.cos(g)*r_teme[:,0] + np.sin(g)*r_teme[:,1]
    y = -np.sin(g)*r_teme[:,0] + np.cos(g)*r_teme[:,1]
    z = r_teme[:,2]
    lon = np.degrees(np.arctan2(y, x))
    p = np.hypot(x, y); lat = np.arctan2(z, p*(1-E2))
    for _ in range(5):
        N = R_E/np.sqrt(1-E2*np.sin(lat)**2); h = p/np.cos(lat) - N
        lat = np.arctan2(z, p*(1-E2*N/(N+h)))
    N = R_E/np.sqrt(1-E2*np.sin(lat)**2); h = p/np.cos(lat) - N
    return np.degrees(lat), lon, h

def sun_elevation(lat_deg, lon_deg, jd, fr):
    """Solar elevation (deg) at ground points; low-precision solar position (Meeus), good to ~0.1 deg."""
    n = jd + fr - 2451545.0
    L = np.radians((280.460 + 0.9856474*n) % 360); g = np.radians((357.528 + 0.9856003*n) % 360)
    lam = L + np.radians(1.915)*np.sin(g) + np.radians(0.020)*np.sin(2*g)
    eps = np.radians(23.439 - 0.0000004*n)
    ra = np.arctan2(np.cos(eps)*np.sin(lam), np.cos(lam)); dec = np.arcsin(np.sin(eps)*np.sin(lam))
    ha = gmst_rad(jd, fr) + np.radians(lon_deg) - ra
    lat = np.radians(lat_deg)
    sin_el = np.sin(lat)*np.sin(dec) + np.cos(lat)*np.cos(dec)*np.cos(ha)
    return np.degrees(np.arcsin(np.clip(sin_el, -1, 1)))

def propagate(tle_rows, times):
    """tle_rows: DataFrame with epoch_utc,line1,line2 for ONE object. Uses the element set nearest in time to each step."""
    jd, fr = jd_from_times(times)
    ep = pd.to_datetime(tle_rows.epoch_utc, utc=True).values.astype("datetime64[ns]").astype(np.int64)/1e9
    tt = pd.DatetimeIndex(times).tz_convert(None).values.astype("datetime64[ns]").astype(np.int64)/1e9
    idx = np.abs(tt[:,None] - ep[None,:]).argmin(axis=1)
    r = np.full((len(times),3), np.nan); err = np.zeros(len(times), dtype=int)
    for k in np.unique(idx):
        m = idx == k
        s = Satrec.twoline2rv(tle_rows.line1.iloc[k], tle_rows.line2.iloc[k])
        e, rr, vv = s.sgp4_array(jd[m], fr[m]); r[m] = rr; err[m] = e
    lat, lon, h = teme_to_geodetic(r, jd, fr)
    return pd.DataFrame({"time": pd.DatetimeIndex(times), "lat": lat, "lon": lon, "alt_km": h, "sgp4_err": err})

def ground_offset_optical(h_km, off_nadir_deg):
    """Across-track ground distance (km) from nadir to the point seen at off-nadir angle theta."""
    th = np.radians(off_nadir_deg)
    gam = np.arcsin(np.clip((R_E + h_km)/R_E*np.sin(th), -1, 1)) - th
    return R_E*gam

def ground_offset_sar(h_km, incidence_deg):
    """Across-track ground distance (km) from nadir to the point seen at incidence angle i."""
    i = np.radians(incidence_deg)
    th = np.arcsin(np.clip(R_E/(R_E + h_km)*np.sin(i), -1, 1))
    return R_E*(i - th)
