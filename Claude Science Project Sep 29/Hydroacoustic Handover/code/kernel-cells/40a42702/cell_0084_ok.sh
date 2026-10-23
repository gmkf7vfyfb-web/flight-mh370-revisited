cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
mkdir -p $OUT/figs
python charts.py $OUT/run $OUT/eta $OUT/inputs/inputs.json $OUT/figs 2>&1 | grep -v Warning | tail -5; ls -la $OUT/figs