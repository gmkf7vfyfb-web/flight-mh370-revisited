cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"
python - <<'EOF'
import pandas as pd
r=pd.read_csv('data/imos/recordings.csv'); print(r.groupby(['logger','role']).size()); print(r.groupby('logger').start_logger.agg(['min','max','count']))
EOF
python - <<'EOF'
from multiprocessing import Pool
try:
    with Pool(2) as p: print(p.map(abs,[-1,-2]))
except Exception as e: print("POOL FAIL", repr(e)[:200])
EOF
grep -n "^def \|^[A-Z_]\+ = " prepare/run_j_windows.py | head -40
cat data/stations.csv | head -12
grep -n "3376\|3274\|offset" results-data/blackman_noise/blackman_noise_offsets.json | head