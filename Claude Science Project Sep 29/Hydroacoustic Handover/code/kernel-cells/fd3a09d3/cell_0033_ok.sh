WS=$PWD
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python - <<'EOF'
import tl_grid_run_j as T, air9_tl_validation as A, numpy as np
rx = T.receivers(['3250','H08N'])
s = T.arc_sources(-41,-20,1.0,[0])
for _,r in s.iterrows():
    for rn in rx:
        b,sp,info = T.build_path(dict(lat=r.lat,lon=r.lon), rx[rn])
        if info['land_on_track']: md='land'
        else:
            rp,pr = A.build_profiles(b,sp); md=round(min(p[0] for p in pr))
        print(r.source_id, rn, 'minprof', md, 'mintrack', info['min_track_depth_m'], 'km<1000', info['km_shallower_1000'])
EOF