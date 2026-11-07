"""Extend the GlobCurrent daily surface currents (version 202411, retires 24 Nov 2026 13:00 UTC) to 2018-12-31.
Same dataset, variables and boxes as the October 2026 fetches; appends to fetch-log.jsonl with SHA-256."""
import os, json, hashlib, datetime, copernicusmarine as cm
v = os.environ['COPERNICUS']; u, p = v.strip().split(':', 1)
D = '/Users/pete/Downloads/mh370-ocean-data/globcurrent'
DS = 'cmems_obs-mob_glo_phy-cur_my_0.25deg_P1D-m'
jobs = [((15, 120), 'globcurrent_my_p1d_uo_vo_err_0m_20170201-20181231.nc'),
        ((120.0, 160.0), 'globcurrent_my_p1d_uo_vo_err_0m_120-160E_20170201-20181231.nc')]
for (lo0, lo1), fn in jobs:
    if os.path.exists(f'{D}/{fn}.part.nc') and not os.path.exists(f'{D}/{fn}'):
        import xarray as xr; t = xr.open_dataset(f'{D}/{fn}.part.nc').time.values; assert str(t[-1])[:10] == '2018-12-31' and len(t) == 699, (t[0], t[-1], len(t)); os.replace(f'{D}/{fn}.part.nc', f'{D}/{fn}')
        h = hashlib.sha256(open(f'{D}/{fn}', 'rb').read()).hexdigest(); n = os.path.getsize(f'{D}/{fn}')
        rec = {'file': fn, 'bytes': n, 'sha256': h, 'request': {'dataset_id': DS, 'dataset_version': '202411', 'variables': ['uo', 'vo', 'err_uo', 'err_vo'], 'start_datetime': '2017-02-01T00:00:00', 'end_datetime': '2018-12-31T00:00:00'}, 'box': {'minimum_longitude': lo0, 'maximum_longitude': lo1, 'minimum_latitude': -50, 'maximum_latitude': 0, 'minimum_depth': 0, 'maximum_depth': 0}, 'fetched_utc': '2026-11-07T19:23:00Z'}
        open(f'{D}/fetch-log.jsonl', 'a').write(json.dumps(rec) + '\n'); print('ok (renamed)', fn, n, h); continue
    if os.path.exists(f'{D}/{fn}'):
        print('exists', fn); continue
    cm.subset(dataset_id=DS, dataset_version='202411', variables=['uo', 'vo', 'err_uo', 'err_vo'], minimum_longitude=lo0, maximum_longitude=lo1,
              minimum_latitude=-50, maximum_latitude=0, minimum_depth=0, maximum_depth=0, start_datetime='2017-02-01T00:00:00', end_datetime='2018-12-31T00:00:00',
              output_directory=D, output_filename=fn + '.part.nc', username=u, password=p, disable_progress_bar=True)
    os.replace(f'{D}/{fn}.part.nc', f'{D}/{fn}')
    h = hashlib.sha256(open(f'{D}/{fn}', 'rb').read()).hexdigest(); n = os.path.getsize(f'{D}/{fn}')
    rec = {'file': fn, 'bytes': n, 'sha256': h, 'request': {'dataset_id': DS, 'dataset_version': '202411', 'variables': ['uo', 'vo', 'err_uo', 'err_vo'], 'start_datetime': '2017-02-01T00:00:00', 'end_datetime': '2018-12-31T00:00:00'},
           'box': {'minimum_longitude': lo0, 'maximum_longitude': lo1, 'minimum_latitude': -50, 'maximum_latitude': 0, 'minimum_depth': 0, 'maximum_depth': 0}, 'fetched_utc': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}
    open(f'{D}/fetch-log.jsonl', 'a').write(json.dumps(rec) + '\n')
    print('ok', fn, n, h)
