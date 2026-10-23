cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/injection_recovery_run_j"
WS=$(pwd | sed 's#/hydro/.*##'); export DYLD_LIBRARY_PATH=/Users/pete/.claude-science/conda/envs/mh370-hydro/lib
python - <<EOF 2>&1 | tail -15
import sys, json, traceback, subprocess, numpy as np
sys.path[:0]=['.','..','../weak_signal']
import templates as T, prereg as R, kraken_tl as KT
from pathlib import Path
ranges, bank = T.range_list('/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-injection/inputs/inputs.json')
print(len(ranges), ranges[:3], ranges[-3:])
z, c = T.PROF["z"], T.PROF["c"]; m = z <= R.TEMPLATE_DEPTH_M
zz = np.concatenate([z[m], [R.TEMPLATE_DEPTH_M]]); cc = np.concatenate([c[m], [np.interp(R.TEMPLATE_DEPTH_M, z, c)]])
w = Path('/tmp/ktest'); w.mkdir(exist_ok=True); root='t00000'
try:
    KT.write_env(w / f"{root}.env", root, 10.0, [(R.TEMPLATE_DEPTH_M, zz, cc)], [R.TEMPLATE_SD_M], [R.TEMPLATE_RD_M], R.BOTTOM, R.FG, 15)
    KT.write_flp(w / f"{root}.flp", [0.0], ranges, [R.TEMPLATE_SD_M], [R.TEMPLATE_RD_M], opt="RAOC")
    r1=subprocess.run(["$WS/tools/Kraken/kraken.exe", root], cwd=w, capture_output=True, text=True); print('kraken', r1.returncode, r1.stdout[-200:], r1.stderr[-300:])
    r2=subprocess.run(["$WS/tools/KrakenField/field.exe", root], cwd=w, capture_output=True, text=True); print('field', r2.returncode, r2.stdout[-200:], r2.stderr[-300:])
    s = KT.read_shd(w / f"{root}.shd"); print(s["p"].shape)
except Exception as e:
    traceback.print_exc()
EOF
ls /tmp/ktest