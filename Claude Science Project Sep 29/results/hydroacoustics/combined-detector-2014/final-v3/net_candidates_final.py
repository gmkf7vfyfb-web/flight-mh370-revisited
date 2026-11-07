import sys, os, numpy as np, pandas as pd
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'ns'))
import network14 as N
rows = []
for run, tag in (('run14v5_final', 'primary'), ('run14v5_final', 'wide_speed')):
    D = pd.read_csv(f'{run}/all_hypotheses_{tag}.csv.gz'); ng = np.load(f'{run}/null_max_k2_{tag}.npy')
    D = D[D.k_sites >= 2].sort_values('minus_log10_p', ascending=False)
    kept = []
    for r in D.itertuples():
        if any(abs(r.arc_lat - k.arc_lat) <= 2 and abs(r.t_imp - k.t_imp) <= 180 for k in kept): continue
        kept.append(r)
        if len(kept) == 10: break
    for i, r in enumerate(kept):
        per = {st: getattr(r, 'p_' + st) for st in N.STATIONS}
        rows.append(dict(speed_model=tag.replace('_', ' '), rank=i + 1, family=r.family, arc_lat_S=-r.arc_lat, offset_nm=r.offset_nm, impact_utc=N.hms(r.t_imp),
                         sites=r.k_sites, network_evidence=round(r.minus_log10_p, 2),
                         global_chance=round((np.sum(ng >= r.minus_log10_p) + 1) / (len(ng) + 1), 3),
                         station_p='; '.join(f'{st} {v:.3g}' for st, v in per.items() if np.isfinite(v))))
R = pd.DataFrame(rows); R.to_csv('network_candidates_ranked_final.csv', index=False)
pd.set_option('display.width', 250); print(R.to_string())
for tag in ('primary', 'wide_speed'):
    ng = np.load(f'run14v5_final/null_max_k2_{tag}.npy'); print(tag, 'global levels 5/20/50 %:', np.round(np.quantile(ng, [0.95, 0.8, 0.5]), 2))
