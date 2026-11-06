"""Implied impact times and places for each Kadri Table 1 transient, for both families (dive and non-dive), both speed models."""
import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
import network14 as N
G = pd.read_csv('grid_ext_paths.csv'); H = N.hypotheses(G)
S = pd.read_csv('run14/seeds.csv'); S = S[S.source == 'Kadri Table 1']
gH = G[G.station == 'H01W'].set_index('point_id').baz_at_station_deg
dbz_all = {}
rows = []
for model, (vmin, vmax, det) in (('primary', (N.V_MIN, N.V_MAX, N.DET)), ('wide speed', (N.V_MIN_S, N.V_MAX_S, N.DET_S))):
    a, b, blocked, _ = N.windows(H, G, 'H01W', vmin, vmax, det)
    for s in S.itertuples():
        dbz = np.abs(((gH.loc[H.point_id].values - s.bearing + 180) % 360) - 180)
        for fam in ('H1 dive', 'H2 non-dive'):
            m = (a - 15 <= s.t) & (b + 15 >= s.t) & ~blocked & (dbz <= 3.0) & (H.family.values == fam)
            r = dict(speed_model=model, seed=s.seed, t_arrival_utc=N.hms(s.t), bearing_deg=s.bearing, family=fam, n_hyp=int(m.sum()))
            if m.any():
                h = H[m]; r.update(t_imp_first=N.hms(h.t_imp.min()), t_imp_last=N.hms(h.t_imp.max()),
                                   arc_lat_S_min=-h.arc_lat.max(), arc_lat_S_max=-h.arc_lat.min(),
                                   offset_nm_min=int(h.offset_nm.min()), offset_nm_max=int(h.offset_nm.max()))
            rows.append(r)
D = pd.DataFrame(rows); D.to_csv('run14/kadri_seeded_windows_both_families.csv', index=False)
P = D[D.speed_model == 'primary']
print(P.pivot_table(index='seed', columns='family', values='n_hyp', aggfunc='sum').to_string())
print(P[(P.family == 'H2 non-dive') & (P.n_hyp > 0)][['seed', 't_imp_first', 't_imp_last', 'arc_lat_S_min', 'arc_lat_S_max', 'offset_nm_min', 'offset_nm_max']].to_string())
