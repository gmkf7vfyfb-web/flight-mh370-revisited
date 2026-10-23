OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
for i in $(seq 1 40); do if [ -f $OUT/wall.json ] && grep -q '"n_jobs": 170' $OUT/wall.json; then break; fi; sleep 15; done
grep -c "ok ram" $OUT/run3_lowband.log; grep -i "failed\|deadline" $OUT/run3_lowband.log | head -3; cat $OUT/wall.json | tr '\n' ' '; echo
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
cd "$P" && (PYTHONPATH=. nohup python imos_ram_grid.py run $OUT --at-bin "$OLDPWD/tools" --procs 6 --bands 10 20 40 --offsets -30 30 --deadline 2026-10-22T06:30 > $OUT/run4_offsets.log 2>&1 &)
sleep 60; grep -v Warning $OUT/run4_offsets.log | head -2; date; uptime