cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
nohup python run_j_levels.py levels --out $OUT > $OUT/logs/levels.log 2>&1 &
nohup python run_j_levels.py noise --out $OUT > $OUT/logs/noise.log 2>&1 &
sleep 90; tail -n 5 $OUT/logs/levels.log; tail -n 3 $OUT/logs/noise.log