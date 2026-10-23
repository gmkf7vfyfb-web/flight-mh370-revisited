cd /Users/pete/Downloads/mh370-exchange
cat searched-areas/run-j-supplement/arc-grid-check.json | head -c 1500; echo
python -c "
import numpy as np; z=np.load('searched-areas/run-j-supplement/arc-grid.npz'); print({k:(z[k].shape,z[k].dtype) for k in z.files}); 
for k in z.files:
    a=z[k]
    if a.ndim==1 and a.size>3: print(k, a[:3], a[-3:])
"
ls searched-areas/run-j-supplement/ | head
ls end-of-flight/run-j/run-j-waypoints/ | head -5; ls end-of-flight/run-j/run-j-waypoints/seed-1/
cat end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt
python -c "
import json;print(json.dumps(json.load(open('end-of-flight/run-j-supplement/reduced/impacts-ruleB.json')))[:1500])"