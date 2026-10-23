cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" && export XDG_CONFIG_HOME=/tmp/xdg
KD="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
python3 prepare/kadri_northern_conditional.py "$KD" results-data/kadri_northern >/dev/null 2>&1
python3 -c "
import pandas as pd, json
pd.set_option('display.width',260)
C=pd.read_csv('results-data/kadri_northern/candidates.csv')
H=C[C.station=='H08S']
print(H[['option','statistic','direction','role','computable','n_shots_in_window','observed','p_panel','indep_rank_panel','n_indep_panel','p_pooled','indep_rank_pooled']].to_string(index=False))
s=json.load(open('results-data/kadri_northern/summary.json'))
print(); print(json.dumps(s['resolution_check'][1]))
"