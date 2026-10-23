WS=$PWD; OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
nohup python tl_grid_ram_subset.py $OUT/ram-subset --at-bin "$WS/tools" --procs 4 > $OUT/ram-subset.log 2>&1 &
python tl_grid_table.py $OUT/tables $OUT/raw/passA $OUT/raw/passB $OUT/raw/passC > $OUT/tables/build.log 2>&1 || { mkdir -p $OUT/tables; python tl_grid_table.py $OUT/tables $OUT/raw/passA $OUT/raw/passB $OUT/raw/passC > $OUT/tables/build.log 2>&1; }
tail -14 $OUT/tables/build.log
python tl_grid_evidence.py $OUT/tables $OUT/evidence > /dev/null
python tl_grid_charts.py $OUT/tables $OUT/evidence /tmp/tlg_charts_final --stamp "Grid: passes A+B (offsets -30/0/+30 NM, mandated) and C (±60 NM, supplementary); module commits fc825c0, 4392091." 
python /tmp/note_numbers.py $OUT/tables $OUT/evidence 2>&1 | sed -n 1,40p
tail -3 $OUT/ram-subset.log