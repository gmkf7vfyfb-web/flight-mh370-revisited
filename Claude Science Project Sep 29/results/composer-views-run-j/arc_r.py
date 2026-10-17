"""Composer views on run J, pass A pooling: r_b = u_b / q_b per 10 NM arc bin and per 00:19 option (and variant), q_b = pooled core
proposal mass of the 00:19:29 crossing in bin b (strata by core P(family), seeds by evidence, as compose_views), u uniform per NM
over the arc span the run J crossings reach (bins with >= 10 crossings, pooled; contiguous from first to last). Also pools the
end-of-flight displacement (impact minus crossing) under core D0. Usage: python arc_r.py OUT.npz"""
import sys, glob, json, pathlib, re, numpy as np
from scipy.special import logsumexp
HERE = pathlib.Path(__file__).resolve().parent; sys.path.insert(0, str(HERE)); import views_common as V
X = pathlib.Path('/Users/pete/Downloads/mh370-exchange'); A = X / 'composer/run-j-views/work/arcq'
STRATA = ['run-j-waypoints', 'run-j-free', 'run-j-repro-radar', 'run-j-descent-climb']
lnZc = {s: json.load(open(X / f'core/run-j/{s}/summary.json'))['cases'][0]['log_evidence'] for s in STRATA}
lse = logsumexp(list(lnZc.values())); PF = {s: float(np.exp(v - lse)) for s, v in lnZc.items()}
F = {(s, st): sorted(glob.glob(str(A / f'{s}_{st}_*.npz'))) for s in ('prod', 'both') for st in STRATA}
raw = sum(np.load(f)['raw_sb'] for st in STRATA for f in F[('prod', st)])
have = raw[:V.NSB] >= 10; idx = np.where(have)[0]; span = np.zeros(V.NSB, bool); span[idx.min():idx.max() + 1] = True
u = np.where(span, 1.0, 0.0); u /= u.sum()
out = {'span': span, 'raw': raw, 'u': u}; info = {'span_nm': [float(idx.min() * V.SBIN_NM), float((idx.max() + 1) * V.SBIN_NM)]}
info['span_ends_latlon'] = [list(map(float, V.arc_point(info['span_nm'][0]))), list(map(float, V.arc_point(info['span_nm'][1])))]
info['bins_in_span_with_lt10'] = int((span & ~have).sum())
disp = 0.0
for variant in ('head', 'prodonly'):
    for d in [f'D{i}' for i in range(6)]:
        if variant == 'prodonly' and d not in ('D3', 'D4'):
            continue
        cs = []
        for st in STRATA:
            fl = F[('both' if (variant == 'head' and d in ('D3', 'D4') and st == 'run-j-waypoints') else 'prod', st)]
            for f in fl:
                z = np.load(f)
                if int(z[f'{d}|valid']):
                    cs.append((np.log(PF[st] / len(fl)) + float(z[f'{d}|s']), z[f'{d}|q'], st, f))
        cref = max(c for c, *_ in cs); q = sum(np.exp(c - cref) * qq for c, qq, *_ in cs)
        info[f'{variant}|{d}|share_burst_nan_or_off_arc'] = float(q[V.NSB] / q.sum()); q = q[:V.NSB] / q[:V.NSB].sum()
        reach = span & (q > 1e-280); r = np.where(reach, u / np.where(reach, q, 1), 0.0)
        info[f'{variant}|{d}|uniform_share_unreachable'] = float(u[span & ~reach].sum())
        out[f'{variant}|{d}|q'] = q; out[f'{variant}|{d}|r'] = r
        if variant == 'head' and d == 'D0':
            for c, qq, st, f in cs:
                z = np.load(f); disp = disp + np.exp(c - cref) * z['disp']
            info['disp_out_max'] = max(float(np.load(f)['disp_out']) for *_, f in cs)
out['disp'] = disp / disp.sum(); out['info'] = json.dumps(info)
np.savez(sys.argv[1], **out); print(json.dumps(info, indent=0)[:1500])
