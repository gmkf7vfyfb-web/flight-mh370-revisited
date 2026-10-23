cd /tmp
python - <<'EOF'
import pandas as pd, numpy as np
e=pd.read_csv('/tmp/tlg_ev_A/evidence_alone.csv', dtype={'receiver':str}); g=e[(e.receiver=='3274')&(e.eta==1e-5)&(e.offset_nm==0)]
print(g[g.frac_pd>0][['lat','spl_q50','noise_median','frac_pd','n_bands_blocked','status']].to_string())
t=pd.read_csv('/tmp/tlg_tables_A/imos_tl_ramcorr_arc.csv',dtype={'logger':str}); h=t[(t.logger=='3274')&(t.src_depth_m==10)&(t.offset_nm==0)]
print(h[h.lat.isin([-33.0,-32.5,-32.0])][['lat','fc_hz','tl_db','status','n_modes_min','min_profile_depth_m','range_km']].to_string())
raw=pd.read_csv('/tmp/tlg_tables_A/tl_grid.csv.gz'); r=raw[(raw.receiver=='3274')&(raw.src_depth_m==10)&(raw.offset_nm==0)&(raw.lat==-32.5)]
print(r[['fc_hz','tl_db','status','n_modes_first','n_modes_min','min_track_depth_m','km_shallower_1000']].to_string())
c=pd.read_csv("hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/ram_check/ram_vs_kraken.csv") if False else None
EOF
cat "$PWD/../hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/ram_check/ram_vs_kraken.csv" 2>/dev/null | grep imp500_3274 || grep imp500_3274 "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/fd3a09d3-4e0f-4f0c-9e05-c56066b94f5f/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/ram_check/ram_vs_kraken.csv"