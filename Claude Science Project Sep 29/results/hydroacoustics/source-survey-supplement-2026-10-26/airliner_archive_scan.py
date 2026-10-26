"""Open-archive seismic check of airliner ocean impacts (EXPLORATORY). For each case: USGS ComCat and ISC
catalogue queries (+-15 min, 300 km / 3 deg), FDSN federated station list within 3 deg (340 km kept),
waveform fetch for up to 4 nearest stations with data, STA/LTA (1 s / 30 s) maximum in a P-to-Lg window
widened by the impact-time uncertainty, empirical p-value against same-length windows of the +-40 min record.
Run from the workspace root:  python scripts/airliner_archive_scan.py
"""
import io, time, requests, numpy as np, pandas as pd
from obspy import read, read_inventory, UTCDateTime
from obspy.geodetics import gps2dist_azimuth
from obspy.signal.trigger import recursive_sta_lta
FED = 'https://service.earthscope.org/irisws/fedcatalog/1/query'
CASES = [  # name, lat, lon, nominal impact UTC, time uncertainty (s), aircraft and impact, source of position/time
 ('TWA 800', 40.6492, -72.6369, '1996-07-18T00:31:12', (0, 90), 'B747-131; in-flight break-up, fragments reach the sea over tens of seconds', 'Wikipedia infobox position; 20:31:12 EDT last transponder return'),
 ('EgyptAir 990', 40.3475, -69.75667, '1999-10-31T06:52:00', (-90, 90), 'B767-366ER; steep high-speed dive; water about 80 m (Canadian Encyclopedia)', 'Wikipedia position; NTSB AAB-02/01 about 0152 EST'),
 ('Alaska 261', 34.05833, -119.34667, '2000-02-01T00:21:00', (-60, 60), 'MD-83; inverted nose-down dive', 'Wikipedia position; NTSB AAR-02/01 about 1621 PST'),
 ('Adam Air 574', -3.67889, 118.15111, '2007-01-01T07:00:00', (-300, 300), 'B737-400; high-speed descent, Makassar Strait (deep water)', 'Wikipedia position; final radar contact about 15:00 local (UTC+8)'),
 ('Ethiopian 409', 33.75778, 35.43028, '2010-01-25T00:41:00', (-60, 60), 'B737-800; spiral dive after take-off', 'Wikipedia position; 02:41 local EET (Lebanese report p.15 via Wikipedia)'),
 ('Flash Airlines 604', 27.83333, 34.38333, '2004-01-03T02:45:00', (-60, 60), 'B737-300; spiral dive after take-off, Red Sea', 'Wikipedia position (region level, 1 arcmin); 04:45 EGY'),
 ('EgyptAir 804', 33.6757, 28.7924, '2016-05-19T00:33:00', (-300, 300), 'A320; descent into deep eastern Mediterranean', 'Wikipedia LAST KNOWN position (not wreck); 02:33 EGY'),
 ('Lion Air 610', -5.77083, 107.12111, '2018-10-28T23:32:00', (-90, 90), 'B737 MAX 8; high-speed dive, Java Sea', 'Wikipedia position; take-off 23:20 UTC, ATC contact lost 06:33 local'),
 ('Sriwijaya Air 182', -5.96389, 106.57444, '2021-01-09T07:40:00', (-90, 90), 'B737-500; steep dive, Java Sea; water 20-23 m (Jerusalem Post, search police)', 'Wikipedia position; about 14:40 WIB (departure 07:36 UTC)'),
]
def fedcat(lat, lon, t, fmt):
    t = UTCDateTime(t); return requests.get(FED, params=dict(starttime=(t-600).isoformat(), endtime=(t+900).isoformat(), latitude=lat, longitude=lon, maxradius=3.0, channel='BHZ,HHZ,EHZ,SHZ', format=fmt), timeout=180).text
