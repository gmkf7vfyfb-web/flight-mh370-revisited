"""Network detection SNR for two independent IMOS sites at equal SNR (review 3e).
Per-logger known-time injection p values are combined by Fisher's method and compared with the global 5 % level
from the time-shift null. Dilution case: one more covering station that carries only noise (p uniform), k = 3."""
import os, sys, numpy as np, pandas as pd
from scipy.stats import chi2
INJ = os.environ.get('INJ', 'imos_injections_physics_v2.csv'); THR = float(os.environ.get('THR', '3.39'))
D = pd.read_csv(INJ)
PAIRS = [('IMOS3376', 'IMOS3274'), ('IMOS3376', 'IMOS3250'), ('IMOS3274', 'IMOS3250'), ('IMOS3315', 'IMOS3274')]
rng = np.random.default_rng(0); out = []
for fam in sorted(D.family.unique()):
    for a, b in PAIRS:
        for kx in (0, 1):
            row = dict(family=fam, pair=f'{a[4:]}+{b[4:]}', extra_noise_stations=kx); pdv = []
            for s in sorted(D.snr.unique()):
                pa = D[(D.station == a) & (D.family == fam) & (D.snr == s)].p_combined.values
                pb = D[(D.station == b) & (D.family == fam) & (D.snr == s)].p_combined.values
                A = rng.choice(pa, 4000); B = rng.choice(pb, 4000); X = -2 * (np.log(A) + np.log(B)); k = 2
                if kx:
                    X = X - 2 * np.log(rng.uniform(size=4000)); k = 3
                pdv.append((s, float((-np.log10(chi2.sf(X, 2 * k)) >= THR).mean())))
            x = np.array([p[0] for p in pdv]); y = np.array([p[1] for p in pdv]); i = np.where(y >= 0.5)[0]
            row['SNR50'] = np.nan if len(i) == 0 else (x[0] if i[0] == 0 else x[i[0] - 1] + (0.5 - y[i[0] - 1]) * (x[i[0]] - x[i[0] - 1]) / (y[i[0]] - y[i[0] - 1]))
            row['PD_at_0dB'] = dict(pdv)[0.0]; row['PD_at_10dB'] = dict(pdv)[10.0]; out.append(row)
O = pd.DataFrame(out); O.to_csv(os.environ.get('OUTCSV', 'network_detection_snr_v2.csv'), index=False)
print(O.pivot_table(index=['pair', 'extra_noise_stations'], columns='family', values='SNR50').round(1).to_string())
