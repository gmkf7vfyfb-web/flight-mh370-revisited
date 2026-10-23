cd .tmp/standin; rm -rf module_prepare; export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1; P="$(cd ..; pwd)/hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; python - "$P" <<'EOF'
import sys,time; sys.argv=[sys.argv[0]]+sys.argv[1:]
sys.path.insert(0, sys.argv[1]); import calibration_events as CE
import pandas as pd
from pathlib import Path
D=Path("/Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration")
for n in ["af447-H10S","sanjuan-charge-H10N"]:
    b=pd.read_csv(D/f"bathy_{n}.csv"); s=pd.read_csv(D/f"ssp_{n}.csv")
    t=time.time(); r,p=CE.A.build_profiles(b,s); print(n, len(r), "profiles", f"{time.time()-t:.1f}s", "minD", min(x[0] for x in p))
EOF
( time python run_event_tl.py "$P" "$(cd ../at; pwd)" /Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration smoke40 40 ) 2>&1 | tail -6; cat smoke40/event_tl.csv; du -sh smoke40