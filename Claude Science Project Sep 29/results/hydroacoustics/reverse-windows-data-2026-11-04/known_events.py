"""Known-event catalogue for 8 Mar 2014 with predicted arrival windows at every station (travel time only).

Speeds and detour as arrival_windows.py: water group speed 1.40-1.56 km/s, path up to 5 % longer.
Located events (earthquakes, Royer 2016 events):
  T (water) window: source-side rock leg Ls = distance from the epicentre along the path to the first point with
     water depth >= 1000 m (the slope where seismic energy converts to sound), at 3.5-8.1 km/s, plus hypocentre depth
     at 3.5-8.1 km/s; remaining path in water.
     earliest = t0 - dt0 + (depth + Ls)/8.1 + (L - Ls)/1.56 ; latest = t0 + dt0 + (depth + Ls)/3.5 + 1.05 (L - Ls)/1.40 + coda
     Location error: L and Ls evaluated at the centre and the 4 corners of the published lat/lon error box.
  Body-wave window (earthquakes only): first P to first S + coda, IASP91 (obspy TauP), energy that couples into the water
     at the receiver.
  coda: earthquakes 60 s + 60 s per magnitude unit above 3 (60-600 s); Royer icequakes and unclassified events 120 s.
Bearing-only observations (Kadri 2024 Table 1, Kadri 2019 Table 3, CMST detections): the source lies on the bearing line
  from the observing station, in water, inside the line of sight of that station (first blocked point ends the line),
  25-5000 km. For each point r: origin in [t - 1.05 r/1.40, t - r/1.56]; arrival at another station from that point.
Airgun shots at Diego Garcia South: same bearing-line method, bearing 34.9-35.4 deg (CMST), 500-5000 km.
Treatment: earthquakes / Royer events -> remove only at association probability >= 0.95 (screening step);
  airgun shots -> label and interference test, never removed (Pete's rule, 23 Oct 2026); bearing-only -> label.
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite3
from pathlib import Path
import numpy as np, pandas as pd
import netCDF4
from obspy.taup import TauPyModel
import paths_lib
from paths_lib import GEOD, screen

A = Path('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63')
DB = A / 'b3b0fe8f-b907-4214-9c02-18f9a4bf778c/v321ea0f6_hydro_data.sqlite'
OUT = Path('events'); OUT.mkdir(exist_ok=True)
T_REF = pd.Timestamp('2014-03-08T00:00:00Z')
C_MIN, C_MAX, DET, CR_MIN, CR_MAX = 1.40, 1.56, 0.05, 3.5, 8.1
con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
site = pd.read_sql('select site_id, lat, lon from site', con).set_index('site_id')
rdep = pd.read_sql('select site_id, avg(receiver_depth_m) d from arc_path group by 1', con).set_index('site_id').d
STATIONS = ['H01W', 'H08S', 'H08N', 'IMOS3315', 'IMOS3376', 'IMOS3250', 'IMOS3274', 'IMOS3275',
            'SWAMS1', 'SWAMS2', 'SWAMS3', 'SSEIR', 'MAD', 'NCRO', 'WKER', 'NEAMS']
TAUP = TauPyModel('iasp91')

# ---- GEBCO south of 60 S (outside the raw grid): block read from GEBCO_2026.nc once
nc = netCDF4.Dataset('/Users/pete/Downloads/mh370-ocean-data/gebco/GEBCO_2026.nc')
latv, lonv = nc['lat'][:], nc['lon'][:]
i0, i1 = np.searchsorted(latv, -72.0), np.searchsorted(latv, -59.9)
j0, j1 = np.searchsorted(lonv, 40.0), np.searchsorted(lonv, 180.0)
SOUTH = np.asarray(nc['elevation'][i0:i1, j0:j1]).astype(np.int16)
SLAT0, SLON0 = float(latv[i0]), float(lonv[j0])
_elev_raw = paths_lib.elev


def elev(lat, lon):
    lat = np.asarray(lat, float); lon = np.asarray(lon, float)
    z = _elev_raw(lat, lon)
    m = lat < -59.99
    if m.any():
        ii = np.clip(np.rint((lat[m] - SLAT0) * 240).astype(int), 0, SOUTH.shape[0] - 1)
        jj = np.clip(np.rint((lon[m] - SLON0) * 240).astype(int), 0, SOUTH.shape[1] - 1)
        z[m] = SOUTH[ii, jj]
    return z


paths_lib.elev = elev            # screen() now sees the southern block too


def hms(x):
    if x is None or not np.isfinite(x):
        return ''
    sgn = '-' if x < 0 else ''
    x = abs(float(x))
    return f'{sgn}{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:04.1f}'


def to_s(ts):
    t = pd.to_datetime(pd.Series(ts).astype(str).str.replace('Z', '', regex=False), utc=True, format='ISO8601')
    return ((t - T_REF).dt.total_seconds()).to_numpy()


def source_leg(lat, lon, st):
    """Distance from source to first point with depth >= 1000 m on the path to station st (km); path class; L."""
    s, la, lo, L, az, baz = paths_lib.path(lat, lon, site.loc[st].lat, site.loc[st].lon)
    z = elev(la, lo)
    k = np.where(-z >= 1000)[0]
    Ls = float(s[k[0]]) if len(k) else L
    return L, Ls


# ================================================================ located events
ev = []
# Royer 2016 located events
rev = pd.read_sql('select * from dg_royer_2016_royer_events', con)
for r in rev.itertuples():
    ev.append(dict(event_id=f'ROYER{int(r.index):02d}' + (f'-{r.label}' if r.label else ''), catalogue='Royer et al. 2016 (located from hydrophones)',
                   source_class=r.event_class, origin_s=float(r.origin_s_after_T0), origin_err_s=float(r.err_time_s),
                   lat=r.lat_deg, lon=r.lon_deg, err_lat=r.err_lat_deg, err_lon=r.err_lon_deg, depth_km=0.0, magnitude=np.nan,
                   size='', place=r.type_text, coda_s=120.0, body_waves=(r.event_class == 'earthquake')))
# earthquakes: project merged catalogue (DB known_event) + new downloads (USGS, EMSC, ISC FDSN, 4 Nov 2026)
ke = pd.read_sql("select * from known_event where source_class='earthquake'", con)
ke['t'] = to_s(ke.time_utc)
ke = ke[(ke.t >= -3 * 3600) & (ke.t <= 3.5 * 3600)]


def mag(sz):
    try:
        return float(str(sz).split()[-1])
    except Exception:
        return np.nan


for r in ke.itertuples():
    M = mag(r.size)
    ev.append(dict(event_id=f'EQ-{r.event_id}', catalogue=f'project merged catalogue ({r.database})', source_class='earthquake',
                   origin_s=r.t, origin_err_s=2.0, lat=r.lat, lon=r.lon, err_lat=0.1, err_lon=0.1, depth_km=float(r.depth_km or 0),
                   magnitude=M, size=r.size, place=r.place, coda_s=float(np.clip(60 + 60 * (M - 3), 60, 600)) if np.isfinite(M) else 300.0,
                   body_waves=True))
dl = []
for k in ['usgs', 'emsc', 'isc']:
    d = pd.read_csv(f'eq/{k}.txt', sep='|')
    d.columns = [c.strip('#').strip() for c in d.columns]
    d = d.dropna(subset=['Time'])
    d['cat'] = k
    dl.append(d)
dl = pd.concat(dl, ignore_index=True)
dl['t'] = to_s(dl.Time)
known = pd.DataFrame([e for e in ev if e['event_id'].startswith('EQ-')])
newrows = []
for r in dl.itertuples():
    m = known[(abs(known.origin_s - r.t) < 20) & (abs(known.lat - r.Latitude) < 1.5) & (abs(known.lon - r.Longitude) < 1.5)]
    if len(m):
        continue
    dup = [x for x in newrows if abs(x['origin_s'] - r.t) < 20 and abs(x['lat'] - r.Latitude) < 1.5 and abs(x['lon'] - r.Longitude) < 1.5]
    if dup:
        dup[0]['catalogue'] += f';{r.cat}'
        continue
    M = float(r.Magnitude)
    newrows.append(dict(event_id=f'EQ-{r.cat.upper()}-{r.EventID}', catalogue=f'downloaded 4 Nov 2026 ({r.cat})', source_class='earthquake',
                        origin_s=r.t, origin_err_s=2.0, lat=r.Latitude, lon=r.Longitude, err_lat=0.1, err_lon=0.1,
                        depth_km=float(r._5), magnitude=M, size=f'{r.MagType} {M}', place=r.EventLocationName,
                        coda_s=float(np.clip(60 + 60 * (M - 3), 60, 600)), body_waves=True))
ev += newrows
EV = pd.DataFrame(ev)
EV['origin_utc'] = EV.origin_s.map(hms)
EV['treatment'] = 'remove at association probability >= 0.95 (screening step)'

# observed Royer picks for validation
rp = pd.read_sql('select * from dg_royer_2016_royer_arrivals', con).dropna(subset=['arrival_s_after_T0'])
rp['st'] = rp.station.str.upper().str.replace(r'^H01W\d$', 'H01W', regex=True)

rows = []
for e in EV.itertuples():
    corners = [(e.lat, e.lon)] + [(e.lat + a * e.err_lat, e.lon + b * e.err_lon) for a in (-1, 1) for b in (-1, 1)]
    for st in STATIONS:
        Ls_, L_ = [], []
        for la, lo in corners:
            L, Ls = source_leg(la, lo, st)
            L_.append(L); Ls_.append(Ls)
        q = screen(e.lat, e.lon, site.loc[st].lat, site.loc[st].lon, float(rdep[st]))
        # all-rock limit: if no deep water is reached the leg equals the path (T phase not formed in deep water)
        early = min(e.origin_s - e.origin_err_s + (e.depth_km + Ls) / CR_MAX + (L - Ls) / C_MAX for L, Ls in zip(L_, Ls_))
        late = max(e.origin_s + e.origin_err_s + (e.depth_km + Ls) / CR_MIN + (1 + DET) * (L - Ls) / C_MIN for L, Ls in zip(L_, Ls_)) + e.coda_s
        obs = rp[(rp['index'].astype(str) == e.event_id[5:7].lstrip('0')) & (rp.st == st)] if e.event_id.startswith('ROYER') else rp.iloc[0:0]
        rec = dict(event_id=e.event_id, station=st, phase='T (water-borne sound)', dist_km=L_[0], source_rock_leg_km=Ls_[0],
                   path_class=q['cls'], earliest_s=early, latest_s=late,
                   royer_observed_s=';'.join(f'{x:.2f}' for x in obs.arrival_s_after_T0.astype(float)) if len(obs) else '')
        if len(obs):
            o = obs.arrival_s_after_T0.astype(float)
            rec['royer_observed_inside'] = bool(((o >= early) & (o <= late)).all())
        rows.append(rec)
        if e.body_waves:
            deg = L_[0] / 111.195
            dep = max(e.depth_km, 0.0)
            tp = [a.time for a in TAUP.get_travel_times(dep, deg, phase_list=['ttp'])]
            ts = [a.time for a in TAUP.get_travel_times(dep, deg, phase_list=['tts'])]
            if tp:
                rows.append(dict(event_id=e.event_id, station=st, phase='P to S (body waves, IASP91)', dist_km=L_[0],
                                 source_rock_leg_km=np.nan, path_class='not applicable (through the Earth)',
                                 earliest_s=e.origin_s - e.origin_err_s + min(tp),
                                 latest_s=e.origin_s + e.origin_err_s + (min(ts) if ts else max(tp)) + e.coda_s))
AR = pd.DataFrame(rows)

# ---- overlap with the impact arrival windows and with the data held
SU = pd.read_csv('windows/arrival_windows_station_union.csv')
SU = SU[SU.subset == 'unblocked grid points'].set_index('station')
cov = pd.read_csv('station-data/coverage_blocks.csv')


def overlap(st, a, b):
    if st not in SU.index or not np.isfinite(SU.loc[st].earliest_s):
        return 0.0
    return max(0.0, min(b, SU.loc[st].latest_s) - max(a, SU.loc[st].earliest_s))


def data_overlap(st, a, b):
    c = cov[cov.station == st]
    return float(sum(max(0.0, min(b, y) - max(a, x)) for x, y in zip(c.t_start_s, c.t_end_s)))


AR['overlap_with_impact_window_s'] = [overlap(r.station, r.earliest_s, r.latest_s) for r in AR.itertuples()]
AR['overlap_with_data_held_s'] = [data_overlap(r.station, r.earliest_s, r.latest_s) for r in AR.itertuples()]
AR['earliest_utc'] = AR.earliest_s.map(hms)
AR['latest_utc'] = AR.latest_s.map(hms)

# ================================================================ bearing-only observations and airgun shots
def bearing_line(st, bearings, rmin=25, rmax=5000, step=25):
    """Water points on bearing lines from station st, inside its line of sight (stop at the first blocked point)."""
    pts = []
    s0 = site.loc[st]
    lim = min(float(rdep[st]), 200.0)
    for b in bearings:
        rr = np.arange(step, rmax + step, step / 25)            # 1 km sampling for the blocking test
        lo, la, _ = GEOD.fwd(np.full(len(rr), s0.lon), np.full(len(rr), s0.lat), np.full(len(rr), b), rr * 1000)
        z = elev(la, lo)
        bad = ((z >= 0) | (-z < lim)) & (rr > 20)
        stop = rr[bad][0] if bad.any() else np.inf
        for r_, la_, lo_ in zip(rr, la, lo):
            if r_ >= stop:
                break
            if r_ >= rmin and abs(r_ % step) < 1e-6:
                pts.append((r_, la_, lo_, b))
    return pd.DataFrame(pts, columns=['r_km', 'lat', 'lon', 'bearing']), stop


obs = []
k1 = pd.read_sql('select * from dg_data_kadri_fig9_digitised_kadri_table1_transients', con)
for r in k1.itertuples():
    obs.append(dict(obs_id=f'KADRI24-T1-{r.event_id}', catalogue='Kadri 2024 Table 1 (transient at Cape Leeuwin)', station='H01W',
                    t_obs_s=to_s(['2014-03-08T' + r.time_utc])[0], bearings=[r.bearing_deg - 1, r.bearing_deg, r.bearing_deg + 1],
                    note=r.figure9_status, rmin=25, rmax=5000))
k3 = pd.read_sql('select * from dg_kadri_2019_kadri2019_table3_ha08s_signals', con)
tfix = {'HA_30': '2014-03-07T23:57:00', 'HA_31': '2014-03-08T00:11:00'}
for r in k3.itertuples():
    t = tfix.get(r.signal, '2014-03-08T' + r.time_utc + ':00')
    rng = str(r.distance_km or '')
    if '+/-' in rng:
        c, e_ = [float(x) for x in rng.split('+/-')]
        rmin, rmax = max(25, c - e_), c + e_
    else:
        rmin, rmax = 25, 5000
    obs.append(dict(obs_id=f'KADRI19-{r.signal}', catalogue='Kadri 2019 Table 3 (signal at Diego Garcia South)', station='H08S',
                    t_obs_s=to_s([t])[0], bearings=[r.bearing_from_HA08s_deg - 1, r.bearing_from_HA08s_deg, r.bearing_from_HA08s_deg + 1],
                    note=f'printed range {rng} km; time printed to the minute (+/- 60 s added)', rmin=rmin, rmax=rmax, t_err=60))
cm = pd.read_sql("select * from known_event where database like 'CMST 2014-30 (held)' and source_class like 'unidentified%'", con)
for r in cm.itertuples():
    st = 'H01W' if 'HA01' in r.event_id else 'H08S'
    b = float(str(r.size).split()[1])
    obs.append(dict(obs_id=r.event_id, catalogue='CMST 2014 report (detection of interest)', station=st, t_obs_s=to_s([r.time_utc])[0],
                    bearings=[b - 1, b, b + 1], note=r.place, rmin=25, rmax=5000))
shots = pd.read_sql("select * from pick where dataset_id='h08s_airgun_shots'", con)
shots['t_s'] = to_s(shots.t_utc)
obs.append(dict(obs_id='H08S-AIRGUN-SERIES', catalogue='airgun shots at Diego Garcia South (module, from Kadri Fig. 9 envelope)',
                station='H08S', t_obs_s=shots.t_s.min(), t_obs_end_s=shots.t_s.max(), bearings=[34.9, 35.15, 35.4],
                note=f'{len(shots)} shots {hms(shots.t_s.min())}-{hms(shots.t_s.max())}; bearing CMST 2014 (off Sri Lanka or Bay of Bengal)',
                rmin=500, rmax=5000))
OB, orow = [], []
for o in obs:
    line, stop = bearing_line(o['station'], o['bearings'], o['rmin'], o['rmax'])
    t_err = o.get('t_err', 2.0)
    t_end = o.get('t_obs_end_s', o['t_obs_s'])
    OB.append(dict(obs_id=o['obs_id'], catalogue=o['catalogue'], station=o['station'], t_obs_utc=hms(o['t_obs_s']),
                   t_obs_end_utc=hms(t_end), bearing_deg=o['bearings'][1], bearing_band_deg=f"{o['bearings'][0]:.2f}-{o['bearings'][-1]:.2f}",
                   range_used_km=(f"{o['rmin']:.0f}-{min(o['rmax'], line.r_km.max()):.0f}" if len(line) else
                                  f"none: no water point in line of sight within {o['rmin']:.0f}-{o['rmax']:.0f} km"),
                   line_of_sight_ends_km=float(line.r_km.max()) if len(line) else 0.0, n_points=len(line), note=o['note'],
                   treatment=('label and interference test; never removed (airgun rule)' if 'AIRGUN' in o['obs_id']
                              else 'label only (source position unknown)')))
    if not len(line):
        continue
    org_lo = o['t_obs_s'] - t_err - (1 + DET) * line.r_km.to_numpy() / C_MIN
    org_hi = t_end + t_err - line.r_km.to_numpy() / C_MAX
    for st in STATIONS:
        if st == o['station']:
            continue
        sp = site.loc[st]
        Ly = GEOD.inv(line.lon.to_numpy(), line.lat.to_numpy(), np.full(len(line), sp.lon), np.full(len(line), sp.lat))[2] / 1000
        a = org_lo + Ly / C_MAX
        b = org_hi + (1 + DET) * Ly / C_MIN
        # line-of-sight of the receiving station from each candidate point (coarse: every 8th point, 200 km)
        idx = np.arange(0, len(line), 8)
        cls = [screen(line.lat.iloc[i], line.lon.iloc[i], sp.lat, sp.lon, float(rdep[st]))['cls'] for i in idx]
        ok = np.array([c != 'blocked' for c in cls])
        ii = idx[ok]
        orow.append(dict(obs_id=o['obs_id'], observed_at=o['station'], station=st,
                         earliest_s=a.min(), latest_s=b.max(), earliest_utc=hms(a.min()), latest_utc=hms(b.max()),
                         earliest_unblocked_utc=hms(a[ii].min()) if len(ii) else '', latest_unblocked_utc=hms(b[ii].max()) if len(ii) else '',
                         frac_points_unblocked=ok.mean(),
                         overlap_with_impact_window_s=overlap(st, a.min(), b.max())))
OB, OR = pd.DataFrame(OB), pd.DataFrame(orow)

# ================================================================ persistent / continuous sources (labels)
ps = pd.read_sql("select * from known_event where source_class not in ('earthquake') and source_class not like 'unidentified%'", con)
prow = []
for r in ps.itertuples():
    for st in STATIONS:
        if not (np.isfinite(r.lat) and np.isfinite(r.lon)):
            prow.append(dict(source_id=r.event_id, source_class=r.source_class, station=st, note='no position'))
            continue
        q = screen(r.lat, r.lon, site.loc[st].lat, site.loc[st].lon, float(rdep[st]))
        prow.append(dict(source_id=r.event_id, source_class=r.source_class, database=r.database, lat=r.lat, lon=r.lon,
                         active=f'{r.time_utc} to {r.end_time_utc}', station=st, dist_km=q['dist_km'], path_class=q['cls'],
                         travel_min_s=q['dist_km'] / C_MAX, travel_max_s=(1 + DET) * q['dist_km'] / C_MIN,
                         note='continuous or repeated source: label only; a signal emitted at time t arrives in [t + travel_min, t + travel_max]'))
PS = pd.DataFrame(prow)

EV.to_csv(OUT / 'known_events.csv', index=False, float_format='%.4f')
AR.to_csv(OUT / 'known_event_arrivals.csv', index=False, float_format='%.2f')
OB.to_csv(OUT / 'observed_transients.csv', index=False, float_format='%.3f')
OR.to_csv(OUT / 'observed_transient_arrivals_elsewhere.csv', index=False, float_format='%.2f')
shots[['pick_id', 'site_id', 'label', 't_utc', 't_s', 'note']].to_csv(OUT / 'h08s_airgun_shots.csv', index=False)
PS.to_csv(OUT / 'persistent_sources_paths.csv', index=False, float_format='%.2f')
print('events', len(EV), EV.source_class.value_counts().to_dict())
print('arrival rows', len(AR), 'observed', len(OB), 'obs rows', len(OR), 'persistent rows', len(PS))
v = AR[AR.royer_observed_s.fillna('') != '']
print('Royer picks inside predicted T window:', int(v.royer_observed_inside.sum()), 'of', len(v))
print(v[~v.royer_observed_inside.astype(bool)][['event_id', 'station', 'earliest_utc', 'latest_utc', 'royer_observed_s']].to_string())
