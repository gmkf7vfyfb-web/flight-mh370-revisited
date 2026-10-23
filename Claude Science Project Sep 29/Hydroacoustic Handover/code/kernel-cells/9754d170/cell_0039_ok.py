
import pandas as pd, numpy as np
HB="audit/hb/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/"
mod=pd.read_csv(HB+"results-data/shared_env/air9_tl_model.csv")
obs=pd.read_csv(HB+"data/blackman/fig23_air9_digitised.csv",comment='#')
print(obs.head(3)); print(obs.columns.tolist(), obs.groupby(obs.columns[0]).size() if obs.shape[1]>2 else '')
p=mod[(mod.bottom=='hard')].pivot_table(index='fc_hz',columns=['station','src_depth_m'],values='tl_db')
print(p.round(1))
