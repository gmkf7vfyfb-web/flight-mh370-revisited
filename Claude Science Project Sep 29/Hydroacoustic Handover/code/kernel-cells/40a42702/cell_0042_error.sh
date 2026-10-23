cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python inputs.py $OUT/inputs > $OUT/inputs/inputs.log 2>&1; tail -2 $OUT/inputs/inputs.log