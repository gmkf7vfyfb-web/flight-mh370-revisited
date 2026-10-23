mkdir -p "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j" "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/searches_run_j" /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "logon\[" run_j_windows.py | head -3; grep -n "logon = \|logon=" run_j_windows.py | head -5; grep -n "^T0\|^T_M0019B\|^T_LOI" run_j_windows.py
python -c "
import json; m=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/run.json')); print([k for k in m.keys()][:40]); print({k:m[k] for k in m if 'log' in k.lower() or 'lag' in k.lower()})" | head -c 1500