"""Arrival windows at each station for impacts on a sparse grid around the 7th arc (reverse sensing, travel time only).

Grid      : 7th arc (arcs-sea-level.csv, artifact 6c2e8e10 v20aa918f, sea-level 00:19 arc) at 20, 21, ..., 41 S;
            cross-arc offsets -50, -25, 0, +25, +50 NM along the geodesic normal to the arc (+ = north-west, away from Australia).
Source    : impact time 00:19:38 - 00:29:44 UTC (Pete's ruling, 4 Nov 2026).
Water path: WGS84 geodesic length L, lengthened by a detour factor 1 + d, d in [0, 0.05]; horizontal group speed
            c in [1.40, 1.56] km/s.  earliest = 00:19:38 + L / 1.56 ; latest = 00:29:44 + 1.05 L / 1.40.
Mixed path (sensitivity, earliest bound only): a crustal leg of Lc km next to the receiver at 3.5-8.1 km/s replaces Lc km
            of water path. M100: Lc = 100 km; M300: Lc = 300 km. For blocked paths, MB: Lc = measured blocked span.
Blocking  : paths_lib.screen (GEBCO 2026, rule of hydro_data.sqlite arc_path; reproduces DB classes on 352/352 test paths).
Amplitude : not used anywhere (propagation is used for travel time only).
"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sqlite3, json
from pathlib import Path
import numpy as np, pandas as pd
from paths_lib import GEOD, screen

A = Path('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63')
DB = A / 'b3b0fe8f-b907-4214-9c02-18f9a4bf778c/v321ea0f6_hydro_data.sqlite'
ARC = A / '6c2e8e10-0f8c-4e09-ac7b-c103190012fc'
OUT = Path('windows'); OUT.mkdir(exist_ok=True)

T_SRC0, T_SRC1 = 19 * 60 + 38.0, 29 * 60 + 44.0           # s after 2014-03-08 00:00 UTC
C_MIN, C_MAX, DETOUR = 1.40, 1.56, 0.05                    # km/s, km/s, fractional lengthening
C_CR_MIN, C_CR_MAX = 3.5, 8.1                              # crustal leg speeds, km/s (Lg/Sn low, Pn high)
LATS = np.arange(-20.0, -41.0 - 1e-9, -1.0)
OFFS_NM = np.array([-50, -25, 0, 25, 50.0])
NM = 1.852

con = sqlite3.connect(f'file:{DB}?mode=ro', uri=True)
arcf = Path(__file__).resolve().parent / 'inputs/arcs-sea-level.csv'
if not arcf.exists():
    arcf = sorted(ARC.glob('*arcs-sea-level.csv'))[0]
arc = pd.read_csv(arcf).dropna(subset=['lon_arc7'])
arc_lon = lambda la: float(np.interp(la, arc.lat, arc.lon_arc7))

# stations: position from the DB site table; receiver depth as used in the DB arc_path table
site = pd.read_sql('select site_id, name, network, lat, lon, sensor_depth_m from site', con).set_index('site_id')
rdep = pd.read_sql('select site_id, avg(receiver_depth_m) d from arc_path group by 1', con).set_index('site_id').d
STATIONS = ['H01W', 'H08S', 'H08N', 'IMOS3315', 'IMOS3376', 'IMOS3250', 'IMOS3274', 'IMOS3275',
            'SWAMS1', 'SWAMS2', 'SWAMS3', 'SSEIR', 'MAD', 'NCRO', 'WKER', 'NEAMS']

# ---- grid
grid = []
sub = (0.570, 64.252)  # arc small-circle centre (sub-satellite side) used only to orient the normal toward the north-west
for la in LATS:
    lo = arc_lon(la)
    lo_n, lo_s = arc_lon(la + 0.1), arc_lon(la - 0.1)
    az_t, _, _ = GEOD.inv(lo_s, la - 0.1, lo_n, la + 0.1)        # local arc tangent (towards north)
    cand = [(az_t + 90) % 360, (az_t - 90) % 360]
    az_c, _, _ = GEOD.inv(lo, la, sub[1], sub[0])
    az_nw = min(cand, key=lambda a: abs(((a - az_c + 180) % 360) - 180))  # normal pointing to the arc centre side
    for off in OFFS_NM:
        if off == 0:
            glon, glat = lo, la
        else:
            a = az_nw if off > 0 else (az_nw + 180) % 360
            glon, glat, _ = GEOD.fwd(lo, la, a, abs(off) * NM * 1000)
        grid.append(dict(arc_lat=la, offset_nm=off, lat=glat, lon=glon, normal_az_nw_deg=az_nw))
grid = pd.DataFrame(grid)
grid['point_id'] = [f'{-r.arc_lat:.0f}S_{int(r.offset_nm):+d}NM' for r in grid.itertuples()]

# ---- per station x grid point
rows = []
for st in STATIONS:
    s = site.loc[st]
    for g in grid.itertuples():
        q = screen(g.lat, g.lon, s.lat, s.lon, float(rdep[st]))
        L = q['dist_km']
        e_w = T_SRC0 + L / C_MAX
        l_w = T_SRC1 + (1 + DETOUR) * L / C_MIN
        e_m100 = T_SRC0 + (L - 100) / C_MAX + 100 / C_CR_MAX
        e_m300 = T_SRC0 + (L - 300) / C_MAX + 300 / C_CR_MAX
        if q['cls'] == 'blocked':
            Lc = q['block_span_km']
            e_mb = T_SRC0 + (L - Lc) / C_MAX + Lc / C_CR_MAX
            l_mb = T_SRC1 + (1 + DETOUR) * (L - Lc) / C_MIN + Lc / C_CR_MIN
        else:
            Lc, e_mb, l_mb = 0.0, np.nan, np.nan
        rows.append(dict(station=st, point_id=g.point_id, arc_lat=g.arc_lat, offset_nm=g.offset_nm, lat=g.lat, lon=g.lon,
                         path_class=q['cls'], dist_km=L, baz_at_station_deg=q['baz_rcv_deg'], blocking_km=q['blocking_km'],
                         blocked_span_km=Lc, km_shallower_1000m=q['km_shallower_1000m'],
                         km_shallower_receiver=q['km_shallower_receiver'], shallowest_m=q['shallowest_m'],
                         earliest_s=e_w, latest_s=l_w, earliest_mixed100_s=e_m100, earliest_mixed300_s=e_m300,
                         earliest_mixed_blocked_s=e_mb, latest_mixed_blocked_s=l_mb))
W = pd.DataFrame(rows)


def hms(x):
    if not np.isfinite(x):
        return ''
    x = float(x)
    return f'{int(x // 3600):02d}:{int(x % 3600 // 60):02d}:{x % 60:04.1f}'


# ---- data coverage (continuous forms only; picks are not coverage)
cov = pd.read_csv('station-data/coverage_blocks.csv')


def union(iv):
    out = []
    for a, b in sorted(iv):
        if out and a <= out[-1][1]:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


FORMS = {'raw waveform (duty-cycled)': 'raw', 'digitised envelope (Kadri 2024 Fig. 9)': 'kadri',
         'digitised spectrogram (Royer 2016)': 'royer', 'digitised trace (CMST 2014)': 'cmst'}
U = {}
for st in STATIONS:
    c = cov[cov.station == st]
    U[(st, 'any')] = union(list(zip(c.t_start_s, c.t_end_s)))
    for f, k in FORMS.items():
        cf = c[c.form == f]
        U[(st, k)] = union(list(zip(cf.t_start_s, cf.t_end_s)))


def covered(st, k, a, b):
    return sum(max(0.0, min(b, y) - max(a, x)) for x, y in U[(st, k)])


for k in ['any'] + list(FORMS.values()):
    W[f'cov_{k}'] = [covered(r.station, k, r.earliest_s, r.latest_s) / (r.latest_s - r.earliest_s) for r in W.itertuples()]
for c in ['earliest_s', 'latest_s', 'earliest_mixed100_s', 'earliest_mixed300_s', 'earliest_mixed_blocked_s', 'latest_mixed_blocked_s']:
    W[c.replace('_s', '_utc')] = W[c].map(hms)
W.to_csv(OUT / 'arrival_windows_grid.csv', index=False, float_format='%.4f')

# ---- union window per station
S = []
for st in STATIONS:
    w = W[W.station == st]
    for subset, ww in [('all grid points', w), ('unblocked grid points', w[w.path_class != 'blocked'])]:
        if len(ww) == 0:
            S.append(dict(station=st, subset=subset, n_points=0))
            continue
        a, b = ww.earliest_s.min(), ww.latest_s.max()
        rec = dict(station=st, subset=subset, n_points=len(ww), n_blocked=int((ww.path_class == 'blocked').sum()),
                   n_clear=int((ww.path_class == 'clear').sum()), dist_min_km=ww.dist_km.min(), dist_max_km=ww.dist_km.max(),
                   earliest_s=a, latest_s=b, window_len_s=b - a,
                   earliest_mixed300_s=ww.earliest_mixed300_s.min(),
                   earliest_utc=hms(a), latest_utc=hms(b), earliest_mixed300_utc=hms(ww.earliest_mixed300_s.min()))
        for k in ['any'] + list(FORMS.values()):
            rec[f'union_cov_{k}'] = covered(st, k, a, b) / (b - a)
            rec[f'mean_point_cov_{k}'] = ww[f'cov_{k}'].mean()
            rec[f'points_cov_ge50pct_{k}'] = int((ww[f'cov_{k}'] >= 0.5).sum())
        S.append(rec)
S = pd.DataFrame(S)
S.to_csv(OUT / 'arrival_windows_station_union.csv', index=False, float_format='%.4f')
grid.to_csv(OUT / 'grid_points.csv', index=False, float_format='%.5f')
json.dump(dict(t_src0_s=T_SRC0, t_src1_s=T_SRC1, c_min=C_MIN, c_max=C_MAX, detour=DETOUR, c_crust=[C_CR_MIN, C_CR_MAX],
               arc_file=str(arcf), lats=LATS.tolist(), offsets_nm=OFFS_NM.tolist()), open(OUT / 'parameters.json', 'w'), indent=1)
print(S[S.subset == 'all grid points'][['station', 'n_blocked', 'dist_min_km', 'dist_max_km', 'earliest_utc', 'latest_utc',
                                         'earliest_mixed300_utc', 'union_cov_any', 'mean_point_cov_any']].to_string())
