cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
timeout 60 python - 2>&1 <<'EOF' | head -5
import multiprocessing as mp
try:
    with mp.Pool(2) as p: print(p.map(abs,[-1,-2]))
except Exception as e: print("POOL FAIL", type(e).__name__, str(e)[:200])
EOF
sed -n 102,117p run_j_windows.py; sed -n 152,200p run_j_windows.py