"""Item 7: independent re-run of the 94 run A nodes carrying 95 % of run J core mass (seed 2, env seeds 5-8, 1e5 particles per node).
Compares new vs stored node ln L (empirical Monte Carlo noise), pools them (mean in likelihood), and recomputes the D0' drift
statistics (finds only, and the headline Australian scheme) with stored, new-only and pooled values at those nodes.
Usage: python refine_compare.py glorys12=<new nodes.csv> [globcurrent=<new nodes.csv>]"""
import sys, json, numpy as np
new = dict(a.split('=', 1) for a in sys.argv[1:])
sys.argv = ['apply_australia.py', 'unused.json', 'glorys12=aus160-out/aus160-glorys12/nodes.csv', 'globcurrent=aus160-out/aus160-globcurrent/nodes.csv']
src = open('apply_australia.py').read(); exec(src.split("res = {'models'")[0])
SEL = json.load(open('job3/nodes94.json'))
PARTS = {}
for mod, path in args.items():
    df = pd.read_csv(path); p = {s: np.mean([df[f'p_{c}_{i}'] for c in CLS], 0) for i, s in enumerate(SEGS)}
    meta = deltas(path)[2]; OUTER = [s for s in SEGS if s.endswith('-outer')]
    PARTS[mod] = spread(df.node.values.astype(int), np.asarray(-meta['k'] * np.log1p(0.5 * (sum(p[s] for s in POP) + 0.3 * sum(p[s] for s in OUTER)) / (meta['c'] * sum(p[s] for s in SEGS[:6]))), float))
res = {'nodes': len(SEL)}; L = {}
for mod in ('glorys12', 'globcurrent'):
    old = node_L(mod, 'h50').copy(); L[(mod, 'stored')] = old
    if mod in new:
        nd = pd.read_csv(new[mod]); v = dict(zip(nd.node.astype(int), nd.ln_l))
        idx = [n for n in SEL if n in v and np.isfinite(v[n]) and np.isfinite(old[n])]
        lo = np.log(old[idx]) + LREF if False else None
        oldln = np.array([np.log(old[n]) for n in idx]); newln = np.array([v[n] - LREF for n in idx])  # node_L is exp(ln_l - LREF)
        d = newln - oldln
        res[mod] = {'compared': len(idx), 'mean_diff': float(d.mean()), 'sd_diff': float(d.std()), 'per_node_sd_est': float(d.std() / np.sqrt(2)), 'max_abs_diff': float(np.abs(d).max())}
        nw = old.copy(); pl = old.copy()
        for n, x in zip(idx, newln): nw[n] = np.exp(x); pl[n] = 0.5 * (old[n] + np.exp(x))
        L[(mod, 'new')] = nw; L[(mod, 'pooled')] = pl
    else:
        L[(mod, 'new')] = old; L[(mod, 'pooled')] = old
def two(kind, aus):
    Ls = {m: L[(m, kind)] * (np.exp(PARTS[m]) if aus else 1) for m in ('glorys12', 'globcurrent')}; T = {m: lin_terms('D0', m, Ls[m]) for m in Ls}
    out = {}
    for m in Ls:
        s = stats('D0', f'{m}_h50', allidx, Ln=Ls[m], q1=T[m][0], lat1=T[m][1], c1=T[m][2]); out[m] = round(s['mean_lat_shift'], 3)
    Ln = np.where(np.isfinite(Ls['glorys12']) & np.isfinite(Ls['globcurrent']), 0.5 * (Ls['glorys12'] + Ls['globcurrent']), np.nan)
    (qg, ag, cg), (qc, ac, cc) = T['glorys12'], T['globcurrent']
    s = stats('D0', 'mean_h50', allidx, Ln=Ln, q1=0.5 * (qg + qc), lat1=0.5 * (ag + ac), c1=0.5 * (cg + cc))
    out['two models'] = round(s['mean_lat_shift'], 3); out['lnBF'] = round(s['lnBF_core_vs_uniform'], 3); return out
res['finds_only'] = {k: two(k, False) for k in ('stored', 'new', 'pooled')}
res['headline_australia'] = {k: two(k, True) for k in ('stored', 'new', 'pooled')}
json.dump(res, open('drift-items/refine-core94.json', 'w'), indent=1); print(json.dumps(res, indent=1))
