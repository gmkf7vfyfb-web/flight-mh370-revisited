P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
mkdir -p $OUT; df -k /System/Volumes/Data | tail -1 | awk '{print $4/1048576 " GiB free"}'
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$P" && PYTHONPATH=. python imos_ram_grid.py run $OUT --at-bin "$OLDPWD/tools" --procs 4 --timing --only arc036.0S_+0-3315 arc038.0S_+0-3274 arc024.0S_+0-3250 2>&1 | grep -v Warning | tail -15
cat $OUT/wall_timing.json; cat $OUT/paths_meta_timing.csv; uptime