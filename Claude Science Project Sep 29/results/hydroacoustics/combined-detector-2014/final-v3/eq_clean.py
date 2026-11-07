"""Earthquake-cleaned IMOS noise calibration (answers Pete 6 Nov: tail removal with known earthquakes).
USGS M>=3.5 within 70 deg of each site, 27 Feb - 16 Mar 2014. A record is flagged when its 307 s overlaps
[origin + D/1.52 - 30 s, origin + D/1.45 + 180 s] (same rule as the 6 Nov IMS test). Point maps, Fisher map and
window-max tables are rebuilt from unflagged records only (record scores unchanged; whitening constants unchanged)."""
import sys, os, io, pickle, numpy as np, pandas as pd, requests
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
import __main__, imos_calib as IC; __main__.TailMap = IC.TailMap
from imos_calib import TailMap, COMP, fisher
import imosdet as ID
from obspy import UTCDateTime
SITES = {'IMOS3250': (-15.4834, 121.2510), 'IMOS3274': (-38.5370, 141.2476), 'IMOS3275': (-38.5424, 141.2256),
         'IMOS3315': (-31.8672, 115.0011), 'IMOS3376': (-31.8422, 115.0137), 'H01W': (-34.8929, 114.1539), 'H08S': (-7.6453, 72.4744)}
T8 = UTCDateTime('2014-03-08T00:00:00').timestamp
def cat(st):
    fn = f'usgs2014_{st}.csv'
    if os.path.exists(fn): return pd.read_csv(fn)
    la, lo = SITES[st]
    u = (f'https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime=2014-02-27&endtime=2014-03-16&latitude={la}&longitude={lo}'
         f'&maxradius=70&minmagnitude=3.5&orderby=time-asc&limit=20000')
    d = pd.read_csv(io.StringIO(requests.get(u, timeout=120).text)); d.to_csv(fn, index=False); return d
def gc(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2); dl = np.radians(lo2 - lo1)
    return 6371 * np.arccos(np.clip(np.sin(p1) * np.sin(p2) + np.cos(p1) * np.cos(p2) * np.cos(dl), -1, 1))
def windows(st):
    d = cat(st); ot = np.array([UTCDateTime(t).timestamp for t in d.time]) - T8
    D = gc(*SITES[st], d.latitude.values, d.longitude.values)
    return ot + D / 1.52 - 30, ot + D / 1.45 + 180, d
def flag_interval(st, a, b):
    lo, hi, _ = windows(st); a = np.atleast_1d(a); b = np.atleast_1d(b)
    return np.array([bool(np.any((hi >= x) & (lo <= y))) for x, y in zip(a, b)])
if __name__ == '__main__':
    cal = pickle.load(open('imos_calib.pkl', 'rb')); new = {}; rows = []
    for lg, c in cal.items():
        t0 = np.asarray(c['t0'], float); f = flag_interval(lg, t0, t0 + 307.0)
        bad = ~np.isfinite(c['null']['d0']).all(1) | (c['null']['d0'] > 100).any(1)      # instrument faults
        ok = ~f & ~bad
        G = {k: c['null'][k][ok] for k in COMP}
        maps = {k: TailMap(G[k].ravel()) for k in COMP}; Fpt = fisher(maps, G); maps['F'] = TailMap(Fpt.ravel())
        rng = np.random.default_rng(1); wmax = {}
        for nwin in range(1, len(ID.CENT) + 1):
            s0 = rng.integers(0, len(ID.CENT) - nwin + 1, size=len(Fpt))
            wmax[nwin] = np.sort(np.array([np.nanmax(Fpt[i, s:s + nwin]) for i, s in enumerate(s0)]))
        cc = dict(c); cc.update(maps=maps, wmax=wmax, n_records=int(ok.sum()), t0=t0[ok], null={**{k: c['null'][k][ok] for k in c['null']}}, Fpt=Fpt)
        new[lg] = cc
        # effect on tails: thresholds for point F and band energy before/after
        r = dict(station=lg, n_records=len(t0), n_flagged_quake=int(f.sum()), n_fault=int(bad.sum()), n_kept=int(ok.sum()))
        for k in ('d0', 'F'):
            v_all = c['maps'][k].v; v_cl = maps[k].v
            for q in (0.95, 0.99, 0.999):
                r[f'{k}_q{q}_all'] = float(np.quantile(v_all, q)); r[f'{k}_q{q}_clean'] = float(np.quantile(v_cl, q))
        rows.append(r)
    pickle.dump(new, open('imos_calib_eqclean.pkl', 'wb'))
    R = pd.DataFrame(rows); R.to_csv('eqclean_calibration_effect.csv', index=False)
    pd.set_option('display.width', 250); print(R.round(3).to_string())
    for st in SITES: print(st, 'catalogue events', len(cat(st)))
