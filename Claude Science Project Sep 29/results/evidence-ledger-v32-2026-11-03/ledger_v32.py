"""Evidence ledger on composer views v3.2 (run J), 3 Nov 2026.  Usage: python ledger_v32.py OUTDIR [NB]

How much does each type of evidence narrow the 7th arc, alone and in every combination, and do the types agree?
Reuses the composer v3.2 machinery unchanged: compose_v3.py is executed up to its main loop (V32=1 DEXT=1, RULED unset), and
prepare(D, 'all', 'mix', 'head', with_u=True) gives the per-outcome base weights w0 (core), mu (uniform per NM along the arc) and the
factor arrays. Types: core (satellite data, flight models, end of flight, settling; inseparable in this sample), drift (finds only),
aus (no debris on populated Australian coasts, measured; labelled sensitivity), search (per-cell model V1 central, Ocean Infinity
included), ple (Pleiades objects; conditional). Hydroacoustics has zero weight by ruling (no column).
Ocean-model terms (drift, aus, ple) are multiplied INSIDE the ocean-model average: 0.5 * sum_m prod_k L_k|m (composer convention;
no double counting of the shared ocean model). aus alone = d|pop|m / d|off|m.
Primary measure: information along the arc, entropy on 10 NM bins of the impact arc position, against the uniform base restricted to
the arc where every module is computed (40.25-19.9 S). Views without core: bin mass = u * E[L | bin] over core outcomes (ratio
estimator, recomputed in every bootstrap draw). 2-D metrics (HPD areas, best-block mass) only for subsets that include core.
Attribution: Shapley values over all subsets of each set. Agreement: suspiciousness ln S = ln R - ln I with Bayesian model
dimensionality d (Handley and Lemos 2019), p = chi2.sf(d - 2 ln S, d), one type against the product of the others.
Uncertainty: seed bootstrap, NB draws, the composer's resampling groups (stratum, seed // 10000).
"""
import os, sys, json, math, pathlib, itertools, time
import numpy as np, pandas as pd
from scipy.stats import chi2
os.environ['V32'] = '1'; os.environ['DEXT'] = '1'; os.environ.pop('RULED', None)
HERE = pathlib.Path(__file__).resolve().parent
CV = HERE.parent / 'composer-views-v3-run-j' / 'compose_v3.py'
OUT = pathlib.Path(sys.argv[1]).resolve(); OUT.mkdir(parents=True, exist_ok=True)
NB = int(sys.argv[2]) if len(sys.argv) > 2 else 400
src = CV.read_text(); cut = src.index("RES = {'meta'")
g = {'__file__': str(CV), '__name__': 'compose_v3_lib'}
_argv = sys.argv; sys.argv = [str(CV), str(OUT / '_compose_unused'), '1']
exec(compile(src[:cut], str(CV), 'exec'), g); sys.argv = _argv
V, VL, T = g['V'], g['VL'], g['T']; prepare, summarise, kl, hist_cell = g['prepare'], g['summarise'], g['kl'], g['hist_cell']
U_ARC, SPAN = g['U_ARC'], g['SPAN']
NSB, SBNM, CELL = V.NSB, V.SBIN_NM, V.CELL_KM2
uvec = np.where(SPAN, U_ARC, 0.0); uvec = uvec / uvec.sum()
TY = ['core', 'drift', 'search', 'aus', 'ple']
NMN = {'core': 'satellite data and flight (core)', 'drift': 'debris drift (finds)', 'search': 'searched areas (no find)',
       'aus': 'no debris on populated Australian coasts', 'ple': 'Pleiades objects (if debris)'}
LAT = {'headline': ['core', 'drift', 'search'], 'with Australian non-finds': ['core', 'drift', 'search', 'aus'],
       'with Pleiades (conditional)': ['core', 'drift', 'search', 'ple']}
