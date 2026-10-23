P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
sed -n '57,104p' "$P/weak_signal/methods.py"
echo ==== PREREG consts
grep -n "^[A-Z_]* *=" "$P/weak_signal/preregistration.py" | head -50
echo ==== templates
python - <<'EOF'
import numpy as np, json
z=np.load('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/templates/templates_raw.npz')
print(z.files[:12], len(z.files)); print(float(z['fs']))
k=[f for f in z.files if f.startswith('h2_')]; print(len(k), k[:5], z[k[0]].shape)
print(json.load(open('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-weak-signal/templates/template_build.json')))
EOF