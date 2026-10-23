cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls results-data/injection_run_j results-data/levels_run_j prepare/composition_run_j
python - <<'EOF'
import json
d=json.load(open('results-data/injection_run_j/fits.json'))
print(type(d), list(d)[:20] if isinstance(d,dict) else len(d))
import itertools
k=list(d)[0]; print(k, json.dumps(d[k])[:1500])
EOF
grep -n "^def \|^    \"\"\"" prepare/composition_run_j/common.py | head -60