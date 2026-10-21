
"""Polar-orbiter pass geometry for the continuously recording imager study.
SGP4 is initialised from the parsed Space-Track GP fields (Hugging Face export juliensimon/space-track-tle-history,
tle_2014.parquet); the element set nearest in epoch to each time step is used. TEME->Earth-fixed via GMST only
(satgeom.teme_to_geodetic). Spherical Earth (R=6371 km) for cross-track offsets (coincide.crossings)."""
import numpy as np, pandas as pd
from sgp4.api import Satrec, WGS72
EPOCH0 = pd.Timestamp("1949-12-31T00:00:00Z")
def satrec_from_row(r):
    s = Satrec()
    ep = (pd.Timestamp(r.epoch) - EPOCH0).total_seconds()/86400.0
    s.sgp4init(WGS72, 'i', int(r.norad_id), ep, float(r.bstar), float(r.mean_motion_dot)*2*np.pi/1440**2, 0.0,
               float(r.eccentricity), np.radians(r.arg_perigee), np.radians(r.inclination), np.radians(r.mean_anomaly),
               float(r.mean_motion)*2*np.pi/1440.0, np.radians(r.raan))
    return s
def propagate_fields(rows, times, satgeom):
    rows = rows.sort_values("epoch").reset_index(drop=True)
    jd, fr = satgeom.jd_from_times(times)
    ep = rows.epoch.values.astype("datetime64[ns]").astype(np.int64)/1e9
    tt = pd.DatetimeIndex(times).tz_convert(None).values.astype("datetime64[ns]").astype(np.int64)/1e9
    idx = np.abs(tt[:,None]-ep[None,:]).argmin(1)
    rr = np.full((len(times),3), np.nan); err = np.zeros(len(times), int)
    for k in np.unique(idx):
        m = idx==k; s = satrec_from_row(rows.iloc[k]); e, p, v = s.sgp4_array(jd[m], fr[m]); rr[m]=p; err[m]=e
    lat, lon, h = satgeom.teme_to_geodetic(rr, jd, fr)
    epoch_used = rows.epoch.values[idx]
    return pd.DataFrame({"time": pd.DatetimeIndex(times), "lat": lat, "lon": lon, "alt_km": h, "err": err,
                         "tle_epoch": epoch_used})
