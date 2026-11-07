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
G = pd.read_csv(os.environ.get('GRID', 'grid_ext_paths_wide.csv'))
CASE = os.environ.get('BEARINGS', 'corrected')     # corrected (ruling B1, primary) | published (sensitivity)
KC = pd.read_csv('kadri_table1_bearings_corrected.csv')
KB = {(r.time_utc, round(r.bearing_published, 2)): (r.bearing_corrected, 1.645 * r.sigma_deg) for r in KC.itertuples()}
OUTF = os.environ.get('CANDOUT', 'cand_all.csv')
def ts(s): h, m, x = str(s).split(':'); return int(h) * 3600 + int(m) * 60 + float(x)
c = []
for r in S.itertuples():
    if r.station not in ('H01W', 'H08S'): continue
    src = 'Kadri' if r.source == 'Kadri Table 1' else ('ours (combined detector on envelope)' if r.source.startswith('combined') else 'ours (4 Nov screening)')
    b, tol = r.bearing, 3.0
    if src == 'Kadri':
        key = (r.seed.split()[1], round(r.bearing, 2))
        b_cor, tol_cor = KB[key]
        if CASE == 'corrected': b, tol = b_cor, tol_cor
    c.append(dict(station=r.station, t=r.t, bearing=b, bearing_published=r.bearing, tol=tol, source=src, label=r.seed))
sc = pd.read_csv('screening_seeds.csv')
lab = {(r.station, round(ts(r.t_onset_utc), 1)): (r.method, r.known_event_label) for r in sc.itertuples()}
C = pd.DataFrame(c)
# merge: non-Kadri picks within 30 s of a Kadri transient join it; other picks within 30 s of each other merge
ev = []
K = C[C.source == 'Kadri'].copy()
for r in K.itertuples():
    ev.append(dict(station=r.station, t=r.t, bearing=r.bearing, bearing_published=r.bearing_published, tol=r.tol, members=[r.label], src={'Kadri'}))
for r in C[C.source != 'Kadri'].sort_values('t').itertuples():
    best = None
    for e in ev:
        if e["station"] == r.station and abs(e["t"] - r.t) <= (30 if "Kadri" in e["src"] else 45) and (best is None or abs(e['t'] - r.t) < abs(best['t'] - r.t)):
            best = e
    if best is not None:
        best['members'].append(r.label); best['src'].add('ours')
    else:
        ev.append(dict(station=r.station, t=r.t, bearing=np.nan, bearing_published=np.nan, tol=np.nan, members=[r.label], src={'ours'}))
E = pd.DataFrame(ev)
def env_p(st, t):
    h = ser[(ser.station == st) & (ser.t_s >= t - 15) & (ser.t_s <= t + 15)]
    return (h.p_F.min() if len(h) else np.nan)
E['envelope_p'] = [env_p(r.station, r.t) for r in E.itertuples()]
E['source'] = ['Kadri and ours' if s == {'Kadri', 'ours'} else ('Kadri' if s == {'Kadri'} else 'ours') for s in E.src]
E['screening_known_label'] = ['; '.join(sorted({f'{lab[k][0]}: {lab[k][1]}' for m in mm for k in lab if m.startswith('Screening') and abs(k[1] - ts(m.split()[2])) < 0.2})) for mm in E.members]
E = E.sort_values('envelope_p').reset_index(drop=True)
# arrival-time span (7 Nov 2026): onset pick minus 20 s (emergent lag between Royer Table 5 picks and envelope onsets, 13.8-20 s)
# to the envelope peak within onset-10 s ... onset+40 s
LAG = 20.0
def env_peak(st, t):
    h = ser[(ser.station == st) & (ser.t_s >= t - 10) & (ser.t_s <= t + 40)]
    return float(h.loc[h.E.idxmax(), 't_s']) if len(h) else t
