python - <<'EOF' > drift_result.txt
import json
d=json.load(open('handoff_kadri_results.json'))
for k,r in d.items():
    if r.get('name')!='Drift': continue
    so=r.get('structured_output') or {}
    print('SUMMARY:',so.get('summary'))
    for x in so.get('key_numbers',[]): print(' -',x)
    for x in so.get('likelihood_terms',[]): print(' LT',x)
    print('ARTIFACTS',so.get('artifacts')); print('COMMIT',so.get('commit')); print('OPEN',so.get('open_issues'))
EOF
wc -c drift_result.txt