cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - <<'EOF'
import json,collections
d=json.load(open('results-data/injection_run_j/fits.json'))
c=collections.Counter((k.split('|')[0],k.split('|')[1]) for k in d); print(c)
s=json.load(open('results-data/injection_run_j/summary.json')); print(list(s))
EOF
grep -n -E "^[A-Z_]+ *=" prepare/composition_run_j/prereg.py | cut -c1-250
grep -n -i "locus\|def " prepare/composition_run_j/reduce.py | head -40