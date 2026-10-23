cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows/ | grep -v "^_w_" ; ls /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows/seed-hist 2>/dev/null | head -3
grep -n "^def \|^RECEIVERS\|^RECV\|^[A-Z_]* = " run_j_windows.py | head -60
grep -n "3274\|3275\|Portland" run_j_windows.py | head -5
grep -n "def lnw\|def weights\|def option_weights\|loglik" run_j_windows.py | head -20
cat /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows/COLUMNS.txt 2>/dev/null | head -20
python - <<'EOF'
import multiprocessing as mp
try:
    with mp.Pool(2) as p: print(p.map(abs,[-1,-2]))
except Exception as e: print("POOL FAIL", e)
EOF