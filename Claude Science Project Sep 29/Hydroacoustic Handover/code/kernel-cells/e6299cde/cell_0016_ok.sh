cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - <<'EOF' 2>&1 | head -60
import numpy as np, json
E="/Users/pete/Downloads/mh370-exchange/hydroacoustics/"
z=np.load(E+"run-j-windows/pooled.npz"); print("pooled keys", list(z.keys())[:12], len(z.keys())); 
k=list(z.keys())[1]; print(k, z[k].shape)
s=np.load(E+"run-j-windows/supplement.npz"); print("supp keys", list(s.keys())[:12], len(s.keys()))
T=np.load(E+"run-j-weak-signal/templates/templates_raw.npz"); print("templates", list(T.keys()))
print(json.load(open(E+"run-j-weak-signal/templates/template_build.json")).keys())
th=json.load(open(E+"run-j-weak-signal/injection/thresholds.json")); print("thr", str(th)[:400])
n=np.load(E+"run-j-weak-signal/injection/null_maxima_3376.npz"); print("null3376", list(n.keys()), [n[k].shape for k in n])
import os; print(os.listdir(E+"run-j-tl-grid/raw/passA")[:10])
EOF
echo "== request.json"; python -c "
import json;r=json.load(open('data/ocean_paths/request.json'));print([(p['name'],p['b']) for p in r['paths']][:12])"
echo "== kadri digitised"; ls data/kadri_fig9_digitised; 
echo "== stageB map funcs"; grep -n "^def " prepare/imos_stageB_map.py | head; grep -n "^def " prepare/h08s_shot_outliers.py prepare/h08s_pulse_energy.py | head
echo "== bank.py"; sed -n 1,60p prepare/weak_signal/bank.py
echo "== prereg constants"; grep -n "^[A-Z_]* *=" prepare/weak_signal/preregistration.py | head -40