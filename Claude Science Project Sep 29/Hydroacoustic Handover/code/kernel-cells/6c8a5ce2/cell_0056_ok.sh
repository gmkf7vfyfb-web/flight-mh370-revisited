cd .tmp/standin; OMP_NUM_THREADS=2 python - <<'EOF'
import numpy as np, json, glob, os
E="/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c"
edges=np.logspace(-2,2,161); out={}
for st in ["next-c-free","next-c-repro-radar","next-c-descent-climb","next-c-routes"]:
    h=np.zeros(160); n=0; lo=hi=0; ws=0
    for f in sorted(glob.glob(f"{E}/{st}/seed-*/tau90_v1.npz")):
        z=np.load(f); t=z["tau90_s"].astype(float); assert int(z["method"])==1
        h+=np.histogram(np.clip(t,1.0001e-2,99.99),edges)[0]; n+=len(t); lo+=(t<0.05).sum(); hi+=(t>10).sum(); ws+=(z["w_steep"]>=0.5).sum()
    out[st]=dict(hist=h.tolist(),n=int(n),seeds=len(glob.glob(f"{E}/{st}/seed-*/tau90_v1.npz")),share_below_0p05=lo/n,share_above_10=hi/n,share_steep_ge_half=ws/n)
    print(st,out[st]["seeds"],n,round(lo/n,4),round(hi/n,4),round(ws/n,3))
json.dump(dict(edges=edges.tolist(),strata=out),open("tau90_hist.json","w"))
EOF