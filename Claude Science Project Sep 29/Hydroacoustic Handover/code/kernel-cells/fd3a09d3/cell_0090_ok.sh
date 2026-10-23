python - <<'EOF'
import pandas as pd
g=pd.read_csv('/tmp/tlg_tables_AB/tl_grid.csv.gz', dtype={'receiver':str}); g=g[(g.offset_nm==0)&(g.src_depth_m==10)&(g.fc_hz.isin([31.5,40.0]))]
for rec,lat in [("H01W",-33.0),("H08S",-35.0),("H08N",-32.0),("H08N",-33.0),("H08N",-31.5),("H08N",-32.5),("3315",-36.0),("3376",-25.0),("3274",-36.0),("3275",-40.0),("3250",-24.0)]:
    h=g[(g.receiver==rec)&(g.src_lat==lat)]
    print(rec,lat, h.status.tolist(), h.tl_db.round(1).tolist(), 'susp_excl_rx', h.adiabatic_suspect_excl_rx.iloc[0], 'mincorr', h.min_corridor_depth_m.iloc[0], 'range', round(h.range_km.iloc[0]), 'srcdepth', h.source_water_depth_m.iloc[0])
EOF
grep paths /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passC.log | tail -1