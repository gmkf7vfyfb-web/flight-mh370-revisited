cd gfx; python - <<'E'
import pandas as pd, numpy as np
d=pd.read_csv('data/detectable_corrected.csv',dtype={'receiver':str})
v=pd.read_csv('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/levels-rerun-v2/tables/detectable.csv',dtype={'receiver':str})
o=pd.read_csv('../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/levels_run_j/detectable.csv',dtype={'receiver':str})
m=d[d.key=='D0/p0.5'].merge(v[['receiver','eta','frac_matched_filter','frac_baseline','level_q50']],on=['receiver','eta'],suffixes=('','_v2'))
print((m.frac_matched_filter-m.frac_matched_filter_v2).abs().max(),(m.level_q50-m.level_q50_v2).abs().max())
m=d.merge(o[o.receiver.isin(['H01W','H08S','H08N'])][['key','receiver','eta','frac_matched_filter','level_q50']],on=['key','receiver','eta'],suffixes=('','_old'))
print((m.frac_matched_filter-m.frac_matched_filter_old).abs().max(),(m.level_q50-m.level_q50_old).abs().max())
b=pd.read_csv('data/best_receiver_corrected.csv'); ob=pd.read_csv('../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/levels_run_j/best_receiver.csv')
x=b.merge(ob[ob.key.str.endswith('p0.5')][['key','eta','frac_matched_filter','frac_baseline']],on=['key','eta'],suffixes=('','_old'))
print(x[x.eta.isin([1e-3,2.1e-4])][['key','eta','frac_matched_filter','frac_matched_filter_old','frac_baseline','frac_baseline_old','share_best_H01W','share_best_3315','share_best_3376','share_best_H08S','share_best_3275']].round(4).to_string())
print(d[(d.eta.isin([1e-3,2.1e-4,1e-5]))&(d.key=='D0/p0.5')][['receiver','eta','frac_matched_filter','frac_baseline','level_q50','level_q90']].round(4).to_string())
E