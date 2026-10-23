OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
for i in $(seq 1 36); do if grep -q '"n_jobs": 112' $OUT/wall.json 2>/dev/null; then break; fi; sleep 15; done
cat $OUT/wall.json | tr '\n' ' '; echo; L1=$(stat -f %m $OUT/run4_offsets.log); sleep 20; L2=$(stat -f %m $OUT/run4_offsets.log); echo "log advancing: $([ $L1 != $L2 ] && echo yes || echo no)"; echo "pids on rows: $(lsof -t $OUT/ram_grid_rows.csv 2>/dev/null | tr '\n' ' ')"
if grep -q '"n_jobs": 112' $OUT/wall.json && [ -z "$(lsof -t $OUT/ram_grid_rows.csv 2>/dev/null)" ]; then
  export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMBA_NUM_THREADS=1
  cd "$P" && (PYTHONPATH=. nohup python imos_ram_grid.py run $OUT --at-bin "$OLDPWD/tools" --procs 6 --bands 5 8 --offsets -30 30 --deadline 2026-10-22T06:15 > $OUT/run5_lowband_offsets.log 2>&1 &)
  sleep 45; grep -v Warning $OUT/run5_lowband_offsets.log | head -1; grep -c "ok ram" $OUT/run5_lowband_offsets.log
else echo "run4 still alive; not launching"; fi; date