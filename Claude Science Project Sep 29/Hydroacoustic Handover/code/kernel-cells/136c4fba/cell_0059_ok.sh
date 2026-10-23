cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" && export XDG_CONFIG_HOME=/tmp/xdg
KD="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
python3 prepare/kadri_northern_conditional.py "$KD" results-data/kadri_northern >/dev/null 2>&1
python3 -c "
import pandas as pd, json, numpy as np
pd.set_option('display.width',250)
L=pd.read_csv('results-data/kadri_northern/likelihood_ratio.csv'); print(L.to_string(index=False))
s=json.load(open('results-data/kadri_northern/summary.json'))
print(); print('TL', round(s['h08s_predicted']['tl_db'],1),'dB at', s['h08s_predicted']['tl_range_km'],'km; sd', s['h08s_predicted']['tl_sd_db'])
print('median shot E_peak', s['median_shot_E_peak'])
print('resolution', json.dumps(s['resolution_check']))
# which shots drive the H08S text window
C=pd.read_csv('results-data/kadri_northern/candidates.csv')
print(); print(C[(C.station=='H08S')&(C.option=='text')][['statistic','direction','observed','p_panel','rank_panel','p_pooled']].to_string(index=False))
"