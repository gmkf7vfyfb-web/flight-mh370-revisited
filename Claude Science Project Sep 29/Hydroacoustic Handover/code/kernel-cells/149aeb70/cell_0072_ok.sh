cd /Users/pete/Downloads/mh370-exchange/end-of-flight && for r in run-i run-i-dive run-i-c2aim; do echo "== $r  impacts:$(ls $r/*/seed-*/impacts32.npy 2>/dev/null | wc -l)  tau90:$(ls $r/*/seed-*/tau90_v1.npz 2>/dev/null | wc -l)  size:$(du -sh $r | cut -f1)"; done
python3 -c "
import pandas as pd
bl=pd.read_csv('$PWD/../../../../../dev/null') if False else None"
cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i && python3 - <<'PY'
import numpy as np, json
cols=json.load(open("next-i-free/seed-1/run.json"))["impact_columns"]; ix={c:i for i,c in enumerate(cols)}
a=np.load("next-i-free/seed-1/impacts32.npy",mmap_mode="r")[:400000]
for c in ["family_code","family4_code","onset_code","control_code","latent:onset_mechanism","latent:control_realised","latent:profile_shape","latent:spiral_divergent"]:
    v=np.asarray(a[:,ix[c]],dtype=np.float64)
    u,ct=np.unique(v[np.isfinite(v)],return_counts=True)
    print(f"{c:34s}", list(zip(u[:8].tolist(),(ct[:8]/len(v)).round(3).tolist())))
PY