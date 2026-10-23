cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows
python run_j_windows.py seeds --eof /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j --out $OUT --workers 2 > $OUT/driver.log 2>&1
tail -3 $OUT/driver.log; ls $OUT/*/seed-*.npz | wc -l