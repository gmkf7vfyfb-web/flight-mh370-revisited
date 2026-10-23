cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows; mkdir -p $OUT
time python run_j_windows.py seeds --eof /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j --out $OUT --workers 1 --strata run-j-free --seeds 1 2>&1 | tail -5
ls -la $OUT/run-j-free/