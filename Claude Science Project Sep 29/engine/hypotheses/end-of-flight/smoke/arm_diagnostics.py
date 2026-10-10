"""Diagnostics of the 22:41 arms (V1b, V2) against the 23:15 / 00:11 data (Pete's questions, 10 Oct 2026).

For each arm (seeds pooled, equal weight per seed) and each option x log-on cause:
- selectivity: effective parents / impacts, ln Z;
- survival by the state at 00:11 (cruise, descending, steep, level after onset, down before 00:11), and by onset
  window, as prior share, posterior share and the selection factor posterior/prior;
- V2's evidence decomposed by onset mechanism, Z_k = E[L | mechanism k], and the identity
  Z(V2) = sum_k pi_k Z_k (pi_k the mechanism prior), so ln BF(V2:V1b) is read as a mixture of component ratios;
- V2 anticipatory evidence by lead bin.

Usage (from engine/): python arm_diagnostics.py OUT.json runs/eof-2241-tr-v1-s1 runs/eof-2241-tr-v1-s2 -- runs/eof-2241-tr-v2-s1 runs/eof-2241-tr-v2-s2
"""
import json, pathlib, sys
import numpy as np
from scipy.special import logsumexp

from displacement_hist import option_posteriors

OPTS = ["none__other", "m2315-bfo__other", "m0011-bto__other", "m0011-bfo__other", "m0011__other", "m0011__fuel-exhaustion",
        "r600_no-offset__other", "r600_no-offset__fuel-exhaustion", "m0011+r600_no-offset__other"]


def seed_dirs(run):
    return sorted((run / "bto-bfo").glob("seed-*"))


def load(run, sd):
    m = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(m["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r"); g = lambda k: np.array(X[:, cols[k]], float)
    ep = {e["id"]: e["logged_unix_s"] for e in m["terminal"]["epochs"]}
    return m, g, ep


def categories(g, ep):
    t11 = ep["m0011"]; on = g("latent:onset_unix_s"); imp = g("unix_s"); vz = g("latent:state_m0011_vertical_speed_fpm")
    c = {}
    c["down before 00:11"] = imp < t11
    c["cruise at 00:11 (onset later)"] = on > t11
    flown = np.isfinite(vz) & ~c["down before 00:11"]
    c["descending at 00:11 (< -300 ft/min)"] = flown & (vz < -300)
    c["steep at 00:11 (< -3,000 ft/min)"] = flown & (vz < -3000)
    c["level or climbing after onset at 00:11"] = flown & (vz >= -300)
    c["onset before 23:15"] = on < ep["m2315"]
    c["onset 23:15-00:11"] = (on >= ep["m2315"]) & (on <= t11)
    return c


def main():
    out = pathlib.Path(sys.argv[1]); args = sys.argv[2:]; k = args.index("--")
    arms = {"V1b": [pathlib.Path(a) for a in args[:k]], "V2": [pathlib.Path(a) for a in args[k + 1:]]}
    res = {}
    for arm, runs in arms.items():
        per = {}
        for run in runs:
            for sd in seed_dirs(run):
                m, g, ep = load(run, sd)
                w0 = g("weight"); w0 = w0 / w0.sum(); cats = categories(g, ep); mech = g("latent:onset_mechanism"); lead = g("latent:predicted_endurance_at_onset_s")
                par = g("parent").astype(np.int64)
                for key, p, c in option_posteriors(run, sd):
                    if key not in OPTS:
                        continue
                    # ln Z and the per-mechanism components, recomputed from the loglik column (option_posteriors normalises)
                    row = per.setdefault(key, {"seeds": []})
                    o, cause = key.split("__")
                    col = "loglik:" + o.replace("_", "/", 1)  # option_posteriors joins option and BFO model with '_'; option ids have none
                    ll = g(col); ll = np.where(np.isfinite(ll), ll, -np.inf)
                    if cause == "fuel-exhaustion":
                        from scipy.special import gammaln
                        lg = m["config"]["hypotheses"]["end-of-flight"]["logon"]; lag = lg["logon_unix_s"] - g("latent:realised_flameout_unix_s")
                        with np.errstate(divide="ignore", invalid="ignore"):
                            lfe = (lg["lag_shape"] - 1) * np.log(lag) - lag / lg["lag_scale_s"] - lg["lag_shape"] * np.log(lg["lag_scale_s"]) - gammaln(lg["lag_shape"])
                        ll = ll + np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
                    a = np.log(w0) + ll; lz = float(logsumexp(a)); q = np.exp(a - lz)
                    P = np.bincount(np.unique(par, return_inverse=True)[1], weights=q)
                    s = {"ln_evidence": lz, "effective_impacts": float(1 / np.sum(q ** 2)), "effective_parents": float(1 / np.sum(P ** 2)),
                         "categories": {n: {"prior": float(w0[mk].sum()), "posterior": float(q[mk].sum())} for n, mk in cats.items()}}
                    if arm == "V2":
                        comp = {}
                        for name, code in (("anticipatory", 0), ("fuel_cue", 1), ("flameout_assoc", 2)):
                            mk = mech == code
                            if w0[mk].sum() > 0:
                                comp[name] = {"prior_share": float(w0[mk].sum()), "ln_Z_component": float(logsumexp(a[mk]) - np.log(w0[mk].sum()))}
                        s["components"] = comp
                        bins = [0, 600, 1200, 2400, 3600, 5760]
                        s["anticipatory_by_lead_s"] = []
                        for lo, hi in zip(bins[:-1], bins[1:]):
                            mk = (mech == 0) & (lead >= lo) & (lead < hi)
                            if w0[mk].sum() > 0:
                                s["anticipatory_by_lead_s"].append({"lead_s": [lo, hi], "prior_share": float(w0[mk].sum()), "ln_Z_bin": float(logsumexp(a[mk]) - np.log(w0[mk].sum()))})
                    row["seeds"].append(s)
        res[arm] = per
    json.dump(res, open(out, "w"), indent=1)
    print("wrote", out)


if __name__ == "__main__":
    main()
