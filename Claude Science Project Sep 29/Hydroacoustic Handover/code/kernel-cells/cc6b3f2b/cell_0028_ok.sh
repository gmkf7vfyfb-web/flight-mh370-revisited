cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/weak_signal"
export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib OMP_NUM_THREADS=1
ls ../../../../../../../tools/Kraken | head; 
python - <<'EOF'
import sys, numpy as np, os, traceback
sys.path.insert(0,'.'); import template as T, preregistration as R, kraken_tl as KT
from pathlib import Path
at=os.path.abspath('../../../../../../../tools'); print(at, os.path.exists(f"{at}/Kraken/kraken.exe"))
z,c=T.PROF["z"],T.PROF["c"]; m=z<=R.TEMPLATE_DEPTH_M
zz=np.concatenate([z[m],[R.TEMPLATE_DEPTH_M]]); cc=np.concatenate([c[m],[np.interp(R.TEMPLATE_DEPTH_M,z,c)]])
w=Path('/tmp/wsig_dbg'); w.mkdir(exist_ok=True); root='dbg'
try:
    KT.write_env(w/f"{root}.env", root, 20.0, [(R.TEMPLATE_DEPTH_M, zz, cc)], [R.TEMPLATE_SD_M],[R.TEMPLATE_RD_M], R.BOTTOM, R.FG, 15)
    KT.write_flp(w/f"{root}.flp",[0.0],T.RANGES,[R.TEMPLATE_SD_M],[R.TEMPLATE_RD_M],opt="RAOC")
    import subprocess
    k=subprocess.run([f"{at}/Kraken/kraken.exe", root], cwd=w, capture_output=True, text=True); print("kraken rc",k.returncode, k.stdout[-300:], k.stderr[-300:])
    f=subprocess.run([f"{at}/KrakenField/field.exe", root], cwd=w, capture_output=True, text=True); print("field rc",f.returncode, f.stdout[-300:], f.stderr[-300:])
    print(os.listdir(w)); print(open(w/f"{root}.prt").read()[-800:])
except Exception: traceback.print_exc()
EOF