E['t_peak'] = [env_peak(r.station, r.t) for r in E.itertuples()]
E['t_a'] = E.t - LAG; E['t_b'] = np.maximum(E.t, E.t_peak)
import sqlite3, glob
_con = sqlite3.connect(glob.glob('/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/artifacts/proj_9cc1a5a85f63/b3b0fe8f-b907-4214-9c02-18f9a4bf778c/*.sqlite')[-1])
_ra = pd.read_sql("select * from dg_royer_2016_royer_arrivals", _con); _fm = pd.read_sql("select * from dg_royer_2016_royer_figure_marks", _con)
_ev = pd.read_sql("select * from dg_royer_2016_royer_events", _con) if 'dg_royer_2016_royer_events' in [t[0] for t in _con.execute("select name from sqlite_master")] else None
def royer_match(st, t):
    if st != 'H01W': return ''
    out = []
    for _, x in _ra[_ra.station.str.startswith('H01W') & _ra.arrival_utc.notna()].iterrows():
        dt = ts(x.arrival_utc) - t
        if -40 <= dt <= 10: out.append((abs(dt), f"Royer event {int(x['index'])}{' (' + x.label + ')' if isinstance(x.label, str) else ''}, {x.event_class}, table pick {x.arrival_utc[:8]} ({dt:+.0f} s)"))
    for _, x in _fm[_fm.station.str.startswith('H01W') & _fm.figure.str.startswith('fig')].iterrows():
        dt = x.t_utc_s - t
        if abs(dt) <= 15: out.append((abs(dt) - 100, f"Royer {x.figure.replace('_', ' ')} pick bar {x.t_utc[:8]} ({dt:+.0f} s)"))
    out = sorted(out)
    return '; '.join(dict.fromkeys(o[1] for o in out[:2]))
E['royer_match'] = [royer_match(r.station, r.t) for r in E.itertuples()]
# implied impact
out = []
for r in E.itertuples():
    g = G[G.station == r.station].copy()
    if np.isfinite(r.bearing):
        d = np.abs(((g.baz_at_station_deg - r.bearing + 180) % 360) - 180); g = g[d <= r.tol]
    else:
        g = g[(g.arc_lat <= -20) & (g.arc_lat >= -41)]          # no bearing: ruled arc range only
    g['t_imp_lo'] = r.t_a - g.dist_km * (1 + DET) / VMIN; g['t_imp_hi'] = r.t_b - g.dist_km / VMAX
    g = g[(g.t_imp_hi >= T_IMP[0]) & (g.t_imp_lo <= T_IMP[1])]
    if len(g) == 0:
        out.append(dict(n_points=0)); continue
    g0 = g[g.offset_nm == 0] if (g.offset_nm == 0).any() else g
    out.append(dict(n_points=len(g), arc_lat_S_min=-g.arc_lat.max(), arc_lat_S_max=-g.arc_lat.min(),
                    arc_lat_S_on_arc=('; '.join(f'{-a:.0f}' for a in sorted(g0.arc_lat.unique(), reverse=True)) if np.isfinite(r.bearing) else 'any (no bearing)'),
                    t_imp_first=N.hms(max(g.t_imp_lo.min(), T_IMP[0])), t_imp_last=N.hms(min(g.t_imp_hi.max(), T_IMP[1])),
                    outside_ruled_arc_range=bool(((g.arc_lat > -20) | (g.arc_lat < -41)).all()),
                    steep_dive_fits=bool(((g.t_imp_hi >= N.H1[0]) & (g.t_imp_lo <= N.H1[1]) & (g.offset_nm.abs() <= 25)).any()),
                    points=';'.join(g.point_id)))
E = pd.concat([E, pd.DataFrame(out)], axis=1)
E['t_utc'] = [N.hms(t) for t in E.t]; E['members'] = ['; '.join(m) for m in E.members]
E.drop(columns=['src']).to_csv(OUTF, index=False)
print(E[['station', 't_utc', 'bearing_published', 'bearing', 'source', 'envelope_p', 'n_points', 'arc_lat_S_on_arc', 't_imp_first', 't_imp_last', 'steep_dive_fits', 'outside_ruled_arc_range']].head(16).to_string())
print('total events', len(E), E.station.value_counts().to_dict())
