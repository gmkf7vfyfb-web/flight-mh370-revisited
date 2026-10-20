"""Item 6: populated-coast Australian factor at the Pleiades rating-5 targets vs the run J core (D0', two models, rho = 1 and others).
Factor at a point = L'(x)/L(x), L = 0.5(Lg + Lc) bilinear in likelihood over the run A node grid (land nodes renormalised out),
L' with each model's node values multiplied by exp(Delta_pop) (IDW-spread from the 15-160 E pilot). Core factor = Z'/Z from the composition."""
import sys, json, numpy as np
sys.argv = ['apply_australia.py', 'unused.json', 'glorys12=aus160-out/aus160-glorys12/nodes.csv', 'globcurrent=aus160-out/aus160-globcurrent/nodes.csv']
src = open('apply_australia.py').read(); exec(src.split("res = {'models'")[0])
PTS = [(91.356810, -34.453888), (91.306093, -34.501360), (91.298172, -34.546695), (90.456295, -34.557090), (90.493447, -34.593840), (90.457967, -35.205320)]
def interp(Ln, lon, lat):
    fi = (lat - G['lat0']) / G['dlat']; fj = (lon - G['lon0']) / G['dlon']; i, j = int(fi), int(fj); ti, tj = fi - i, fj - j
    ids = [i * NL + j, (i + 1) * NL + j, i * NL + j + 1, (i + 1) * NL + j + 1]; w = np.array([(1 - ti) * (1 - tj), ti * (1 - tj), (1 - ti) * tj, ti * tj])
    v = np.array([Ln[k] for k in ids]); ok = np.isfinite(v); return float((w[ok] * v[ok]).sum() / w[ok].sum())
P = {}
for mod, path in args.items():
    df = pd.read_csv(path); p = {s: np.mean([df[f'p_{c}_{i}'] for c in CLS], 0) for i, s in enumerate(SEGS)}
    F = sum(p[s] for s in SEGS[:6]); Wpop = sum(p[s] for s in POP); meta = deltas(path)[2]; P[mod] = (df.node.values.astype(int), F, Wpop, meta['k'], meta['c'])
out = {}
for rho in (0.1, 0.3, 1.0, 2.0):
    Lg, Lc = node_L('glorys12', 'h50'), node_L('globcurrent', 'h50'); Dl = {}
    for mod, (pn, F, Wpop, k, c) in P.items(): Dl[mod] = spread(pn, np.asarray(-k * np.log1p(rho * Wpop / (c * F)), float))
    Lg2, Lc2 = Lg * np.exp(Dl['glorys12']), Lc * np.exp(Dl['globcurrent'])
    fac = [np.log((interp(Lg2, *x) + interp(Lc2, *x)) / (interp(Lg, *x) + interp(Lc, *x))) for x in PTS]
    fg = [np.log(interp(Lg2, *x) / interp(Lg, *x)) for x in PTS]; fc = [np.log(interp(Lc2, *x) / interp(Lc, *x)) for x in PTS]
    # core Z'/Z, two-model mean
    (qg, ag, cg), (qc, ac, cc) = lin_terms('D0', 'glorys12', Lg), lin_terms('D0', 'globcurrent', Lc); (qg2, _, _), (qc2, _, _) = lin_terms('D0', 'glorys12', Lg2), lin_terms('D0', 'globcurrent', Lc2)
    e = np.exp(Z['D0|logc'] - Z['D0|logc'].max()); core = np.log((e * 0.5 * (qg2 + qc2)).sum() / (e * 0.5 * (qg + qc)).sum())
    out[rho] = {'pleiades_ln_factor_each': [round(x, 3) for x in fac], 'pleiades_ln_factor_mean_in_L': float(np.log(np.mean(np.exp(fac)))),
                'glorys12_each': [round(x, 3) for x in fg], 'globcurrent_each': [round(x, 3) for x in fc], 'core_ln_factor': float(core),
                'ln_LR_pleiades_vs_core': float(np.log(np.mean(np.exp(fac))) - core)}
    print(rho, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in out[rho].items()})
json.dump(out, open('pleiades-australia.json', 'w'), indent=1)
