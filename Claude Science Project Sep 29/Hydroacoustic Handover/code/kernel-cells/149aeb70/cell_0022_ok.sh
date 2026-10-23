cat > /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i/loud_tail_ess.py <<'EOF'
import numpy as np, json, glob, os, collections
R = "/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i"
cols = json.load(open(f"{R}/next-i-free/seed-1/run.json"))["impact_columns"]
ix = {c: i for i, c in enumerate(cols)}
OPTS = [c for c in cols if c.startswith("loglik:")]
strata = sorted(os.path.basename(p) for p in glob.glob(f"{R}/next-i-*"))
store = {}
for s in strata:
    W, LL, PR, EN, TA, VU = [], [], [], [], [], []
    for sd in sorted(glob.glob(f"{R}/{s}/seed-*/impacts32.npy")):
        c2 = json.load(open(os.path.join(os.path.dirname(sd), "run.json")))["impact_columns"]
        assert c2 == cols, sd
        a = np.load(sd, mmap_mode="r")
        n = a.shape[0]
        w = np.empty(n, np.float64); ll = np.empty((len(OPTS), n), np.float32); vu = np.empty(n, np.float32)
        step = 400_000
        for i in range(0, n, step):
            blk = np.asarray(a[i:i+step])
            w[i:i+step] = blk[:, ix["weight"]]
            vu[i:i+step] = blk[:, ix["velocity_up_mps"]]
            for k, o in enumerate(OPTS):
                ll[k, i:i+step] = blk[:, ix[o]]
        z = np.load(sd.replace("impacts32.npy", "tau90_v1.npz"))
        assert z["peak_rate_w"].shape[0] == n
        W.append(w); LL.append(ll); VU.append(vu)
        PR.append(z["peak_rate_w"]); EN.append(z["energy_transferred_j"]); TA.append(z["tau90_s"])
    store[s] = dict(w=np.concatenate(W), ll=np.concatenate(LL, axis=1),
                    pr=np.concatenate(PR), en=np.concatenate(EN), ta=np.concatenate(TA), vu=np.concatenate(VU))
    print("loaded", s, store[s]["w"].shape, flush=True)

def wq(v, w, q):
    o = np.argsort(v); c = np.cumsum(w[o]); c /= c[-1]
    return float(v[o][np.searchsorted(c, q)])

# baseline (00:19 held out) combined weights, strata equally weighted
base = {s: store[s]["w"] / store[s]["w"].sum() / len(strata) for s in strata}
pr_all = np.concatenate([store[s]["pr"] for s in strata])
bw_all = np.concatenate([base[s] for s in strata])
thr = {q: wq(pr_all, bw_all, q) for q in (0.5, 0.9, 0.99)}
print("\npeak radiated power thresholds (W) under held-out baseline:",
      {k: f"{v:.3e}" for k, v in thr.items()}, flush=True)

def ess(w):
    s1 = w.sum(); return 0.0 if s1 <= 0 else float(s1 * s1 / np.square(w).sum())

rows = []
def row(label, wd):
    wc = np.concatenate([wd[s] for s in strata]); wc = wc / wc.sum()
    out = dict(option=label, ess_all=ess(wc))
    for q in (0.9, 0.99):
        m = pr_all > thr[q]
        out[f"mass_p{int(q*100)}"] = float(wc[m].sum())
        out[f"ess_p{int(q*100)}"] = ess(wc[m])
    out["med_peak_W"] = wq(pr_all, wc, 0.5)
    ta_all = np.concatenate([store[s]["ta"] for s in strata])
    out["med_tau90_s"] = wq(ta_all, wc, 0.5)
    rows.append(out)

row("none (00:19 held out)", base)
per_stratum = collections.defaultdict(dict)
for k, o in enumerate(OPTS):
    wd = {}
    for s in strata:
        lw = store[s]["ll"][k].astype(np.float64)
        w = store[s]["w"] * np.exp(np.where(np.isfinite(lw), lw, -np.inf))
        tot = w.sum()
        per_stratum[o][s] = (ess(w), tot)
        wd[s] = (w / tot / len(strata)) if tot > 0 else w
    row(o.replace("loglik:", ""), wd)

hdr = ["option", "ess_all", "mass_p90", "ess_p90", "mass_p99", "ess_p99", "med_peak_W", "med_tau90_s"]
print("\n" + " | ".join(h.ljust(22 if h == "option" else 11) for h in hdr))
for r in rows:
    print(" | ".join(
        (r["option"].ljust(22) if h == "option" else
         (f"{r[h]:11.0f}" if h.startswith("ess") else
          (f"{r[h]:11.4f}" if h.startswith("mass") else f"{r[h]:11.3e}")))
        for h in hdr))
print("\nper-stratum ESS (all impacts):")
for o in OPTS:
    print(o.replace("loglik:", "").ljust(22), " ".join(f"{s.replace('next-i-','')}={per_stratum[o][s][0]:.0f}" for s in strata))
json.dump({"thresholds_W": thr, "rows": rows,
           "per_stratum_ess": {o: {s: per_stratum[o][s][0] for s in strata} for o in OPTS}},
          open(f"{R}/loud_tail_ess.json", "w"), indent=1)
EOF
cd /Users/pete/Downloads/mh370-exchange/end-of-flight/run-i && time python3 loud_tail_ess.py