DKN = {'D0': '00:19 data held out', 'D1': '00:19 BTO only (R600)', 'D2': '00:19 BTO + raw BFO (R600)', 'D3': '00:19 BTO + both BFOs as recorded',
       'D4': '00:19 BTO + both BFOs, Holland transient bias added', 'D5': '00:19 BTO + R600 and R1200 BFOs, Holland transient bias added'}
LATLIM = (-40.25, -19.9)


def subset_w(sub, blocks, restrict=True):
    ws = []
    for b in blocks:
        F = b['F']; t = T[b['fs']]; i = b['idx']
        base = b['w0'] if 'core' in sub else b['mu']
        if restrict and 'core' in sub:
            base = np.where(b['mu'] > 0, base, 0.0)
        if any(k in sub for k in ('drift', 'aus', 'ple')):
            acc = 0.0
            for m in 'GC':
                if 'drift' in sub and 'aus' in sub: f = F[f'd|pop|{m}']
                elif 'drift' in sub: f = F[f'd|off|{m}']
                elif 'aus' in sub: f = F[f'd|pop|{m}'] / F[f'd|off|{m}']
                else: f = 1.0
                if 'ple' in sub: f = f * F[f'p|{m}']
                acc = acc + 0.5 * f
        else:
            acc = 1.0
        if 'search' in sub:
            acc = acc * t['P|V1_central'][i]
        ws.append(base * acc)
    return ws


def H2(m):
    p = m / m.sum(); q = p[p > 0]; return float(-(q * np.log2(q)).sum())
def hpd_len(m, lv=0.9):
    p = np.sort(m / m.sum())[::-1]; return float((np.searchsorted(np.cumsum(p), lv) + 1) * SBNM)
def KLb(m, mu_):
    p = m / m.sum(); q = mu_ / mu_.sum(); ok = p > 0; return float((p[ok] * np.log(p[ok] / q[ok])).sum())
def bmd_b(m, mu_):
    p = m / m.sum(); q = mu_ / mu_.sum(); ok = p > 0; x = np.log(p[ok] / q[ok]); mm = (p[ok] * x).sum(); return float(2 * (p[ok] * (x - mm) ** 2).sum())
def arc_mass(blocks, ws):
    return sum(np.bincount(b['sb'], w, NSB + 1)[:NSB] for b, w in zip(blocks, ws))
