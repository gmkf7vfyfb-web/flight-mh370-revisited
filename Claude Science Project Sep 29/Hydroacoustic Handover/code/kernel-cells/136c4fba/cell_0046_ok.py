import pandas as pd, json, numpy as np
pd.set_option("display.width",250); pd.set_option("display.max_columns",40)
O="repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/kadri_northern/"
C=pd.read_csv(O+"candidates.csv")
print(C.columns.tolist())
print(C[["station","option","statistic","direction","role","computable","n_shots_in_window","observed","p_panel","n_null_panel","floor_panel","p_pooled","note"]].to_string())
