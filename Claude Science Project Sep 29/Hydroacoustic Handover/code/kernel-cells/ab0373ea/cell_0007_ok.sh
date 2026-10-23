P="hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
X="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid"
sed -n 89,133p "$P"/tl_grid_run_j.py; sed -n 218,272p "$P"/tl_grid_run_j.py
grep -n "FG\s*=\|def fg\|francois\|Francois" "$P"/air9_tl_validation.py "$P"/kraken_tl.py | head
head -3 "$X/raw/passB/sources.csv"
cd "$P" && python - <<'EOF'
import pandas as pd, numpy as np
t=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ramcorr_arc.csv",dtype={"logger":str})
t=t[np.isclose(t.src_depth_m,10)&(t.offset_nm.abs()<=30)&(np.isclose(t.lat%1,0))]
print(t.groupby(["logger","fc_hz"]).status.value_counts().unstack(fill_value=0).loc[(slice(None),[10.0,20.0,40.0]),:])
op=t[(t.fc_hz==40)].groupby(["logger","offset_nm"]).apply(lambda g:(g.status!="land").sum())
print(op); print("total non-land paths", int(op.sum()))
print(t[(t.fc_hz==40)&(t.offset_nm==0)&(t.logger=="3250")][["lat","status","range_km","rcv_depth_m"]].to_string())
EOF
uptime