def stations(lat, lon, t):
    rows = []; dc = None
    for l in fedcat(lat, lon, t, 'text').splitlines():
        if l.startswith('#DATACENTER='): dc = l.split('=')[1].split(',')[0]
        elif l and not l.startswith('#') and '|' in l:
            f = l.split('|'); rows.append(dict(dc=dc, net=f[0], sta=f[1], cha=f[3], lat=float(f[4]), lon=float(f[5])))
    svc = {}; cur = None
    for l in fedcat(lat, lon, t, 'request').splitlines():
        if l.startswith('DATACENTER='): cur = l.split('=')[1].split(',')[0]; svc[cur] = {}
        elif cur and l.split('=')[0] in ('DATASELECTSERVICE', 'STATIONSERVICE'): svc[cur][l.split('=')[0]] = l.split('=', 1)[1]
    df = pd.DataFrame(rows)
    df['dist_km'] = [gps2dist_azimuth(lat, lon, a, b)[0]/1e3 for a, b in zip(df.lat, df.lon)]
    return df[df.dist_km <= 340], svc
def catalogues(lat, lon, t):
    t = UTCDateTime(t); out = {}
    r = requests.get('https://earthquake.usgs.gov/fdsnws/event/1/query', params=dict(starttime=(t-900).isoformat(), endtime=(t+900).isoformat(), latitude=lat, longitude=lon, maxradiuskm=300, format='csv'), timeout=60)
    out['comcat'] = '; '.join(r.text.strip().splitlines()[1:]) or 'no event'
    for k in range(5):
        r = requests.get('https://www.isc.ac.uk/fdsnws/event/1/query', params=dict(starttime=(t-900).isoformat(), endtime=(t+900).isoformat(), latitude=lat, longitude=lon, maxradius=3, format='text', includeallorigins='true'), timeout=90)
        if r.status_code != 429: break
        time.sleep(15)
    out['isc'] = ('no event' if r.status_code == 204 else ('; '.join(r.text.strip().splitlines()[1:]) if r.status_code == 200 else f'HTTP {r.status_code}'))
    return out
def fetch(svc, net, sta, cha, t, half=2400):
    p = dict(network=net, station=sta, channel=cha, starttime=(t-half).isoformat(), endtime=(t+half).isoformat())
    r = requests.get(svc['DATASELECTSERVICE'].rstrip('/')+'/query', params=p, timeout=180)
    if r.status_code != 200 or len(r.content) < 512: return None, None, f'HTTP {r.status_code}'
    st = read(io.BytesIO(r.content))
    ri = requests.get(svc['STATIONSERVICE'].rstrip('/')+'/query', params=dict(network=net, station=sta, channel=cha, starttime=(t-60).isoformat(), endtime=(t+60).isoformat(), level='response'), timeout=120)
    return st, (read_inventory(io.BytesIO(ri.content)) if ri.status_code == 200 else None), f'ok {len(st)} segment(s)'
def test(st, inv, t0, dkm, lo, hi, net):
    tr = st.merge(fill_value=0)[0]; fs = tr.stats.sampling_rate; tr.detrend('demean'); tr.detrend('linear'); tr.taper(0.01); unit = 'counts'
    if inv is not None:
        try: tr.remove_response(inventory=inv, output='VEL', pre_filt=[0.3, 0.5, 0.45*fs, 0.48*fs], water_level=60); unit = 'nm/s'
        except Exception: pass
    f2 = min(15, 0.4*fs); f1 = 2.0 if f2 > 8 else 1.0
    x = tr.copy().filter('bandpass', freqmin=f1, freqmax=f2, corners=4, zerophase=True)
    cft = recursive_sta_lta(x.data, int(fs), int(30*fs)); t = x.times(reftime=t0)
    a = lo+dkm/6.4-3; b = hi+dkm/3.0+15; L = b-a; m = (t >= a) & (t < b)
    if m.sum() < 0.9*L*fs: return dict(note='gap in search window')
    stat = cft[m].max(); nulls = []; s0 = t[0]+60
    while s0+L < t[-1]:
        mm = (t >= s0) & (t < s0+L)
        if not (s0 < b+30 and s0+L > a-30) and mm.sum() > 0.9*L*fs: nulls.append(cft[mm].max())
        s0 += L
    nulls = np.array(nulls); k = int((nulls >= stat).sum()); nz = x.data[(t >= a-330) & (t < a-30)]; sc = 1e9 if unit == 'nm/s' else 1
    flag = 'amplitude not used: Raspberry Shake response not verified' if net == 'AM' else ''
    return dict(band=f'{f1:g}-{f2:g} Hz', search_window_s=f'{a:.0f} to {b:.0f}', max_sta_lta=round(float(stat), 2), t_of_max_s=round(float(t[m][cft[m].argmax()]), 1),
                snr_peak=round(float(abs(x.data[m]).max()/nz.std()), 2), n_null=len(nulls), k_null_ge=k, p=round((k+1)/(len(nulls)+1), 4), p_floor=round(1/(len(nulls)+1), 4),
                noise_rms=(np.nan if net == 'AM' else float(nz.std()*sc)), amp_unit=unit, amplitude_flag=flag)
