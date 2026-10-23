cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare" && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python - <<'EOF'
import time, pathlib, numpy as np, json, sys
sys.path.insert(0,'.')
import run_j_windows as W
sd=pathlib.Path('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1')
t=time.time(); g,meta,n=W.load_seed(sd); logon=meta["config"]["hypotheses"]["end-of-flight"]["logon"]
lnw=W.ln_weights(g,logon,"D0"); print(n, time.time()-t)
arc=g("arc_distance_nm"); print(np.nanpercentile(arc,[1,50,99]))
z=np.load(sd/'tau90_v1.npz'); print(z.files, z['tau90_s'].shape)
e=g("latent:impact_energy_transferred_j"); print(np.allclose(np.nan_to_num(e), np.nan_to_num(z['energy_transferred_j'])), np.nanmedian(e))
fe=json.load(open('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/summary/family-evidence-run-j.json')); print(fe['p_core'])
print(time.time()-t)
EOF