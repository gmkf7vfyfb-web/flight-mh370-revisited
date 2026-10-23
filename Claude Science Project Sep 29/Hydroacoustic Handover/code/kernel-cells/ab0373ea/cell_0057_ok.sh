python - <<'EOF'
import pandas as pd, numpy as np
OUT="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-imos-ram-grid"
o=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-levels/tables/band_levels_eta1.csv",dtype={"receiver":str}); n=pd.read_csv(f"{OUT}/levels-rerun/tables/band_levels_eta1.csv",dtype={"receiver":str})
o=o[(o.key=="D0/p0.5")&(o.chain=="module")]; n=n[(n.chain=="module")]
for lg in ["3315","3376","3275"]:
    m=o[o.receiver==lg].merge(n[n.receiver==lg],on="fc_hz",suffixes=("_o","_n"))
    print(lg); print(m[["fc_hz","q50_o","q50_n","q90_o","q90_n","blocked_mass_o","blocked_mass_n"]].round(1).to_string(index=False))
old=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ramcorr_arc.csv",dtype={"logger":str})
new=pd.read_csv("/tmp/interim/tables/imos_tl_ram_arc.csv",dtype={"logger":str})
for t,nm in ((old,"old"),(new,"new")):
    g=t[(t.logger=="3315")&(t.offset_nm==0)&np.isclose(t.src_depth_m,10)&(t.lat.isin([-38,-37,-36,-35,-34]))]
    print(nm); print(g.pivot(index="lat",columns="fc_hz",values="tl_db").round(0).to_string())
EOF