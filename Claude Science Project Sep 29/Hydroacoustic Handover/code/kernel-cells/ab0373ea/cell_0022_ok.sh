P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$P" && PYTHONPATH=. python imos_ram_grid.py run $OUT/accept38p5 --at-bin "$OLDPWD/tools" --procs 1 --timing --lat-step 0.5 --bands 31.5 40 --only arc038.5S_+0-3376 2>&1 | grep -v Warning | tail -4
cat $OUT/accept38p5/ram_grid_rows_timing.csv | cut -d, -f1-6