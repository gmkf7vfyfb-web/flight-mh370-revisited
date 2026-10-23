cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data"
ls stageB nx2d near_limits ram_check | head -40
cat stageB/imos_tl_wall.json 2>/dev/null | head -30
cat */air9_tl_summary.json 2>/dev/null | head -20
find . -name "*wall*" | head