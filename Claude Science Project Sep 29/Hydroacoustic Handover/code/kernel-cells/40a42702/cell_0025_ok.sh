cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 150,200p prepare/run_j_windows.py
python -c "
import json;d=json.load(open('results-data/stageB/pd_samples_summary.json'));print({k:(v if len(str(v))<400 else str(v)[:400]) for k,v in d.items()})" | head -c 1500; echo
ls results-data/imos2b results-data/imos1d | head; grep -rl "bmed\|background_median" results-data/imos2b results-data/imos1d results-data/stageA 2>/dev/null | head -3
head -3 /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt; python -c "
import numpy as np; z=np.load('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/tau90_v1.npz'); print({k:(z[k].shape, z[k].dtype) for k in z.files}); print(np.nanpercentile(z['tau90_s'],[5,50,95]))"