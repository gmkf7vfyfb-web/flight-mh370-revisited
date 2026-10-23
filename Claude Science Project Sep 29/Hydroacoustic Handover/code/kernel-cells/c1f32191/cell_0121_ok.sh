python - <<'EOF'
import numpy as np, json
O="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated-v2"; S="/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated/stats-ramgrid"
for sd in ["run-j-free/seed-3","run-j-waypoints/seed-1","run-j-repro-radar/seed-2"]:
    a=np.load(f"{O}/{sd}/acc.npz"); b=np.load(f"{S}/{sd}/acc.npz")
    for k in ["wL_a0.05","wPnd_a0.05","wLmarg_a0.05","half_wL_a0.05","wL_ims_a0.05"]:
        x,y=a[k],b[k]; rel=np.max(np.abs(x-y)/np.maximum(np.abs(y),1e-300)); print(sd,k,"max rel diff", f"{rel:.2e}")
    print(json.loads(str(a["meta"]))["imos_tl"], json.loads(str(b["meta"]))["imos_tl"])
EOF