tests, cases = [], []
for name, lat, lon, ts, (lo, hi), ac, src in CASES:
    t0 = UTCDateTime(ts); df, svc = stations(lat, lon, ts); cat = catalogues(lat, lon, ts); time.sleep(2)
    pref = {'HHZ': 0, 'BHZ': 1, 'EHZ': 2, 'SHZ': 3}
    d2 = df.assign(pr=df.cha.map(pref)).sort_values(['dist_km', 'pr']).drop_duplicates(['net', 'sta'])
    ok = 0; tried = 0
    for _, s in d2.iterrows():
        if ok >= 4 or tried >= 14: break
        tried += 1; sv = svc.get(s.dc, {})
        if 'DATASELECTSERVICE' not in sv: continue
        st, inv, msg = fetch(sv, s.net, s.sta, s.cha, t0); cha = s.cha
        if st is None and s.cha != 'BHZ':
            st2, inv2, msg2 = fetch(sv, s.net, s.sta, 'BHZ', t0)
            if st2 is not None: st, inv, msg, cha = st2, inv2, msg2+' (BHZ fallback)', 'BHZ'
        row = dict(case=name, data_centre=s.dc, station=f'{s.net}.{s.sta}.{cha}', dist_km=round(s.dist_km, 1), fetch=msg)
        if st is not None:
            try: row.update(test(st, inv, t0, s.dist_km, lo, hi, s.net)); ok += ('p' in row)
            except Exception as e: row['note'] = 'test error '+str(e)[:60]
        tests.append(row)
    T = pd.DataFrame([r for r in tests if r['case'] == name])
    tt = T.dropna(subset=['p']) if 'p' in T else pd.DataFrame()
    best = tt.sort_values('p').iloc[0] if len(tt) else None
    cases.append(dict(case=name, impact_utc_nominal=ts, time_uncertainty_s=f'{lo:+d} to {hi:+d}', lat=lat, lon=lon, aircraft_and_impact=ac, position_time_source=src,
                      comcat=cat['comcat'][:200], isc=cat['isc'][:200], n_open_stations_le_340km=int(df[['net', 'sta']].drop_duplicates().shape[0]),
                      nearest_open_station_km=round(df.dist_km.min(), 1) if len(df) else np.nan, n_stations_fetched=int(len(T)), n_stations_tested=int(len(tt)),
                      best_station=(best.station if best is not None else ''), best_station_km=(best.dist_km if best is not None else np.nan),
                      min_p=(best.p if best is not None else np.nan), p_floor_at_min=(best.p_floor if best is not None else np.nan),
                      snr_at_min=(best.snr_peak if best is not None else np.nan),
                      bonferroni_min_p=(min(1, best.p*len(tt)) if best is not None else np.nan)))
    print(name, 'tested', len(tt), flush=True)
TS = pd.DataFrame(tests); TS['rank_by_p_within_case'] = TS.groupby('case').p.rank(method='min')
TS['likelihood_ratio'] = 'not computed (no calibrated signal model)'
TS.to_csv('out/airliner-ocean-impacts-station-tests.csv', index=False)
pd.DataFrame(cases).to_csv('work/airliner_cases_scan.csv', index=False)
print(pd.DataFrame(cases)[['case', 'n_open_stations_le_340km', 'n_stations_tested', 'best_station', 'min_p', 'p_floor_at_min', 'bonferroni_min_p']].to_string())
