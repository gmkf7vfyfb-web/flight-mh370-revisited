"""SBC smoke test, part A, matched to the real curve: choose the toy likelihood width s so that (a) the posterior standard deviation of the drift-alone
posterior at the observed centre (30.3 S) equals that of the real curve (3.76 deg) and (b) the median effective dimension d equals the real one (0.864).
Then report the fraction of null datasets with p <= 0.1091 (the real nominal p) and ln S <= -0.705."""
import sys; sys.path.insert(0, 'sbc')
import numpy as np, pandas as pd, tension_lib as T
from scipy import optimize
exec(open('sbc/sbc_toy.py').read().split('rows = []')[0].split('post_alone = None')[0].replace("rng = np.random.default_rng(2026)", "rng = np.random.default_rng(31)"))
def post_sd(s, y=-30.3):
    L = np.exp(-0.5 * ((la - y) / s) ** 2); p = pi * L; p /= p.sum(); m = (p * la).sum(); return float(np.sqrt((p * (la - m) ** 2).sum()))
s_sd = optimize.brentq(lambda s: post_sd(s) - 3.76, 2, 20)
def median_d(s, n=4000):
    x = draw_truth(n); y = x + s * rng.standard_normal(n); out = []
    for k in range(n):
        lL = -0.5 * ((la - y[k]) / s) ** 2; out.append(T.tension(np.exp(lL - lL.max()))['d'])
    return float(np.median(out))
s_d = optimize.brentq(lambda s: median_d(s) - 0.864, 3, 9, xtol=0.05)
print('s matching posterior sd 3.76:', round(s_sd, 2), '; s matching median d 0.864:', round(s_d, 2))
rows = []
for name, s in (('width matched to posterior sd', s_sd), ('width matched to effective dimension', s_d)):
    n = 100000; x = draw_truth(n); y = x + s * rng.standard_normal(n); res = []
    for k in range(n):
        lL = -0.5 * ((la - y[k]) / s) ** 2; r = T.tension(np.exp(lL - lL.max())); res.append((r['lnS'], r['d'], r['p']))
    a = np.array(res); ok = np.isfinite(a[:, 2]); p = a[ok, 2]
    rows.append(dict(match=name, s_deg=round(s, 2), n=int(ok.sum()), median_d=round(float(np.median(a[ok, 1])), 3), P_p_le_0p05=float((p <= .05).mean()), P_p_le_0p10=float((p <= .10).mean()),
                     P_p_le_0p1091=float((p <= 0.1091).mean()), P_lnS_le_m0p705=float((a[ok, 0] <= -0.7053).mean())))
df = pd.DataFrame(rows); print(df.round(3).to_string()); df.to_csv('sbc/sbc_toy_matched_real_curve.csv', index=False)
