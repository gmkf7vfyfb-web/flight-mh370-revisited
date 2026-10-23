cd /tmp
python - <<'EOF'
import pandas as pd, numpy as np, sys
sys.path.insert(0, "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/fd3a09d3-4e0f-4f0c-9e05-c56066b94f5f/hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare")
import tl_grid_run_j as T
raw=pd.read_csv('/tmp/tlg_tables_A/tl_grid.csv.gz', dtype={'receiver':str}); raw=raw[(raw.src_depth_m==10)&(raw.offset_nm==0)&(raw.status=='ok')]
pd.set_option('display.width',250)
for lg in ['H01W','H08S','3274']:
    p=raw[raw.receiver==lg].pivot_table(index='src_lat',columns='fc_hz',values='tl_db'); print(lg); print(p.loc[-34.0:-30.0].round(0).T.to_string() if -32.0 in p.index else p.round(0).T.iloc[:, :5])
s=pd.read_csv('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid/raw/passA/sources.csv')
m,el,tid=T.gebco()
for _,r in s[s.lat.isin([-33.0,-32.5,-32.0,-31.5,-31.0])].iterrows():
    i,j=T._ij(m,np.array([r.lat]),np.array([r.lon])); print(r.source_id, round(r.lon,3), 'GEBCO elev at source', int(el[i,j][0]))
EOF