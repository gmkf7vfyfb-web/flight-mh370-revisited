cd /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/panels
python - <<'EOF'
import pandas as pd, numpy as np
pd.set_option('display.width',250)
W=pd.read_csv('panel_windows.csv'); C=pd.read_csv('panel_candidates.csv')
print(W.groupby(['receiver','detector','band_hz']).size())
print(C.groupby(['receiver','label']).size().unstack(fill_value=0))
print(C[['receiver','panel','time_utc','detector','band_hz','statistic','p','p_A','p_B','label','in_window_sofar','kadri_label','eta_needed']].head(30).to_string())
print(pd.read_csv('box_minima.csv').to_string())
print(pd.read_csv('h08s_suppression.csv'))
EOF