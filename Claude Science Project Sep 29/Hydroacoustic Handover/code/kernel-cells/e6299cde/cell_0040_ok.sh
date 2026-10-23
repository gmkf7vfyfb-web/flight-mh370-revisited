cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "def log_t" -A4 prepare/kadri_table1_test.py
python -c "
import json,numpy as np; a=json.load(open('results-data/windows_run_j/arc_lat_lon.json'))['D0/p0.5']; print(a.keys()); print({k:(len(v), v[:3]) for k,v in a.items() if isinstance(v,list)})"
head -3 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA/sources.csv