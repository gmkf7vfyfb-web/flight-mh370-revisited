"""Background tail probability per 2-min look: empirical below the 90th percentile, generalised Pareto above."""
import numpy as np, pandas as pd
from scipy.stats import genpareto
STATS = ['L_d0', 'L_d1', 'S_d1', 'C_any', 'C_imp', 'E_pers']
NAMES = {'L_d0': 'Band energy', 'L_d1': 'Loose impact spectral templates', 'S_d1': 'Spectral shape change',
         'C_any': 'Successive-sample correlation, no template', 'C_imp': 'Successive-sample correlation, impact pattern',
         'E_pers': 'Envelope persistence (sign count)', 'COMB': 'Combined (band energy + shape + correlation + persistence)'}
COMB = ['L_d0', 'S_d1', 'C_imp', 'E_pers']


class PMap:
    def __init__(self, B, kind='rnd'):
        self.f = {}
        for (st), g in B[B.kind == kind].groupby('st'):
            for s in STATS:
                v = np.sort(g[s].values[np.isfinite(g[s].values)]); m = int(0.1 * len(v)); u = v[-m - 1]; ex = v[-m:] - u + 1e-9
                c, loc, sc = genpareto.fit(ex, floc=0)
                self.f[(st, s)] = (v, u, c, sc)
            # combined statistic calibration on the same background
            F = self.fisher(st, {s: g[s].values for s in COMB})
            self.f[(st, 'COMB')] = np.sort(F)

    def p(self, st, s, x):
        v, u, c, sc = self.f[(st, s)]
        x = np.asarray(x, float); n = len(v); bad = ~np.isfinite(x); x = np.where(bad, -np.inf, x)
        pe = (n - np.searchsorted(v, x, side='left') + 1) / (n + 1)
        pt = 0.1 * genpareto.sf(x - u, c, 0, sc)
        return np.clip(np.where(x > u, pt, pe), 1e-15, 1)

    def fisher(self, st, d):
        return -2 * sum(np.nan_to_num(np.log(self.p(st, s, d[s])), nan=0.0) for s in COMB)

    def thr(self, st, s, alpha):
        """Threshold with per-look false-alarm probability alpha (tail model beyond the data)."""
        if s == 'COMB':
            F = self.f[(st, 'COMB')]; n = len(F)
            if alpha * n >= 3:
                return np.quantile(F, 1 - alpha)
            # extrapolate the Fisher tail with a GPD over its top 10 %
            m = int(0.1 * n); u = F[-m - 1]; ex = F[-m:] - u + 1e-9; c, _, sc = genpareto.fit(ex, floc=0)
            return u + genpareto.isf(alpha / 0.1, c, 0, sc)
        v, u, c, sc = self.f[(st, s)]
        if alpha * len(v) >= 3 and alpha >= 0.01:
            return np.quantile(v, 1 - alpha)
        return u + genpareto.isf(alpha / 0.1, c, 0, sc)
