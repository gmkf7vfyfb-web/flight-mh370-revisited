cd hydro/"Claude Science Project Sep 29"; grep -rn "3250" engine/hypotheses/hydroacoustics/prepare/imos_stageB_map.py | head -5; grep -rn "near_limits_eof289" --include=*.md --include=*.py --include=*.txt --include=*.json . 2>/dev/null | grep -v "^./engine/hypotheses/hydroacoustics/prepare/exploratory/near_limits_eof289.py" | head -5; python - <<'E'
import json
d=json.load(open("engine/hypotheses/hydroacoustics/results-data/stageA/summary_union.json")); print(list(d)[:10]); print([k for k in d.get("fits",{})][:20])
s=json.load(open("engine/hypotheses/hydroacoustics/results-data/imos2b/summary.json")); print(list(s)[:20]); print(s.get("background_spl_median"))
E
cat engine/hypotheses/hydroacoustics/results-data/near_limits/near_limits_eof289_KE.json | head -40