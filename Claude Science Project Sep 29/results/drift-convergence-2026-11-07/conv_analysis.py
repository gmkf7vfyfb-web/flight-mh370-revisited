"""Analysis of the 7 Nov 2026 convergence and coefficient run (84 arc-latitude points x 2 ocean models, 16 environments).
Usage: python conv_analysis.py <run_dir with conv-<model>-<k>-{coefficients.jsonl,coefficients-meta.json,nodes.csv}> <old_arclat_dir> <old_ext_dir> <accumulators.npz> <out_dir>
Every number is an exact offline re-scoring of the stored coefficients (drift_coef.py), validated against the module's own columns."""
import sys, os, glob, json, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drift_coef as dc
RUN, OLDA, OLDE, ACC, OUT = sys.argv[1:6]; os.makedirs(OUT, exist_ok=True)
MODELS = ('globcurrent', 'glorys12')
AU = ['AU-north-east-city-inner', 'AU-south-city-inner', 'AU-wa-city-inner', 'AU-north-east-outer', 'AU-south-outer', 'AU-wa-outer',
      'AU-indian-ocean-territories-remote', 'AU-north-east-remote', 'AU-south-remote', 'AU-wa-remote']
def ruled_mu(meta, rho, outer=0.3, remote=0.0):
    lv = lambda s: np.log(rho) if 'city-inner' in s else (np.log(outer * rho) if ('outer' in s and outer > 0) else (np.log(remote * rho) if ('remote' in s and remote > 0) else -30.0))
    return meta.mu({s: [lv(s)] * meta.np for s in AU})
# ---- load
meta, recs, tabs = {}, {m: {} for m in MODELS}, {m: [] for m in MODELS}
for m in MODELS:
    for f in sorted(glob.glob(f'{RUN}/conv-{m}-*-coefficients.jsonl')):
        lab = os.path.basename(f).replace('-coefficients.jsonl', '')
        meta[m] = dc.Meta(f'{RUN}/{lab}-coefficients-meta.json')
        for nd in dc.read_nodes(f): recs[m][nd['node']] = nd
        if os.path.exists(f'{RUN}/{lab}-nodes.csv'): tabs[m].append(pd.read_csv(f'{RUN}/{lab}-nodes.csv'))
    tabs[m] = pd.concat(tabs[m], ignore_index=True) if tabs[m] else pd.DataFrame()
# supplement (conv2-*): 16 further environments at the southern points; pooled by concatenating environment lists
nenv = {m: {} for m in MODELS}
for m in MODELS:
    for k in recs[m]: nenv[m][k] = len(recs[m][k]['sets'][0]['full'])
    for f in sorted(glob.glob(f'{RUN}/conv2-{m}-*-coefficients.jsonl')):
        m2 = dc.Meta(f.replace('-coefficients.jsonl', '-coefficients-meta.json')); assert np.array_equal(m2.z, meta[m].z)
        for nd in dc.read_nodes(f):
            if nd['node'] not in recs[m]: continue
            for si, st in enumerate(nd['sets']):
                for part in ('full', 'half_a', 'half_b'): recs[m][nd['node']]['sets'][si][part] = recs[m][nd['node']]['sets'][si][part] + st[part]
            nenv[m][nd['node']] = len(recs[m][nd['node']]['sets'][0]['full'])
M0 = meta[MODELS[0]]; assert np.array_equal(M0.z, meta[MODELS[1]].z)
common = sorted(set(recs[MODELS[0]]) & set(recs[MODELS[1]]))
print('nodes per model', {m: len(recs[m]) for m in MODELS}, 'common', len(common))
FIND = [f['id'].replace('debris:', '') for f in M0.finds]
# ---- cases: name -> (bandwidth set index, part, mu, finds, env slice)
off = M0.mu({s: [-30.0] * M0.np for s in AU})
cases = {'finds only': (0, 'full', off, None, None), 'finds only half a': (0, 'half_a', off, None, None), 'finds only half b': (0, 'half_b', off, None, None),
         'option B (module primary)': (0, 'full', M0.mu_primary, None, None)}
