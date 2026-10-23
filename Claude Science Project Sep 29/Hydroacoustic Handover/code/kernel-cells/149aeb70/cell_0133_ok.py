import numpy as np, json
E = "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive/next-i-free/seed-1"
cols = json.load(open(f"{E}/run.json"))["impact_columns"]; ix = {c: i for i, c in enumerate(cols)}
print("push/dive-related columns:", [c for c in cols if "push" in c or "surface" in c or "dive" in c or "level" in c])
a = np.load(f"{E}/impacts32.npy", mmap_mode="r")
g = lambda c: np.asarray(a[:, ix[c]], dtype=np.float64)
pd_ = g("latent:pushover_drawn"); fpa = g("flight_path_angle_deg"); w = g("weight")
print("\npushover_drawn values:", np.unique(pd_))
for c in [c for c in cols if "push" in c]:
    v = g(c); u = np.unique(v[np.isfinite(v)])
    print(f"  {c:38s} n_unique={len(u):6d} first={u[:4]}")
m = pd_ > 0.5
print(f"\namong pushover draws (n={m.sum()}): fraction impacting steeper than 10 deg = {(fpa[m] > 10).mean():.3f}")
