"""Analysis of the extended-window drift run (finds window to 30 Jan 2017; 7-8 Nov 2026; 84 arc points x 2 ocean models;
16 environments, 32 south of 33.25 S). Exact offline re-scoring of the stored coefficients, including the shadow finds
(drift_coef.ln_l_sel). Same core posterior, interpolation and estimators as conv_analysis.py (run of 7 Nov).
Usage: python ext_analysis.py <pack_dir> <accumulators.npz> <ledger.npz> <out_dir>"""
import sys, os, glob, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import drift_coef as dc
RUN, ACC, LED, OUT = sys.argv[1:5]; os.makedirs(OUT, exist_ok=True)
MODELS = ('globcurrent', 'glorys12')
AU = ['AU-north-east-city-inner', 'AU-south-city-inner', 'AU-wa-city-inner', 'AU-north-east-outer', 'AU-south-outer', 'AU-wa-outer',
      'AU-indian-ocean-territories-remote', 'AU-north-east-remote', 'AU-south-remote', 'AU-wa-remote']
PARTS = ('full', 'half_a', 'half_b', 'shadow_full', 'shadow_half_a', 'shadow_half_b')
def ruled_mu(meta, rho, outer=0.3, remote=0.0):
    lv = lambda s: np.log(rho) if 'city-inner' in s else (np.log(outer * rho) if ('outer' in s and outer > 0) else (np.log(remote * rho) if ('remote' in s and remote > 0) else -30.0))
    return meta.mu({s: [lv(s)] * meta.np for s in AU})
# ---- load and pool (ext2-* adds 16 environments at the southern points; all parts incl. shadows concatenated)
meta, recs, tabs, nenv = {}, {m: {} for m in MODELS}, {m: [] for m in MODELS}, {m: {} for m in MODELS}
for m in MODELS:
    for f in sorted(glob.glob(f'{RUN}/ext-{m}-?-coefficients.jsonl')):
        lab = os.path.basename(f).replace('-coefficients.jsonl', '')
        meta[m] = dc.Meta(f'{RUN}/{lab}-coefficients-meta.json')
        for nd in dc.read_nodes(f): recs[m][nd['node']] = nd
        tabs[m].append(pd.read_csv(f'{RUN}/{lab}-nodes.csv'))
    tabs[m] = pd.concat(tabs[m], ignore_index=True)
    for k in recs[m]: nenv[m][k] = len(recs[m][k]['sets'][0]['full'])
    for f in sorted(glob.glob(f'{RUN}/ext2-{m}-?-coefficients.jsonl')):
        m2 = dc.Meta(f.replace('-coefficients.jsonl', '-coefficients-meta.json')); assert np.array_equal(m2.z, meta[m].z)
        assert [s['id'] for s in m2.m['shadow_finds']] == [s['id'] for s in meta[m].m['shadow_finds']]
        for nd in dc.read_nodes(f):
            assert nd['node'] in recs[m]
            for si, st in enumerate(nd['sets']):
                for part in PARTS: recs[m][nd['node']]['sets'][si][part] = recs[m][nd['node']]['sets'][si][part] + st[part]
            nenv[m][nd['node']] = len(recs[m][nd['node']]['sets'][0]['full'])
