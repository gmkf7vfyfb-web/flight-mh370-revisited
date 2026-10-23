cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
WS=$(cd ../../../../../../..; pwd); export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python run_kadri.py "$WS/out/templates/templates_raw.npz" "$WS/out/kadri" 3 2>&1 | grep -v Warning | tail -5
python run_h08s.py "$WS/out/templates/templates_raw.npz" "$WS/out/h08s" 2>&1 | grep -v Warning | tail -8