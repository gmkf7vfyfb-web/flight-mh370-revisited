"""Aggregate the per-seed FLIGHT-leg reductions (run_flight_leg.py) into Q1 / Q2 tables and pooled histograms.
Pools: 'run J' (four strata mixed by core P(family), seeds pooled by evidence, as option_table_0019.main) and
'arm V2 joined at 00:11' (waypoints only, seeds 1-21, equal weight per seed, as joined_v2_summary)."""
import numpy as np
from scipy.special import logsumexp

LAM_RATE = 18.0 / (1260.0 * 140.0)     # Kadri Table 1: 18 transients in 21 min (00:36-00:57), bearings 200-340 deg -> per s per deg
LAM_ONE = 1.0 / (1260.0 * 140.0)       # one chance arrival uniform over the same window (sensitivity: 18x less conservative)
P_C1 = 0.75                            # q = 1/3 -> p = 1/(1+q)


def L(vals):
    v = np.asarray([x for x in vals if np.isfinite(x)], float)
    return float(logsumexp(v)) if len(v) else -np.inf


def pool_of(r):
    return 'joined' if r['stratum'] == 'joined-v2' else 'main'


def q1_table(seeds, pool, keys, regions):
    S = [r for r in seeds if pool_of(r) == pool]; out = []
    for k in keys:
        if k not in S[0]['prior']: continue
        tot = L(r['prior'][k]['all']['l1'] for r in S)
        famtot = [L(r['prior'][k]['all']['fam1'][j] for r in S) for j in range(3)]
        for rn in regions:
            l1 = L(r['prior'][k][rn]['l1'] for r in S); l2 = L(r['prior'][k][rn]['l2'] for r in S); p2 = L(r['prior'][k][rn]['par2'] for r in S)
            f1 = [L(r['prior'][k][rn]['fam1'][j] for r in S) for j in range(3)]; f2 = [L(r['prior'][k][rn]['fam2'][j] for r in S) for j in range(3)]
            row = dict(pool=pool, key=k, region=rn, share=float(np.exp(l1 - tot)) if np.isfinite(l1) else 0.0,
                       ess=float(np.exp(2 * l1 - l2)) if np.isfinite(l2) else 0.0, eff_parents=float(np.exp(2 * l1 - p2)) if np.isfinite(p2) else 0.0,
                       parents_positive=int(sum(r['prior'][k][rn]['npar'] for r in S)),
                       rows_geometric=int(sum(r['geom_rows'][rn] for r in S)), parents_geometric=int(sum(r['geom_parents'][rn] for r in S)))
            for j, n in enumerate(('A1', 'A2', 'B')):
                row[f'{n}_share_in_region'] = float(np.exp(f1[j] - l1)) if np.isfinite(f1[j]) and np.isfinite(l1) else 0.0
                row[f'{n}_ess_in_region'] = float(np.exp(2 * f1[j] - f2[j])) if np.isfinite(f2[j]) else 0.0
                row[f'P_region_given_{n}'] = float(np.exp(f1[j] - famtot[j])) if np.isfinite(f1[j]) and np.isfinite(famtot[j]) else 0.0
            # per log-on cause (total cells only): share of the region's mass from fuel exhaustion (C1)
            if ' total ' in k:
                kc1 = k.split(' ')[0] + 'xC1'
                if kc1 in S[0]['prior']:
                    lc1 = L(r['prior'][kc1][rn]['l1'] for r in S)
                    row['C1_share_in_region'] = float(np.exp(np.log(P_C1) + lc1 - l1)) if np.isfinite(lc1) and np.isfinite(l1) else 0.0
                    lc1a = L(r['prior'][kc1]['all']['l1'] for r in S)
                    row['C1_share_overall'] = float(np.exp(np.log(P_C1) + lc1a - tot))
            # seed-to-seed spread of the share (waypoints / joined seeds only, conditional per seed)
            sh = [np.exp(r['prior'][k][rn]['l1'] - r['prior'][k]['all']['l1']) if np.isfinite(r['prior'][k][rn]['l1']) else 0.0
                  for r in S if r['stratum'] in ('run-j-waypoints', 'joined-v2')]
            row['seed_share_mean'] = float(np.mean(sh)); row['seed_share_se'] = float(np.std(sh, ddof=1) / np.sqrt(len(sh))) if len(sh) > 1 else float('nan')
            row['n_seeds_spread'] = len(sh)
            out.append(row)
    return out