for bi, h in enumerate([25, 100, 200], 1): cases[f'finds only, kernel {h} km'] = (bi, 'full', off, None, None)
for r in (1.0, 0.65, 0.5, 0.25, 0.1, 0.05):
    cases[f'Australia ratio {r}'] = (0, 'full', ruled_mu(M0, r), None, None)
    cases[f'Australia ratio {r} half a'] = (0, 'half_a', ruled_mu(M0, r), None, None); cases[f'Australia ratio {r} half b'] = (0, 'half_b', ruled_mu(M0, r), None, None)
    cases[f'Australia ratio {r}, populated only'] = (0, 'full', ruled_mu(M0, r, outer=0.0), None, None)
for j, n in enumerate(FIND):
    cases[f'only {n}'] = (0, 'full', off, [j], None); cases[f'all but {n}'] = (0, 'full', off, [k for k in range(len(FIND)) if k != j], None)
MB = [j for j, n in enumerate(FIND) if n.startswith('mossel-bay') or n.startswith('paindane')]
cases['all but Mossel Bay and Paindane'] = (0, 'full', off, [k for k in range(len(FIND)) if k not in MB], None)
cases['Australia ratio 0.25, all but Mossel Bay and Paindane'] = (0, 'full', ruled_mu(M0, 0.25), [k for k in range(len(FIND)) if k not in MB], None)
cases['finds only, first 16 environments'] = (0, 'full', off, None, slice(0, 16))
cases['finds only, environments 17-32'] = (0, 'full', off, None, slice(16, 32))
for g in range(4): cases[f'finds only, environments {4*g+1}-{4*g+4}'] = (0, 'full', off, None, slice(4 * g, 4 * g + 4))
for g in range(2): cases[f'finds only, environments {8*g+1}-{8*g+8}'] = (0, 'full', off, None, slice(8 * g, 8 * g + 8))
V = {m: {} for m in MODELS}
for m in MODELS:
    for name, (bi, part, mu, finds, es) in cases.items():
        V[m][name] = np.array([(dc.ln_l(recs[m][k]['sets'][bi][part][es] if es else recs[m][k]['sets'][bi][part], meta[m], mu, finds)
                                if (es is None or es.start < nenv[m][k]) else np.nan) for k in common])
# bandwidth marginal (equal weights on 25/50/100/200 km, i.e. log-uniform), in likelihood
for m in MODELS:
    L = np.stack([V[m]['finds only']] + [V[m][f'finds only, kernel {h} km'] for h in (25, 100, 200)])
    mx = L.max(0); V[m]['finds only, kernel marginalised 25-200 km'] = mx + np.log(np.mean(np.exp(L - mx), 0))
# ---- validation against the module's own columns
val = []
for m in MODELS:
    t = tabs[m].set_index('node')
    for name, col in [('option B (module primary)', 'ln_l'), ('finds only', 'ln_l_lev_off'), ('finds only half a', 'ln_l_lev_off_half_a'),
                      ('Australia ratio 1.0', 'ln_l_lev_ruled_r100'), ('Australia ratio 0.5', 'ln_l_lev_ruled_r050'), ('Australia ratio 0.25', 'ln_l_lev_ruled_r025'),
                      ('finds only, kernel 25 km', None)]:
        if col is None or col not in t.columns: continue
        bi, part, mu, finds, _ = cases[name]
        v16 = np.array([dc.ln_l(recs[m][k]['sets'][bi][part][:16], meta[m], mu, finds) for k in common])
        mod = t.loc[common, col].values; d = v16 - mod; ok = np.isfinite(mod)
        val.append(dict(model=m, case=name, column=col, n=int(ok.sum()), max_abs_diff=float(np.nanmax(np.abs(d[ok]))) if ok.any() else np.nan,
                        nan_agree=bool(np.array_equal(~ok, ~np.isfinite(v16)))))
