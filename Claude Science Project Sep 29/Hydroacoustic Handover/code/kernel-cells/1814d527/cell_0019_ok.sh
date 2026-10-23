P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n '70,100p;118,135p;152,200p;240,272p' "$P/run_j_windows.py"
echo ==== supplement json
python -c "
import json;d=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.json'));print(json.dumps(d)[:1500])
import numpy as np; z=np.load('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz'); print([(k,z[k].shape,z[k].dtype) for k in z.files])"