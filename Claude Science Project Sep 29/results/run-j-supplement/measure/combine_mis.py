"""Run-J northern supplement: across-replicate multiple importance sampling at the 00:11 hand-off (core-level check).
Technique 1 = run J waypoints normal 00:11 hand-offs (24 seeds), technique 2 = supplement hand-offs (new seeds).
Each technique's standalone weights (weight x exp(log_correction), seeds pooled with equal weight) are multiplied by the
balance-heuristic partition of unity beta1 = n1/(n1 + n2 r_hat(lat)), beta2 = n2 r_hat/(n1 + n2 r_hat).
Reports, per band of 00:11 latitude: mass and Kish ESS over distinct (seed, state) for production alone and combined,
and combined-vs-production means (z from seed scatter of production).
    python combine_mis.py STAGE_DIR R_HAT_JSON OUT_JSON"""
import sys, json, pathlib, numpy as np
STAGE = pathlib.Path(sys.argv[1]); RH = json.load(open(sys.argv[2])); OUT = sys.argv[3]
X = pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo")
e = np.array(RH["edges_deg"]); rv = np.array(RH["r_hat"]); out_r = RH["outside"]
def r_hat(lat):
    b = np.searchsorted(e, lat, side="right") - 1; ok = (b >= 0) & (b < len(rv)); r = np.full(len(lat), out_r); r[ok] = rv[b[ok]]; return r
def load(paths, sub):
    rows = []
    for k, p in enumerate(paths):
        H = np.load(p / sub / "handoff.npy"); _, sid = np.unique(H[:, [1, 2, 3, 8]], axis=0, return_inverse=True)
        w = H[:, 0] * np.exp(H[:, 13]); rows.append(np.column_stack([w / len(paths), H[:, 1], H[:, 6], np.full(len(H), k), sid.ravel()]))
    return np.vstack(rows)
prod = sorted(X.glob("seed-*"), key=lambda p: int(p.name[5:])); sup = sorted((STAGE / "north").glob("seed-*"), key=lambda p: int(p.name[5:]))
A = load(prod, "handoff-m0011"); B = load(sup, "handoff-m0011-supplement"); n1, n2 = len(A), len(B)
ra, rb = r_hat(A[:, 1]), r_hat(B[:, 1])
wa = A[:, 0] * n1 / (n1 + n2 * ra); wb = B[:, 0] * n2 * rb / (n1 + n2 * rb)
BANDS = [(-40, -35), (-35, -30), (-30, -25), (-25, -20), (-20, -15)]
def ess_states(w, lat, key, lo, hi):
    b = (lat > lo) & (lat <= hi)
    if not b.any(): return 0.0, 0.0, 0
    u, inv = np.unique(key[b], return_inverse=True); s = np.bincount(inv, w[b]); return float(w[b].sum()), float(s.sum() ** 2 / (s ** 2).sum()), int((s > 0).sum())
keyA = A[:, 3] * 1e7 + A[:, 4]; keyB = 1e9 + B[:, 3] * 1e7 + B[:, 4]
res = {"n1_rows": n1, "n2_rows": n2, "seeds_production": len(prod), "seeds_supplement": len(sup), "bands_0011": {}}
for lo, hi in BANDS:
    m0, e0, d0 = ess_states(A[:, 0], A[:, 1], keyA, lo, hi)
    m1, e1, d1 = ess_states(np.r_[wa, wb], np.r_[A[:, 1], B[:, 1]], np.r_[keyA, keyB], lo, hi)
    per_mode = {}
    for md in range(5):
        sa, sb = A[:, 2] == md, B[:, 2] == md
        per_mode[md] = [ess_states(A[sa, 0], A[sa, 1], keyA[sa], lo, hi)[1], ess_states(np.r_[wa[sa], wb[sb]], np.r_[A[sa, 1], B[sb, 1]], np.r_[keyA[sa], keyB[sb]], lo, hi)[1]]
    res["bands_0011"][f"{-hi}-{-lo} S"] = {"mass_production": m0, "mass_combined": m1, "ess_states_production": e0, "ess_states_combined": e1,
                                           "distinct_states_production": d0, "distinct_states_combined": d1, "per_mode_ess_states_prod_comb": per_mode}
# combined vs production means: seed-level jackknife-free comparison (production seed scatter as the scale)
def seedmeans(R, w, f):
    return np.array([np.sum(w[R[:, 3] == k] * f(R[R[:, 3] == k])) / np.sum(w[R[:, 3] == k]) for k in np.unique(R[:, 3])])
F = {"lat": lambda R: R[:, 1], "north_33": lambda R: (R[:, 1] > -33) * 1.0, "north_30": lambda R: (R[:, 1] > -30) * 1.0, "north_25": lambda R: (R[:, 1] > -25) * 1.0}
for m in range(5): F[f"mode{m}"] = (lambda m: lambda R: (R[:, 2] == m) * 1.0)(m)
tot = wa.sum() + wb.sum(); res["weight_sum_combined"] = float(tot); res["means"] = {}
for k, f in F.items():
    comb = (np.sum(wa * f(A)) + np.sum(wb * f(B))) / tot; pm = seedmeans(A, A[:, 0], f); se = pm.std(ddof=1) / np.sqrt(len(pm))
    sm = seedmeans(B, B[:, 0], f); se2 = sm.std(ddof=1) / np.sqrt(len(sm))
    res["means"][k] = {"production": float(pm.mean()), "supplement_alone": float(sm.mean()), "combined": float(comb),
                       "z_supp_vs_prod": float((sm.mean() - pm.mean()) / np.hypot(se, se2)), "z_comb_vs_prod_seedSE": float((comb - pm.mean()) / se)}
json.dump(res, open(OUT, "w"), indent=1)
for b, v in res["bands_0011"].items():
    print(f"00:11 {b}: mass prod {v['mass_production']:.4f} comb {v['mass_combined']:.4f} | state-ESS prod {v['ess_states_production']:.0f} comb {v['ess_states_combined']:.0f} | distinct prod {v['distinct_states_production']} comb {v['distinct_states_combined']}")
for k, v in res["means"].items(): print(f"{k:9s} prod {v['production']:.5f} supp {v['supplement_alone']:.5f} comb {v['combined']:.5f} z(supp-prod) {v['z_supp_vs_prod']:+.2f} z(comb-prod) {v['z_comb_vs_prod_seedSE']:+.2f}")
print("rows", n1, n2, "weight sum", tot)
