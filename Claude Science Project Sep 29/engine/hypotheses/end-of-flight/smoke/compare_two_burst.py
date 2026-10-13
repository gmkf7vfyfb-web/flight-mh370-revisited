"""Compare two end-of-flight seeds on the two-burst options (diagnostic smokes 1 and 2, 10 Oct 2026).
For each option x cause (with the `alive` existence constraint, as in the core option set): ln Z relative to the
hand-off (sum of prior weight x likelihood), effective parents and impacts, the posterior share by realised control,
the posterior median 00:19:29 / 00:19:37 vertical speed and their difference, and the prior tail P(dv <= -10,450 ft/min).
Usage: python compare_two_burst.py OUT.json LABEL_A RUN_A SEED_A LABEL_B RUN_B SEED_B
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp
from displacement_hist import option_posteriors, constraint_log_factor

KEYS = {"00:19 Holland H2": "both_no-offset__other", "00:19 Holland H1": "both_startup-offset__fuel-exhaustion",
        "00:19 R600 BTO + Raw BFO": "r600_no-offset__other", "00:19 R600 BTO Only": "r600-bto__other", "00:19 Held Out": "none__other"}


def wmed(x, w):
    ok = np.isfinite(x) & (w > 0); o = np.argsort(x[ok]); c = np.cumsum(w[ok][o]); c /= c[-1]
    return float(x[ok][o][np.searchsorted(c, 0.5)])


def one(run, sd):
    run, sd = pathlib.Path(run), pathlib.Path(sd)
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r"); g = lambda k: np.asarray(X[:, cols[k]], float)
    w = g("weight"); par = g("parent").astype(np.int64)
    va, vb = g("latent:state_m0019a_vertical_speed_fpm"), g("latent:state_m0019b_vertical_speed_fpm")
    dv = vb - va; alive = np.isfinite(constraint_log_factor(g, meta["config"]["hypotheses"]["end-of-flight"]["logon"], "other", "alive"))
    pw = w / w.sum(); ok = alive & np.isfinite(dv)
    res = {"prior_tail_dv_le_-10450": float(pw[ok & (dv <= -10450)].sum() / pw[ok].sum()),
           "prior_tail_dv_le_-8000": float(pw[ok & (dv <= -8000)].sum() / pw[ok].sum()), "options": {}}
    want = {v + "+alive" for v in KEYS.values()}
    for key, p, c in option_posteriors(run, sd, constraints=("alive",)):
        if key not in want: continue
        o, cause = key[:-6].split("__")
        base = g("loglik:" + o.replace("_", "/", 1)) if ("loglik:" + o.replace("_", "/", 1)) in cols else None
        mass = np.bincount(par, weights=p)
        ctrl = {name: float(p[c["ctrl"] == i].sum()) for i, name in enumerate(c["controls"])}
        res["options"][key] = {"effective_parents": float(1 / (mass ** 2).sum()), "effective_impacts": float(1 / (p ** 2).sum()),
                               "control_share": ctrl, "median_vs_001929_fpm": wmed(va, p), "median_vs_001937_fpm": wmed(vb, p),
                               "median_dv_fpm": wmed(dv, p), "median_lat": wmed(c["lat"], p)}
    return res


def lnz(run, sd):
    """ln Z per option x cause +alive, relative to the hand-off: log sum_rows (w/sum w) * exp(ll)."""
    from displacement_hist import gammaln  # noqa
    run, sd = pathlib.Path(run), pathlib.Path(sd)
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r"); g = lambda k: np.asarray(X[:, cols[k]], float)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]; w = g("weight"); lw = np.log(w / w.sum())
    from scipy.special import gammaln as GL
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - GL(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    out = {}
    for name, key in KEYS.items():
        o, cause = key.split("__")
        col = "loglik:" + (o.replace("_", "/", 1) if o != "r600-bto" else None) if o not in ("r600-bto", "none") else None
        if o == "none": ll = np.zeros_like(w)
        elif col in cols: ll = g(col)
        else: continue
        ll = np.where(np.isfinite(ll), ll, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0) + constraint_log_factor(g, logon, cause, "alive")
        out[key + "+alive"] = float(logsumexp(lw + ll))
    return out


if __name__ == "__main__":
    out = {}
    a = sys.argv[2:]
    for i in range(0, len(a), 3):
        lab, run, sd = a[i:i + 3]
        r = one(run, sd); r["ln_Z"] = lnz(run, sd); out[lab] = r
    pathlib.Path(sys.argv[1]).write_text(json.dumps(out, indent=1))
    for lab, r in out.items():
        print("==", lab, "prior tail dv<=-10450: %.5f  <=-8000: %.5f" % (r["prior_tail_dv_le_-10450"], r["prior_tail_dv_le_-8000"]))
        for k, v in r["options"].items():
            top = max(v["control_share"].items(), key=lambda kv: kv[1])
            print("  %-48s lnZ %7.2f  parents %8.1f impacts %9.1f  vs %6.0f / %6.0f dv %6.0f lat %.2f  ctrl %s" % (
                k, r["ln_Z"].get(k, float("nan")), v["effective_parents"], v["effective_impacts"], v["median_vs_001929_fpm"],
                v["median_vs_001937_fpm"], v["median_dv_fpm"], v["median_lat"], {kk: round(x, 3) for kk, x in v["control_share"].items()}))
