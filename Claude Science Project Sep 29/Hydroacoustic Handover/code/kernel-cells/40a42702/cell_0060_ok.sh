mkdir -p tools && tar xzf "{{artifact:1bd321c2-571c-42e1-a8f4-b0a2c3eff82e}}" -C tools && ls tools/Kraken/kraken.exe tools/KrakenField/field.exe
AT=$PWD/tools
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python templates.py $OUT/inputs/inputs.json $OUT/templates $AT 4 > $OUT/templates.log 2>&1; tail -3 $OUT/templates.log