cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
head -c 600 results-data/stageB/imos_tl_wall.json; echo; grep -n "QLAT\|quantile" prepare/imos_stageB_tl.py | head -12; grep -n "QLAT\[" -B2 -A4 prepare/imos_stageB_map.py | head -30
python - <<'EOF'
import pandas as pd
rc=pd.read_csv('results-data/ram_check/imos_tl_ramcorr.csv'); print(rc.groupby(['quantile','logger']).range_km.first().unstack())
EOF