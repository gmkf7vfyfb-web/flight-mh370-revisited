P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
python - <<'EOF'
import pandas as pd, numpy as np
old=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ramcorr_arc.csv",dtype={"logger":str})
new=pd.read_csv("/tmp/interim/tables/imos_tl_ram_arc.csv",dtype={"logger":str})
assert (old[["quantile","logger","fc_hz","src_depth_m"]].values==new[["quantile","logger","fc_hz","src_depth_m"]].values).all()
s=new.copy(); m=s.band_extrapolated.values.astype(bool)
s.loc[m,"tl_db"]=old.loc[m,"tl_db"].values; s.loc[m,"status"]=old.loc[m,"status"].values
s.to_csv("hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/tl_grid_run_j/imos_tl_ram_arc_SENS.csv",index=False); print("rows swapped", m.sum())
EOF
mkdir -p $OUT/levels-rerun-sens-lowband-old; ln -sfn /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/draws $OUT/levels-rerun-sens-lowband-old/draws
cd "$P" && PYTHONPATH=. OMP_NUM_THREADS=2 python run_j_levels.py levels --out $OUT/levels-rerun-sens-lowband-old --repo-out $OUT/levels-rerun-sens-lowband-old/repo_copy --imos-tl-file imos_tl_ram_arc_SENS.csv --keys D0/p0.5 --receivers 3315 3376 3274 3275 3250 2>&1 | grep -v Warning | tail -1
rm ../results-data/tl_grid_run_j/imos_tl_ram_arc_SENS.csv
python - <<'EOF'
import pandas as pd
OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid"
n=pd.read_csv(f"{OUT}/levels-rerun/tables/detectable.csv",dtype={"receiver":str}); s=pd.read_csv(f"{OUT}/levels-rerun-sens-lowband-old/tables/detectable.csv",dtype={"receiver":str})
m=n.merge(s,on=["receiver","eta"],suffixes=("_new","_sens")); m=m[m.eta.isin([0.001,0.00021])]
print(m[["receiver","eta","frac_matched_filter_new","frac_matched_filter_sens","frac_baseline_new","frac_baseline_sens","snr_q50_new","snr_q50_sens"]].round(4).to_string(index=False))
EOF