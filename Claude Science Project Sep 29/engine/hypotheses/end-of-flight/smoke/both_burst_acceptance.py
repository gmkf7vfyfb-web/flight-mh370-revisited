"""Both-burst fix (core's 22:59Z 15 Oct note): acceptance (a)-(d) for an aimed arm against the unaimed arm on the same hand-offs.
(a) effective parents and effective impacts per 00:19 option; (b) prior recovery under the sampling weight alone (family shares,
max weighted-CDF deviation of aimed and outcome latents, total weight ratio); (c) ln Z per option; (d) split-half test on the
parent level: G_A over the first half of each parent's descents (the first half of its children), G_B over the other half; ceiling = (sum G)^2 / (4 sum
G_A G_B), corr(G_A, G_B). Rows per parent are contiguous and child-major (checked: equal count per parent).
Usage: python both_burst_acceptance.py OUT_JSON base=SEED_DIR aimed=SEED_DIR [label=SEED_DIR ...]"""
import sys, json
import numpy as np
from compact_impacts import load

OPTS = ["none", "r600/no-offset", "both/no-offset", "both/startup-offset", "both/inflated"]
LAT = ["latitude_deg", "unix_s", "latent:onset_unix_s", "latent:pushover_rate_fpm", "latent:pushover_hold_s", "latent:max_descent_rate_fpm",
       "flight_path_angle_deg"]


def wcdf_maxdev(x0, w0, x1, w1):
    m0, m1 = np.isfinite(x0) & (w0 > 0), np.isfinite(x1) & (w1 > 0)
    if m0.sum() < 10 or m1.sum() < 10: return None
    grid = np.quantile(x0[m0], np.linspace(0.01, 0.99, 99))
    def cdf(x, w): o = np.argsort(x); c = np.cumsum(w[o]); c /= c[-1]; return np.interp(grid, x[o], c)
    return float(np.max(np.abs(cdf(x0[m0], w0[m0]) - cdf(x1[m1], w1[m1]))))


def arm(sd):
    m, g = load(sd); w = g("weight"); par = g("parent").astype(np.int64)
    n = len(w); assert np.all(np.diff(par) >= 0)
    rpp = n // len(np.unique(par)); assert n % rpp == 0 and rpp % 2 == 0, rpp
    out = {"rows": n, "rows_per_parent": int(rpp), "weight_sum": float(w.sum()), "opts": {}}
    for o in OPTS:
        ll = np.zeros(n) if o == "none" else g("loglik:" + o)
        ll = np.where(np.isfinite(ll), ll, -np.inf); s = np.max(ll[np.isfinite(ll)])
        L = w * np.exp(ll - s); G = L.reshape(-1, rpp); Gt = G.sum(1); GA = G[:, :rpp // 2].sum(1); GB = G[:, rpp // 2:].sum(1)
        cross = float(np.sum(GA * GB))
        out["opts"][o] = {"ln_Z_rel": float(np.log(L.sum()) + s - np.log(w.sum())),
                          "eff_impacts": float(L.sum() ** 2 / np.square(L).sum()),
                          "eff_parents": float(Gt.sum() ** 2 / np.square(Gt).sum()),
                          "eff_parents_half_A": float(GA.sum() ** 2 / np.square(GA).sum()), "eff_parents_half_B": float(GB.sum() ** 2 / np.square(GB).sum()),
                          "ceiling_parent_ess": float(Gt.sum() ** 2 / (4 * cross)) if cross > 0 else None,
                          "corr_halves": float(np.corrcoef(GA, GB)[0, 1])}
    fam = g("family4_code") if "family4_code" in m["impact_columns"] else None
    return out, w, {c: g(c) for c in LAT}, fam


def main(outp, arms):
    res, raw = {}, {}
    for lab, sd in arms.items():
        res[lab], w, lat, fam = arm(sd); raw[lab] = (w, lat, fam)
        for o, v in res[lab]["opts"].items():
            print(f"{lab:6s} {o:20s} lnZ {v['ln_Z_rel']:9.3f} eff impacts {v['eff_impacts']:10,.0f} eff parents {v['eff_parents']:10,.0f} "
                  f"(halves {v['eff_parents_half_A']:,.0f} / {v['eff_parents_half_B']:,.0f}) ceiling {v['ceiling_parent_ess'] or float('nan'):10,.0f} corr {v['corr_halves']:+.3f}", flush=True)
    w0, l0, f0 = raw["base"]
    for lab in arms:
        if lab == "base": continue
        w1, l1, f1 = raw[lab]
        t6 = {"weight_ratio_aimed_over_base": float(w1.sum() / w0.sum()),
              "max_cdf_dev": {c: wcdf_maxdev(l0[c], w0, l1[c], w1) for c in LAT}}
        if f0 is not None and f1 is not None:
            t6["family_shares_base"] = {str(int(k)): float(w0[f0 == k].sum() / w0.sum()) for k in np.unique(f0[np.isfinite(f0)])}
            t6["family_shares_aimed"] = {str(int(k)): float(w1[f1 == k].sum() / w1.sum()) for k in np.unique(f1[np.isfinite(f1)])}
        res[lab]["test6_vs_base"] = t6
        print(f"test 6 ({lab} vs base, sampling weight alone): weight ratio {t6['weight_ratio_aimed_over_base']:.4f}; max CDF dev",
              {k: (round(v, 4) if v is not None else None) for k, v in t6["max_cdf_dev"].items()})
        if "family_shares_base" in t6: print("   families base", {k: round(v, 4) for k, v in t6["family_shares_base"].items()}, "aimed", {k: round(v, 4) for k, v in t6["family_shares_aimed"].items()})
    json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], {a.split("=", 1)[0]: a.split("=", 1)[1] for a in sys.argv[2:]})
