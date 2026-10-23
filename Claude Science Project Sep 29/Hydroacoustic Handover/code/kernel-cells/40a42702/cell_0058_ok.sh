cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
AT=$(python -c "import os;print(os.path.abspath('../../../../../../../tools'))"); ls $AT/Kraken/kraken.exe
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python templates.py $OUT/inputs/inputs.json $OUT/templates $AT 4 > $OUT/templates.log 2>&1; tail -3 $OUT/templates.log