M0 = meta[MODELS[0]]; assert np.array_equal(M0.z, meta[MODELS[1]].z)
common = sorted(set(recs[MODELS[0]]) & set(recs[MODELS[1]]))
print('nodes per model', {m: len(recs[m]) for m in MODELS}, 'common', len(common), 'env counts', sorted(set(nenv['globcurrent'].values())))
NINE = [f['id'] for f in M0.finds]; ID = {i.split(':')[1].split('-20')[0] if i.startswith('shadow') else i.split(':')[1]: i for i in NINE + [s['id'] for s in M0.m['shadow_finds']]}
LL, NB = 'shadow:linga-linga-2016-08-26', 'shadow:nautilus-bay-2016-12-23'
HEAD = NINE + [LL]
def swap(sel, a, b): return [b if x == a else x for x in sel]
P = lambda s: 'debris:' + s
MB, PA, FL = P('mossel-bay-engine-cowling-roy'), P('paindane-right-flap-fairing'), P('reunion-right-flaperon')
CIRC = [s['id'] for s in M0.m['shadow_finds'] if 'identity-from-drift' in s['id']]
off = M0.mu({s: [-30.0] * M0.np for s in AU})
SHORT = {i: i.split(':')[1] for i in NINE + [LL, NB]}
# ---- cases: name -> (bandwidth set, part, mu, selection, env slice)
C = {}
C['headline: nine finds and Linga Linga'] = (0, 'full', off, HEAD, None)
C['nine finds only (Linga Linga non-find implied)'] = (0, 'full', off, NINE, None)
C['headline and Nautilus Bay'] = (0, 'full', off, HEAD + [NB], None)
C['headline, half a'] = (0, 'half_a', off, HEAD, None); C['headline, half b'] = (0, 'half_b', off, HEAD, None)
for bi, h in enumerate([25, 100, 200], 1): C[f'headline, kernel {h} km'] = (bi, 'full', off, HEAD, None)
C['Mossel Bay at second beaching (21-22 Mar 2016)'] = (0, 'full', off, swap(HEAD, MB, 'shadow:mossel-bay-refound-2016-03-21'), None)
alt = [(P('vilanculos-horizontal-stabilizer-panel'), 'shadow:vilanculos-official-2016-02-27', 'NO STEP panel on 27 Feb 2016'),
       (P('pemba-right-outboard-flap'), 'shadow:pemba-official-2016-06-20', 'Pemba flap on 20 Jun 2016'),
       (P('mauritius-left-outboard-flap'), 'shadow:mauritius-2016-05-08', 'Mauritius flap on 8 May 2016')]
s3 = HEAD
for a, b, lab in alt:
    C[lab] = (0, 'full', off, swap(HEAD, a, b), None); s3 = swap(s3, a, b)
C['all three official alternative dates'] = (0, 'full', off, s3, None)
fr = [(FL, 'shadow:flaperon-fresh-3d', 'flaperon fresh, 3 d'), (FL, 'shadow:flaperon-fresh-10d', 'flaperon fresh, 10 d'),
      (MB, 'shadow:mossel-bay-fresh-3d', 'Mossel Bay fresh, 3 d'), (MB, 'shadow:mossel-bay-fresh-10d', 'Mossel Bay fresh, 10 d'),
      (PA, 'shadow:paindane-fresh-14d', 'Paindane fresh, 14 d')]
for a, b, lab in fr: C[f'time ashore: {lab}'] = (0, 'full', off, swap(HEAD, a, b), None)
C['time ashore: all three marks (3 d, 3 d, 14 d)'] = (0, 'full', off, swap(swap(swap(HEAD, FL, fr[0][1]), MB, fr[2][1]), PA, fr[4][1]), None)
C['time ashore: all three marks (10 d, 10 d, 14 d)'] = (0, 'full', off, swap(swap(swap(HEAD, FL, fr[1][1]), MB, fr[3][1]), PA, fr[4][1]), None)
C['headline and five items identified from drift (sensitivity)'] = (0, 'full', off, HEAD + CIRC, None)
for i in HEAD:
    C[f'only {SHORT[i]}'] = (0, 'full', off, [i], None); C[f'all but {SHORT[i]}'] = (0, 'full', off, [x for x in HEAD if x != i], None)
C['all but Mossel Bay and Paindane'] = (0, 'full', off, [x for x in HEAD if x not in (MB, PA)], None)
for r in (1.0, 0.5, 0.25, 0.1, 0.05):
    C[f'Australia ratio {r}'] = (0, 'full', ruled_mu(M0, r), HEAD, None)
    C[f'Australia ratio {r}, populated coasts only'] = (0, 'full', ruled_mu(M0, r, outer=0.0), HEAD, None)
C['Australia ratio 0.25, half a'] = (0, 'half_a', ruled_mu(M0, 0.25), HEAD, None); C['Australia ratio 0.25, half b'] = (0, 'half_b', ruled_mu(M0, 0.25), HEAD, None)
C['Australia ratio 0.25, all but Mossel Bay and Paindane'] = (0, 'full', ruled_mu(M0, 0.25), [x for x in HEAD if x not in (MB, PA)], None)
C['headline, environments 1-16'] = (0, 'full', off, HEAD, slice(0, 16)); C['headline, environments 17-32'] = (0, 'full', off, HEAD, slice(16, 32))
for g in range(4): C[f'headline, environments {4*g+1}-{4*g+4}'] = (0, 'full', off, HEAD, slice(4 * g, 4 * g + 4))
def sl(setd, es):
    return setd if es is None else {k: v[es] for k, v in setd.items()}
