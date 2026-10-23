cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
python - <<'EOF'
import re
s=open("template.py").read()
s=s.replace("RANGES = list(R.BANK_RANGES_KM) + list(R.EXTRA_RANGES_KM.values())",
"RANGES = sorted(set([float(v) for v in np.arange(R.INJ_RANGE_KM[0], R.INJ_RANGE_KM[1] + 1e-9, 25.0)] + list(R.BANK_RANGES_KM) + list(R.EXTRA_RANGES_KM.values())))   # 25 km grid for injection ranges + bank + IMOS/IMS ranges")
open("template.py","w").write(s)
EOF
WS=$(cd ../../../../../../..; pwd)
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
python template.py "$WS/out/templates" "$WS/tools" 3 2>&1 | tail -2
python -c "
import numpy as np; T=np.load('$WS/out/templates/templates_raw.npz'); print(T['ranges_km'].shape, T['H'].shape)"