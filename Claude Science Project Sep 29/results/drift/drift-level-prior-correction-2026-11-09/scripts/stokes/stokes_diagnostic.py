"""Stokes drift versus 10 m wind in the drift region (Mac; WAVERYS surface Stokes drift VSDX/VSDY and ERA5 u10/v10, both 3-hourly, 2014-03-07 to 2016-12-31).
For every daily 00 UTC slab, regions R1 (transit, 25-40 S, 40-110 E), R2 (approach to South Africa, 30-38 S, 15-35 E) and R3 (20-45 S, 30-110 E):
 along-wind fraction f_par = (Us . U10)/|U10|^2, cross-wind fraction f_perp = (Us x U10)/|U10|^2 (positive = Stokes drift clockwise of the wind), angle between them,
 ratio |Us|/|U10|. Samples every 3rd grid point. Statistics weighted by |U10| (displacement scale) and unweighted."""
import json, numpy as np, xarray as xr, pandas as pd, os
from scipy.ndimage import map_coordinates
D = '/Users/pete/Downloads/mh370-ocean-data'
files = [('20140307-20141231', 2014), ('20150101-20151231', 2015), ('20160101-20161231', 2016)]
REG = {'R1 transit 25-40S 40-110E': (-40, -25, 40, 110), 'R2 approach to South Africa 30-38S 15-35E': (-38, -30, 15, 35), 'R3 broad 20-45S 30-110E': (-45, -20, 30, 110)}
rows = {k: [] for k in REG}
for tag, yr in files:
    meta = json.load(open(f'{D}/era5/era5_u10_v10_3h_15-120E_50-0S_{tag}.json')); nt = len(meta['time_unix_s']); lat_e = np.array(meta['lat']); lon_e = np.array(meta['lon'])
    W = np.memmap(f'{D}/era5/' + meta['data_file'], dtype='<f4', mode='r', shape=(nt, len(lat_e), len(lon_e), 2))
    ds = xr.open_dataset(f'{D}/waverys/waverys_VSDX_VSDY_15-120E_50-0S_{tag}.nc')
    assert ds.sizes['time'] == nt, (ds.sizes['time'], nt)
    tw = ds.time.values.astype('datetime64[s]').astype(np.int64); te = np.array(meta['time_unix_s']).astype(np.int64)
    assert (tw == te).all(), 'time axes differ'
    lat_w = ds.latitude.values.astype(float); lon_w = ds.longitude.values.astype(float)
    for it in range(0, nt, 8):
        vx = ds.VSDX.isel(time=it).values; vy = ds.VSDY.isel(time=it).values
        for name, (la0, la1, lo0, lo1) in REG.items():
            ia = np.where((lat_w >= la0) & (lat_w <= la1))[0][::3]; ib = np.where((lon_w >= lo0) & (lon_w <= lo1))[0][::3]
            LA, LO = np.meshgrid(lat_w[ia], lon_w[ib], indexing='ij')
            ci = (LA - lat_e[0]) / 0.25; cj = (LO - lon_e[0]) / 0.25
            ue = map_coordinates(W[it, :, :, 0], [ci, cj], order=1); un = map_coordinates(W[it, :, :, 1], [ci, cj], order=1)
            sx = vx[np.ix_(ia, ib)]; sy = vy[np.ix_(ia, ib)]
            ok = np.isfinite(sx) & np.isfinite(sy) & np.isfinite(ue)
            w2 = ue[ok] ** 2 + un[ok] ** 2; sp = np.sqrt(w2)
            fpar = (sx[ok] * ue[ok] + sy[ok] * un[ok]) / w2; fperp = (sx[ok] * un[ok] - sy[ok] * ue[ok]) / w2   # cross product z: Us x U10 -> positive = Stokes counter-clockwise of wind; sign flipped below
            ang = np.degrees(np.arctan2(sx[ok] * un[ok] - sy[ok] * ue[ok], sx[ok] * ue[ok] + sy[ok] * un[ok]))
            rows[name].append(np.column_stack([np.full(ok.sum(), it), sp, np.hypot(sx[ok], sy[ok]), fpar, fperp, ang]))
    ds.close(); print(tag, 'done', flush=True)
out = []
def wq(x, w, qs):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]; return [float(x[o][np.searchsorted(c, q)]) for q in qs]
QS = (0.05, 0.25, 0.5, 0.75, 0.95)
for name, L in rows.items():
    A = np.vstack(L); sp, us, fpar, fperp, ang = A[:, 1], A[:, 2], A[:, 3], A[:, 4], A[:, 5]
    m = sp >= 3.0                                  # below 3 m/s the ratio is not meaningful (the displacement is small)
    for lab, sel in (('all winds >= 3 m/s', m), ('3-6 m/s', m & (sp < 6)), ('6-9 m/s', (sp >= 6) & (sp < 9)), ('9-12 m/s', (sp >= 9) & (sp < 12)), ('>= 12 m/s', sp >= 12)):
        if sel.sum() < 100: continue
        w = sp[sel]
        row = dict(region=name, wind_class=lab, n=int(sel.sum()), mean_fpar_pct=100 * float(np.average(fpar[sel], weights=w)), sd_fpar_pct=100 * float(np.sqrt(np.average((fpar[sel] - np.average(fpar[sel], weights=w)) ** 2, weights=w))))
        for q, v in zip(QS, wq(fpar[sel], w, QS)): row[f'fpar_p{int(q*100)}_pct'] = 100 * v
        row['fperp_mean_pct'] = 100 * float(np.average(fperp[sel], weights=w)); row['angle_sd_deg'] = float(np.sqrt(np.average((ang[sel] - np.average(ang[sel], weights=w)) ** 2, weights=w)))
        row['angle_mean_deg'] = float(np.average(ang[sel], weights=w)); row['frac_fpar_outside_0.5_2pct'] = float(np.average((fpar[sel] < 0.005) | (fpar[sel] > 0.02), weights=w))
        row['frac_fpar_outside_0.3_5pct'] = float(np.average((fpar[sel] < 0.003) | (fpar[sel] > 0.05), weights=w)); row['frac_abs_angle_gt_10deg'] = float(np.average(np.abs(ang[sel]) > 10, weights=w))
        out.append(row)
df = pd.DataFrame(out).round(3); df.to_csv('stokes/stokes-vs-wind-statistics.csv', index=False)
pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); print(df[['region', 'wind_class', 'n', 'mean_fpar_pct', 'sd_fpar_pct', 'fpar_p5_pct', 'fpar_p50_pct', 'fpar_p95_pct', 'angle_mean_deg', 'angle_sd_deg', 'frac_fpar_outside_0.5_2pct', 'frac_fpar_outside_0.3_5pct']].to_string())