VAL = pd.DataFrame(val); VAL.to_csv(f'{OUT}/validation-offline-vs-module.csv', index=False); print(VAL.to_string(index=False))
# ---- geometry and core posterior (2-D run J histogram, as merge_arclat / ruled_australia_offline)
lat = np.array([recs[MODELS[0]][k]['lat'] for k in common]); lon = np.array([recs[MODELS[0]][k]['lon'] for k in common])
A = np.load(ACC)
def core_cells(key):
    H = A[key].astype(float); hl0, hn0, hg = float(A['lat0']), float(A['lon0']), float(A['grid'])
    hlat = hl0 + (np.arange(H.shape[0]) + 0.5) * hg; hlon = hn0 + (np.arange(H.shape[1]) + 0.5) * hg
    ii, jj = np.nonzero(H > 0); return hlat[ii], hlon[jj], H[ii, jj]
def shifter(key):
    cl, cn, hw = core_cells(key)
    dist = np.hypot((cn[:, None] - lon[None]) * 111.2 * np.cos(np.radians(cl[:, None])), (cl[:, None] - lat[None]) * 111.2)
    nn = np.argsort(dist, 1)[:, :6]; W = 1 / np.maximum(np.take_along_axis(dist, nn, 1), 1.0) ** 2; W /= W.sum(1, keepdims=True)
    p0 = hw / hw.sum(); o = np.argsort(cl)
    def summ(p):
        return dict(mean=(p * cl).sum(), median=cl[o][np.searchsorted(np.cumsum(p[o]), 0.5)], p05=cl[o][np.searchsorted(np.cumsum(p[o]), 0.05)],
                    p95=cl[o][np.searchsorted(np.cumsum(p[o]), 0.95)], N33=100 * p[cl >= -33].sum(), N26=100 * p[cl >= -26].sum(), S38=100 * p[cl < -38].sum())
    base = summ(p0)
    def post(lnG, lnY=None, ret_p=False):
        a = (W * lnG[nn]).sum(1); b = a if lnY is None else (W * lnY[nn]).sum(1); mx = max(a.max(), b.max())
        Lc = 0.5 * (np.exp(a - mx) + np.exp(b - mx)); p = p0 * Lc; Z = p.sum(); p = p / Z
        s = summ(p); s['shift'] = s['mean'] - base['mean']; s['lnZ_rel'] = np.log(Z) + mx
        return (s, p) if ret_p else s
    return base, post, (cl, W, nn, p0)
rows = []
for key in ('H_D0_all', 'H_D1_all', 'H_D2_all') if 'H_D2_all' in A.files else ('H_D0_all',):
    base, post, _ = shifter(key); rows.append(dict(core=key, case='core only', **{k: base[k] for k in base}, shift=0.0))
    for name in V[MODELS[0]]:
        s = post(V['globcurrent'][name], V['glorys12'][name]); rows.append(dict(core=key, case=name, **s))
        if not name.startswith('only') and not name.startswith('all but') and 'environments' not in name and 'half' not in name:
            for m in MODELS:
                s = post(V[m][name]); rows.append(dict(core=key, case=f'{name} [{m} only]', **s))
P = pd.DataFrame(rows); P.to_csv(f'{OUT}/posterior-summaries.csv', index=False)
# ---- old 4-environment run at the same points (independent seeds), finds only, for the convergence comparison
def load_old(m):
    fs = sorted(glob.glob(f'{OLDA}/arclat-{m}-*-nodes.csv')) + [f for f in sorted(glob.glob(f'{OLDE}/arclat-ext-{m}-*-nodes.csv')) if 'seedcheck' not in f]
    d = pd.concat([pd.read_csv(f) for f in fs], ignore_index=True); d['k'] = list(zip(d.lat_deg.round(4), d.lon_deg.round(4)))
    return d.drop_duplicates('k').set_index('k')
oldv = {}
for m in MODELS:
    d = load_old(m); keys = list(zip(lat.round(4), lon.round(4)))
    dl = np.array([k[0] for k in d.index]); dn = np.array([k[1] for k in d.index]); vv = d['ln_l_lev_off'].values
    idx = [int(np.argmin(np.hypot(dl - a, (dn - b) * np.cos(np.radians(a))))) for a, b in zip(lat, lon)]
    dmin = [float(np.hypot(dl[i] - a, (dn[i] - b) * np.cos(np.radians(a)))) for i, a, b in zip(idx, lat, lon)]
    assert max(dmin) < 0.01, max(dmin); oldv[m] = vv[idx]
