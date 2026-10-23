cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
time python run_j_levels.py check --out $OUT 2>&1 | tail -60