P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid
TG=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables
mkdir -p /tmp/interim2; cp $OUT/plan.csv /tmp/interim2/
python - <<'EOF'
import pandas as pd
d=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid/ram_grid_rows.csv", on_bad_lines="skip").drop_duplicates(["tag","fc_hz"])
d.to_csv("/tmp/interim2/ram_grid_rows.csv", index=False); print(len(d), d.groupby("fc_hz").size().to_dict())
EOF
cd "$P" && PYTHONPATH=. python imos_ram_grid.py build /tmp/interim2 $TG /tmp/interim2/tables 2>&1 | grep -v Warning | head -8
cp /tmp/interim2/tables/imos_tl_ram_arc.csv ../results-data/tl_grid_run_j/imos_tl_ram_arc.csv
mkdir -p $OUT/levels-rerun-v2; ln -sfn /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/draws $OUT/levels-rerun-v2/draws
PYTHONPATH=. OMP_NUM_THREADS=2 python run_j_levels.py levels --out $OUT/levels-rerun-v2 --repo-out $OUT/levels-rerun-v2/repo_copy --imos-tl-file imos_tl_ram_arc.csv --keys D0/p0.5 --receivers 3315 3376 3274 3275 3250 2>&1 | grep -v Warning | tail -1
python - <<'EOF'
import pandas as pd, numpy as np
OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid"
L=["3315","3376","3274","3275","3250"]
o=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/detectable.csv",dtype={"receiver":str}); o=o[(o.key=="D0/p0.5")&o.receiver.isin(L)]
v1=pd.read_csv(f"{OUT}/levels-rerun/tables/detectable.csv",dtype={"receiver":str}); v2=pd.read_csv(f"{OUT}/levels-rerun-v2/tables/detectable.csv",dtype={"receiver":str}); sn=pd.read_csv(f"{OUT}/levels-rerun-sens-lowband-old/tables/detectable.csv",dtype={"receiver":str})
m=o.merge(v1,on=["receiver","eta"],suffixes=("_old","_v1")).merge(v2.rename(columns=lambda c: c+"_v2" if c not in("receiver","eta") else c),on=["receiver","eta"]).merge(sn.rename(columns=lambda c: c+"_sens" if c not in("receiver","eta") else c),on=["receiver","eta"])
m=m[m.eta.isin([0.001,0.00021])]
print(m[["receiver","eta","frac_matched_filter_old","frac_matched_filter_v1","frac_matched_filter_v2","frac_matched_filter_sens","frac_baseline_v1","frac_baseline_v2","snr_q50_v1","snr_q50_v2"]].round(4).to_string(index=False))
e1=pd.read_csv(f"{OUT}/levels-rerun/tables/eta_50.csv",dtype={"receiver":str}); e2=pd.read_csv(f"{OUT}/levels-rerun-v2/tables/eta_50.csv",dtype={"receiver":str})
print(e1.merge(e2,on=["receiver","threshold"],suffixes=("_v1","_v2"))[["receiver","threshold","eta_50_v1","eta_50_v2"]].to_string(index=False))
b1=pd.read_csv(f"{OUT}/levels-rerun/tables/band_levels_eta1.csv",dtype={"receiver":str}); b2=pd.read_csv(f"{OUT}/levels-rerun-v2/tables/band_levels_eta1.csv",dtype={"receiver":str})
bb=b1.merge(b2,on=["receiver","fc_hz","chain"],suffixes=("_v1","_v2")); print(bb[bb.fc_hz<=10][["receiver","fc_hz","q50_v1","q50_v2"]].round(1).to_string(index=False))
d=pd.read_csv("/tmp/interim2/tables/imos_ram_minus_kraken_arc.csv",dtype={"logger":str}); d=d[(d.offset_nm==0)&(d.fc_hz<=8)]
print(d.groupby(["logger","fc_hz"]).ram_minus_kraken_db.describe(percentiles=[.1,.5,.9])[["count","10%","50%","90%"]].round(1).to_string())
print("kraken no modes at 5/8 Hz (ram-only nodes):", d.ram_minus_kraken_db.isna().groupby([d.logger,d.fc_hz]).sum().to_dict())
EOF