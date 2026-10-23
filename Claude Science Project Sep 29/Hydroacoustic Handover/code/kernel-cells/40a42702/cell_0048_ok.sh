cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - <<'EOF'
import json; d=json.load(open('data/ocean_paths/request.json')); print(type(d), list(d)[:8] if isinstance(d,dict) else d[:2])
s=json.dumps(d); import re
for q in ['025','250','500','750','975']:
    i=s.find(f'imp{q}'); print(q, s[i:i+220].replace('\n',' '))
EOF