V = {m: {} for m in MODELS}; ZF = {m: {} for m in MODELS}
for m in MODELS:
    for name, (bi, part, mu, sel, es) in C.items():
        out = []; zf = []
        for k in common:
            if es is not None and es.start >= nenv[m][k]: out.append(np.nan); zf.append(np.nan); continue
            v, z = dc.ln_l_sel(sl(recs[m][k]['sets'][bi], es), part, meta[m], mu, sel, return_zero_fraction=True); out.append(v); zf.append(z)
        V[m][name] = np.array(out); ZF[m][name] = np.array(zf)
for m in MODELS:
    L = np.stack([V[m]['headline: nine finds and Linga Linga']] + [V[m][f'headline, kernel {h} km'] for h in (25, 100, 200)])
    mx = L.max(0); V[m]['headline, kernel marginalised 25-200 km'] = mx + np.log(np.mean(np.exp(L - mx), 0))
# ---- validation against the module (first 16 environments; nine scored finds)
val = []
for m in MODELS:
    t = tabs[m].set_index('node')
    for col, mu in [('ln_l', M0.mu_primary), ('ln_l_lev_off', off), ('ln_l_lev_ruled_r025', ruled_mu(M0, 0.25)), ('ln_l_lev_ruled_r100', ruled_mu(M0, 1.0))]:
        v16 = np.array([dc.ln_l_sel(sl(recs[m][k]['sets'][0], slice(0, 16)), 'full', meta[m], mu, NINE) for k in common])
        mod = t.loc[common, col].values; ok = np.isfinite(mod)
        val.append(dict(model=m, column=col, n=int(ok.sum()), max_abs_diff=float(np.nanmax(np.abs(v16[ok] - mod[ok]))), undefined_agree=bool(np.array_equal(~ok, ~np.isfinite(v16)))))
VAL = pd.DataFrame(val); VAL.to_csv(f'{OUT}/validation-offline-vs-module.csv', index=False); print(VAL.to_string(index=False))
# ---- core posterior (run J 2-D histogram), as conv_analysis.py
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
        q = lambda f: cl[o][np.searchsorted(np.cumsum(p[o]), f)]
        return dict(mean=(p * cl).sum(), median=q(0.5), p05=q(0.05), p95=q(0.95), N33=100 * p[cl >= -33].sum(), N26=100 * p[cl >= -26].sum(), S38=100 * p[cl < -38].sum())
    base = summ(p0)
    def post(lnG, lnY=None, ret_p=False):
        a = (W * lnG[nn]).sum(1); b = a if lnY is None else (W * lnY[nn]).sum(1); mx = max(a.max(), b.max())
        Lc = 0.5 * (np.exp(a - mx) + np.exp(b - mx)); p = p0 * Lc; Z = p.sum(); p = p / Z
        s = summ(p); s['shift'] = s['mean'] - base['mean']; s['lnZ_rel'] = np.log(Z) + mx
        return (s, p) if ret_p else s
    return base, post, (cl, W, nn, p0)
rows = []
for key in ('H_D0_all', 'H_D1_all', 'H_D2_all'):
    if key not in A.files: continue
    base, post, _ = shifter(key); rows.append(dict(core=key, case='core only', **base, shift=0.0))
    for name in V[MODELS[0]]:
        rows.append(dict(core=key, case=name, **post(V['globcurrent'][name], V['glorys12'][name])))
        if name.startswith(('headline:', 'Australia ratio 0.25', 'headline, kernel marginalised')) and 'half' not in name and 'all but' not in name:
            for m in MODELS: rows.append(dict(core=key, case=f'{name} [{m} only]', **post(V[m][name])))
PS = pd.DataFrame(rows); PS.to_csv(f'{OUT}/posterior-summaries.csv', index=False)
print(PS[PS.core == 'H_D0_all'][['case', 'mean', 'median', 'shift', 'N33']].round(3).to_string(index=False))
# ---- evidence ratio of the core against a uniform-along-arc prior (1-D ledger, 00:19 data held out)
Z = np.load(LED); la = Z['D0|lat']; ok = np.isfinite(la); la = la[ok]; pc = np.nan_to_num(Z['D0|core'])[ok]; pu = np.nan_to_num(Z['D0|(uniform along the arc)'])[ok]
pc, pu = pc / pc.sum(), pu / pu.sum(); arc = np.round(lat * 2) / 2; rows = []
for name in V[MODELS[0]]:
    a, b = V['globcurrent'][name], V['glorys12'][name]
    if not (np.isfinite(a).all() and np.isfinite(b).all()): rows.append(dict(case=name, lnR=np.nan)); continue
    mx = max(a.max(), b.max()); L = 0.5 * (np.exp(a - mx) + np.exp(b - mx))
    Lb = pd.Series(L).groupby(arc).mean(); Li = np.interp(la, Lb.index.values, Lb.values)
    rows.append(dict(case=name, lnR=np.log((pc * Li).sum() / (pu * Li).sum())))
