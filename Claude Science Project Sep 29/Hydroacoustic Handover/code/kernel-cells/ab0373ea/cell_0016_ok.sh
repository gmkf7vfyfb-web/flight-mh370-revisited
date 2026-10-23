P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
cp $OUT/ram_grid_rows_timing.csv $OUT/ram_grid_rows.csv
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$P" && PYTHONPATH=. nohup python imos_ram_grid.py run $OUT --at-bin "$OLDPWD/tools" --procs 6 --deadline 2026-10-23T03:50 > $OUT/run.log 2>&1 &
echo started $!; date