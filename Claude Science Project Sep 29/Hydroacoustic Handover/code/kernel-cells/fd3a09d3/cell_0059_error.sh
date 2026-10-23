cd /tmp
python - <<'EOF'
import pandas as pd, numpy as np
raw=pd.read_csv('/tmp/tlg_tables_A/tl_grid.csv.gz'); raw=raw[(raw.src_depth_m==10)&(raw.offset_nm==0)&(raw.status=='ok')]
ref={'3274':'imp500_3274','3315':'imp500_3376','3376':'imp500_3376','3275':'imp500_3274'}
rv=pd.read_csv("/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/fd3a09d3-4e0f-4f0c-9e05-c56066b94f5f/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/results-data/ram_check/ram_vs_kraken.csv")
pd.set_option('display.width',250)
for lg in [3315,3376,3274,3275]:
    g=raw[raw.receiver==lg]
    p=g.pivot_table(index='src_lat',columns='fc_hz',values='tl_db')
    print(lg); print(p[[5.0,10.0,20.0,40.0]].round(0).T.to_string())
    r=rv[(rv.path==ref[str(lg)])&(rv.src_depth_m==10)].set_index('fc_hz'); print('ref kraken', r.tl_kraken_db.round(0).to_dict(), 'ref ram', r.tl_ram_db.round(0).to_dict())
EOF