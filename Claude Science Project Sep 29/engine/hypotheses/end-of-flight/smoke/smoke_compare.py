"""Smoke comparison of end-of-flight runs (full layout RUN/run.json + RUN/bto-bfo/seed-1/impacts.npy), constraint `unpowered`:
prior push-over tail, per 00:19 option ln Z / effective parents / median latitude / share above 212 m/s, four-family shares, and, when
the run has the item-4 push-over latents, the posterior share in push-over rows and ln Z as a function of the prior push-over
probability q (exact re-weighting from the proposal probability p0). SMOKE TOOL: N = 1 runs only identify direction and size.
Usage: python smoke_compare.py OUT_JSON RUN [RUN ...]
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp, gammaln
from displacement_hist import derived_logliks, constraint_log_factor
from compact_impacts import family_labels

CORE = [("00:19 Held Out", "none", "other"), ("00:19 R600 BTO Only", "r600-bto", "other"), ("00:19 R600 BTO + Raw BFO", "r600/no-offset", "other"),
        ("00:19 Holland H1", "both/startup-offset", "fuel-exhaustion"), ("00:19 Holland H2", "both/no-offset", "other")]
QS = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]


def run_stats(run):
    run = pathlib.Path(run); meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(run / "bto-bfo" / "seed-1" / "impacts.npy", mmap_mode="r"); g = lambda k: np.asarray(X[:, cols[k]], float)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]; env = meta["config"]["hypotheses"]["end-of-flight"]["envelope"]
    w = g("weight"); lw = np.log(w) - np.log(w.sum()); lat = g("latitude_deg"); par = g("parent").astype(np.int64)
    speed = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
    alive = g("unix_s") > 1394237977.443
    dv = g("latent:state_m0019b_vertical_speed_fpm") - g("latent:state_m0019a_vertical_speed_fpm")
    pw = np.exp(lw)
    out = {"run": str(run), "rows": int(len(w)), "prior": {"P(dv<=-10450, airborne)": float(pw[alive & (dv <= -10450)].sum()),
           "P(dv<=-8000, airborne)": float(pw[alive & (dv <= -8000)].sum()), "P(contact speed > 212 m/s)": float(pw[speed > 212].sum())}}
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    has_po = "latent:pushover_drawn" in cols
    if has_po:
        el, dr = g("latent:pushover_eligible") == 1, g("latent:pushover_drawn") == 1; p0 = float(env.get("rapid_descent_probability", 0.0))
        out["prior"].update({"P(eligible)": float(pw[el].sum()), "P(push-over drawn)": float(pw[dr].sum()), "proposal p0": p0})
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    der = derived_logliks(meta, g, present)
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    out["options"] = {}
    for name, o, cause in CORE:
        base = der[o] if o in der else g("loglik:" + o)
        ll = np.where(np.isfinite(base), base, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0) + constraint_log_factor(g, logon, cause, "unpowered")
        lz = float(logsumexp(lw + ll)); p = np.exp(lw + ll - lz); P = np.bincount(par, weights=p)
        o_ = np.argsort(lat); cw = np.cumsum(p[o_])
        r = {"ln_Z": lz, "eff_parents": float(1 / (P ** 2).sum()), "eff_impacts": float(1 / (p ** 2).sum()),
             "median_lat": float(lat[o_][np.searchsorted(cw, 0.5)]), "share_above_212": float(p[speed > 212].sum()),
             "families": {n: float(p[f4 == c].sum()) for c, n in ((1, "A1"), (2, "A2"), (3, "B"), (6, "outside B"))}}
        if has_po and 0 < p0 < 1:
            r["posterior_share_push_over"] = float(p[dr].sum())
            r["ln_Z_of_q"] = {}
            for q in QS:
                f = np.where(dr, q / p0, np.where(el, (1 - q) / (1 - p0), 1.0))
                with np.errstate(divide="ignore"):
                    r["ln_Z_of_q"][str(q)] = float(logsumexp(lw + ll + np.log(f)))
            pp = p * dr; Pp = np.bincount(par, weights=pp)
            r["eff_parents_push_over_rows"] = float(Pp.sum() ** 2 / (Pp ** 2).sum()) if Pp.sum() > 0 else 0.0
        out["options"][name] = r
    return out


if __name__ == "__main__":
    res = [run_stats(r) for r in sys.argv[2:]]
    json.dump(res, open(sys.argv[1], "w"), indent=1)
    for r in res:
        print(r["run"], {k: round(v, 5) for k, v in r["prior"].items()})
        for n, v in r["options"].items():
            extra = f" | push-over share {v['posterior_share_push_over']:.3f} effpar {v['eff_parents_push_over_rows']:.1f} lnZ(q=0/0.5/1) {v['ln_Z_of_q']['0.0']:.2f}/{v['ln_Z_of_q']['0.5']:.2f}/{v['ln_Z_of_q']['1.0']:.2f}" if "ln_Z_of_q" in v else ""
            print(f"   {n:26s} lnZ {v['ln_Z']:8.3f} effpar {v['eff_parents']:9.1f} lat {v['median_lat']:.2f} >212 {v['share_above_212']:.3f} fam " + " ".join(f"{k}:{x:.3f}" for k, x in v['families'].items()) + extra)
