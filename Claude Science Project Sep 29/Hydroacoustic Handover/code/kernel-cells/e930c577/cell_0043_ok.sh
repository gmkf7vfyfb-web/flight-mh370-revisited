cd leg; python - <<'E'
import pandas as pd
R=pd.read_csv('out/window_statistics.csv')
print(R.columns.tolist()); 
cols=['source_set','station','option','statistic','direction','role','computable','n_shots_in_window','observed','p_panel','n_null_panel','floor_panel','indep_rank_panel','n_indep_panel','p_pooled','covered_s','snr_db','peak_utc']
cols=[c for c in cols if c in R.columns]
pd.set_option('display.width',250)
print(R[cols].to_string(index=False, float_format=lambda x:f"{x:.4g}"))
E