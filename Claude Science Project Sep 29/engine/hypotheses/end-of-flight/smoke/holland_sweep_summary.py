"""H1/H2 full-sweep summary (architecture 20:55Z 11 Oct readout) from the compact seed files of `full/sweep_holland.sh`.
Per 00:19 option, PRIMARY = with the survival factor (1 - latent:inflight_p_breakup_to_m0019b, adopted as part of the 00:19 data
model) and SENSITIVITY = without it, constraint `unpowered`: ln Z per stratum and for the core-weighted stratum mixture, effective
impacts (overall, per family A1 / A2 / B), family shares, P(in-flight breakup), share with contact speed <= 212 m/s, latitude
q05/q50/q95, B posterior by onset window, and H1:H2 ln BF as a function of the declared log-on window W.
Combination: row mass = P_s / K_s x w_i L_i / sum_k w (seed k of stratum s; K_s seeds; P_s core's P(family) for the stratum), so
seeds of a stratum are pooled by their evidence and strata by core's weight x end-of-flight evidence. Everything is additive.
Usage: python holland_sweep_summary.py OUT_ROOT OUT_JSON stratum=P [stratum=P ...]
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp, gammaln
from compact_impacts import load, family_labels
from displacement_hist import derived_logliks, constraint_log_factor
from smoke_compare import CORE

T29 = 1394237969.416; T2315 = 1394236800 - 2700; T0011 = 1394237459.0
LAT = np.linspace(-45.0, -20.0, 2501); FAMS = ((1, "A1"), (2, "A2"), (3, "B"))
WIN = (("before 23:15", -np.inf, T2315), ("23:15-00:11", T2315, T0011), ("after 00:11", T0011, np.inf))


def seed_terms(sd):
    meta, g = load(sd)
    h = meta["config"]["hypotheses"]["end-of-flight"]; logon = h["logon"]
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    pb_all = np.clip(g("latent:inflight_p_breakup"), 0, 1); pb19 = np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0, 1)
    feas = g("latent:contact_speed_feasible") == 1; lat = g("latitude_deg"); onset = g("latent:onset_unix_s")
    li = np.clip(np.searchsorted(LAT, lat), 0, len(LAT) - 1)
    out = {}
    for name, o, cause in CORE:
        base = der[o] if o in der else g("loglik:" + o)
        ll0 = np.where(np.isfinite(base), base, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0) + constraint_log_factor(g, logon, cause, "unpowered")
        for ver, extra in (("primary", np.log1p(-pb19)), ("without survival factor", 0.0)):
            with np.errstate(divide="ignore"):
                a = lw + ll0 + extra
            m = np.exp(a - a.max()); s = float(a.max())
            def two(mask):   # log sum and log sum of squares of the masked mass
                x = m[mask]
                return [float(np.log(x.sum()) + s) if x.sum() > 0 else -np.inf, float(np.log((x * x).sum()) + 2 * s) if x.sum() > 0 else -np.inf]
            t = {"all": two(np.ones(len(m), bool)), "fam": {n: two(f4 == c) for c, n in FAMS},
                 "B_window": {k: two((f4 == 3) & (onset >= lo) & (onset < hi)) for k, lo, hi in WIN},
                 "breakup": float(np.log((m * pb_all).sum()) + s) if (m * pb_all).sum() > 0 else -np.inf,
                 "feasible": two(feas)[0],
                 "lat_hist_log_scale": s, "lat_hist": np.bincount(li, weights=m, minlength=len(LAT)).tolist()}
            out[(name, ver)] = t
    return out


def main(root, outp, strata):
    root = pathlib.Path(root); acc = {}; per = {}
    for st, P in strata.items():
        seeds = sorted(p for p in (root / st).glob("seed-*") if p.is_dir())
        K = len(seeds)
        for sd in seeds:
            terms = seed_terms(sd); c = np.log(P / K)
            for key, t in terms.items():
                per.setdefault(f"{st}|{key[0]}|{key[1]}", []).append(t["all"][0])
                A = acc.setdefault(key, {"all": [], "all2": [], "fam": {}, "fam2": {}, "win": {}, "br": [], "fe": [], "hist": np.zeros(len(LAT))})
                A["all"].append(c + t["all"][0]); A["all2"].append(2 * c + t["all"][1])
                for n, v in t["fam"].items():
                    A["fam"].setdefault(n, []).append(c + v[0]); A["fam2"].setdefault(n, []).append(2 * c + v[1])
                for n, v in t["B_window"].items():
                    A["win"].setdefault(n, []).append(c + v[0])
                A["br"].append(c + t["breakup"]); A["fe"].append(c + t["feasible"])
                A["hist"] += np.asarray(t["lat_hist"]) * np.exp(c + t["lat_hist_log_scale"] - 0.0)
            print(f"  {st} {sd.name} done", flush=True)
    res = {"strata_weights": strata, "per_stratum_seed_lnZ": per, "options": {}}
    for (name, ver), A in acc.items():
        lz = float(logsumexp(A["all"])); ess = float(np.exp(2 * lz - logsumexp(A["all2"])))
        fam = {}
        for n in A["fam"]:
            l1 = logsumexp(A["fam"][n]); l2 = logsumexp(A["fam2"][n])
            fam[n] = {"share": float(np.exp(l1 - lz)), "eff_impacts": float(np.exp(2 * l1 - l2)) if np.isfinite(l2) else 0.0}
        hcum = np.cumsum(A["hist"]); hcum /= hcum[-1]
        q = {str(k): float(LAT[np.searchsorted(hcum, k)]) for k in (0.05, 0.5, 0.95)}
        res["options"].setdefault(name, {})[ver] = {"ln_Z_mixture": lz, "eff_impacts": ess, "families": fam,
            "B_onset_window_share_of_B": {n: float(np.exp(logsumexp(v) - logsumexp(A["fam"]["B"]))) for n, v in A["win"].items()},
            "P_inflight_breakup": float(np.exp(logsumexp(A["br"]) - lz)), "share_contact_le_212": float(np.exp(logsumexp(A["fe"]) - lz)),
            "latitude_q05_q50_q95": q}
    for ver in ("primary", "without survival factor"):
        a = res["options"]["00:19 Holland H1"][ver]["ln_Z_mixture"]; b = res["options"]["00:19 Holland H2"][ver]["ln_Z_mixture"]
        res.setdefault("H1_vs_H2", {})[ver] = {"ln_BF_at_W_s": {str(W): a - b + float(np.log(W)) for W in (60, 300, 900, 1775, 3600)}, "break_even_W_s": float(np.exp(b - a))}
    json.dump(res, open(outp, "w"), indent=1)
    for name, v in res["options"].items():
        for ver, r in v.items():
            fam = " ".join(f"{n}:{d['share']:.2f}/{d['eff_impacts']:.0f}" for n, d in r["families"].items())
            print(f"{name:26s} {ver:24s} lnZ {r['ln_Z_mixture']:8.3f} ESS {r['eff_impacts']:10.0f} | {fam} | breakup {r['P_inflight_breakup']:.3f} <=212 {r['share_contact_le_212']:.3f} | lat {r['latitude_q05_q50_q95']}")
    print(json.dumps(res["H1_vs_H2"]))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], {a.split("=")[0]: float(a.split("=")[1]) for a in sys.argv[3:]})
