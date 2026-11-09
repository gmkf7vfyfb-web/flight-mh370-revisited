"""SBC smoke test, part A (statistic only; NOT evidence about the drift module). Truth x ~ ruled core posterior; synthetic drift data from a toy
model with a known likelihood; the module's tension statistic (tension_lib.tension, reproduces p = 0.109 on the headline curve) is applied; we ask
whether the nominal chi-square p-value is uniform under the null (core correct, drift model correct)."""
import sys, json, time; sys.path.insert(0, 'sbc')
import numpy as np, tension_lib as T
from scipy import stats
rng = np.random.default_rng(2026); la, pi, pc = T.la, T.pi, T.pc
cdf = np.cumsum(pc)
def draw_truth(n): return la[np.minimum(np.searchsorted(cdf, rng.random(n)), len(la) - 1)] + rng.uniform(-0.05, 0.05, n)
def gp_noise(n, ell, sd):
    D = np.abs(la[:, None] - la[None, :]); K = (1 + np.sqrt(3) * D / ell) * np.exp(-np.sqrt(3) * D / ell) * sd ** 2 + 1e-9 * np.eye(len(la))
    Lc = np.linalg.cholesky(K); return (Lc @ rng.standard_normal((len(la), n))).T
post_alone = None
def run(name, s, n, noise=None, flat_extra=0.0):
    x = draw_truth(n); y = x + s * rng.standard_normal(n)
    nz = gp_noise(n, *noise) if noise else np.zeros((n, len(la)))
    res = []
    t0 = time.time()
    for k in range(n):
        lL = -0.5 * ((la - y[k]) / s) ** 2 + nz[k]
        r = T.tension(np.exp(lL - lL.max())); res.append((r['lnS'], r['d'], r['p']))
    a = np.array(res); ok = np.isfinite(a[:, 2]); p = a[ok, 2]
    out = dict(case=name, s_deg=s, n=n, noise=noise, frac_d_undefined=float(1 - ok.mean()), seconds=round(time.time() - t0, 1),
               ks_stat=float(stats.kstest(p, 'uniform').statistic), ks_p=float(stats.kstest(p, 'uniform').pvalue),
               **{f'P(p<={al})': float((p <= al).mean()) for al in (0.01, 0.05, 0.1, 0.2, 0.5)},
               frac_lnS_below_minus_0p705=float((a[ok, 0] <= -0.7053).mean()), median_d=float(np.median(a[ok, 1])))
    return out
rows = []
for s in (2.0, 3.0, 4.5, 6.0):
    rows.append(run('A: Gaussian likelihood', s, 20000))
for s in (3.0, 4.5):
    rows.append(run('B: Gaussian + smooth random departures (sd 0.4 ln, length 1.5 deg)', s, 20000, noise=(1.5, 0.4)))
json.dump(rows, open('sbc/sbc_toy_results.json', 'w'), indent=1)
import pandas as pd; df = pd.DataFrame(rows); pd.set_option('display.width', 250); pd.set_option('display.max_columns', 30); print(df.drop(columns=['noise']).round(3).to_string())
