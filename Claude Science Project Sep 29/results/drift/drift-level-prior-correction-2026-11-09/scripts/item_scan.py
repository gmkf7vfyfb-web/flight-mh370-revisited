"""ITEM-SPECIFIC WINDAGE SCAN (11 Nov 2026), ocean drift module, exterior class.
Each exterior item gets its own windage distribution: a target of the reweighted wide legs (log-normal, sigma 0.35, median m) or a linear mixture of targets
(coefficients a and A are linear in the particle weights, so a mixture of windage densities is the same mixture of coefficients). Class-wide scenarios must
reproduce res-grid/<tag>/lm-head-s*.npz (validation). Item terms are cached as per-node float32 arrays; a scenario is their sum over items.
Usage: VARIANT=RG-val_production OUTD=res-item TAGS='{"P":"RG-val_production",...}' SCEN=scenarios.json LEVELS=ramp python item_scan.py head SEED [SEED ...]
Output: res-item/<scenario>/lm-head-s<seed>.npz (same format as stage 1).
"""
import sys, os, time, resource, numpy as np
CFG = sys.argv[1]; SEEDS = [int(s) for s in sys.argv[2:]]
sys.argv = ['x', 'rescore/x', '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/run-j-maps-accumulators.npz', 'arcm.npz', 'audit.csv', os.environ['OUTD']]
_RA = open('offline/rescore_analysis.py').read().split('rows = []; nodevals = {}')[0]     # third block of ocean samples (wide3, seeds 233-248) merged with the second
_OLD = "for f in sorted(glob.glob(pat.format('ext2', m))):"; assert _OLD in _RA
exec(_RA.replace(_OLD, "for f in sorted(glob.glob(pat.format('ext2', m))) + sorted(glob.glob(pat.format('ext3', m))):"))
ZDRAWS = 16384; t0 = time.time()
meta, recs, nenv = load(os.environ['VARIANT'])
common = sorted(set(recs['globcurrent']) & set(recs['glorys12'])); lat = np.array([recs['globcurrent'][k]['lat'] for k in common]); lon = np.array([recs['globcurrent'][k]['lon'] for k in common])
ids = [f['id'] for f in meta.finds]
NINE = [f for f in ids if f.startswith('item:') and aud.loc[f.split(':')[1], 'stringent_nine'] == 'yes']
HI = NINE + [f'item:{o}' for o in ('linga-linga-vertical-stabilizer', 'nautilus-bay-right-aileron', 'mpame-right-flap-fairing') if f'item:{o}' in ids]
PW = {f: GRADE_P[aud.loc[f.split(':')[1], 'official_classification']] for f in HI}; MB = 'item:mossel-bay-engine-cowling-roy'
MAR = 'shadow:mossel-bay-refound-2016-03-21'; F10 = 'shadow:mossel-bay-fresh-10d'
for _s in (MAR, F10): PW[_s] = PW[MB]  # same identity grade as the original item; only the date model changes
if CFG == 'pw1': PW = {f: 1.0 for f in PW}   # sensitivity: every item certain (no mixture with unrelated debris)
if CFG == 'pwlow': PW = {f: {1.0: 1.0, 0.98: 0.9, 0.9: 0.7}.get(v, v) for f, v in PW.items()}   # sensitivity: pessimistic weights 1 / 0.9 / 0.7
swapmb = lambda new: [new if x == MB else x for x in HI]
CONF = {'pw1': (HI, mu_tiers(meta)), 'pwlow': (HI, mu_tiers(meta)), 'mbonly': ([MB], mu_tiers(meta)), 'mbonlymar': ([MAR], mu_tiers(meta)), 'mar': (swapmb(MAR), mu_tiers(meta)), 'fresh10': (swapmb(F10), mu_tiers(meta)), 'head': (HI, mu_tiers(meta)), 'au025': (HI, mu_tiers(meta, au=ruled_au(0.25))), 'butmb': ([x for x in HI if x != MB], mu_tiers(meta)),
        'au025nomb': ([x for x in HI if x != MB], mu_tiers(meta, au=ruled_au(0.25)))}
sel, mu = CONF[CFG]; wnode = np.load('res-smooth-w48/wnode_df.npy'); assert len(wnode) == len(common) == 84, (len(wnode), len(common))
p = np.array([PW.get(f, 1.0) for f in sel])

