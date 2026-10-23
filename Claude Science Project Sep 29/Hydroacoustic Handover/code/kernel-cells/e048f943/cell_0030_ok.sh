cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels; mkdir -p $OUT/logs
EOF=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
ALL=$(for s in run-j-waypoints run-j-free run-j-descent-climb run-j-repro-radar; do for d in $EOF/$s/seed-*; do echo "$s/$(basename $d)"; done; done)
echo "$ALL" | wc -l
for w in 0 1 2 3; do
  SEEDS=$(echo "$ALL" | awk -v w=$w 'NR%4==w')
  nohup python run_j_levels.py draw --out $OUT --seeds $SEEDS > $OUT/logs/draw-$w.log 2>&1 &
done
sleep 60; tail -n 2 $OUT/logs/draw-*.log