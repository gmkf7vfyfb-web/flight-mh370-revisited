cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
sed -n 100,125p prepare/kadri_northern_conditional.py
echo ==== supplement
S=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement
ls -la $S $S/reduced | head -30
python - <<'EOF'
import json,numpy as np
S='/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/'
import glob
for j in glob.glob(S+'*.json'):
    d=json.load(open(j)); print(j); print(json.dumps(d,indent=1)[:4000])
z=np.load(S+'impacts-ruleB.npz')
for k in z.files: print(k, z[k].shape, z[k].dtype)
EOF