cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels; mkdir -p $OUT
time python run_j_levels.py supplement --out $OUT 2>&1 | tail -3
time python run_j_levels.py draw --out $OUT --seeds run-j-free/seed-1 2>&1 | tail -3
python -c "
import numpy as np, json; z=np.load('$OUT/draws/run-j-free/seed-1.npz'); m=json.loads(str(z['meta'])); print(m['res']['n'], m['res']['alloc']); print({k:v['n_draws'] for k,v in m['sums'].items()}); print(len(z.files))
s=np.load('$OUT/draws/supplement.npz'); print(len(s['D0/p0.5/idx']), s['D0/p0.5/E'][:3], s['D0/p0.5/lat'][:3])"
du -sh $OUT