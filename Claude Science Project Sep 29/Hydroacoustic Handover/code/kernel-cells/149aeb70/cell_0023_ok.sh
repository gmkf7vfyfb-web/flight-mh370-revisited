cat > /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i/parent_ess.py <<'EOF'
import numpy as np, json, glob, os
R = "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i"
meta = json.load(open(f"{R}/loud_tail_ess.json")); THR = meta["thresholds_W"]["0.9"]
cols = json.load(open(f"{R}/next-i-free/seed-1/run.json"))["impact_columns"]
ix = {c: i for i, c in enumerate(cols)}
OPTS = [c for c in cols if c.startswith("loglik:")]
strata = sorted(os.path.basename(p) for p in glob.glob(f"{R}/next-i-*"))
tot = {o: {"all": [], "loud": []} for o in OPTS}
nparents = 0
for s in strata:
    for si, sd in enumerate(sorted(glob.glob(f"{R}/{s}/seed-*/impacts32.npy"))):
        a = np.load(sd, mmap_mode="r"); n = a.shape[0]
        par = np.empty(n, np.int64); w = np.empty(n, np.float64)
        ll = np.empty((len(OPTS), n), np.float32)
        for i in range(0, n, 400_000):
            b = np.asarray(a[i:i+400_000])
            par[i:i+400_000] = b[:, ix["parent"]].astype(np.int64)
            w[i:i+400_000] = b[:, ix["weight"]]
            for k, o in enumerate(OPTS):
                ll[k, i:i+400_000] = b[:, ix[o]]
        loud = np.load(sd.replace("impacts32.npy", "tau90_v1.npz"))["peak_rate_w"] > THR
        np_ = int(par.max()) + 1; nparents += np_
        for k, o in enumerate(OPTS):
            lw = ll[k].astype(np.float64)
            wo = w * np.exp(np.where(np.isfinite(lw), lw, -np.inf))
            tot[o]["all"].append(np.bincount(par, weights=wo, minlength=np_))
            tot[o]["loud"].append(np.bincount(par[loud], weights=wo[loud], minlength=np_))
    print("done", s, flush=True)
def ess(v):
    v = np.concatenate(v); s = v.sum()
    return 0.0 if s <= 0 else float(s * s / np.square(v).sum())
out = {o.replace("loglik:", ""): {"ess_parents_all": ess(tot[o]["all"]),
                                  "ess_parents_loud_p90": ess(tot[o]["loud"])} for o in OPTS}
print(f"\nparents in run I (all strata, all seeds): {nparents}")
print(f"loud tail = peak radiated power > {THR:.3e} W (top decile of held-out baseline)\n")
print("option".ljust(22), "ess_parents_all".rjust(16), "ess_parents_loud".rjust(17))
for k, v in out.items():
    print(k.ljust(22), f"{v['ess_parents_all']:16.0f}", f"{v['ess_parents_loud_p90']:17.0f}")
json.dump({"n_parents": nparents, "loud_threshold_W": THR, "options": out},
          open(f"{R}/parent_ess.json", "w"), indent=1)
EOF
cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i && time python3 parent_ess.py