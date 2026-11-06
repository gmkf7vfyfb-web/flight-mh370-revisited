import sys, os, pickle, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
from multiprocessing import Pool
from scipy.stats import chi2
import network14 as N
import multiprocessing as mp
GLOB = {}


def _slide(i):
    rng = np.random.default_rng(GLOB['seed'] + i); sh = {}
    for grp in ('CL', 'DGS'):
        st = 'H01W' if grp == 'CL' else 'H08S'; L = GLOB['STA'][st].span[1] - GLOB['STA'][st].span[0]
        sh[grp] = rng.uniform(300, max(L - 300, 301))
    for grp in ('PC', 'PO', 'SR'):
        sh[grp] = 900.0 * rng.integers(2, 9) * rng.choice([-1, 1])
    _, _, _, a2, a1, ss = GLOB['evaluate'](sh)
    return a2, a1, ss

from imos_calib import TailMap, COMP

OUT = os.environ.get('OUT', 'run14'); os.makedirs(OUT, exist_ok=True)
NSLIDE = int(os.environ.get('NSLIDE', 1000))
import __main__, imos_calib as _IC
__main__.TailMap = _IC.TailMap
cal = pickle.load(open(os.environ.get('CALFILE', 'imos_calib.pkl'), 'rb'))


def _ev(lg):
    return N.imos_event_day(lg, cal[lg])


def split_half_check():
    rows = []
    for lg in N.LOGGERS:
        G = cal[lg]['null']; nrec = G['d0'].shape[0]; ev = np.arange(nrec) % 2 == 0
        maps = {k: TailMap(G[k][ev].ravel()) for k in COMP}
        F = lambda s: sum(-2 * np.nan_to_num(np.log(maps[k].p(G[k][s].ravel())), nan=0.0) for k in COMP)
        mF = TailMap(F(ev)); pt = mF.p(F(~ev))
        rows.append(dict(station=lg, n_test_points=len(pt), **{f'frac_p<{a}': float(np.mean(pt < a)) for a in (0.2, 0.05, 0.01, 0.001)}))
    return pd.DataFrame(rows)


def seeds(series, G):
    S = []
    k = pd.read_sql_table if False else None
    kad = pd.read_csv('kadri_table1_bearings_corrected.csv')
    corr = os.environ.get('KADRI_BEARINGS', 'published') == 'corrected'
    for r in kad.itertuples():
        b = r.bearing_corrected if corr else r.bearing_published; tol = 1.645 * r.sigma_deg if corr else 3.0
        S.append(dict(seed=f'Kadri {r.time_utc} ({r.bearing_published:.1f} deg)', source='Kadri Table 1', station='H01W', t=N_ts(r.time_utc), bearing=b, tol=tol))
    sc = pd.read_csv('screening_seeds.csv')
    for r in sc.itertuples():
        if r.station in N.STATIONS:
            S.append(dict(seed=f'Screening {r.station} {r.t_onset_utc} ({r.method})', source='screening 4 Nov', station=r.station, t=N_ts(r.t_onset_utc), bearing=np.nan))
    # combined-detector best impact-like points in each station's possible arrival span (all-data bootstrap)
    for st in N.STATIONS:
        g = G[G.station == st]; lo = N.H1[0] + g.dist_km.min() / N.V_MAX; hi = N.H2[1] + g.dist_km.max() * (1 + N.DET) / N.V_MIN
        s = series[(series.station == st) & (series.t_s >= lo) & (series.t_s <= hi)].copy()
        if st.startswith('IMOS'):
            s = s[s.winner.isin(['dive', 'ditch'])]
        s = s.sort_values('p_F').drop_duplicates('rec' if st.startswith('IMOS') else 't_s').head(5)
        for r in s.itertuples():
            S.append(dict(seed=f'Combined best {st} {N.hms(r.t_s)}', source='combined detector all-data', station=st, t=r.t_s, bearing=np.nan, seed_pF=r.p_F))
    # network cells of earlier searches (pre-registration B7); scored over all stations in the cell
    for nm, lat, t0, t1 in (('3 Nov graded best 39.5 S 00:44:30', 39.5, '00:43:30', '00:45:30'),
                            ('3 Nov hourly best 38.0 S 00:33:30', 38.0, '00:32:30', '00:34:30'),
                            ('4 Nov dive-window best 29.5-30.5 S 00:19:38-00:21:18', 30.0, '00:19:38', '00:21:18')):
        S.append(dict(seed=f'Cell {nm}', source='earlier network cells', station='cell', t=np.nan, bearing=np.nan,
                      cell_lat=lat, cell_t0=N_ts(t0), cell_t1=N_ts(t1)))
    return pd.DataFrame(S)


def nsites(U):
    out = 0
    for g in sorted(set(N.GROUP.values())):
        out = out + np.any(np.vstack([U[st] for st in N.STATIONS if N.GROUP[st] == g]), axis=0).astype(int)
    return out


