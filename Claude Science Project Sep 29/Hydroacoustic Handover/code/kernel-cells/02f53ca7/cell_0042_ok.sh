AT=$PWD/tools; W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p ../results-data/tl_recal_block9
python tl_recal_block9.py tl $W/sections $AT $W/scratch ../results-data/tl_recal_block9 3 > $W/tl.log 2>&1
tail -25 $W/tl.log