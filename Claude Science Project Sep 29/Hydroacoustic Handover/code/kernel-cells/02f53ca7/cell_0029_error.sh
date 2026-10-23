cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
W=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal; AT=$(cd ../../../../../../tools && pwd)
python - <<EOF
import sys; sys.argv=['x']
import tl_recal_block9 as B, time
from pathlib import Path
sec=Path('$W/sections')
t=time.time()
r=B.tl_job(('smoke_air9_H01W', sec/'shared'/'bathy_air9_H01W.csv', sec/'shared'/'ssp_air9_H01W.csv', 12.5, [9.0,10.0,12.0], 1055.0, '$W/scratch_smoke', '$AT'))
for x in r: print({k:(round(v,2) if isinstance(v,float) else v) for k,v in x.items()})
print('wall', time.time()-t)
EOF