cd leg; python - <<'E'
import pandas as pd, numpy as np
R=pd.read_csv('out/window_statistics.csv')
R=R[R.statistic!='coverage'].copy()
R['p']=R.p_panel
g=R.groupby(['source_set','option']).apply(lambda d: pd.Series(dict(n=len(d), computable=int(d.computable.sum()), n_p03=int((d.p<=0.3).sum()), exp03=float((d.computable*0.3).sum()), n_p01=int((d.p<=0.1).sum()), n_p005=int((d.p<=0.05).sum()), min_p=d.p.min())))
print(g.to_string())
cov=pd.read_csv('out/window_statistics.csv'); print(cov[cov.statistic=='coverage'][['source_set','station','option','note']].drop_duplicates().to_string(index=False))
h=R[(R.p<=0.1)]
print(h[['source_set','station','option','statistic','direction','role','n_shots_in_window','observed','p','floor_panel','n_indep_panel','p_pooled','snr_db','peak_utc']].to_string(index=False,float_format=lambda x:f"{x:.4g}"))
print(R[~R.computable.astype(bool)][['source_set','station','option','statistic','direction']].to_string(index=False))
E