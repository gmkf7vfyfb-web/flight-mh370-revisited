"""Item 2: populated-coast Australian term vs assumed relative detection level rho (populated Australian coast vs find coasts;
rho = 1 is the find-coast level used for the headline sensitivity). Reuses apply_australia.py's fitted law, IDW spread and composition."""
import sys, json, numpy as np
sys.argv = ['apply_australia.py', 'unused.json', 'glorys12=aus160-out/aus160-glorys12/nodes.csv', 'globcurrent=aus160-out/aus160-globcurrent/nodes.csv']
src = open('apply_australia.py').read(); exec(src.split("res = {'models'")[0])
RHO = [0.0, 0.01, 0.03, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0, 3.0]
PARTS = {}
for mod, path in args.items():
    df = pd.read_csv(path); p = {s: np.mean([df[f'p_{c}_{i}'] for c in CLS], 0) for i, s in enumerate(SEGS)}
    F = sum(p[s] for s in SEGS[:6]); Wpop = sum(p[s] for s in POP); k, c = deltas(path)[2]['k'], deltas(path)[2]['c']
    PARTS[mod] = (df.node.values.astype(int), F, Wpop, k, c)
out = {}
for D in ['D0', 'D1', 'D2', 'D3', 'D4', 'D5']:
    for rho in RHO:
        Ls, terms = {}, {}
        for mod, (pn, F, Wpop, k, c) in PARTS.items():
            d = -k * np.log1p(rho * Wpop / (c * F)); Ls[mod] = node_L(mod, 'h50') * np.exp(spread(pn, np.asarray(d, float))); terms[mod] = lin_terms(D, mod, Ls[mod])
        row = {}
        for mod in PARTS:
            s = stats(D, f'{mod}_h50', allidx, Ln=Ls[mod], q1=terms[mod][0], lat1=terms[mod][1], c1=terms[mod][2]); row[mod] = (s['mean_lat_shift'], s['lnBF_core_vs_uniform'])
        lg, lc = Ls['glorys12'], Ls['globcurrent']; Ln = np.where(np.isfinite(lg) & np.isfinite(lc), 0.5 * (lg + lc), np.nan)
        (qg, ag, cg), (qc, ac, cc) = terms['glorys12'], terms['globcurrent']
        s = stats(D, 'mean_h50', allidx, Ln=Ln, q1=0.5 * (qg + qc), lat1=0.5 * (ag + ac), c1=0.5 * (cg + cc))
        row['two models'] = (s['mean_lat_shift'], s['lnBF_core_vs_uniform'], s['mean_lat_with_drift'], s['drift_mass_in_core90'])
        out[f'{D}|{rho}'] = row
json.dump(out, open('detection-curve.json', 'w'), indent=1)
for rho in RHO: print(rho, {m: tuple(round(x, 3) for x in v) for m, v in out[f'D0|{rho}'].items()})
