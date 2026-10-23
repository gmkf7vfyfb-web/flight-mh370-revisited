cd hydro/"Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-windows
grep -L "rc=0" $OUT/driver.log >/dev/null; grep -c "rc=0" $OUT/driver.log
time python run_j_windows.py supplement --supp /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/reduced/impacts-ruleB.npz --out $OUT 2>&1 | tail -3
time python run_j_windows.py pool --eof /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j --out $OUT --repo-out ../results-data/windows_run_j 2>&1 | tail -20