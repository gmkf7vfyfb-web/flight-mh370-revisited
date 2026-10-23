"""Sighting hook (Kadri-Haixun conditional, drift leg Q7, 18 Oct 2026).
Given a sighting position and radius band, report (1) the forward share of floating objects from each L release that lie in the
band at a chosen time, and (2) the backward origin density P(start | object in band) on the 8 Mar origin grid (uniform-area prior).
Inputs (exchange): snapL-<model>.bin (88-byte records: u8 release, env, class, fate; f32 first-beaching day, lon, lat; 9 x f32 lon, lat),
snapG-<model>.bin (36-byte records: u8 release(chunk-local), env, class, fate; f32 lon, lat at 4 Apr 00Z, 4 Apr 12Z, 5 Apr 00Z, 5 Apr 12Z),
optional snapE-<model>.bin (extension grid, same layout), meta.json / meta-ext.json.
Usage: python ring_hook.py EXCHANGE_DIR LAT LON R_IN_KM R_OUT_KM [HOUR_UTC_ON_5_APR=3.25]
"""
import sys, json, numpy as np
d, lat0, lon0, r0, r1 = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), float(sys.argv[5])
hr = float(sys.argv[6]) if len(sys.argv) > 6 else 3.25
def hav(a1, o1, a2, o2):
    p1, p2 = np.radians(a1), np.radians(a2); dl = np.radians(o2 - o1)
    return 2*6371.0088*np.arcsin(np.sqrt(np.sin((p2-p1)/2)**2 + np.cos(p1)*np.cos(p2)*np.sin(dl/2)**2))
fr = hr/12.0
dL = np.dtype([('rel','u1'),('env','u1'),('cls','u1'),('fate','u1'),('bt','<f4'),('blon','<f4'),('blat','<f4'),('pos','<f4',(9,2))])
dG = np.dtype([('rel','u1'),('env','u1'),('cls','u1'),('fate','u1'),('pos','<f4',(4,2))])
meta = json.load(open(f'{d}/meta.json'))
for m in ('globcurrent', 'glorys12'):
    a = np.fromfile(f'{d}/snapL-{m}.bin', dtype=dL)
    p = a['pos'][:, 6, :] + (a['pos'][:, 7, :] - a['pos'][:, 6, :])*fr
    dd = hav(lat0, lon0, p[:, 1], p[:, 0]); inb = (dd >= r0) & (dd < r1)
    for i, r in enumerate(meta['L']):
        s = a['rel'] == i; print(m, 'forward', r['point'], r['branch'], f'{inb[s].mean():.5f}')
    g = np.fromfile(f'{d}/snapG-{m}.bin', dtype=dG); per = 1200
    lons = np.array(meta['grid_lons']); lats = np.array(meta['grid_lats']); gi = np.arange(len(g))//per
    q = g['pos'][:, 2, :] + (g['pos'][:, 3, :] - g['pos'][:, 2, :])*fr
    dd = hav(lat0, lon0, q[:, 1], q[:, 0]); inb = (dd >= r0) & (dd < r1)
    od = (np.bincount(gi[inb], minlength=len(lats)*len(lons))/per).reshape(len(lats), len(lons))
    post = od*np.cos(np.radians(lats))[:, None]; post /= post.sum()
    for i, r in enumerate(meta['L'][:6]):
        near = hav(r['lat'], r['lon'], lats[:, None], lons[None, :]) < 50
        print(m, 'backward', r['point'], 'posterior mass within 50 km', f'{post[near].sum():.5f}')
