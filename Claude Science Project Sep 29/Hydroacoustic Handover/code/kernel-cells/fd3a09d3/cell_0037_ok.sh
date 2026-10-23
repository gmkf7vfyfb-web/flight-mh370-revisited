cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 1,40p prepare/ram_tl_check.py | head -60
grep -n "ramcorr\|delta" prepare/ram_tl_check.py | head -30
head -3 results-data/ram_check/ram_vs_kraken.csv; wc -l results-data/ram_check/ram_vs_kraken.csv
python -c "
import pandas as pd; d=pd.read_csv('results-data/ram_check/ram_vs_kraken.csv'); print(d.columns.tolist()); print(d.groupby(['path','src_depth_m']).delta_db.describe()[['count','mean','min','max']] if 'delta_db' in d else d.head())
a=pd.read_csv('results-data/ram_check/imos_tl_ramcorr.csv'); b=pd.read_csv('results-data/stageB/imos_tl.csv'); m=a.merge(b,on=['quantile','logger','fc_hz','src_depth_m'],suffixes=('_rc','_k')); m['d']=m.tl_db_rc-m.tl_db_k; print(m.groupby(['logger','fc_hz','src_depth_m']).d.agg(['mean','std']).round(3).head(12)); print(m.groupby('logger').d.std().round(4))"