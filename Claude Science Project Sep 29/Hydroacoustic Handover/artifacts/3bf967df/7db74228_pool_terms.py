"""Pool reduce_kh.py per-seed files and surface_drift.py cell likelihoods into the searched-areas likelihood terms.

Seeds pooled by evidence within a stratum (ln(P_s/K_s) + seed scale, as option_table_0019); strata mixed by core run J P(family)
(end-of-flight/run-j/summary/family-shares-run-j.json p_core). Locality vs complement (= run J outside the bearing strip).
Usage: python pool_terms.py PER_SEED_DIR DRIFT_DIR OUT.csv
"""
import sys, glob, re, json
import numpy as np, pandas as pd
PF = json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/family-shares-run-j.json'))['p_core']
STR = ['run-j-waypoints', 'run-j-free', 'run-j-repro-radar', 'run-j-descent-climb']
DK = [f'D{d}' for d in range(6)]; AK = ['Tcore', 'Twide', 'Ccore', 'Cwide']; LSV = ['s00', 's05', 's25', 's50', 'x05']
GNY, GNX = 152, 136


def main(sd, dd, outp):
    Z = {s: [dict(np.load(f)) for f in sorted(glob.glob(f'{sd}/{s}_*.npz'), key=lambda f: int(re.findall(r'_(\d+)\.npz', f)[0]))] for s in STR}
    def seeds(d, extra=None):
        L = []
        for s in STR:
            for z in Z[s]:
                if int(z[f'{d}|valid']):
                    c = np.log(PF[s] / len(Z[s])) + float(z[f'{d}|s']) + (float(z[f'{d}|{extra}|sa']) if extra else 0.0)
                    L.append((z, c))
        cm = max(c for _, c in L); return [(z, np.exp(c - cm)) for z, c in L]
    Lg = {}
    for a in ('0.005', '0.012', '0.025'):
        for pk in ('csiro', 'field', 'item'):
            g = np.full(GNY * GNX + 1, np.nan)
            for part in ('sparse', 'dense'):
                q = np.load(f'{dd}/drift_{part}_{a}.npz'); g[q['cells']] = q[f'L|{pk}']
            Lg[(a, pk)] = g
    rows = []
    for d in DK:
        S = seeds(d); P = lambda k: sum(w * z[k] for z, w in S)
        M = P(f'{d}|M'); Mm = P(f'{d}|strip|M')
        comp = {v: (P(f'{d}|all|LS|{v}') - P(f'{d}|strip|LS|{v}')) / (M - Mm) for v in LSV}
        hall = P(f'{d}|hist|all'); hst = P(f'{d}|hist|strip')
        for key in ['strip'] + AK:
            if key == 'strip':
                ls = {v: P(f'{d}|strip|LS|{v}') / Mm for v in LSV}; h = hst
            else:
                SA = seeds(d, key); PA = lambda k: sum(w * z[k] for z, w in SA); W = PA(f'{d}|{key}|W')
                ls = {v: PA(f'{d}|{key}|LS|{v}') / W for v in LSV}; h = PA(f'{d}|hist|{key}')
            row = {'option': d, 'locality': key}
            for v in LSV:
                row[f'seabed lnB {v}'] = np.log(ls[v] / comp[v])
            for (a, pk), g in Lg.items():
                ok = np.isfinite(g)
                e = (h[ok] * g[ok]).sum() / h[ok].sum(); eall = (hall[ok] * g[ok]).sum() / hall[ok].sum(); est = (hst[ok] * g[ok]).sum() / hst[ok].sum()
                m = Mm / M; ec = (eall - m * est) / (1 - m)
                row[f'surface lnB a{a} {pk}'] = np.log(e / ec)
            rows.append(row)
    pd.DataFrame(rows).to_csv(outp, index=False); print(pd.DataFrame(rows).round(3).iloc[:, :8].to_string())


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