base, post, _ = shifter('H_D0_all')
conv = [dict(case='4 environments, 18-20 Oct run (seeds 1-4)', **post(oldv['globcurrent'], oldv['glorys12']))]
for g in range(4): conv.append(dict(case=f'4 environments, this run ({4*g+101}-{4*g+104})', **post(V['globcurrent'][f'finds only, environments {4*g+1}-{4*g+4}'], V['glorys12'][f'finds only, environments {4*g+1}-{4*g+4}'])))
for g in range(2): conv.append(dict(case=f'8 environments, this run ({8*g+101}-{8*g+108})', **post(V['globcurrent'][f'finds only, environments {8*g+1}-{8*g+8}'], V['glorys12'][f'finds only, environments {8*g+1}-{8*g+8}'])))
conv.append(dict(case='16 environments, this run (101-116), all points', **post(V['globcurrent']['finds only, first 16 environments'], V['glorys12']['finds only, first 16 environments'])))
conv.append(dict(case='pooled: 32 environments south of 33.25 S (101-132), 16 north', **post(V['globcurrent']['finds only'], V['glorys12']['finds only'])))
for nm in ('finds only half a', 'finds only half b'):
    conv.append(dict(case=f'pooled, particle {nm[-6:]}', **post(V['globcurrent'][nm], V['glorys12'][nm])))
CV = pd.DataFrame(conv); CV.to_csv(f'{OUT}/convergence-finds-only.csv', index=False)
# node-level scatter, old vs new, finds only
nd = pd.DataFrame(dict(lat=lat, lon=lon, **{f'new_{m}': V[m]['finds only'] for m in MODELS}, **{f'old_{m}': oldv[m] for m in MODELS},
                       **{f'halfdiff_{m}': V[m]['finds only half a'] - V[m]['finds only half b'] for m in MODELS},
                       **{f'env4_sd_{m}': np.std([V[m][f'finds only, environments {4*g+1}-{4*g+4}'] for g in range(4)], 0, ddof=1) for m in MODELS}))
nd.to_csv(f'{OUT}/node-values-finds-only.csv', index=False)
# per-node all cases (both models) for reuse
pd.DataFrame({f'{m}|{n}': V[m][n] for m in MODELS for n in V[m]}, index=pd.MultiIndex.from_arrays([lat, lon], names=['lat', 'lon'])).to_csv(f'{OUT}/node-values-all-cases.csv')
print(CV.round(3).to_string(index=False))
print(P[P.core == 'H_D0_all'][['case', 'shift', 'median', 'N33', 'lnZ_rel']].round(3).to_string(index=False))

# ---- evidence ratio of the core against a uniform-along-arc prior, under each drift case (1-D ledger bins, 00:19 data held out)
LED = os.environ.get('LEDGER_NPZ')
if LED:
    Z = np.load(LED); la = Z['D0|lat']; ok = np.isfinite(la); la = la[ok]; pc = np.nan_to_num(Z['D0|core'])[ok]; pu = np.nan_to_num(Z['D0|(uniform along the arc)'])[ok]
    pc, pu = pc / pc.sum(), pu / pu.sum()
    arc = np.round(lat * 2) / 2
    rows = []
    for name in V[MODELS[0]]:
        a, b = V['globcurrent'][name], V['glorys12'][name]
        if not (np.isfinite(a).all() and np.isfinite(b).all()): rows.append(dict(case=name, lnR=np.nan)); continue
        mx = max(a.max(), b.max()); L = 0.5 * (np.exp(a - mx) + np.exp(b - mx))
        Lb = pd.Series(L).groupby(arc).mean(); Li = np.interp(la, Lb.index.values, Lb.values)
        rows.append(dict(case=name, lnR=np.log((pc * Li).sum() / (pu * Li).sum())))
    pd.DataFrame(rows).to_csv(f'{OUT}/evidence-ratio-core-vs-uniform.csv', index=False)
