python - <<'EOF'
import pandas as pd, numpy as np
old=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ramcorr_arc.csv",dtype={"logger":str})
new=pd.read_csv("/tmp/interim/tables/imos_tl_ram_arc.csv",dtype={"logger":str})
m=old.merge(new,on=["quantile","logger","fc_hz","src_depth_m"],suffixes=("_old","_new"))
m=m[(m.offset_nm_old==0)&np.isclose(m.src_depth_m,10)&m.ram_grid_covered]; m["d"]=m.tl_db_new-m.tl_db_old
print(m[m.d.abs()>60][["logger","lat_old","fc_hz","status_old","status_new","tl_db_old","tl_db_new","tl_db_raw_kraken_old","ram_grid_mode","ramcorr_floored_old"]].round(1).to_string(index=False))
d=pd.read_csv("/tmp/interim/tables/imos_ram_minus_kraken_arc.csv",dtype={"logger":str})
print(d[(d.logger=="3274")&(d.offset_nm==0)&(d.fc_hz==40)][["lat","tl_ram_db","tl_kraken_noabs_db","ram_minus_kraken_db"]].round(1).to_string(index=False))
EOF