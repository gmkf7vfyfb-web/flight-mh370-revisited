"""Ranges from Royer 2016 located events south of 50 S to the AADC moorings vs to Royer's own receivers (dg_royer_2016_royer_stations)."""
import pandas as pd, numpy as np
from obspy.geodetics import gps2dist_azimuth
ev = pd.read_csv('royer_events.csv'); st = pd.read_csv('royer_stations.csv')
latc = [c for c in st.columns if 'lat' in c.lower()][0]; lonc = [c for c in st.columns if 'lon' in c.lower()][0]
namec = st.columns[0] if 'name' not in ' '.join(st.columns).lower() else [c for c in st.columns if 'name' in c.lower() or 'station' in c.lower()][0]
pa = pd.read_csv('out/aadc-predicted-arrivals-known-events.csv'); pa = pa[pa.source.str.startswith('Royer')]
rows = []
for _, e in ev[ev.lat_deg < -50].iterrows():
    d = [(gps2dist_azimuth(e.lat_deg, e.lon_deg, s[latc], s[lonc])[0] / 1e3, s[namec]) for _, s in st.iterrows()]
    d.sort()
    eid = f"Royer #{int(e['index'])}" + (f" ({e.label})" if isinstance(e.label, str) and e.label else "")
    p = pa[pa.event_id == eid].set_index('receiver')
    rows.append(dict(event_id=eid, event_class=e.event_class, origin_utc=f"{e.origin_date} {e.origin_time_utc}", lat=e.lat_deg, lon=e.lon_deg,
                     royer_err_time_s=e.err_time_s, n_hydrophones=e.n_hydrophones,
                     nearest_royer_receiver=d[0][1], nearest_royer_receiver_km=round(d[0][0]), second_royer_receiver_km=round(d[1][0]),
                     kerguelen_km=p.loc['Kerguelen2014', 'dist_km'], kerguelen_pred_utc=p.loc['Kerguelen2014', 'pred_arrival_rule_utc'][11:], kerguelen_path=p.loc['Kerguelen2014', 'path_class'],
                     casey_km=p.loc['Casey2014', 'dist_km'], casey_pred_utc=p.loc['Casey2014', 'pred_arrival_rule_utc'][11:], casey_path=p.loc['Casey2014', 'path_class'],
                     casey_min_depth_m=p.loc['Casey2014', 'min_seafloor_depth_m'], kerguelen_min_depth_m=p.loc['Kerguelen2014', 'min_seafloor_depth_m']))
out = pd.DataFrame(rows)
out['mooring_closer_than_nearest_royer'] = np.minimum(out.kerguelen_km, out.casey_km) < out.nearest_royer_receiver_km
out.to_csv('out/aadc-royer-southern-events-ranges.csv', index=False)
pd.set_option('display.width', 250); print(out.drop(columns=['kerguelen_path','casey_path']).to_string())
