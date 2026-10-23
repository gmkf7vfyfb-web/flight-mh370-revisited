WS=$(pwd); cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
mkdir -p "$WS/out/templates"
python template.py "$WS/out/templates" "$WS/tools" 3 2>&1 | tail -12