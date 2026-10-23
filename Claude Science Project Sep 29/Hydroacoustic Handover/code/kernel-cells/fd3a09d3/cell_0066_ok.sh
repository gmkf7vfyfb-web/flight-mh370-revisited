python - <<'EOF'
import pandas as pd
t=pd.read_csv('/tmp/tlg_tables_A/ims_tl_kraken_arc.csv'); g=t[(t.station=='H01W')&(t.src_depth_m==10)&(t.fc_hz==20)&(t.offset_nm==0)].sort_values('lat')
print(g[['lat','lon','source_water_depth_m','tl_db','range_km']].round(1).to_string(index=False))
EOF