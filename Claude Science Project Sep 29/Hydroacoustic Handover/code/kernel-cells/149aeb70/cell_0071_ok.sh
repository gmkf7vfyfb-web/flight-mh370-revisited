cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i && python3 - <<'PY'
import numpy as np, json
cols=json.load(open("next-i-free/seed-1/run.json"))["impact_columns"]; ix={c:i for i,c in enumerate(cols)}
a=np.load("next-i-free/seed-1/impacts32.npy",mmap_mode="r")
w=np.asarray(a[:,ix["weight"]],dtype=np.float64); w/=w.sum()
for c in ["latent:timed_out","t_impact_s","latent:terminal_window_unix_s","latent:recovery_attempted" if "latent:recovery_attempted" in ix else "latent:control_realised"]:
    v=np.asarray(a[:,ix[c]],dtype=np.float64)
    if c=="t_impact_s":
        o=np.argsort(v); cw=np.cumsum(w[o])
        qs=[np.interp(q,cw,v[o]) for q in (0.05,0.25,0.5,0.75,0.95,0.99)]
        print("t_impact weighted quantiles (min after 00:00):", [round(x/60,2) for x in qs], "max", v.max()/60)
    else:
        print(c, "unique:", np.unique(v)[:6], "weighted mean:", round(float((w*v).sum()),4))
PY