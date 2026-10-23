cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
uptime
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python run.py $OUT/inputs/inputs.json $OUT/templates/templates_raw.npz $OUT/run 4 > $OUT/run.log 2>&1; tail -5 $OUT/run.log