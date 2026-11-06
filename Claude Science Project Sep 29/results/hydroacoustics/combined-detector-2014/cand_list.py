"""Top Cape Leeuwin / Diego Garcia South candidate events, pooled from Kadri Table 1, our combined detector on the
Kadri envelopes, and the 4 Nov screening picks. Ranked by one common measure: envelope evidence at the station
(combined band energy + persistence, smallest p within +-15 s). Implied impact times use the physics sound-speed
bounds 1.40-1.56 km/s with 5 % path detour, restricted to the impact window 00:19:38-00:55:00."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
import network14 as N
VMIN, VMAX, DET = N.V_MIN_S, N.V_MAX_S, N.DET_S
T_IMP = (N.H2[0], N.H2[1])
ser = pd.read_csv('run14/station_point_series.csv'); S = pd.read_csv('run14/seeds.csv')
G = pd.read_csv('grid_ext_paths.csv')
def ts(s): h, m, x = str(s).split(':'); return int(h) * 3600 + int(m) * 60 + float(x)
c = []
for r in S.itertuples():
    if r.station not in ('H01W', 'H08S'): continue
    src = 'Kadri' if r.source == 'Kadri Table 1' else ('ours (combined detector on envelope)' if r.source.startswith('combined') else 'ours (4 Nov screening)')
    c.append(dict(station=r.station, t=r.t, bearing=r.bearing, source=src, label=r.seed))
sc = pd.read_csv('screening_seeds.csv')
lab = {(r.station, round(ts(r.t_onset_utc), 1)): (r.method, r.known_event_label) for r in sc.itertuples()}
C = pd.DataFrame(c)
# merge: non-Kadri picks within 30 s of a Kadri transient join it; other picks within 30 s of each other merge
ev = []
K = C[C.source == 'Kadri'].copy()
for r in K.itertuples():
    ev.append(dict(station=r.station, t=r.t, bearing=r.bearing, members=[r.label], src={'Kadri'}))
for r in C[C.source != 'Kadri'].sort_values('t').itertuples():
    best = None
    for e in ev:
        if e["station"] == r.station and abs(e["t"] - r.t) <= (30 if "Kadri" in e["src"] else 45) and (best is None or abs(e['t'] - r.t) < abs(best['t'] - r.t)):
            best = e
    if best is not None:
        best['members'].append(r.label); best['src'].add('ours')
    else:
        ev.append(dict(station=r.station, t=r.t, bearing=np.nan, members=[r.label], src={'ours'}))
E = pd.DataFrame(ev)
def env_p(st, t):
    h = ser[(ser.station == st) & (ser.t_s >= t - 15) & (ser.t_s <= t + 15)]
    return (h.p_F.min() if len(h) else np.nan)
E['envelope_p'] = [env_p(r.station, r.t) for r in E.itertuples()]
E['source'] = ['Kadri and ours' if s == {'Kadri', 'ours'} else ('Kadri' if s == {'Kadri'} else 'ours') for s in E.src]
E['screening_known_label'] = ['; '.join(sorted({f'{lab[k][0]}: {lab[k][1]}' for m in mm for k in lab if m.startswith('Screening') and abs(k[1] - ts(m.split()[2])) < 0.2})) for mm in E.members]
E = E.sort_values('envelope_p').reset_index(drop=True)
# implied impact
out = []
for r in E.itertuples():
    g = G[G.station == r.station].copy()
    if np.isfinite(r.bearing):
        d = np.abs(((g.baz_at_station_deg - r.bearing + 180) % 360) - 180); g = g[d <= 3.0]
    g['t_imp_lo'] = r.t - g.dist_km * (1 + DET) / VMIN; g['t_imp_hi'] = r.t - g.dist_km / VMAX
    g = g[(g.t_imp_hi >= T_IMP[0]) & (g.t_imp_lo <= T_IMP[1])]
    if len(g) == 0:
        out.append(dict(n_points=0)); continue
    g0 = g[g.offset_nm == 0] if (g.offset_nm == 0).any() else g
    out.append(dict(n_points=len(g), arc_lat_S_min=-g.arc_lat.max(), arc_lat_S_max=-g.arc_lat.min(),
                    arc_lat_S_on_arc=('; '.join(f'{-a:.0f}' for a in sorted(g0.arc_lat.unique(), reverse=True)) if np.isfinite(r.bearing) else 'any (no bearing)'),
                    t_imp_first=N.hms(max(g.t_imp_lo.min(), T_IMP[0])), t_imp_last=N.hms(min(g.t_imp_hi.max(), T_IMP[1])),
                    steep_dive_fits=bool(((g.t_imp_hi >= N.H1[0]) & (g.t_imp_lo <= N.H1[1]) & (g.offset_nm.abs() <= 25)).any()),
                    points=';'.join(g.point_id)))
E = pd.concat([E, pd.DataFrame(out)], axis=1)
E['t_utc'] = [N.hms(t) for t in E.t]; E['members'] = ['; '.join(m) for m in E.members]
E.drop(columns=['src']).to_csv('cand_all.csv', index=False)
print(E[['station', 't_utc', 'bearing', 'source', 'envelope_p', 'n_points', 'arc_lat_S_on_arc', 't_imp_first', 't_imp_last', 'steep_dive_fits']].head(16).to_string())
print('total events', len(E), E.station.value_counts().to_dict())
