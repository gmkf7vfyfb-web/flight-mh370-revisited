cd "repo/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
echo "=== imos_coincidence.json ==="; python3 -m json.tool results-data/pair_tests/imos_coincidence.json | head -50
echo; echo "=== run-i-dive on disk ==="; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/ 2>/dev/null
echo "=== stageB / kadri_package ==="; ls results-data/stageB results-data/kadri_package/next-run-b 2>/dev/null | head -20
echo "=== h08s_template injection_pd ==="; python3 -c "
import json;d=json.load(open('results-data/h08s_template/h08s_template.json'));print(json.dumps(d['injection_pd'])[:600]); print('results keys',list(d['results'].keys())[:10])"