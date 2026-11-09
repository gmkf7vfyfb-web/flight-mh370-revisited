"""Final drift tables for the extended-window run (8 Nov 2026): 16384 level draws (converged to about 0.05 deg in the mean shift).
Model ladder, headline (all western Indian Ocean coasts, four detection periods, identity-weighted non-circular items), sensitivities,
three core posteriors, evidence ratio against a uniform-along-arc prior, latitude densities for the figure."""
import sys, os, glob, numpy as np, pandas as pd
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', 'res-final-ramp']
exec(open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0])
ZDRAWS, ZSEED = 16384, 31
Z = np.load(LED); la = Z['D0|lat']; okl = np.isfinite(la); la = la[okl]
pc = np.nan_to_num(Z['D0|core'])[okl]; pu = np.nan_to_num(Z['D0|(uniform along the arc)'])[okl]; pc, pu = pc / pc.sum(), pu / pu.sum()
def lnR(Lg, Ly, lat):
    if not (np.isfinite(Lg).all() and np.isfinite(Ly).all()): return np.nan
    mx = max(Lg.max(), Ly.max()); L = 0.5 * (np.exp(Lg - mx) + np.exp(Ly - mx)); arc = np.round(lat * 2) / 2
    Lb = pd.Series(L).groupby(arc).mean(); Li = np.interp(la, Lb.index.values, Lb.values); return float(np.log((pc * Li).sum() / (pu * Li).sum()))
def density(key, lat, lon, Lg, Ly, edges):
    H = A[key].astype(float); hl0, hn0, hg = float(A['lat0']), float(A['lon0']), float(A['grid'])
    hlat = hl0 + (np.arange(H.shape[0]) + 0.5) * hg; hlon = hn0 + (np.arange(H.shape[1]) + 0.5) * hg
    ii, jj = np.nonzero(H > 0); cl, cn, hw = hlat[ii], hlon[jj], H[ii, jj]
    dist = np.hypot((cn[:, None] - lon[None]) * 111.2 * np.cos(np.radians(cl[:, None])), (cl[:, None] - lat[None]) * 111.2)
    nn = np.argsort(dist, 1)[:, :6]; W = 1 / np.maximum(np.take_along_axis(dist, nn, 1), 1.0) ** 2; W /= W.sum(1, keepdims=True)
    p = hw / hw.sum()
    if Lg is not None:
        a = (W * Lg[nn]).sum(1); b = (W * Ly[nn]).sum(1); mx = max(a.max(), b.max()); p = p * 0.5 * (np.exp(a - mx) + np.exp(b - mx)); p /= p.sum()
    h, _ = np.histogram(cl, edges, weights=p); return h / np.diff(edges)
