mkdir -p tools && tar xzf "{{artifact:1bd321c2-571c-42e1-a8f4-b0a2c3eff82e}}" -C tools && ls tools/Kraken | head -3
WS=$(pwd)
cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1
python - "$WS/tools" <<'EOF'
import sys, numpy as np, os, time
sys.path.insert(0,'.'); import template as T
at=sys.argv[1]; print(os.path.exists(f"{at}/Kraken/kraken.exe"))
for f in (48.0, 5.0, 20.0):
    t0=time.time(); k,p,nm=T.one((0, f, '/tmp/wsig_test', at)); print(f, "Hz:", round(time.time()-t0,2),"s modes",nm, np.round(-20*np.log10(np.abs(p)),1))
EOF