pd.DataFrame(rows).to_csv(f'{OUT}/evidence-ratio-core-vs-uniform.csv', index=False)
# ---- per-node values and convergence diagnostics
nd = {'lat': lat, 'lon': lon}
for m in MODELS:
    nd[f'{m}|headline'] = V[m]['headline: nine finds and Linga Linga']; nd[f'{m}|halfdiff'] = V[m]['headline, half a'] - V[m]['headline, half b']
    nd[f'{m}|env4_sd'] = np.nanstd([V[m][f'headline, environments {4*g+1}-{4*g+4}'] for g in range(4)], 0, ddof=1)
    nd[f'{m}|zero_env_fraction_headline'] = ZF[m]['headline: nine finds and Linga Linga']
    for i in HEAD: nd[f'{m}|zero_env_fraction_only_{SHORT[i]}'] = ZF[m][f'only {SHORT[i]}']
    nd[f'{m}|n_env'] = np.array([nenv[m][k] for k in common])
pd.DataFrame(nd).to_csv(f'{OUT}/node-diagnostics.csv', index=False)
pd.DataFrame({f'{m}|{n}': V[m][n] for m in MODELS for n in V[m]}, index=pd.MultiIndex.from_arrays([lat, lon], names=['lat', 'lon'])).to_csv(f'{OUT}/node-values-all-cases.csv')
# ---- posterior predictive check: expected identified finds by class, segment and period, headline posterior
base, post, (cl, W, nn, p0) = shifter('H_D0_all')
_, pcell = post(V['globcurrent']['headline: nine finds and Linga Linga'], V['glorys12']['headline: nine finds and Linga Linga'], ret_p=True)
wnode = np.zeros(len(common)); np.add.at(wnode, nn.ravel(), (pcell[:, None] * W).ravel()); wnode /= wnode.sum()
nu = np.exp(off[None, :] + M0.sigma * M0.z); ex = {m: np.zeros((M0.ncls, len(M0.seg), M0.np)) for m in MODELS}
for m in MODELS:
    for i, k in enumerate(common):
        acc = np.zeros((M0.ncls, len(M0.seg), M0.np)); ne = 0
        for env in recs[m][k]['sets'][0]['full']:
            ne += 1
            for c, kk in enumerate(env):
                if kk is None: continue
                Ab = np.asarray(kk['A'])[None, :] * nu; acc[c] += (Ab / Ab.sum(1, keepdims=True)).mean(0).reshape(len(M0.seg), M0.np)
        ex[m] += wnode[i] * acc / max(ne, 1)
tab = dc.find_table(M0); brk = M0.m['period_breaks_days']; obs = np.zeros((M0.ncls, len(M0.seg), M0.np))
tstart = {f['id']: f['t_start_days'] for f in M0.finds}; tstart.update({s['id']: s['t_start_days'] for s in M0.m['shadow_finds']})
for i in HEAD:
    _, c, sg, _ = tab[i]; obs[c, sg, int(np.searchsorted(brk, tstart[i], side='right'))] += 1
ncls = obs.sum((1, 2)); rows = []
PER = ['before 29 Jul 2015', '29 Jul 2015 - 29 Feb 2016', '1 Mar 2016 - 30 Jan 2017']
for c, cn_ in enumerate(M0.m['classes']):
    for sgi in range(6):
        for p in range(M0.np):
            e = 0.5 * (ex['globcurrent'][c, sgi, p] + ex['glorys12'][c, sgi, p]) * ncls[c]
            if e > 0.005 or obs[c, sgi, p] > 0: rows.append(dict(cls=cn_ if isinstance(cn_, str) else cn_.get('name'), segment=M0.seg[sgi], period=PER[p], expected=e, observed=obs[c, sgi, p]))
pd.DataFrame(rows).to_csv(f'{OUT}/posterior-predictive-finds.csv', index=False); print(pd.DataFrame(rows).round(2).to_string(index=False))
