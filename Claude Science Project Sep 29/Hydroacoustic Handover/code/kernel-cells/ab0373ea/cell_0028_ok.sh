P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
TG=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables
cd "$P" && PYTHONPATH=. python imos_ram_grid.py build $OUT $TG /tmp/smoke_tables 2>&1 | grep -v Warning | tail -30
cp /tmp/smoke_tables/imos_tl_ram_arc.csv ../results-data/tl_grid_run_j/imos_tl_ram_arc_SMOKE.csv
mkdir -p $OUT/levels-smoke; ln -sfn /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/draws $OUT/levels-smoke/draws
time PYTHONPATH=. OMP_NUM_THREADS=2 python run_j_levels.py levels --out $OUT/levels-smoke --repo-out /tmp/smoke_repo --imos-tl-file imos_tl_ram_arc_SMOKE.csv --keys D0/p0.5 --receivers 3315 3376 3274 3275 3250 2>&1 | grep -v Warning | tail -5
python - <<'EOF'
import pandas as pd
d=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/levels-smoke/tables/detectable.csv",dtype={"receiver":str})
d=d[d.eta.isin([0.001,0.00021])]; print("SMOKE (partial coverage, not evidence)"); print(d[["receiver","eta","frac_matched_filter","frac_baseline","snr_q50","blocked_mass"]].to_string(index=False))
EOF
rm ../results-data/tl_grid_run_j/imos_tl_ram_arc_SMOKE.csv; df -k /System/Volumes/Data | tail -1 | awk '{print $4/1048576 " GiB free"}'