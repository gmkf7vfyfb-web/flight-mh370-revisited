cat note_tables.txt | sed -n 1,60p
python - <<'EOF'
import pandas as pd
n=pd.read_csv("/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/tables/imos_tl_ram_arc.csv",dtype={"logger":str})
print(n[n.below_physical_floor][["logger","lat","offset_nm","fc_hz","src_depth_m","tl_db","tl_db_raw_kraken","ram_grid_mode","delta_jump_db","range_km"]].round(1).to_string(index=False))
EOF