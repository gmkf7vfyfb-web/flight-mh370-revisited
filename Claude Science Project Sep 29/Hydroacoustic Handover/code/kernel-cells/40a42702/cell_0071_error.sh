cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
sed -i '' 's/pd_any_max_at_1e-2=pdmax/pd_any_max_at_1e_2=pdmax/' eta_map.py
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection
OMP_NUM_THREADS=1 python eta_map.py $OUT/inputs $OUT/run $OUT/eta 2>&1 | tail -15