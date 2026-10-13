"""Run C: per-stratum split-half (8 seeds, floor 0.924), tank diagnostics (tanks32), and (b)/(a)/C comparison.
usage: python runc_analysis.py RUNC_DIR   (after report/early_families.py has written RUNC_DIR/report/early-families-summary.csv)"""
import sys, json, os
from itertools import combinations
import numpy as np, pandas as pd
from scipy.ndimage import gaussian_filter1d
WS = "/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/386151e9-859f-412a-8d9d-b8da48899575"
C = sys.argv[1]; NB, NA = f"{WS}/out/next-run-b", f"{WS}/out/next-run-a"
T0 = 1394236800.0; T0011 = 1394237459.0; STEP = 0.05; edges = np.arange(-45, -20 + STEP / 2, STEP)
FLOOR = {4: 0.896, 6: 0.914, 8: 0.924}
def wq(x, w, q):
    o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]; return float(np.interp(q, c, x[o]))
def seeds_of(d): return sorted(int(s.split("-")[1]) for s in os.listdir(f"{d}/bto-bfo") if s.startswith("seed-"))
def seed_dens(d):
    out = []
    for sd in seeds_of(d):
        a = np.load(f"{d}/bto-bfo/seed-{sd}/final.npy", mmap_mode="r")
        h, _ = np.histogram(np.asarray(a[:, 1]), bins=edges, weights=np.asarray(a[:, 0], float))
        out.append(gaussian_filter1d(h / h.sum() / STEP, 0.1 / STEP))
    return out
def split_half(ds):
    n = len(ds); ov = []
    for half in combinations(range(n), n // 2):
        other = [i for i in range(n) if i not in half]
        ov.append(float(np.minimum(np.mean([ds[i] for i in half], 0), np.mean([ds[i] for i in other], 0)).sum() * STEP))
    return float(np.mean(ov)), float(np.min(ov)), float(np.max(ov))
def tankdiag(d):
    W_, FT, SE, SEA = [], [], [], []
    for sd in seeds_of(d):
        a = np.load(f"{d}/bto-bfo/seed-{sd}/final.npy", mmap_mode="r"); w = np.asarray(a[:, 0], float); W_.append(w / w.sum())
        p32 = f"{d}/bto-bfo/seed-{sd}/tanks32.npy"
        if os.path.exists(p32):
            tk = np.load(p32, mmap_mode="r"); ft = np.asarray(tk[:, 5], float) + T0
        else:
            tk = np.load(f"{d}/bto-bfo/seed-{sd}/tanks.npy", mmap_mode="r"); ft = np.asarray(tk[:, 5], float)
        FT.append(ft); SE.append(np.asarray(tk[:, 6], float)); SEA.append(np.asarray(tk[:, 7], float))
    w = np.concatenate(W_); ft = np.concatenate(FT); se = np.concatenate(SE); sea = np.concatenate(SEA); pos = se > 0
    return dict(P_first_tank_dry_before_0011=float(w[ft < T0011].sum() / w.sum()),
                med_one_engine_min=wq(se[pos], w[pos], .5) / 60 if pos.any() else float("nan"),
                frac_one_engine_above_ceiling=float((w[pos] * sea[pos]).sum() / (w[pos] * se[pos]).sum()) if pos.any() else float("nan"))
rows = []
STRATA = [("repro-radar", "Davey dynamics + radar", "next-repro-radar", "next-a-repro-radar", "next-c-repro-radar"),
          ("free", "free", "next-free", "next-a-free", "next-c-free"),
          ("routes", "routes", "next-routes", "next-a-routes", "next-c-routes"),
          ("descent-climb", "descent-climb", "next-descent-climb", "next-a-descent-climb", "next-c-descent-climb")]
summ = {tag: pd.read_csv(f"{d}/report/early-families-summary.csv") for tag, d in (("(b)", NB), ("(a)", NA), ("C", C))}
for key, lab, bn, an, cn in STRATA:
    for tag, d, nm in (("(b)", NB, bn), ("(a)", NA, an), ("C", C, cn)):
        if not os.path.exists(f"{d}/{nm}/run.json"): continue
        s = summ[tag]; r = s[s.arm == nm].iloc[0]; ds = seed_dens(f"{d}/{nm}"); m, lo, hi = split_half(ds); n = len(ds)
        rows.append(dict(stratum=lab, run=tag, seeds=n, P_family=r.P_family_equal_prior, log_mean_Z=r.log_mean_Z,
                         lat0019_p50=r.lat0019_p50, lat0019_p05=r.lat0019_p05, lat0019_p95=r.lat0019_p95, lat0011_p50=r.lat0011_p50,
                         split_half_mean=m, split_half_min=lo, split_half_max=hi, floor=FLOOR.get(n), converged=m >= FLOOR.get(n, 0.9), **tankdiag(f"{d}/{nm}")))
T = pd.DataFrame(rows); os.makedirs(f"{C}/report", exist_ok=True)
T.to_csv(f"{C}/report/c-vs-a-vs-b-strata.csv", index=False, float_format="%.4f"); print(T.round(3).to_string())
