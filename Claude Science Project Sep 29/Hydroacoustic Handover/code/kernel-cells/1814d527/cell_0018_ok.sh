P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
grep -n "^def \|^[A-Z_]* *=" "$P/run_j_windows.py" | head -60
echo ====
cat /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt
ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1/
ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/ /Users/pete/Downloads/mh370-exchange/searched-areas/run-j-supplement/ 2>&1 | head
python - <<'EOF'
import numpy as np
z=np.load('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows/pooled.npz',allow_pickle=True)
print([(k,z[k].shape) for k in z.files][:20])
s=np.load('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows/supplement.npz',allow_pickle=True)
print([(k,s[k].shape) for k in s.files][:20])
EOF