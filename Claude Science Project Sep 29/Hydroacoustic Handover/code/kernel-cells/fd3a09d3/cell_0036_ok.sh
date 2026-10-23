WS=$PWD
OUT=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tl-grid; mkdir -p $OUT/raw
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 PYTHONPATH=.
EXTRA=$(python -c "
import json; d=json.load(open('../data/ocean_paths/request.json')); seen={}
for p in d['paths']:
    n=p['name'].split('-')[0]
    if n.startswith('imp') and n not in seen: seen[n]=p['a']
print(' '.join(f'{n}:{a[1]}:{a[0]}' for n,a in seen.items()))")
echo "extra: $EXTRA"
nohup bash -c "
python tl_grid_run_j.py $OUT/raw/passA --at-bin '$WS/tools' --offsets 0 --extra-sources $EXTRA --procs 4 --work /tmp/tlg_work > $OUT/raw/passA.log 2>&1
python tl_grid_run_j.py $OUT/raw/passB --at-bin '$WS/tools' --offsets -30 30 --procs 4 --work /tmp/tlg_work > $OUT/raw/passB.log 2>&1
python tl_grid_run_j.py $OUT/raw/passC --at-bin '$WS/tools' --offsets -60 60 --procs 4 --work /tmp/tlg_work > $OUT/raw/passC.log 2>&1
echo ALLDONE > $OUT/raw/ALLDONE
" > /dev/null 2>&1 &
sleep 20; cat $OUT/raw/passA.log; date -u