pkill -f "run_j_levels.py draw" ; sleep 2
cd hydro/"Claude Science Project Sep 29"/engine/hypotheses/hydroacoustics/prepare
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels
EOF=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j
ALL=$(for s in run-j-waypoints run-j-free run-j-descent-climb run-j-repro-radar; do for d in $EOF/$s/seed-*/; do echo "$s/$(basename $d)"; done; done)
echo "$ALL" | wc -l
# remove any partial file written by a killed worker (npz written atomically by savez? not guaranteed) -> verify loadable later
for w in 0 1 2 3; do
  SEEDS=$(echo "$ALL" | awk -v w=$w 'NR%4==w')
  nohup python run_j_levels.py draw --out $OUT --seeds $SEEDS > $OUT/logs/draw-$w.log 2>&1 &
done
sleep 45; tail -qn 1 $OUT/logs/draw-*.log; ls $OUT/draws/run-j-waypoints | wc -l