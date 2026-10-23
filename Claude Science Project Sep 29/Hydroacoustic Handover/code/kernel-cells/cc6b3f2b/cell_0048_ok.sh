cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
sed -i '' 's/^import numpy as np$/import numpy as np, warnings\nwarnings.filterwarnings("ignore", category=RuntimeWarning)/' methods.py
WS=$(cd ../../../../../../..; pwd); mkdir -p "$WS/out/injection"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python run_injection.py "$WS/out/templates/templates_raw.npz" "$WS/out/injection" 3 2>&1 | grep -v Warning | tail -30