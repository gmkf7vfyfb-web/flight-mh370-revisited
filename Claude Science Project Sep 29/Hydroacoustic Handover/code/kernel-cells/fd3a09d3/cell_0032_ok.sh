WS=$PWD
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
time python tl_grid_run_j.py /tmp/tlg_val2 --at-bin "$WS/tools" --lat-south -30 --lat-north -30 --offsets 0 --receivers 3250 --procs 1 --no-prescreen 2>&1 | tail -1
python -c "
import pandas as pd; d=pd.read_csv('/tmp/tlg_val2/tl_grid.csv'); print(d[d.src_depth_m==10][['source_id','receiver','fc_hz','tl_db','status','range_km','min_track_depth_m','min_profile_depth_m','km_shallower_1000','land_on_track']].round(1).to_string())"