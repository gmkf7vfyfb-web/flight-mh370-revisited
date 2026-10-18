"""Three-tier Australian term (Pete 17 Oct): ABS blue (major city + inner regional) = 1, yellow (outer regional) = y, red (remote) = 0,
times the 2014 level rho (relative to find-coast peak). Same fitted law, IDW spread and composition as apply_australia.py. D0', two models."""
import sys, json, numpy as np
sys.argv = ['apply_australia.py', 'unused.json', 'glorys12=aus160-out/aus160-glorys12/nodes.csv', 'globcurrent=aus160-out/aus160-globcurrent/nodes.csv']
src = open('apply_australia.py').read(); exec(src.split("res = {'models'")[0])
OUTER = [s for s in SEGS if s.endswith('-outer')]; print('outer segments', OUTER)
PARTS = {}
for mod, path in args.items():
    df = pd.read_csv(path); p = {s: np.mean([df[f'p_{c}_{i}'] for c in CLS], 0) for i, s in enumerate(SEGS)}
    meta = deltas(path)[2]; PARTS[mod] = (df.node.values.astype(int), sum(p[s] for s in SEGS[:6]), sum(p[s] for s in POP), sum(p[s] for s in OUTER), meta['k'], meta['c'])
rows = []
for D in ['D0', 'D1', 'D2', 'D3', 'D4', 'D5']:
    for y in ([0.0, 0.1, 0.3, 0.5] if D == 'D0' else [0.3]):
        for rho in ([0.1, 0.3, 0.5, 0.65, 1.0] if D == 'D0' else [0.3, 0.5, 0.65]):
            Ls, T = {}, {}
            for mod, (pn, F, Wp, Wo, k, c) in PARTS.items():
                d = -k * np.log1p(rho * (Wp + y * Wo) / (c * F)); Ls[mod] = node_L(mod, 'h50') * np.exp(spread(pn, np.asarray(d, float))); T[mod] = lin_terms(D, mod, Ls[mod])
            r = dict(D=D, outer_weight=y, rho_2014=rho)
            for mod in PARTS:
                s = stats(D, f'{mod}_h50', allidx, Ln=Ls[mod], q1=T[mod][0], lat1=T[mod][1], c1=T[mod][2]); r[f'shift_{mod}'] = round(s['mean_lat_shift'], 3)
            lg, lc = Ls['glorys12'], Ls['globcurrent']; Ln = np.where(np.isfinite(lg) & np.isfinite(lc), 0.5 * (lg + lc), np.nan)
            (qg, ag, cg), (qc, ac, cc) = T['glorys12'], T['globcurrent']
            s = stats(D, 'mean_h50', allidx, Ln=Ln, q1=0.5 * (qg + qc), lat1=0.5 * (ag + ac), c1=0.5 * (cg + cc))
            r.update(shift_two_models=round(s['mean_lat_shift'], 3), lnBF=round(s['lnBF_core_vs_uniform'], 3), mean_lat_with_drift=round(s['mean_lat_with_drift'], 3),
                     q05_q50_q95=[round(x, 2) for x in s.get('latitude_q05_q50_q95_with_drift', [np.nan] * 3)] if 'latitude_q05_q50_q95_with_drift' in s else None, drift_in_core90=round(s['drift_mass_in_core90'], 3))
            rows.append(r)
R = pd.DataFrame(rows); R.to_csv('drift-items/australia-three-tier.csv', index=False)
print(R.drop(columns=['q05_q50_q95']).to_string(index=False))
