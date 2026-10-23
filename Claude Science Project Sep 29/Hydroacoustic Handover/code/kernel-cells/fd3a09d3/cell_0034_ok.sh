WS=$PWD
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
python tl_grid_run_j.py /tmp/tlg_val3 --at-bin "$WS/tools" --lat-south -36 --lat-north -26 --lat-step 10 --offsets 0 --receivers 3250 H08N --procs 4 --no-prescreen 2>&1 | tail -1
python -c "
import pandas as pd; d=pd.read_csv('/tmp/tlg_val3/tl_grid.csv'); print(d[d.src_depth_m==10].groupby(['source_id','receiver','status']).size()); print(d.groupby(['source_id','receiver']).min_profile_depth_m.first())"
grep -A3 '"arc' /tmp/tlg_val3/wall.json | grep -v range