cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics" && export XDG_CONFIG_HOME=/tmp/xdg
KD="../../../../Archive ISO Pre Sept 28/codebases/v01-share-withdrawn/v01/workspace/.sources/kadri-2024-hydroacoustics/data"
python3 prepare/kadri_h01w_time_discriminant.py "$KD" results-data/kadri_northern 2>&1 | grep -viE "userwarning|_set_context|runtimewarning|ax.legend" | tail -40
echo "=== table ==="
python3 -c "
import pandas as pd
R=pd.read_csv('results-data/kadri_northern/h01w_time_discriminant.csv')
print(R[['option','statistic','observed','p_panelc','indep_rank_panelc','n_indep_panelc','p_pooled','indep_rank_pooled']].to_string(index=False))"