"""Independent review checks of the reverse-sensing association report (4-5 Nov 2026).
Recomputes only the values needed to test the report's claims, from committed CSV tables.
Inputs: arrival_windows_grid.csv, known_events.csv, kadri-form-matched-null-calibration.csv,
per-method-summary.csv (paths given as arguments or env). No pipeline rerun."""
import sys, numpy as np, pandas as pd
from pyproj import Geod
from scipy.optimize import least_squares
from scipy.stats import norm, beta
G = Geod(ellps='WGS84')
win = pd.read_csv(sys.argv[1]); ke = pd.read_csv(sys.argv[2]).set_index('event_id'); kn = pd.read_csv(sys.argv[3])
def tod(x): h, m, s = x.split(':'); return int(h)*3600 + int(m)*60 + float(s)
def hms(s): s = float(s); return f"{int(s//3600):02d}:{int(s%3600//60):02d}:{s%60:04.1f}"
def gd(la1, lo1, la2, lo2):
    la2 = np.atleast_1d(la2); lo2 = np.atleast_1d(lo2)
    return G.inv(np.full(la2.shape, lo1), np.full(la2.shape, la1), lo2, la2)[2] / 1000
T0, T1, D = tod('00:19:38'), tod('00:29:44'), 6.0  # impact window; tolerance 5 s + 2 x 0.5 s
# 1. station positions inverted from the grid distances (WGS84 geodesic)
pos = {}
for st, g in win.groupby('station'):
    best = None
    for a in range(-60, 10, 10):
        for b in range(40, 160, 15):
            r = least_squares(lambda x: gd(x[0], x[1], g.lat.values, g.lon.values) - g.dist_km.values, [a, b])
            best = r if best is None or r.cost < best.cost else best
    pos[st] = best.x
# 2. Royer B distance to the arc line (offset 0, linear interpolation between 1-degree points)
arc = win[(win.station == 'H01W') & (win.offset_nm == 0)].sort_values('arc_lat')
q = np.linspace(-41, -20, 2101)
la = np.interp(q, arc.arc_lat, arc.lat); lo = np.interp(q, arc.arc_lat, arc.lon)
B = ke.loc['ROYER04-B']; dB = gd(B.lat, B.lon, la, lo)
print(f"Royer B to arc line: {dB.min():.1f} km (arc lat {q[dB.argmin()]:.2f})")
# 3. predicted arrivals of Royer A, B, 6 at selected stations, empirical speed range of the A/B/6 picks
vlo, vhi = 1.4673, 1.5068
for e in ['ROYER03-A', 'ROYER04-B', 'ROYER06']:
    E = ke.loc[e]
    for st in ['H08S', 'IMOS3275', 'IMOS3250']:
        L = gd(E.lat, E.lon, pos[st][0], pos[st][1])[0]
        print(f"{e}->{st}: {L:.1f} km, {hms(E.origin_s + L/vhi)}-{hms(E.origin_s + L/vlo)}")
L6 = gd(ke.loc['ROYER06'].lat, ke.loc['ROYER06'].lon, *pos['IMOS3275'])[0]
print('speed needed for Royer 6 to reach Portland 3275 at 01:07:43.1:', round(L6/(tod('01:07:43.1') - ke.loc['ROYER06'].origin_s), 4))
# 4. rank-1 member intersections on the 1-degree x 25 NM grid
mem = {'H01W': '00:36:07.4', 'H08S': '01:04:30.0', 'IMOS3275': '01:07:43.1', 'IMOS3250': '00:48:48.3'}
rows = []
for st, t in mem.items():
    g = win[win.station == st]; t = tod(t)
    tmax = g.latest_s - T1
    for geo, tmin in [('base', g.earliest_s - T0), ('rock', np.minimum(g.earliest_mixed300_s.fillna(g.earliest_s), g.earliest_s) - T0)]:
        rows.append(pd.DataFrame(dict(st=st, geo=geo, pt=g.point_id, lat=g.arc_lat, off=g.offset_nm, cls=g.path_class,
                                      lo=(t - tmax - D).values, hi=(t - tmin + D).values)))
I = pd.concat(rows)
for skip in [('blocked',), ('blocked', 'large attenuation')]:
    for geo in ['base', 'rock']:
        for sts in [['H08S', 'IMOS3275'], ['H08S', 'IMOS3275', 'IMOS3250'], ['H01W', 'H08S', 'IMOS3275'], list(mem)]:
            s = I[(I.geo == geo) & I.st.isin(sts) & ~I.cls.isin(skip)]
            w = s.groupby('pt').agg(lo=('lo', 'max'), hi=('hi', 'min'), n=('st', 'nunique'), lat=('lat', 'first'), off=('off', 'first'))
            w['lo'] = np.maximum(w.lo, T0); w['hi'] = np.minimum(w.hi, T1); ok = w[(w.n == len(sts)) & (w.hi >= w.lo)]
            print(skip, geo, '+'.join(sts), len(ok), '/110', (f"{-ok.lat.max():.0f}-{-ok.lat.min():.0f} S" if len(ok) else ''))
# 5. pair statistic for DGS 01:04:30 + Portland 01:07:43
zp = norm.isf(0.002616) + min(norm.isf(8.4e-5), 4.26)
print('pair z sum', round(zp, 2), '(compare observed best-pair maximum 8.026, p 0.92 base / 0.941 rock-leg)')
# 6. Kadri form-matched null: Clopper-Pearson 95 % intervals on false alarms per look (80 s blocks)
k = kn[kn.mean_block_s == 80].copy(); k['k'] = np.round(k.false_alarm_per_look_at_0p05*k.looks).astype(int)
k['lo95'] = [beta.ppf(.025, a, n-a+1) if a else 0 for a, n in zip(k.k, k.looks)]
k['hi95'] = [beta.ppf(.975, a+1, n-a) for a, n in zip(k.k, k.looks)]
print(k[['detector', 'window_s', 'false_alarm_per_look_at_0p05', 'looks', 'lo95', 'hi95']].round(3).to_string(index=False))
# 7. association model behind the figure-mark P values: P = L/(L+c), L = exp(-dt^2/(2 sd^2)), sd 2 s
c = 0.06/0.94
for dt in [0.0, 1.5, 3.3, 6.5]: print('dt', dt, 'P', round(np.exp(-dt**2/8)/(np.exp(-dt**2/8) + c), 3))
print('largest possible P at sd 2 s:', round(1/(1 + c), 3))