import json, gc
TAGS = json.loads(os.environ['TAGS']); SCEN = json.load(open(os.environ['SCEN']))
RR = {'P': (meta, recs, nenv)}
for k, v in TAGS.items():
    if k != 'P': RR[k] = load(v)
idx = {f['id']: (f['class'], f['segment'], jj) for c in range(meta.ncls) for jj, j in enumerate(meta.by_class[c]) for f in [meta.finds[j]]}
pmap = dict(zip(sel, p)); cls1 = [f for f in sel if idx[f][0] == 1]
if os.environ.get('DRY') == '1':
    for f in sel: print(f, 'class', idx[f][0], 'p', round(float(pmap[f]), 3))
    sys.exit(0)
def short(name):
    hit = [f for f in sel if name in f]; assert len(hit) == 1, (name, hit); return hit[0]
SC = {}
for nm, d in SCEN.items():
    spec = {f: {'P': 1.0} for f in sel}
    for it, sp in d.items():
        if it == '*cls1':
            for f in cls1: spec[f] = sp
        else: spec[short(it)] = sp
    SC[nm] = spec
skey = lambda sp: tuple(sorted(sp.items()))
def T_item(fid, spec, m, nu):
    c, sg, jj = idx[fid]; out = []
    for k in common:
        envs = {t: RR[t][1][m][k]['sets'][0]['full'] for t in spec}; n = len(envs[next(iter(spec))]); T = np.full((n, ZDRAWS), -np.inf)
        for e in range(n):
            ks = {t: envs[t][e][c] for t in spec}
            if any(v is None for v in ks.values()): continue
            q = sum(w * (nu[:, sg * meta.np:(sg + 1) * meta.np] @ np.asarray(ks[t]['a'][jj])) for t, w in spec.items())
            Q = sum(w * (nu @ np.asarray(ks[t]['A'])) for t, w in spec.items())
            with np.errstate(divide='ignore'): T[e] = np.where((q > 0) & (Q > 0), np.log(np.maximum(q, 1e-300)) - np.log(np.maximum(Q, 1e-300)), -np.inf)
        out.append(T)
    return out
def M_item(T, pi):
    if pi >= 1.0: return [t.astype(np.float32) for t in T]
    bj = np.zeros(ZDRAWS)
    for w, Tn in zip(wnode, T):
        with np.errstate(over='ignore'): bj += w * np.exp(Tn).mean(0)
    lb = np.log(np.maximum(bj, 1e-300)); lp = np.log(max(pi, 1e-300)); l1 = np.log(max(1 - pi, 1e-300))
    return [np.logaddexp(lp + Tn, l1 + lb[None, :]).astype(np.float32) for Tn in T]
MAXC = int(os.environ.get('MAXC', '24'))
for seed in SEEDS:
    meta.z = np.random.default_rng(seed).standard_normal((ZDRAWS, meta.z.shape[1])); nu = np.exp(mu[None, :] + meta.sigma * meta.z); out = {nm: {} for nm in SC}
    for m in MODELS:
        base = {f: M_item(T_item(f, {'P': 1.0}, m, nu), pmap[f]) for f in sel}; cache = {}; order = []
        for nm, spec in SC.items():
            S = [np.zeros((len(M), ZDRAWS)) for M in base[sel[0]]]
            for f in sel:
                sp = spec[f]
                if skey(sp) == skey({'P': 1.0}): arr = base[f]
                else:
                    kk = (f, skey(sp))
                    if kk not in cache:
                        cache[kk] = M_item(T_item(f, sp, m, nu), pmap[f]); order.append(kk)
                        while len(order) > MAXC: del cache[order.pop(0)]
                    arr = cache[kk]
                for i in range(len(S)): S[i] += arr[i]
            lm = np.full((len(common), 48), np.nan)
            for i, s in enumerate(S): lm[i, :s.shape[0]] = lmean(s, axis=1)
            out[nm][m] = lm
        del base, cache; gc.collect()
        print('seed', seed, m, 'done', round(time.time() - t0), 's; peak RSS GB', round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 2), flush=True)
    for nm in SC:
        d = f"{os.environ['OUTD']}/{nm}"; os.makedirs(d, exist_ok=True)
        np.savez(f"{d}/lm-{CFG}-s{seed}.npz", lm_globcurrent=out[nm]['globcurrent'], lm_glorys12=out[nm]['glorys12'], lat=lat, lon=lon, nodes=np.array(common))
