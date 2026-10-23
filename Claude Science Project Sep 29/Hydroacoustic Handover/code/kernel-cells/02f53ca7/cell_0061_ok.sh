W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal; tail -2 $W/nx2d.log
AT=$PWD/tools; cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python tl_recal_block9.py ram $W/sections $AT $W/scratch_ram ../results-data/tl_recal_block9 3 > $W/ram.log 2>&1; tail -12 $W/ram.log