def N_ts(s):
    h, m, x = str(s).split(':'); return int(h) * 3600 + int(m) * 60 + float(x)


def run(model):
    vmin, vmax, det = (N.V_MIN_S, N.V_MAX_S, N.DET_S) if model == 'wide speed' else (N.V_MIN, N.V_MAX, N.DET)
    W = {st: N.windows(H, G, st, vmin, vmax, det) for st in N.STATIONS}
    # seeds: consistent hypotheses
    masks = []
    gH = G[G.station == 'H01W'].set_index('point_id').baz_at_station_deg
    for s in SEEDS.itertuples():
        if s.station == 'cell':
            m = (np.abs(-H.arc_lat.values - s.cell_lat) <= 0.5) & (H.t_imp.values >= s.cell_t0) & (H.t_imp.values <= s.cell_t1) & (np.abs(H.offset_nm.values) <= 50)
            masks.append(m); continue
        a, b, blocked, _ = W[s.station]
        m = (a - 15 <= s.t) & (b + 15 >= s.t) & ~blocked
        if np.isfinite(s.bearing):
            dbz = np.abs(((gH.loc[H.point_id].values - s.bearing + 180) % 360) - 180); m &= dbz <= (s.tol if np.isfinite(s.tol) else 3.0)
        masks.append(m)

    def evaluate(shifts):
        per, k, Fn, lp = N.network_scores(H, W, STA, shifts)
        LP = {st: np.where(np.isfinite(per[st]), np.log(np.nan_to_num(per[st], nan=1.0)), 0.0) for st in N.STATIONS}
        U = {st: np.isfinite(per[st]) for st in N.STATIONS}
        ks = nsites(U)                                   # independent sites with data (review 1a)
        g2 = np.where(ks >= 2, lp, -np.inf)
        seedstat = []
        tot = sum(LP.values()); ktot = sum(U[st].astype(int) for st in N.STATIONS)
        for s, m in zip(SEEDS.itertuples(), masks):
            if s.station == 'cell':
                ok = m & (k >= 1)
                if not ok.any():
                    seedstat.append(np.nan); continue
                seedstat.append(float(lp[ok].max())); continue
            grp = [st for st in N.STATIONS if N.GROUP[st] == N.GROUP[s.station]]     # whole site of the seed (review 1b)
            lpo = tot - sum(LP[st] for st in grp); ko = ktot - sum(U[st].astype(int) for st in grp)
            ok = m & (ko >= 1)
            if not ok.any():
                seedstat.append(np.nan); continue
            pc = chi2.sf(-2 * lpo[ok], 2 * ko[ok]); seedstat.append(float(-np.log10(max(pc.min(), 1e-300))))
        return per, k, lp, np.max(g2), np.max(lp), np.array(seedstat)

    per, k, lp, g2obs, g1obs, seedobs = evaluate(None)
    GLOB['evaluate'] = evaluate; GLOB['STA'] = STA; GLOB['seed'] = 1000000 if model == 'primary' else 2000000
    with mp.get_context('fork').Pool(16) as pool:
        R = pool.map(_slide, range(NSLIDE), chunksize=4)
    null_g2 = [r[0] for r in R]; null_g1 = [r[1] for r in R]; null_seed = [r[2] for r in R]
    null_g2 = np.array(null_g2); null_g1 = np.array(null_g1); null_seed = np.array(null_seed)
    # hypothesis table (top by -log10 p among k>=2), with global p from the slide distribution of the max
    Uo = {st: np.isfinite(per[st]) for st in N.STATIONS}; ks = nsites(Uo)
    D = H.copy(); D['k_stations'] = k; D['k_sites'] = ks; D['minus_log10_p'] = lp
    for st in N.STATIONS:
        D['p_' + st] = per[st]
    D['global_p_k2'] = [(np.sum(null_g2 >= v) + 1) / (len(null_g2) + 1) if kk >= 2 else np.nan for v, kk in zip(lp, ks)]
    D['t_imp_utc'] = [N.hms(t) for t in D.t_imp]
    top = D[D.k_sites >= 2].sort_values('minus_log10_p', ascending=False).head(300)
    D.to_csv(f"{OUT}/all_hypotheses_{model.replace(' ', '_')}.csv.gz", index=False)
    sres = SEEDS.copy(); sres['stat_obs'] = seedobs
    sres['p_seed'] = [(np.sum(null_seed[:, j] >= v) + 1) / (NSLIDE + 1) if np.isfinite(v) else np.nan for j, v in enumerate(seedobs)]
    sres['n_consistent_hyp'] = [int(m.sum()) for m in masks]
    # best consistent hypothesis per seed (observed)
    best = []
    for s, m in zip(SEEDS.itertuples(), masks):
        if not m.any():
            best.append(('', '', np.nan, '')); continue
        grp = [] if s.station == 'cell' else [st for st in N.STATIONS if N.GROUP[st] == N.GROUP[s.station]]
        tot = sum(np.where(np.isfinite(per[st]), np.log(np.nan_to_num(per[st], nan=1.0)), 0.0) for st in N.STATIONS if st not in grp)
        ko = sum(np.isfinite(per[st]).astype(int) for st in N.STATIONS if st not in grp)
        sc = np.where(m & (ko >= 1), chi2.sf(-2 * tot, 2 * np.maximum(ko, 1)), 1.0); j = int(np.argmin(sc))
        others = ', '.join(f'{st} {per[st][j]:.3g}' for st in N.STATIONS if st not in grp and np.isfinite(per[st][j]))
        best.append((H.family[j], f'{-H.arc_lat[j]:.0f} S {H.offset_nm[j]:+d} NM', H.t_imp[j], others))
    sres['best_family'] = [b[0] for b in best]; sres['best_point'] = [b[1] for b in best]
    sres['best_t_imp_utc'] = [N.hms(b[2]) if np.isfinite(b[2]) else '' for b in best]; sres['best_other_station_p'] = [b[3] for b in best]
    q = sres.p_seed.values; ok = np.isfinite(q); order = np.argsort(q[ok]); m_ = ok.sum()
    bh = np.full(len(q), np.nan); qq = q[ok][order] * m_ / np.arange(1, m_ + 1); qq = np.minimum.accumulate(qq[::-1])[::-1]
    tmp = np.empty(m_); tmp[order] = np.minimum(qq, 1); bh[ok] = tmp; sres['bh_q'] = bh
    glob = dict(model=model, max_k2_obs=g2obs, p_global_k2=(np.sum(null_g2 >= g2obs) + 1) / (NSLIDE + 1),
                max_k1_obs=g1obs, p_global_k1=(np.sum(null_g1 >= g1obs) + 1) / (NSLIDE + 1), n_hyp=len(H), n_slides=NSLIDE)
    return top, sres, glob, null_g2


