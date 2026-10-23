cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
WS=$(cd ../../../../../.. && pwd)
python - <<'EOF'
import tl_grid_run_j as T, numpy as np
m, el, tid = T.gebco()
i,j = T._ij(m, np.array([-31.842167]), np.array([115.013733])); print('GEBCO at 3376:', el[i,j], 'tid', tid[i,j], '(expect ~ -450 m)')
i,j = T._ij(m, np.array([-34.892899, -7.6453]), np.array([114.1539, 72.4744])); print('H01W1, H08S1 seabed:', el[i,j])
# WOA sanity: c at surface and 1000 m near 35S 95E
z,p = T.woa_profile(-35.0, 95.0); print('WOA c(0), c(1000), c(4000):', p['c_mean'][0], p['c_mean'][list(z).index(1000.0)], p['c_mean'][list(z).index(4000.0)], 'deepest valid', z[np.isfinite(p['c_mean'])].max())
s = T.arc_sources(-41,-20,0.5,[-60,-30,0,30,60]); print(len(s)); print(s.head(6).to_string()); print(s.tail(3).to_string())
EOF
time python tl_grid_run_j.py /tmp/tlg_time --at-bin "$WS/tools" --no-arc --extra-sources t35:-35.0:92.77 --receivers H01W H08S 3274 --procs 3 --keep-paths 2>&1 | tail -5
cat /tmp/tlg_time/wall.json; python -c "
import pandas as pd; d=pd.read_csv('/tmp/tlg_time/tl_grid.csv'); print(d[d.src_depth_m==10][['receiver','fc_hz','tl_db','status','n_modes_first','n_modes_min','range_km','min_track_depth_m','km_shallower_1000','rcv_depth_m']].to_string())"