"""Diagnostic smoke 2: does within-parent sampling limit the two-burst options? Compares, on the same parents,
Z_top = sum_i w_i Lbar_i with the original 32 descents per parent (source seed) against the re-run with many more
(the reduced hand-off of top_parent_handoff.py, hand-off weights unchanged). Also: effective parents and impacts,
and a within-run split-half (descents of each parent split into two halves by row parity; overlap of the two
impact-latitude densities, 0.05 deg bins).
Usage: python saturation.py OUT.json SRC_SEED_DIR TOP_HANDOFF_DIR NEW_RUN
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp
from displacement_hist import constraint_log_factor
from scipy.special import gammaln

OPTS = {"00:19 Holland H2": ("both/no-offset", "other"), "00:19 Holland H1": ("both/startup-offset", "fuel-exhaustion")}


def rows(run, sd):
    meta = json.loads((pathlib.Path(run) / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(pathlib.Path(sd) / "impacts.npy", mmap_mode="r"); g = lambda k: np.asarray(X[:, cols[k]], float)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    out = {"w": g("weight"), "par": g("parent").astype(np.int64), "lat": g("latitude_deg")}
    for name, (col, cause) in OPTS.items():
        ll = g("loglik:" + col); ll = np.where(np.isfinite(ll), ll, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0)
        out[name] = ll + constraint_log_factor(g, logon, cause, "alive")
    return out


def overlap(lat, p, mask):
    e = np.arange(-45, -20, 0.05)
    a = np.histogram(lat[mask], e, weights=p[mask])[0]; b = np.histogram(lat[~mask], e, weights=p[~mask])[0]
    return float(np.minimum(a / a.sum(), b / b.sum()).sum()) if a.sum() > 0 and b.sum() > 0 else None


def main(out, src, top, new):
    info = json.loads((pathlib.Path(top) / "parents.json").read_text()); keep = np.array(info["original_index_of_new_row"])
    A = rows(src, src); B = rows(new, pathlib.Path(new) / "bto-bfo/seed-1")
    hw = np.bincount(A["par"], weights=A["w"])                                   # hand-off weight per original parent
    inA = np.isin(A["par"], keep)
    # new run: rescale so each parent's rows sum to its hand-off weight (whatever normalisation the runner used)
    sB = np.bincount(B["par"], weights=B["w"], minlength=len(keep)); scale = hw[keep][B["par"]] / sB[B["par"]]
    wB = B["w"] * scale
    res = {"parents": int(len(keep)), "descents_per_parent": [int(np.bincount(A["par"][inA]).max()), int(np.bincount(B["par"]).max())], "options": {}}
    for name in OPTS:
        r = {}
        for lab, w, par, ll, lat in (("32", A["w"][inA], A["par"][inA], A[name][inA], A["lat"][inA]), ("many", wB, keep[B["par"]], B[name], B["lat"])):
            lz = logsumexp(np.log(w) + ll)
            # s.e. of Z from the within-parent spread of the likelihood (rows treated as independent within a parent)
            L = np.exp(ll - ll.max()); p = w * L; Z = p.sum()
            byp = {}
            for i in np.unique(par):
                m = par == i; n = m.sum(); wi = w[m].sum(); Li = L[m]
                byp[i] = (wi ** 2) * Li.var(ddof=1) / n if n > 1 else 0.0
            se = float(np.sqrt(sum(byp.values())) / Z)
            pp = p / Z; mass = np.bincount(par, weights=pp)
            half = (np.arange(len(pp)) % 2) == 0
            r[lab] = {"ln_Z": float(lz), "rel_se_Z": se, "effective_parents": float(1 / (mass ** 2).sum()),
                      "effective_impacts": float(1 / (pp ** 2).sum()), "within_run_split_half": overlap(lat, pp, half),
                      "median_lat": float(np.interp(0.5, np.cumsum(pp[np.argsort(lat)]), np.sort(lat)))}
        r["delta_ln_Z_many_minus_32"] = r["many"]["ln_Z"] - r["32"]["ln_Z"]
        r["delta_in_se_of_32"] = r["delta_ln_Z_many_minus_32"] / max(r["32"]["rel_se_Z"], 1e-12)
        res["options"][name] = r
    pathlib.Path(out).write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(*sys.argv[1:5])
