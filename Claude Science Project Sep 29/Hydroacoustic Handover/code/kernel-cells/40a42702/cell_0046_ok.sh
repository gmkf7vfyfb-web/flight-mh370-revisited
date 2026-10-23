cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "lat\b\|latitude\|quantile" prepare/imos_stageB_tl.py | sed -n 1,30p | cut -c1-180
grep -rn "imp025\|lat_q\|quantile_lat" results-data/stageB/*.json results-data/ram_check/*.json 2>/dev/null | head -5 | cut -c1-300