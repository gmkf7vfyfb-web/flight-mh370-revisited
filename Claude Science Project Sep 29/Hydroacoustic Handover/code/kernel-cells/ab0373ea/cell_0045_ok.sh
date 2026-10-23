python - <<'EOF'
import pandas as pd, numpy as np
d=pd.read_csv("/tmp/interim/tables/imos_ram_minus_kraken_arc.csv",dtype={"logger":str}); d0=d[d.offset_nm==0]
q=d0.groupby(["logger","fc_hz"]).ram_minus_kraken_db.describe(percentiles=[.1,.5,.9])[["count","min","10%","50%","90%","max"]].round(1)
print(q.to_string())
old=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ramcorr_arc.csv",dtype={"logger":str})
new=pd.read_csv("/tmp/interim/tables/imos_tl_ram_arc.csv",dtype={"logger":str})
m=old.merge(new,on=["quantile","logger","fc_hz","src_depth_m"],suffixes=("_old","_new"))
m=m[(m.offset_nm_old==0)&np.isclose(m.src_depth_m,10)&m.ram_grid_covered]
m["d"]=m.tl_db_new-m.tl_db_old
print("new - old TL (dB), offset 0, 10 m, covered rows, by logger x band:")
print(m.groupby(["logger","fc_hz"]).d.describe(percentiles=[.1,.5,.9])[["count","10%","50%","90%"]].round(1).unstack("fc_hz")["50%"].to_string())
print(m.groupby("logger").d.describe(percentiles=[.1,.5,.9])[["count","min","10%","50%","90%","max"]].round(1).to_string())
print(new[new.offset_nm==0].groupby(["logger","status"]).size().unstack(fill_value=0))
print(new[(new.offset_nm==0)&np.isclose(new.src_depth_m,10)&(new.fc_hz==20)&(new.logger=="3315")][["lat","tl_db","tl_db_raw_kraken","ram_grid_mode","status"]].to_string(index=False))
EOF