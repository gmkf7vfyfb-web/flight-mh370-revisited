cd .tmp/standin; python - <<'EOF'
import pandas as pd
P="../hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/f35a_cal/f35a_tl.csv"
t=pd.read_csv("tl/event_tl.csv"); f=pd.read_csv(P)
a=t.pivot_table(index="fc_hz",columns=["path","src_depth_m"],values="tl_db").round(1)
print(a.to_string())
print(f.pivot_table(index="fc_hz",columns=["station","src_depth_m"],values="tl_db").round(1).to_string())
print(t.groupby(["path","fc_hz"])[["n_modes_first","n_modes_min"]].first().unstack(0).to_string())
print(f.range_km.unique())
EOF