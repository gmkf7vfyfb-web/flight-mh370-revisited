"""Item 3: uncertainty of the populated-coast Australian term (rho = 1), D0' two models. Replicates (200 each):
(a) drift node noise only (as analyze_runj: ln L_node + N(-s^2/2, s), s per 1-deg band from split halves);
(b) (a) + pilot-node Monte Carlo noise in Delta (N(-s^2/2, s) at each pilot node, s = that model's split-half SD of Delta_B), before IDW;
(c) (b) + law misfit (extra N(0, sd) at each pilot node, sd = SD of the option-C hold-out residual of the fitted law);
plus a 1000-draw seed bootstrap of the point estimate."""
import sys, json, numpy as np
sys.argv = ['apply_australia.py', 'unused.json', 'glorys12=aus160-out/aus160-glorys12/nodes.csv', 'globcurrent=aus160-out/aus160-globcurrent/nodes.csv']
src = open('apply_australia.py').read(); exec(src.split("res = {'models'")[0])
P = {}
for mod, path in args.items():
    pn, Ds, meta = deltas(path); P[mod] = (pn, np.asarray(Ds['populated-only (reconstructed)'], float), meta['split_half_sd_of_Delta_B'], meta['C_residual_mean_sd'][1])
rng = np.random.default_rng(20261017); D = 'D0'
def one(mode, idx=allidx):
    Ls, T = {}, {}
    for mod, (pn, d, sh, misfit) in P.items():
        dd = d.copy()
        if mode in ('b', 'c'): dd = dd + rng.normal(-0.5 * sh ** 2, sh, dd.size)
        if mode == 'c': dd = dd + rng.normal(0, misfit, dd.size)
        dn = 0 if mode == 'point' else rng.normal(-0.5 * SDN[mod] ** 2, SDN[mod])
        Ls[mod] = node_L(mod, 'h50', dn) * np.exp(spread(pn, dd)); T[mod] = lin_terms(D, mod, Ls[mod])
    lg, lc = Ls['glorys12'], Ls['globcurrent']; Ln = np.where(np.isfinite(lg) & np.isfinite(lc), 0.5 * (lg + lc), np.nan)
    (qg, ag, cg), (qc, ac, cc) = T['glorys12'], T['globcurrent']
    s = stats(D, 'mean_h50', idx, Ln=Ln, q1=0.5 * (qg + qc), lat1=0.5 * (ag + ac), c1=0.5 * (cg + cc)); return s['mean_lat_shift'], s['lnBF_core_vs_uniform']
pt = one('point'); out = {'point': pt}
for mode in ('a', 'b', 'c'):
    r = np.array([one(mode) for _ in range(200)]); out[mode] = {'shift_sd': r[:, 0].std(), 'shift_95': np.quantile(r[:, 0], [0.025, 0.975]).tolist(), 'lnBF_sd': r[:, 1].std(), 'lnBF_95': np.quantile(r[:, 1], [0.025, 0.975]).tolist()}
    print(mode, {k: np.round(v, 3) for k, v in out[mode].items()}, flush=True)
b = np.array([one('point', rng.integers(0, K, K)) for _ in range(1000)])
out['seed_bootstrap'] = {'shift_sd': b[:, 0].std(), 'shift_95': np.quantile(b[:, 0], [0.025, 0.975]).tolist(), 'lnBF_sd': b[:, 1].std()}
print('point', np.round(pt, 3), 'boot', {k: np.round(v, 3) for k, v in out['seed_bootstrap'].items()})
json.dump(out, open('aus-noise.json', 'w'), indent=1, default=float)
