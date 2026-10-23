cd /Users/pete/Downloads/mh370-exchange/end-of-flight
python - <<'EOF'
import json, numpy as np
j=json.load(open('run-j-supplement/reduced/impacts-ruleB.json')); print(str(j)[:1500])
z=np.load('run-j-supplement/reduced/impacts-ruleB.npz'); print({k:z[k].shape for k in z.keys()})
import os
for s in ['run-j-waypoints/seed-1','run-j-free/seed-1']:
    X=np.load(f'run-j/{s}/impacts32.npy',mmap_mode='r'); print(s, X.shape, X.dtype)
    print(open(f'run-j/{s}/COLUMNS.txt').read().split()[60:])
EOF