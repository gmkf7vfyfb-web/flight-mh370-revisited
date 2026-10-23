WS=$PWD
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python -c "
import tl_grid_run_j as T; s=T.arc_sources(-41,-20,0.5,[-60,-30,0,30,60]); print(len(s)); print(s[s.arc_fit_extrapolated].to_string()); print(s.arc_fit_rms_deg.describe().round(3).to_dict())"
time python tl_grid_run_j.py /tmp/tlg_time --at-bin "$WS/tools" --no-arc --extra-sources t35:-35.0:92.685 --receivers H01W H08S 3274 --procs 3 --keep-paths 2>&1 | tail -3
cat /tmp/tlg_time/wall.json | head -20; python -c "
import pandas as pd; d=pd.read_csv('/tmp/tlg_time/tl_grid.csv'); print(d[d.src_depth_m==10][['receiver','fc_hz','tl_db','status','n_modes_first','n_modes_min','range_km','min_track_depth_m','min_corridor_depth_m','km_shallower_1000','rcv_depth_m','travel_time_s']].round(1).to_string())"