edges = np.arange(-44.0, -19.99, 0.25)
rows, dens = [], {}
for v in ('R0-module-run', 'R1-oldwindow', 'R4-4periods', 'R2-allcoasts', 'R3-allcoasts-4periods'):
    meta, recs, nenv = load(v)
    common = sorted(set(recs['globcurrent']) & set(recs['glorys12'])); lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
    ids = [f['id'] for f in meta.finds]; has = lambda o: f'item:{o}' in ids
    NINE = [f for f in ids if f.startswith('item:') and aud.loc[f.split(':')[1], 'stringent_nine'] == 'yes']
    LL = ['item:linga-linga-vertical-stabilizer'] if has('linga-linga-vertical-stabilizer') else []
    LATE = LL + [f'item:{o}' for o in ('nautilus-bay-right-aileron', 'mpame-right-flap-fairing') if has(o)]
    CIRC = [f for f in ids if f.startswith('shadow:identity-from-drift')] + [f'item:{o}' for o in ('kosi-bay-right-wing-body-fairing', 'anvil-bay-wing-body-fairing', 'macaneta-left-trailing-edge-panel') if has(o)]
    obj = lambda f: f.split('identity-from-drift-')[-1] if 'identity-from-drift' in f else f.split(':')[1]
    PW = {f: GRADE_P[aud.loc[obj(f), 'official_classification']] for f in NINE + LATE + CIRC}
    swap = lambda sel, a, b: [b if x == a else x for x in sel]
    MB, FL, PA = 'item:mossel-bay-engine-cowling-roy', 'item:reunion-right-flaperon', 'item:paindane-right-flap-fairing'
    fresh = lambda sel, d: swap(swap(swap(sel, FL, f'shadow:flaperon-fresh-{d}d'), MB, f'shadow:mossel-bay-fresh-{d}d'), PA, 'shadow:paindane-fresh-14d')
    mu0 = mu_tiers(meta); H = NINE + LATE
    C = {}
    if v != 'R3-allcoasts-4periods':
        C['ladder: nine finds'] = (NINE, {}, mu0, 0, 'full')
        if LL: C['ladder: nine finds and Linga Linga'] = (NINE + LL, {}, mu0, 0, 'full')
        if len(LATE) == 3: C['ladder: twelve non-circular items, identity-weighted'] = (H, PW, mu0, 0, 'full')
    else:
        C['HEADLINE: twelve non-circular items, identity-weighted'] = (H, PW, mu0, 0, 'full')
        C['ladder: nine finds'] = (NINE, {}, mu0, 0, 'full'); C['ladder: nine finds and Linga Linga'] = (NINE + LL, {}, mu0, 0, 'full')
        C['all identity probabilities set to 1'] = (H, {}, mu0, 0, 'full')
        C['add eight items identified partly from drift (sensitivity)'] = (H + CIRC, PW, mu0, 0, 'full')
        C['without Nautilus Bay and Mpame'] = (NINE + LL, PW, mu0, 0, 'full')
        C['time ashore: fresh marks 10 d, 10 d, 14 d'] = (fresh(H, 10), PW, mu0, 0, 'full')
        C['time ashore: fresh marks 3 d, 3 d, 14 d'] = (fresh(H, 3), PW, mu0, 0, 'full')
        C['Mossel Bay at second beaching (21-22 Mar 2016)'] = (swap(H, MB, 'shadow:mossel-bay-refound-2016-03-21'), PW, mu0, 0, 'full')
        C['three official alternative dates'] = (swap(swap(swap(H, 'item:vilanculos-horizontal-stabilizer-panel', 'shadow:vilanculos-official-2016-02-27'), 'item:pemba-right-outboard-flap', 'shadow:pemba-official-2016-06-20'), 'item:mauritius-left-outboard-flap', 'shadow:mauritius-2016-05-08'), PW, mu0, 0, 'full')
        C['other coasts at the find-coast level'] = (H, PW, mu_tiers(meta, moderate=0.0), 0, 'full')
        C['other coasts at 0.1 of the find-coast level'] = (H, PW, mu_tiers(meta, moderate=np.log(0.1)), 0, 'full')
        C['populated new coasts also at 0.3'] = (H, PW, mu_tiers(meta, populated=np.log(0.3)), 0, 'full')
        for r in (1.0, 0.25, 0.05): C[f'Australia ratio {r}'] = (H, PW, mu_tiers(meta, au=ruled_au(r)), 0, 'full')
        C['all but Mossel Bay'] = ([x for x in H if x != MB], PW, mu0, 0, 'full'); C['all but Mossel Bay and Paindane'] = ([x for x in H if x not in (MB, PA)], PW, mu0, 0, 'full')
        C['only Mossel Bay'] = ([MB], PW, mu0, 0, 'full'); C['only the flaperon'] = ([FL], PW, mu0, 0, 'full')
        for si, h in ((1, 25), (2, 100), (3, 200)): C[f'kernel {h} km'] = (H, PW, mu0, si, 'full')
        C['particle half a'] = (H, PW, mu0, 0, 'half_a'); C['particle half b'] = (H, PW, mu0, 0, 'half_b')
    for name, (sel, pw, mu, si, part) in C.items():
        if not set(sel) <= set(ids): continue
        L = score(meta, recs, nenv, common, mu, sel, pw, part=part, si=si, wnode=core('H_D0_all', lat, lon)[2])
        for key in ('H_D0_all', 'H_D1_all', 'H_D2_all'):
            base, post, _ = core(key, lat, lon)
            if not any(r['case'] == 'core only' and r['core'] == key for r in rows): rows.append(dict(core=key, variant='-', case='core only', n_items=0, **base, shift=0.0, lnR=np.nan))
            if key != 'H_D0_all' and not name.startswith(('HEADLINE', 'ladder')): continue
            rows.append(dict(core=key, variant=v, case=name, n_items=len(sel), **post(L['globcurrent'], L['glorys12']), lnR=lnR(L['globcurrent'], L['glorys12'], lat) if key == 'H_D0_all' else np.nan))
            if key == 'H_D0_all' and name.startswith(('HEADLINE', 'ladder')):
                for m in MODELS: rows.append(dict(core=key, variant=v, case=f'{name} [{m} only]', n_items=len(sel), **post(L[m], L[m]), lnR=np.nan))
        if name in ('HEADLINE: twelve non-circular items, identity-weighted', 'Australia ratio 0.25', 'time ashore: fresh marks 10 d, 10 d, 14 d') or (v == 'R0-module-run' and name == 'ladder: nine finds'):
            dens[f'{v}|{name}'] = density('H_D0_all', lat, lon, L['globcurrent'], L['glorys12'], edges)
        print(v, name, flush=True)
    if 'core' not in dens: dens['core'] = density('H_D0_all', lat, lon, None, None, edges)
os.makedirs('res-final-ramp', exist_ok=True)
PS = pd.DataFrame(rows); PS['level_draws'] = ZDRAWS; PS['level_draw_seed'] = ZSEED; PS.to_csv('res-final-ramp/final-posterior-summaries.csv', index=False)
pd.DataFrame({'lat_lo': edges[:-1], 'lat_hi': edges[1:], **dens}).to_csv('res-final-ramp/latitude-densities.csv', index=False)
pd.set_option('display.width', 250); print(PS[(PS.core == 'H_D0_all') & ~PS.case.str.contains(r'\[')][['variant', 'case', 'n_items', 'mean', 'median', 'p05', 'p95', 'shift', 'N33', 'S38', 'lnR']].round(3).to_string(index=False))
