P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
cp /tmp/interim/tables/imos_tl_ram_arc.csv "$P/../results-data/tl_grid_run_j/imos_tl_ram_arc.csv"
cd "$P" && PYTHONPATH=. OMP_NUM_THREADS=2 python run_j_levels.py levels --out $OUT/levels-rerun --repo-out $OUT/levels-rerun/repo_copy --imos-tl-file imos_tl_ram_arc.csv --keys D0/p0.5 --receivers 3315 3376 3274 3275 3250 2>&1 | grep -v Warning | tail -3
python - <<'EOF'
import pandas as pd
o=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/detectable.csv",dtype={"receiver":str}); n=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/levels-rerun/tables/detectable.csv",dtype={"receiver":str})
o=o[(o.key=="D0/p0.5")&o.receiver.isin(["3315","3376","3274","3275","3250"])&o.eta.isin([0.001,0.00021])]; n=n[n.eta.isin([0.001,0.00021])]
m=o.merge(n,on=["receiver","eta"],suffixes=("_old","_new"))
print(m[["receiver","eta","frac_matched_filter_old","frac_matched_filter_new","frac_baseline_old","frac_baseline_new","snr_q50_old","snr_q50_new","blocked_mass_old","blocked_mass_new"]].round(4).to_string(index=False))
eo=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/eta_50.csv",dtype={"receiver":str}); en=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/levels-rerun/tables/eta_50.csv",dtype={"receiver":str})
eo=eo[(eo.key=="D0/p0.5")&eo.receiver.isin(["3315","3376","3274","3275","3250"])]
print(eo.merge(en,on=["receiver","threshold"],suffixes=("_old","_new"))[["receiver","threshold","snr50_eta1_db_old","snr50_eta1_db_new","eta_50_old","eta_50_new"]].to_string(index=False))
EOF