"""Order (b): impact-condition shares on the feasible set (airborne at 00:19:37.443 x survival factor) from the weight-proportional
per-stratum subsamples written by round3_subsample.py, strata mixed at the core family prior. 00:19 values held out (D0').
Usage: python subsample_feasible.py OUT_JSON label=SUBSAMPLE_DIR [...]   (SUBSAMPLE_DIR holds subsample-<stratum>.npz)"""
import sys, json, os
import numpy as np
STRATA = {"next-i-waypoints": 0.9982, "next-i-free": 0.0011, "next-i-repro-radar": 0.0004, "next-i-descent-climb": 0.0002}
T0, T19 = 1394236800.0, 1394237977.443


def wq(v, w, qs):
    o = np.argsort(v); c = np.cumsum(w[o]); c /= c[-1]
    return [float(v[o][min(int(np.searchsorted(c, q)), len(c) - 1)]) for q in qs]


def main(outp, arms):
    res = {}
    for lab, d in arms.items():
        W, F, E, T, C = [], [], [], [], []
        for st, P in STRATA.items():
            z = np.load(os.path.join(d, f"subsample-{st}.npz"), allow_pickle=True); R = z["rows"]; ix = {c: i for i, c in enumerate(z["columns"])}
            t = R[:, ix["t_impact_s"]].astype(np.float64)
            t = t + T0 if np.nanmedian(t) < 1e6 else t          # compact offsets or unix seconds
            w = np.full(len(R), P / len(R)) * (t > T19) * (1 - np.clip(R[:, ix["latent:inflight_p_breakup_to_m0019b"]], 0, 1))
            W.append(w); F.append(R[:, ix["flight_path_angle_deg"]]); E.append(R[:, ix["energy_transferred_j"]]); T.append(R[:, ix["tau90_s"]])
            C.append(R[:, ix["latent:spiral_bank_cap_deg"]] if "latent:spiral_bank_cap_deg" in ix else np.full(len(R), np.nan))
        w, f, e, ta = (np.concatenate(x) for x in (W, F, E, T)); s = w.sum()
        res[lab] = dict(band_lt10=float(w[f < 10].sum() / s), band_10_45=float(w[(f >= 10) & (f <= 45)].sum() / s), band_gt45=float(w[f > 45].sum() / s),
                        fpa_q05_q50_q95=wq(f, w, [.05, .5, .95]), energy_GJ_q05_q50_q95=[x / 1e9 for x in wq(e, w, [.05, .5, .95])],
                        tau90_s_q05_q50_q95=wq(ta, w, [.05, .5, .95]), eff_impacts=float(s * s / np.square(w).sum()))
        r = res[lab]; print(f"{lab:28s} <10 {r['band_lt10']:.4f} 10-45 {r['band_10_45']:.4f} >45 {r['band_gt45']:.4f} E50 {r['energy_GJ_q05_q50_q95'][1]:.2f} tau50 {r['tau90_s_q05_q50_q95'][1]:.2f} ESS {r['eff_impacts']:,.0f}")
    json.dump(res, open(outp, "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], {a.split("=", 1)[0]: a.split("=", 1)[1] for a in sys.argv[2:]})
