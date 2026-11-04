"""Checks behind the arrival windows.
1. Blocking screen (paths_lib.screen) against hydro_data.sqlite arc_path on every whole-degree arc point 20-41 S, 16 sites.
2. Sea-water sound-speed bounds, Mackenzie (1981) nine-term equation.
3. Implied speeds of the Royer 2016 picks (Royer origins and positions, WGS84 geodesic).
"""
from __future__ import annotations
import sys, os, sqlite3, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pathlib import Path
import numpy as np, pandas as pd
from paths_lib import screen, GEOD

A = Path('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63')
con = sqlite3.connect(f"file:{A / 'b3b0fe8f-b907-4214-9c02-18f9a4bf778c/v321ea0f6_hydro_data.sqlite'}?mode=ro", uri=True)
site = pd.read_sql('select site_id, lat, lon from site', con).set_index('site_id')
OUT = Path('windows')

ap = pd.read_sql('select * from arc_path', con)
ap = ap[np.isclose(ap.arc_lat, np.round(ap.arc_lat)) & (ap.arc_lat >= -41.01) & (ap.arc_lat <= -19.99)]
rows = []
for r in ap.itertuples():
    q = screen(r.arc_lat, r.arc_lon, site.loc[r.site_id].lat, site.loc[r.site_id].lon, r.receiver_depth_m)
    rows.append(dict(site=r.site_id, arc_lat=r.arc_lat, arc_lon=r.arc_lon, db_class=r._15, new_class=q['cls'],
                     db_dist_km=r.dist_km, new_dist_km=q['dist_km'], db_blocking_km=r.blocking_km, new_blocking_km=q['blocking_km']))
v = pd.DataFrame(rows)
v.to_csv(OUT / 'blocking_screen_validation.csv', index=False, float_format='%.3f')


def mack(T, S, D):
    return (1448.96 + 4.591 * T - 5.304e-2 * T ** 2 + 2.374e-4 * T ** 3 + 1.340 * (S - 35) + 1.630e-2 * D + 1.675e-7 * D ** 2
            - 1.025e-2 * T * (S - 35) - 7.139e-13 * T * D ** 3)


cases = [('sea water at freezing point, surface', -1.9, 34.0, 0), ('Southern Ocean surface in March', 8, 34.2, 0),
         ('sound-channel axis, southern Indian Ocean', 4, 34.4, 1000), ('sound-channel axis, central Indian Ocean', 5, 34.6, 1200),
         ('tropical surface water', 30, 35.0, 0), ('abyssal water at 6000 m', 1.2, 34.7, 6000)]
sp = pd.DataFrame([dict(case=c, T_C=t, S_psu=s, depth_m=d, sound_speed_m_s=round(mack(t, s, d), 1)) for c, t, s, d in cases])
sp.to_csv(OUT / 'sound_speed_bounds.csv', index=False)

rp = pd.read_sql('select * from dg_royer_2016_royer_arrivals', con).dropna(subset=['arrival_s_after_T0'])
rev = pd.read_sql('select * from dg_royer_2016_royer_events', con)
r2 = rp.merge(rev[['index', 'lat_deg', 'lon_deg', 'origin_s_after_T0', 'err_time_s']], on='index')
r2['st'] = r2.station.str.upper().str.replace(r'^H01W\d$', 'H01W', regex=True)
r2['L_km'] = [GEOD.inv(lo, la, site.loc[s].lon, site.loc[s].lat)[2] / 1000 for la, lo, s in zip(r2.lat_deg, r2.lon_deg, r2.st)]
r2['speed_km_s'] = r2.L_km / (r2.arrival_s_after_T0.astype(float) - r2.origin_s_after_T0.astype(float))
r2[['index', 'station', 'st', 'arrival_utc', 'L_km', 'speed_km_s', 'err_time_s']].to_csv(OUT / 'royer_implied_speeds.csv', index=False, float_format='%.4f')
summ = dict(blocking_paths=len(v), blocking_class_match=int((v.db_class == v.new_class).sum()),
            blocking_max_dist_diff_km=float((v.db_dist_km - v.new_dist_km).abs().max()),
            blocking_max_blocking_km_diff=float((v.db_blocking_km - v.new_blocking_km).abs().max()),
            sound_speed_min=float(sp.sound_speed_m_s.min()), sound_speed_max=float(sp.sound_speed_m_s.max()),
            royer_n_picks=len(r2), royer_n_paths_H01W2_only=int(((r2.station != 'H01W1') & (r2.station != 'H01W3')).sum()),
            royer_speed_min=float(r2.speed_km_s.min()), royer_speed_median=float(r2.speed_km_s.median()),
            royer_speed_max=float(r2.speed_km_s.max()))
json.dump(summ, open(OUT / 'validation_summary.json', 'w'), indent=1)
print(summ)
