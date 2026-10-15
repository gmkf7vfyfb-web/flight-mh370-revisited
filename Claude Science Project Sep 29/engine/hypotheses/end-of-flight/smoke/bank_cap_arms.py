"""Order (b) item 3: bank-limit arms on the feasible set (D0' = airborne at 00:19:37.443 x survival factor).
For each arm directory (STRATUM/seed-k compact + tau90_v1.npz): flight-path-angle bands, energy quantiles, effective impacts,
and for an arm with latent:spiral_bank_cap_deg sampled, the same by bank-limit bin and under exact re-weighting of the tail weight.
Usage: python bank_cap_arms.py OUT_JSON label=ARM_STRATUM_DIR [label=ARM_STRATUM_DIR ...]"""
import sys, json, glob, pathlib
import numpy as np
from compact_impacts import load
from displacement_hist import T_M0019B

CORE, TAIL_TO, T_SMOKE = (52.0, 63.0), 90.0, 0.2


def wq(v, w, qs):
    o = np.argsort(v, kind="stable"); c = np.cumsum(w[o]); c /= c[-1]
    return [float(v[o][min(int(np.searchsorted(c, q)), len(c) - 1)]) for q in qs]


def stats(w, fpa, en, extra=None):
    t = w.sum()
    d = {"band_lt10": float(w[fpa < 10].sum() / t), "band_10_45": float(w[(fpa >= 10) & (fpa <= 45)].sum() / t),
         "band_gt45": float(w[fpa > 45].sum() / t), "energy_GJ_q05_q50_q95": [x / 1e9 for x in wq(en, w, [0.05, 0.5, 0.95])],
         "fpa_q50_q95": wq(fpa, w, [0.5, 0.95]), "eff_impacts": float(t * t / np.square(w).sum()), "mass": float(t)}
    if extra: d.update(extra)
    return d


def arm(stratum_dir):
    W, F, E, C, SP = [], [], [], [], []
    seeds = sorted(p for p in pathlib.Path(stratum_dir).glob("seed-*") if p.is_dir())
    for sd in seeds:
        m, g = load(sd); w = g("weight"); w = w / w.sum() / len(seeds)
        alive = g("unix_s") > T_M0019B
        surv = 1.0 - np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1)
        z = np.load(sd / "tau90_v1.npz")
        W.append(w * alive * surv); F.append(g("flight_path_angle_deg")); E.append(z["energy_transferred_j"])
        cols = m["impact_columns"]
        C.append(g("latent:spiral_bank_cap_deg") if "latent:spiral_bank_cap_deg" in cols else np.full(len(w), np.nan))
        SP.append(g("latent:spiral_divergent"))
    return [np.concatenate(x) for x in (W, F, E, C, SP)]


def main(outp, arms):
    res = {}
    for lab, d in arms.items():
        w, fpa, en, cap, sp = arm(d)
        r = {"all": stats(w, fpa, en, {"spiral_divergent_share": float(w[sp == 1].sum() / w.sum())})}
        if np.isfinite(cap).any() and np.nanmax(cap) - np.nanmin(cap) > 1e-6:   # sampled, not a fixed cap
            bins = [52, 56, 60, 63, 70, 80, 90.0001]
            r["by_cap_bin"] = {f"{bins[i]:.0f}-{bins[i + 1]:.0f}": stats(w * ((cap >= bins[i]) & (cap < bins[i + 1])), fpa, en)
                               for i in range(len(bins) - 1)}
            core = cap <= CORE[1]
            r["tail_weight_reweighted"] = {}
            for t in (0.0, 0.1, 0.2, 0.35, 0.5):
                f = np.where(core, (1 - t) / (1 - T_SMOKE), t / T_SMOKE)
                r["tail_weight_reweighted"][f"{t:.2f}"] = stats(w * f, fpa, en)
        res[lab] = r
        a = r["all"]
        print(f"{lab:6s} <10 {a['band_lt10']:.4f} 10-45 {a['band_10_45']:.4f} >45 {a['band_gt45']:.4f} E50 {a['energy_GJ_q05_q50_q95'][1]:.2f} "
              f"spiral {a['spiral_divergent_share']:.3f} ESS {a['eff_impacts']:,.0f}", flush=True)
        for k, v in r.get("tail_weight_reweighted", {}).items():
            print(f"    tail weight {k}: 10-45 {v['band_10_45']:.4f} >45 {v['band_gt45']:.4f} ESS {v['eff_impacts']:,.0f}")
    json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], {a.split("=", 1)[0]: a.split("=", 1)[1] for a in sys.argv[2:]})
