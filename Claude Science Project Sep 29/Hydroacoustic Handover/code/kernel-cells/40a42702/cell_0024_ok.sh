cat > /tmp/pooltest.py <<'EOF'
from multiprocessing import Pool
import os
def f(x): return x*x
if __name__ == "__main__":
    with Pool(2) as p: print(p.map(f,[1,2,3]))
EOF
python /tmp/pooltest.py 2>&1 | tail -3
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
grep -n "^def \|^[A-Z_]\+ = " prepare/run_j_windows.py | head -40 | cut -c1-150
head -12 data/stations.csv | cut -c1-200
cat results-data/blackman_noise/blackman_noise_offsets.json | head -c 800