cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "=== candidate_time_sensitivity.json ==="; python3 -m json.tool results-data/kadri2a/candidate_time_sensitivity.json | head -80
echo; echo "=== grep 98 realisations in results-data json ==="
grep -rl "n_background\|n_bg\|realisation" results-data/*/*.json 2>/dev/null | head
echo "=== stageA summary ==="; python3 -c "
import json;d=json.load(open('results-data/stageA/summary.json'));print(list(d.keys()))" 2>/dev/null
echo "=== search_windows dir ==="; ls results-data/search_windows | head