import sys, json; sys.path.insert(0, 'sbc')
import numpy as np, pandas as pd, tension_lib as T
from scipy import stats
exec(open('sbc/sbc_toy.py').read().split('rows = []')[0].split('post_alone = None')[0].replace("rng = np.random.default_rng(2026)", "rng = np.random.default_rng(77)"))
# width of the real drift-alone curve
d0 = pd.read_csv('res-smooth/smoothed-drift-alone-curves.csv'); pa = d0['Two ocean models'].values; pa = pa / pa.sum()
m = (pa * T.la).sum(); sd_real = float(np.sqrt((pa * (T.la - m) ** 2).sum())); print('real drift-alone posterior sd deg', round(sd_real, 2), 'mean', round(m, 2))
rows = []
for s in (4.5, 5.5, 6.5, 8.0):
    n = 50000; x = draw_truth(n); y = x + s * rng.standard_normal(n); res = []
    for k in range(n):
        lL = -0.5 * ((la - y[k]) / s) ** 2; r = T.tension(np.exp(lL - lL.max())); res.append((r['lnS'], r['d'], r['p']))
    a = np.array(res); ok = np.isfinite(a[:, 2]); p = a[ok, 2]
    # posterior sd of the toy drift-alone curve, typical
    rows.append(dict(s_deg=s, n=int(ok.sum()), median_d=float(np.median(a[ok, 1])), P_p_le_0p05=float((p <= .05).mean()), P_p_le_0p10=float((p <= .10).mean()), P_p_le_0p1091=float((p <= 0.1091).mean()), P_lnS_le_m0p705=float((a[ok, 0] <= -0.7053).mean()), P_p_eq_1=float((p >= 1).mean())))
df = pd.DataFrame(rows); print(df.round(3).to_string()); df.to_csv('sbc/sbc_toy_matched_width.csv', index=False)
