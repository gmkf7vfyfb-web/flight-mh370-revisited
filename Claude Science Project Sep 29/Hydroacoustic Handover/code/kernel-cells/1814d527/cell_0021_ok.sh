python - <<'EOF'
import numpy as np, json
z=np.load('/Users/pete/Downloads/mh370-exchange/searched-areas/run-j-supplement/arc-grid.npz',allow_pickle=True)
for k in z.files: print(k, z[k].shape, z[k].dtype, (z[k].ravel()[:5] if z[k].size<1e7 else ''))
EOF
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "^def \|^[A-Z_]* *=" "$P/tl_grid_table.py" | head -30
sed -n '1,40p' "$P/tl_grid_table.py"
head -5 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA/sources.csv