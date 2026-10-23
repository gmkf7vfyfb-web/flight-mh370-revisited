cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" && export XDG_CONFIG_HOME=/tmp/xdg
KD="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
time python3 prepare/kadri_northern_conditional.py "$KD" results-data/kadri_northern >/dev/null 2>&1
python3 -c "
import pandas as pd
pd.set_option('display.width',240)
C=pd.read_csv('results-data/kadri_northern/candidates.csv')
P=C[C.station.str.startswith('PerthCanyon')]
print(P[['station','option','window_utc','statistic','observed','peak_utc','recording','covered_s','snr_db','spl_max_db','p_panel','n_null_panel','note']].to_string(index=False))
print()
L=pd.read_csv('results-data/kadri_northern/likelihood_ratio.csv')
print(L.to_string(index=False))"