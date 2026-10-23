cd leg; python - <<'E'
import pandas as pd, numpy as np
P=pd.read_csv('../hrepo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/pair_tests/kadri_trace_pairs.csv')
print(P.groupby('variant').t_h01w.unique().to_dict())
s=lambda x: sum(float(a)*m for a,m in zip(x.split(':'),(3600,60,1)))
OLD={('T','H08S'):[(s('01:16:19'),s('01:17:33'))],('C','H08S'):[(s('01:18:46'),s('01:20:00'))],
     ('T','PerthCanyon_3376'):[(s('00:50:44'),s('00:51:10')),(s('00:50:09'),s('00:53:15'))],
     ('C','PerthCanyon_3376'):[(s('00:53:11'),s('00:53:37')),(s('00:52:36'),s('00:55:42'))]}
W=pd.read_csv('out/arrival_windows.csv'); rows=[]
for _,r in W[W.station.isin(['H08S','PerthCanyon_3376','PerthCanyon_3315'])].iterrows():
    a,b=r.window_start_s,r.window_end_s; ol=OLD.get((r.branch,r.station),[])
    grid=np.linspace(a,b,2001); cov=np.zeros_like(grid,bool)
    for x,y in ol: cov|=(grid>=x)&(grid<=y)
    rows.append(dict(branch=r.branch,source_set=r.source_set,station=r.station,window=f"{r.window_start}-{r.window_end}",width_s=round(b-a,1),frac_inside_earlier_tested=round(cov.mean(),3),dt_h08s_minus_h01w=f"{r.dt_minus_h01w_s_min:.0f}-{r.dt_minus_h01w_s_max:.0f}"))
C=pd.DataFrame(rows); C.to_csv('out/coverage_vs_earlier.csv',index=False); print(C.to_string(index=False))
R=pd.read_csv('out/window_statistics.csv'); print(R[R.station=='H08S'].groupby(['source_set','option'])[['n_shots_in_window','n_indep_panel','n_indep_pooled']].max())
E