if __name__ == '__main__':
    with Pool(5) as p:
        ser = p.map(_ev, N.LOGGERS)
    series = pd.concat(ser + [N.kadri_series()], ignore_index=True)
    import eq_clean as EQ                               # label looks inside catalogued earthquake arrival windows
    series['eq_window'] = False
    for st in series.station.unique():
        m = series.station == st; series.loc[m, 'eq_window'] = EQ.flag_interval(st, series.loc[m, 't_s'].values - 15, series.loc[m, 't_s'].values + 15)
    if os.environ.get('EQREMOVE'):
        series = series[~(series.eq_window & series.station.str.startswith('IMOS'))].reset_index(drop=True)
    series.to_csv(f'{OUT}/station_point_series.csv', index=False)
    sh_ = split_half_check(); sh_.to_csv(f'{OUT}/split_half_check.csv', index=False); print(sh_.round(4).to_string(), flush=True)
    G = pd.read_csv('grid_ext_paths.csv'); H = N.hypotheses(G)
    WC = {lg: N.WindowCal(lg, cal=cal[lg]) for lg in N.LOGGERS}
    for st in ('H01W', 'H08S'):
        WC[st] = N.WindowCal(st, series=series[series.station == st])
    STA = {st: N.Station(st, series, WC[st]) for st in N.STATIONS}
    SEEDS = seeds(series, G); SEEDS.to_csv(f'{OUT}/seeds.csv', index=False)
    print('hypotheses', len(H), H.family.value_counts().to_dict(), 'seeds', len(SEEDS), flush=True)
    G_ = []
    MODELS = [('primary', None), ('wide speed', None)]
    if os.environ.get('NULLSUB'):                    # e.g. IMOS3275:IMOS3274  (logger:noise source)
        tgt, src = os.environ['NULLSUB'].split(':'); MODELS = [(f'primary {tgt} on {src} noise', (tgt, src))]
    if os.environ.get('MODELS') == 'primary':
        MODELS = MODELS[:1]
    for model, nul in MODELS:
        if nul is not None:
            tgt, src = nul; c = dict(cal[src]); ser = N.imos_event_day(tgt, c)
            series = pd.concat([series[series.station != tgt], ser], ignore_index=True)
            WC[tgt] = N.WindowCal(tgt, cal=c); STA[tgt] = N.Station(tgt, series, WC[tgt])
        top, sres, glob, ng = run(model)
        tag = model.replace(' ', '_')
        top.to_csv(f'{OUT}/top_hypotheses_{tag}.csv', index=False); sres.to_csv(f'{OUT}/seeded_tests_{tag}.csv', index=False)
        np.save(f'{OUT}/null_max_k2_{tag}.npy', ng); G_.append(glob)
        print(glob, flush=True)
    pd.DataFrame(G_).to_csv(f'{OUT}/global_results.csv', index=False)
