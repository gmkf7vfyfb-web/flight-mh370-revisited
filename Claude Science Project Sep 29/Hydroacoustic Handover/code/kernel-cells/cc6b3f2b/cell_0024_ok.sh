cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
ls results-data/stageA; python -c "
import json;s=json.load(open('results-data/stageA/summary.json'));print({k:s[k] for k in ['n_background','excluded','thresholds']});print({k:v for k,v in s['fits'].items() if '3376' in k and 'T_C2' in k})"
for l in 3376 3274 3250; do echo $l $(ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/$l/2014*/*.DAT | wc -l); done
ls /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/3376/ | head -3; ls -la /Users/pete/Downloads/mh370-inputs/hydroacoustics/imos/background/3376/20140301 | head -4
grep -n "def header\|def parse_meta\|def clock_err" prepare/imos_preregistration.py
pip list 2>/dev/null | grep -i "ssqueeze\|ruptures\|numba"