def units_M(blocks, NBt, seed=3112026):
    rng_ = np.random.default_rng(seed); keys = []
    for b in blocks:
        us, si = np.unique(T[b['fs']]['seed'][b['idx']], return_inverse=True); keys.append((us, si))
    units = sorted({(b['s'], int(k)) for b, (us, _) in zip(blocks, keys) for k in us}); uidx = {u: i for i, u in enumerate(units)}
    groups = {}
    for i, (s_, k) in enumerate(units):
        groups.setdefault((s_, k // 10000), []).append(i)
    MU = np.zeros((NBt, len(units)))
    for kk in range(NBt):
        for ix in groups.values():
            MU[kk, ix] = np.bincount(rng_.integers(0, len(ix), len(ix)), minlength=len(ix))
    return keys, [MU[:, [uidx[(b['s'], int(k))] for k in us]] for b, (us, _) in zip(blocks, keys)]
def boot_arc(blocks, ws, keys, Ms):
    tot = 0
    for b, w, (us, si), M in zip(blocks, ws, keys, Ms):
        A = np.bincount(si * (NSB + 1) + b['sb'], w, len(us) * (NSB + 1)).reshape(len(us), NSB + 1)[:, :NSB]; tot = tot + M @ A
    return tot


def ledger_arc(d, types=TY, NBt=NB):
    blocks, Wt, carry = prepare(d, 'all', 'mix', 'head', True)
    keys, Ms = units_M(blocks, NBt)
    w0 = [b['w0'] for b in blocks]; den = arc_mass(blocks, w0); Bden = boot_arc(blocks, w0, keys, Ms)
    lat_num = sum(np.bincount(b['sb'], b['w0'] * T[b['fs']]['ilat'][b['idx']], NSB + 1)[:NSB] for b in blocks)
    blat = np.where(den > 0, lat_num / np.where(den > 0, den, 1), np.nan)
    reach = (den > 0) & SPAN & np.isfinite(blat) & (blat >= LATLIM[0]) & (blat <= LATLIM[1]); ub = np.where(reach, uvec, 0.0)
    def masses(sub):
        wc = subset_w(sorted(set(sub) | {'core'}), blocks); num = arc_mass(blocks, wc); Bnum = boot_arc(blocks, wc, keys, Ms)
        if 'core' in sub:
            return np.where(reach, num, 0.0), np.where(reach, Bnum, 0.0)
        return ub * np.where(den > 0, num / np.where(den > 0, den, 1), 0.0), ub * np.where(Bden > 0, Bnum / np.where(Bden > 0, Bden, 1), 0.0)
    mU, BU = masses([]); out = {}
    for r in range(len(types) + 1):
        for sub in itertools.combinations(types, r):
            m, B = masses(sub)
            out[frozenset(sub)] = dict(m=m, H=H2(m), Hb=np.array([H2(x) for x in B]), Z=m.sum() / mU.sum(), Zb=B.sum(1) / BU.sum(1),
                                       KL=KLb(m, mU), KLb=np.array([KLb(x, y) for x, y in zip(B, BU)]), d=bmd_b(m, mU),
                                       db=np.array([bmd_b(x, y) for x, y in zip(B, BU)]), L90=hpd_len(m), L90b=np.array([hpd_len(x) for x in B]))
    for v in out.values():
        v['bits'] = out[frozenset()]['H'] - v['H']; v['bitsb'] = out[frozenset()]['Hb'] - v['Hb']
    return dict(blocks=blocks, L=out, blat=blat, reach=reach, unreach=float(uvec[SPAN & ~reach].sum()), core_outside=float(den[~reach].sum() / den.sum()))


def ledger_2d(d, types=TY):
    blocks, Wt, carry = prepare(d, 'all', 'mix', 'head', True); rows = {}
    for r in range(1, len(types) + 1):
        for sub in itertools.combinations(types, r):
            if 'core' not in sub:
                continue
            ws = subset_w(list(sub), blocks); s_, S1, MAP = summarise(blocks, ws)
            p = np.sort(MAP.ravel() / MAP.sum())[::-1]
            rows[frozenset(sub)] = dict(median_lat_seabed=s_['median'], north_of_33S_seabed=s_['north_of_33S'], hpd50_km2=s_['hpd50_km2'],
                                        hpd90_km2=s_['hpd90_km2'], p_best_15k_km2=float(p[:int(round(15000 / CELL))].sum()),
                                        p_best_50k_km2=float(p[:int(round(50000 / CELL))].sum()), p_on_searched_ground=s_['p_on_searched_ground'],
                                        kish_ess=float(np.concatenate(ws).sum() ** 2 / (np.concatenate(ws) ** 2).sum()))
    return rows


def shapley(L, types):
    K = len(types); phi = {}
    for k in types:
        o = [x for x in types if x != k]; t = 0.0; tb = 0.0
        for r in range(K):
            for sub in itertools.combinations(o, r):
                w = math.factorial(r) * math.factorial(K - r - 1) / math.factorial(K); S_ = frozenset(sub)
                t += w * (L[S_ | {k}]['bits'] - L[S_]['bits']); tb = tb + w * (L[S_ | {k}]['bitsb'] - L[S_]['bitsb'])
        phi[k] = (t, np.percentile(tb, [2.5, 97.5]))
    return phi


def tension(L, A, B):
    A, B = frozenset(A), frozenset(B); a, b, ab = L[A], L[B], L[A | B]
    lnR = np.log(ab['Z']) - np.log(a['Z']) - np.log(b['Z']); lnS = lnR - (a['KL'] + b['KL'] - ab['KL']); dd = a['d'] + b['d'] - ab['d']
    lnSb = np.log(ab['Zb']) - np.log(a['Zb']) - np.log(b['Zb']) - (a['KLb'] + b['KLb'] - ab['KLb']); ddb = a['db'] + b['db'] - ab['db']
    p = chi2.sf(max(dd - 2 * lnS, 0), max(dd, 1e-3)); pb = np.array([chi2.sf(max(x - 2 * y, 0), max(x, 1e-3)) for x, y in zip(ddb, lnSb)])
    return dict(lnR=float(lnR), lnS=float(lnS), d=float(dd), p=float(p), lnS_q=np.percentile(lnSb, [2.5, 97.5]), p_q=np.percentile(pb, [2.5, 97.5]),
                sigma=float(np.sqrt(chi2.isf(p, 1))) if p > 0 else float('inf'))


if __name__ == '__main__':
    t0 = time.time(); rows, attr, ten, syn, arcs = [], [], [], [], {}
    for d in DKN:
        R = ledger_arc(d); R2 = ledger_2d(d); L = R['L']
        arcs[f'{d}|lat'] = R['blat']; arcs[f'{d}|reach'] = R['reach']
        for k, v in L.items():
            nm = ' + '.join(sorted(k, key=TY.index)) or '(uniform along the arc)'; arcs[f'{d}|{nm}'] = v['m']
            rows.append(dict(option=d, treatment=DKN[d], subset=nm, n_types=len(k), includes_pleiades='ple' in k, includes_australia='aus' in k,
                             bits_along_arc=v['bits'], bits_q025=np.percentile(v['bitsb'], 2.5), bits_q975=np.percentile(v['bitsb'], 97.5),
                             KL_bits_along_arc=v['KL'] / np.log(2), arc90_nm=v['L90'], arc90_q025=np.percentile(v['L90b'], 2.5),
                             arc90_q975=np.percentile(v['L90b'], 97.5), lnZ_vs_uniform=float(np.log(v['Z'])),
                             **R2.get(k, {}), uniform_span_excluded=R['unreach'], core_mass_outside_domain=R['core_outside']))
        for nm, tys in LAT.items():
            for k_, (v_, q_) in shapley(L, tys).items():
                attr.append(dict(option=d, lattice=nm, evidence=NMN[k_], shapley_bits=v_, q025=q_[0], q975=q_[1], total_bits=L[frozenset(tys)]['bits']))
            for k_ in tys:
                t = tension(L, [k_], [x for x in tys if x != k_])
                ten.append(dict(option=d, lattice=nm, test=f'{NMN[k_]} vs the rest', lnR=t['lnR'], lnS=t['lnS'], lnS_q025=t['lnS_q'][0],
                                lnS_q975=t['lnS_q'][1], d_bmd=t['d'], p=t['p'], p_q025=t['p_q'][0], p_q975=t['p_q'][1], sigma=t['sigma']))
        for a, b in itertools.combinations(TY, 2):
            t = tension(L, [a], [b])
            syn.append(dict(option=d, a=NMN[a], b=NMN[b], synergy_bits=L[frozenset([a, b])]['bits'] - L[frozenset([a])]['bits'] - L[frozenset([b])]['bits'],
                            lnS=t['lnS'], d_bmd=t['d'], p_if_d_ge_0p5=t['p'] if t['d'] >= 0.5 else np.nan))
        print(d, 'done %.0fs' % (time.time() - t0), flush=True)
    pd.DataFrame(rows).to_csv(OUT / 'ledger-subsets-v32.csv', index=False)
    pd.DataFrame(attr).to_csv(OUT / 'ledger-shapley-v32.csv', index=False)
    pd.DataFrame(ten).to_csv(OUT / 'ledger-tension-v32.csv', index=False)
    pd.DataFrame(syn).to_csv(OUT / 'ledger-pairs-v32.csv', index=False)
    np.savez_compressed(OUT / 'ledger-arc-masses-v32.npz', **arcs)
    json.dump({'NB': NB, 'lat_limits': LATLIM, 'compose_v3': str(CV.relative_to(HERE.parents[1])), 'env': {'V32': '1', 'DEXT': '1'}},
              open(OUT / 'ledger-meta-v32.json', 'w'), indent=1)
