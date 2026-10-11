"""ESS per 00:19 option and per family for the "make Holland H1/H2 estimable" recipe (architecture 10:50 -0600 11 Oct), constraint
`unpowered` (the reference), weights as written (with `terminal.within_parent = "unnormalised"` they already carry every proposal
correction). For each option: ln Z, effective impacts / parents, per family (A1, A2, B) share and effective impacts, posterior share in
push-over rows and in interim pitch-down rows, ln Z as a function of the prior pitch-down probability q (exact re-weighting from p0),
and H1:H2 as a function of the declared log-on window W ("other" has no log-on-time density: its likelihood is 1/W over W).
SMOKE TOOL. Usage: python holland_ess.py OUT_JSON RUN [RUN ...]   (RUN = full layout, seed directories found under RUN/bto-bfo)
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp, gammaln
from displacement_hist import derived_logliks, constraint_log_factor
from compact_impacts import family_labels
from smoke_compare import CORE, QS

FAM = ((1, "A1"), (2, "A2"), (3, "B"))


def ess(p):
    s = p.sum()
    return float(s * s / (p * p).sum()) if s > 0 else 0.0


def one(run, seed_dir):
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(seed_dir / "impacts.npy", mmap_mode="r"); g = lambda k: np.asarray(X[:, cols[k]], float)
    h = meta["config"]["hypotheses"]["end-of-flight"]; logon = h["logon"]; env = h["envelope"]
    w = g("weight"); lw = np.log(w) - np.log(w.sum()); par = g("parent").astype(np.int64); lat = g("latitude_deg")
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    po = g("latent:pushover_drawn") == 1 if "latent:pushover_drawn" in cols else np.zeros(len(w), bool)
    pde = g("latent:pitchdown_eligible") == 1 if "latent:pitchdown_eligible" in cols else np.zeros(len(w), bool)
    pd = g("latent:pitchdown_drawn") == 1 if "latent:pitchdown_drawn" in cols else np.zeros(len(w), bool)
    p0 = float(env.get("pitchdown_probability", 0.0))
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    der = derived_logliks(meta, g, present)
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    out = {"rows": int(len(w)), "within_parent": meta["config"].get("terminal", {}).get("within_parent", "self-normalised"),
           "burst_target_weight": env.get("burst_target_weight") if env.get("burst_target_unix_s") else 0.0,
           "prior": {"push-over": float(np.exp(lw)[po].sum()), "pitch-down": float(np.exp(lw)[pd].sum())}, "options": {}}
    for name, o, cause in CORE:
        base = der[o] if o in der else g("loglik:" + o)
        ll = np.where(np.isfinite(base), base, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0) + constraint_log_factor(g, logon, cause, "unpowered")
        lz = float(logsumexp(lw + ll)); p = np.exp(lw + ll - lz)
        r = {"ln_Z": lz, "eff_impacts": ess(p), "eff_parents": ess(np.bincount(par, weights=p)),
             "median_lat": float(lat[np.argsort(lat)][np.searchsorted(np.cumsum(p[np.argsort(lat)]), 0.5)]),
             "share_push_over": float(p[po].sum()), "eff_impacts_push_over": ess(p * po),
             "share_pitch_down": float(p[pd].sum()), "eff_impacts_pitch_down": ess(p * pd),
             "families": {n: {"share": float(p[f4 == c].sum()), "eff_impacts": ess(p * (f4 == c)), "eff_parents": ess(np.bincount(par, weights=p * (f4 == c)))} for c, n in FAM}}
        if "latent:inflight_p_breakup_to_m0019b" in cols:
            # G13: a breakup before 00:19:37 contradicts the log-on; the proposed `alive` factor is (1 - P(breakup before)).
            pb = np.clip(g("latent:inflight_p_breakup_to_m0019b"), 0.0, 1.0)
            r["posterior_P_breakup_before_m0019b"] = float((p * pb).sum())
            with np.errstate(divide="ignore"):
                ls = lw + ll + np.log1p(-pb)
            lzs = float(logsumexp(ls)); ps = np.exp(ls - lzs)
            r["with_survival_factor"] = {"ln_Z": lzs, "eff_impacts": ess(ps), "median_lat": float(lat[np.argsort(lat)][np.searchsorted(np.cumsum(ps[np.argsort(lat)]), 0.5)]),
                                         "families": {n: float(ps[f4 == c].sum()) for c, n in FAM}}
        if 0 < p0 < 1:
            r["ln_Z_of_q_pitch_down"] = {}
            for q in QS:
                f = np.where(pd, q / p0, np.where(pde, (1 - q) / (1 - p0), 1.0))
                with np.errstate(divide="ignore"):
                    r["ln_Z_of_q_pitch_down"][str(q)] = float(logsumexp(lw + ll + np.log(f)))
        out["options"][name] = r
    a, b = out["options"]["00:19 Holland H1"]["ln_Z"], out["options"]["00:19 Holland H2"]["ln_Z"]
    out["H1_vs_H2"] = {"ln_BF_at_W_s": {str(W): a - b + float(np.log(W)) for W in (60, 300, 900, 1775, 3600)}, "break_even_W_s": float(np.exp(b - a))}
    return out


if __name__ == "__main__":
    res = {}
    for r in sys.argv[2:]:
        run = pathlib.Path(r)
        for sd in sorted((run / "bto-bfo").glob("seed-*")):
            res[f"{r}/{sd.name}"] = one(run, sd)
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    for k, v in res.items():
        print(k, v["within_parent"], "target w", v["burst_target_weight"], "prior PO %.4f PD %.4f" % (v["prior"]["push-over"], v["prior"]["pitch-down"]))
        for n, o in v["options"].items():
            fam = " ".join(f"{f}:{d['share']:.2f}/{d['eff_impacts']:.0f}" for f, d in o["families"].items())
            print(f"  {n:26s} lnZ {o['ln_Z']:8.2f} ESSimp {o['eff_impacts']:9.1f} ESSpar {o['eff_parents']:8.1f} PO {o['share_push_over']:.2f}/{o['eff_impacts_push_over']:.0f} PD {o['share_pitch_down']:.2f}/{o['eff_impacts_pitch_down']:.0f} lat {o['median_lat']:.2f} | {fam}")
        for n, o in v["options"].items():
            if "with_survival_factor" in o:
                w_ = o["with_survival_factor"]
                print(f"  survival factor  {n:26s} P(breakup before 00:19:37) {o['posterior_P_breakup_before_m0019b']:.3f} lnZ {w_['ln_Z']:8.2f} ESSimp {w_['eff_impacts']:9.1f} lat {w_['median_lat']:.2f} fam " + " ".join(f"{k}:{x:.2f}" for k, x in w_['families'].items()))
        print("  H1:H2", {k2: round(x, 2) for k2, x in v["H1_vs_H2"]["ln_BF_at_W_s"].items()}, "break-even W %.0f s" % v["H1_vs_H2"]["break_even_W_s"])
