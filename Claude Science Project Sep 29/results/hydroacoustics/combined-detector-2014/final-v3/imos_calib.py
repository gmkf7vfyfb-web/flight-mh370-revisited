"""Step 1: IMOS null calibration of the combined detector (pre-registration v1.0, B4)."""
import sys, os, pickle, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
from multiprocessing import Pool
from scipy.stats import genpareto
import sigdet as SD, imosdet as ID
import ns_readers as RD

CACHE = '/Users/pete/Downloads/mh370-inputs/hydroacoustics/imos_250hz_cache'
LOGGERS = ['IMOS3250', 'IMOS3274', 'IMOS3376', 'IMOS3315', 'IMOS3275']
NULLSRC = {'IMOS3250': 'imos3250_background', 'IMOS3274': 'imos3274_background', 'IMOS3376': 'imos3376_background',
           'IMOS3315': 'imos3315_mh370_day', 'IMOS3275': 'imos3275_mh370_day'}
EXCL = (15 * 60.0, 120 * 60.0)        # 00:15-02:00 on 8 March excluded from own-station nulls
COMP = ['d0', 'd1', 's1', 'cimp', 'pers']
WT = SD.whale_templates(ID.F[ID.FBI])


def null_records(lg):
    z = np.load(f'{CACHE}/{NULLSRC[lg]}.npz', allow_pickle=True)
    X, n, t0 = z['x'], z['n'], z['t_start_s']
    ok = (n >= ID.NREC * 0.95) & (X[:, :int(0.95 * ID.NREC)].std(1) > 0) & ((X[:, :int(0.95 * ID.NREC)] == 0).mean(1) < 0.001)
    if 'mh370_day' in NULLSRC[lg]:
        ok &= ~((t0 + 307 > EXCL[0]) & (t0 < EXCL[1]))
    return X[ok], t0[ok]


def _gain(lg):
    fg, G = RD.imos_gain(lg); return ID.gain_shape(fg, G)


def _one(args):
    x, gs, tau = args
    x = x.astype(float); x -= x.mean()
    g = ID.record_stats(x, WT, gs, None, None, tau)
    return {k: v for k, v in g.items()}


class TailMap:
    """Empirical upper-tail probability with a generalised Pareto tail above the 90th percentile."""
    def __init__(self, v):
        v = np.sort(v[np.isfinite(v)]); self.v = v; m = int(0.1 * len(v)); self.u = v[-m - 1]
        self.c, _, self.s = genpareto.fit(v[-m:] - self.u + 1e-9, floc=0)

    def p(self, x):
        x = np.asarray(x, float); n = len(self.v); xx = np.where(np.isfinite(x), x, -np.inf)
        pe = (n - np.searchsorted(self.v, xx, side='left') + 1) / (n + 1)       # share of noise values >= x (ties counted)
        if os.environ.get('A6FLOOR'):            # sensitivity A6: empirical only, floor 1/(n+1)
            return np.clip(pe, 1.0 / (n + 1), 1)
        # Pareto tail only beyond the largest noise value (fix 6 Nov 2026: a saturating statistic such as persistence
        # sits at the sample maximum in 2-7 % of noise looks; the old rule gave those looks the extrapolated tail, ~1e-7).
        pt = 0.1 * genpareto.sf(xx - self.u, self.c, 0, self.s)
        beyond = xx > self.v[-1]
        pt = np.where(pt > 0, np.minimum(pt, 1.0 / (n + 1)), 1.0 / (n + 1))   # bounded tail past its endpoint: empirical floor
        return np.clip(np.where(beyond, pt, pe), 1e-15, 1)


def fisher(maps, g):
    F = 0
    for k in COMP:
        F = F - 2 * np.nan_to_num(np.log(maps[k].p(g[k])), nan=0.0)
    return F


if __name__ == '__main__':
    calib = {}
    for lg in LOGGERS:
        X, t0 = null_records(lg); gs = _gain(lg)
        taus = [ID.thin_lag(ID.envelope_db(X[i].astype(float))) for i in np.linspace(0, len(X) - 1, 60).astype(int)]
        tau = int(np.median(taus))
        with Pool(16) as p:
            R = p.map(_one, [(X[i], gs, tau) for i in range(len(X))], chunksize=4)
        G = {k: np.stack([r[k] for r in R]) for k in R[0]}
        Z = G['z'].reshape(-1, ID.K); Zf = Z[np.isfinite(Z).all(1)]
        mu = np.median(Zf, 0); sd = 1.4826 * np.median(np.abs(Zf - mu), 0)
        # correlation statistic needs per-record lag bank from the record's own whitener
        def cimp_rec(i):
            x = X[i].astype(float); x -= x.mean()
            Wb = ID.lag_bank(ID.ar_whitener(x), gs); return ID.corr_imp(G['z'][i], mu, sd, Wb)
        G['cimp'] = np.stack([cimp_rec(i) for i in range(len(X))])
        maps = {k: TailMap(G[k].ravel()) for k in COMP}
        Fpt = fisher(maps, {k: G[k] for k in COMP})
        maps['F'] = TailMap(Fpt.ravel())
        # window-max calibration: windows of n contiguous points inside records
        wmax = {}
        rng = np.random.default_rng(1)
        for nwin in range(1, len(ID.CENT) + 1):
            st = rng.integers(0, len(ID.CENT) - nwin + 1, size=len(X))
            wmax[nwin] = np.sort(np.array([np.nanmax(Fpt[i, s:s + nwin]) for i, s in enumerate(st)]))
        calib[lg] = dict(tau=tau, mu=mu, sd=sd, gshape=gs, maps=maps, wmax=wmax, n_records=len(X),
                         t0=t0, null=G, Fpt=Fpt)
        print(lg, 'records', len(X), 'tau', tau, 'lag1 mu', round(mu[0], 2), 'sd med', round(float(np.median(sd)), 2),
              'F_pt q50/q95/q99.9', np.round(np.quantile(Fpt, [0.5, 0.95, 0.999]), 2), flush=True)
    pickle.dump(calib, open('imos_calib.pkl', 'wb'))