# ---- posterior predictive check: expected share of identified recoveries by find segment and period, finds-only posterior
base, post, (cl, W, nn, p0) = shifter('H_D0_all')
s_, pcell = post(V['globcurrent']['finds only'], V['glorys12']['finds only'], ret_p=True)
wnode = np.zeros(len(common)); np.add.at(wnode, nn.ravel(), (pcell[:, None] * W).ravel()); wnode /= wnode.sum()
nu = np.exp(off[None, :] + M0.sigma * M0.z); seg6 = list(range(6))
exp_share = {m: np.zeros((M0.ncls, len(M0.seg), M0.np)) for m in MODELS}
for m in MODELS:
    for i, k in enumerate(common):
        acc = np.zeros((M0.ncls, len(M0.seg), M0.np)); ne = 0
        for env in recs[m][k]['sets'][0]['full']:
            ne += 1
            for c, kk in enumerate(env):
                if kk is None: continue
                Ab = np.asarray(kk['A'])[None, :] * nu; acc[c] += (Ab / Ab.sum(1, keepdims=True)).mean(0).reshape(len(M0.seg), M0.np)
        exp_share[m] += wnode[i] * acc / max(ne, 1)
obs = np.zeros((M0.ncls, len(M0.seg), M0.np))
brk = M0.m['period_breaks_days']
for f in M0.finds:
    p = int(np.searchsorted(brk, f['t_start_days'], side='right')); obs[f['class'], f['segment'], p] += 1
nc = obs.sum((1, 2))
rows = []
for c, cn_ in enumerate(M0.m['classes']):
    for sgi in seg6:
        for p in range(M0.np):
            e = 0.5 * (exp_share['globcurrent'][c, sgi, p] + exp_share['glorys12'][c, sgi, p]) * nc[c]
            if e > 0.005 or obs[c, sgi, p] > 0:
                rows.append(dict(cls=cn_, segment=M0.seg[sgi], period=['before 29 Jul 2015', '29 Jul 2015 - 29 Feb 2016', '1 Mar - 30 Jun 2016'][p], expected=e, observed=obs[c, sgi, p]))
pd.DataFrame(rows).to_csv(f'{OUT}/posterior-predictive-finds.csv', index=False)
print(pd.DataFrame(rows).round(2).to_string(index=False))

# ---- point-level environment convergence (finds only): subsets against the pooled estimate
rows = []
for m in MODELS:
    ref = V[m]['finds only']
    for name in [n for n in V[m] if n.startswith('finds only, environments') or n == 'finds only, first 16 environments']:
        v = V[m][name]; ok = np.isfinite(v) & np.isfinite(ref)
        for band, sel in (('south of 33.25 S', lat < -33.25), ('33.25 S and north', lat >= -33.25)):
            k = ok & sel
            rows.append(dict(model=m, subset=name, band=band, points=int(sel.sum()), unresolved=int((~np.isfinite(v) & sel).sum()),
                             mean_diff_vs_pooled=float(np.mean(v[k] - ref[k])) if k.any() else np.nan, rms_diff_vs_pooled=float(np.sqrt(np.mean((v[k] - ref[k]) ** 2))) if k.any() else np.nan))
    for band, sel in (('south of 33.25 S', lat < -33.25), ('33.25 S and north', lat >= -33.25)):
        o = oldv[m]; k = np.isfinite(o) & np.isfinite(ref) & sel
        rows.append(dict(model=m, subset='18-20 Oct run, 4 environments (seeds 1-4)', band=band, points=int(sel.sum()), unresolved=int((~np.isfinite(o) & sel).sum()),
                         mean_diff_vs_pooled=float(np.mean(o[k] - ref[k])), rms_diff_vs_pooled=float(np.sqrt(np.mean((o[k] - ref[k]) ** 2)))))
        hd = (V[m]['finds only half a'] - V[m]['finds only half b'])[sel]
        rows.append(dict(model=m, subset='particle split halves of the pooled run (a minus b)', band=band, points=int(sel.sum()), unresolved=int((~np.isfinite(hd)).sum()),
                         mean_diff_vs_pooled=float(np.nanmean(hd)), rms_diff_vs_pooled=float(np.sqrt(np.nanmean(hd ** 2)))))
EC = pd.DataFrame(rows); EC.to_csv(f'{OUT}/environment-convergence-points.csv', index=False); print(EC.round(2).to_string(index=False))
