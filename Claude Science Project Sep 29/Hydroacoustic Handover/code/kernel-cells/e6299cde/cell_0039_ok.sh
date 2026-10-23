cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "t3\|3\.3\|student\|scale" prepare/kadri_table1_test.py | head -12
python -c "
import json,numpy as np; a=json.load(open('results-data/windows_run_j/arc_lat_lon.json')); print(type(a), list(a.keys())[:5] if isinstance(a,dict) else len(a)); 
import itertools
k=list(a.keys())[0] if isinstance(a,dict) else None; print(str(a)[:300])"
grep -n "GRID0\|GRID1\|^DT" prepare/run_j_windows.py | head -4