def q1_by_stratum(seeds, keys, regions):
    out = []
    for st in ('run-j-waypoints', 'run-j-free', 'run-j-repro-radar', 'run-j-descent-climb'):
        S = [r for r in seeds if r['stratum'] == st]
        if not S: continue
        for k in keys:
            tot = L(r['prior'][k]['all']['l1'] for r in S)
            for rn in regions:
                l1 = L(r['prior'][k][rn]['l1'] for r in S); l2 = L(r['prior'][k][rn]['l2'] for r in S)
                out.append(dict(stratum=st, key=k, region=rn, share_within_stratum=float(np.exp(l1 - tot)) if np.isfinite(l1) else 0.0,
                                ess=float(np.exp(2 * l1 - l2)) if np.isfinite(l2) else 0.0, n_seeds=len(S)))
    return out


def q2_table(seeds, pool, keys, variants):
    S = [r for r in seeds if pool_of(r) == pool]; out = []
    for k in keys:
        if k not in S[0]['acoustic']: continue
        den = L(r['prior'][k]['all']['l1'] for r in S)
        for vn in variants:
            A = [r['acoustic'][k][vn] for r in S]
            n1 = L(a['all']['l1'] for a in A); n2 = L(a['all']['l2'] for a in A); p2 = L(a['all']['par2'] for a in A)
            row = dict(pool=pool, key=k, variant=vn, branch=vn[0], s_b_deg=float(vn[1:]), ln_mean_L=n1 - den,
                       ln_B_rate=n1 - den - np.log(LAM_RATE), ln_B_single=n1 - den - np.log(LAM_ONE),
                       ess_conditional=float(np.exp(2 * n1 - n2)) if np.isfinite(n2) else 0.0,
                       eff_parents_conditional=float(np.exp(2 * n1 - p2)) if np.isfinite(p2) else 0.0,
                       parents_positive=int(sum(a['all']['npar'] for a in A)))
            for rn in ('strip', 'X200', 'H200'):
                x = L(a[rn]['l1'] for a in A); row[f'cond_share_{rn}'] = float(np.exp(x - n1)) if np.isfinite(x) else 0.0
            for j, n in enumerate(('A1', 'A2', 'B')):
                x = L(a['all']['fam1'][j] for a in A); x2 = L(a['all']['fam2'][j] for a in A)
                row[f'cond_{n}_share'] = float(np.exp(x - n1)) if np.isfinite(x) else 0.0
                row[f'cond_{n}_ess'] = float(np.exp(2 * x - x2)) if np.isfinite(x2) else 0.0
                fd = L(r['prior'][k]['all']['fam1'][j] for r in S)
                row[f'ln_B_rate_{n}'] = (x - fd - np.log(LAM_RATE)) if np.isfinite(x) else -np.inf   # B within family (family prior fixed)
            if ' total ' in k:
                kc1 = k.split(' ')[0] + 'xC1'
                if kc1 in S[0]['acoustic']:
                    x = L(r['acoustic'][kc1][vn]['all']['l1'] for r in S)
                    row['cond_C1_share'] = float(np.exp(np.log(P_C1) + x - n1)) if np.isfinite(x) else 0.0
            # per-seed ln B (waypoints / joined seeds; conditional per seed) for seed agreement
            sb = [r['acoustic'][k][vn]['all']['l1'] - r['prior'][k]['all']['l1'] - np.log(LAM_RATE) for r in S
                  if r['stratum'] in ('run-j-waypoints', 'joined-v2') and np.isfinite(r['prior'][k]['all']['l1'])]
            sb = np.asarray(sb); fin = np.isfinite(sb)
            row['seed_lnB_median'] = float(np.median(sb[fin])) if fin.any() else -np.inf
            row['seed_lnB_min'] = float(sb[fin].min()) if fin.any() else -np.inf; row['seed_lnB_max'] = float(sb[fin].max()) if fin.any() else -np.inf
            # pooled-B standard error from seed spread of exp(lnB): ln of mean +/- se
            e = np.exp(sb[fin] - sb[fin].max()) if fin.any() else np.array([0.0])
            row['seed_B_rel_se'] = float(np.std(e, ddof=1) / np.sqrt(len(e)) / e.mean()) if len(e) > 1 and e.mean() > 0 else float('nan')
            row['n_seeds_spread'] = int(fin.sum())
            out.append(row)
    return out


def pooled_hist(seeds, pool, key, reg, which):
    S = [r for r in seeds if pool_of(r) == pool]; acc = None; ref = -np.inf
    for r in S:
        s, h = r['hist'][key][reg][which]
        if not np.isfinite(s): continue
        if acc is None: acc, ref = h.astype(float), s; continue
        m = max(ref, s); acc = acc * np.exp(ref - m) + h * np.exp(s - m); ref = m
    if acc is None: return None, -np.inf
    return acc, ref
