grep -n "imos_tl_ram_arc\|ram_grid_mode\|ram_grid_covered\|band_extrapolated\|below_physical_floor\|delta_jump\|drop-in\|How to use\|loader\|offset" /tmp/ramgrid.md | cut -c1-260 | head -40
python - <<'EOF'
import pandas as pd
t=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv", dtype={"logger":str})
print(t.ram_grid_mode.value_counts().to_dict()); print(t.groupby(["offset_nm"]).ram_grid_covered.mean().round(3).to_dict())
o=t[(t.offset_nm==0)&(t.src_depth_m==10)]
print(o.groupby("logger").agg(n=("tl_db","size"), cov=("ram_grid_covered","mean"), ok=("tl_db", lambda x: x.notna().mean()), bx=("band_extrapolated","mean"), fl=("below_physical_floor","mean")).round(3))
print(o[(o.logger=="3315")&(o.fc_hz==20.0)][["lat","tl_db","tl_db_raw_kraken","ram_grid_mode","ram_grid_covered","band_extrapolated"]].head(8).to_string())
EOF