"""In-flight structural outcome (G13, PROVISIONAL) per 00:19 option and family: posterior-weighted P(intact), P(partial damage),
P(in-flight breakup), share with peak load factor above 2.5 g, by family, constraint `unpowered`. Optional re-pricing with other
fragility parameters is possible from the peak columns (latent:struct_speed_ratio, struct_load_ratio). SMOKE TOOL.
Usage: python inflight_structure.py OUT_JSON RUN [RUN ...]
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp, gammaln
from displacement_hist import derived_logliks, constraint_log_factor
from compact_impacts import family_labels
from smoke_compare import CORE


def one(run, sd):
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r"); g = lambda k: np.asarray(X[:, cols[k]], float)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    w = g("weight"); lw = np.log(w) - np.log(w.sum())
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]; der = derived_logliks(meta, g, present)
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    pi, pp, pb = g("latent:inflight_p_intact"), g("latent:inflight_p_partial"), g("latent:inflight_p_breakup")
    nmax = g("latent:struct_max_load_factor_g")
    f4 = family_labels(g("latent:onset_mechanism"), g("latent:control_realised"), g("latent:recovery_attempted"))["family4_code"]
    def summ(p):
        r = {"intact": float((p * pi).sum()), "partial": float((p * pp).sum()), "breakup": float((p * pb).sum()), "n_max_above_2.5g": float(p[nmax > 2.5].sum())}
        r["families"] = {n: ({"share": float(p[f4 == c].sum()), "intact": float((p * pi)[f4 == c].sum() / p[f4 == c].sum()), "breakup": float((p * pb)[f4 == c].sum() / p[f4 == c].sum())} if p[f4 == c].sum() > 0 else None) for c, n in ((1, "A1"), (2, "A2"), (3, "B"))}
        return r
    out = {"prior": summ(np.exp(lw)), "options": {}}
    for name, o, cause in CORE:
        base = der[o] if o in der else g("loglik:" + o)
        ll = np.where(np.isfinite(base), base, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0) + constraint_log_factor(g, logon, cause, "unpowered")
        out["options"][name] = summ(np.exp(lw + ll - logsumexp(lw + ll)))
    return out


if __name__ == "__main__":
    res = {}
    for r in sys.argv[2:]:
        run = pathlib.Path(r)
        for sd in sorted((run / "bto-bfo").glob("seed-*")):
            res[f"{r}/{sd.name}"] = v = one(run, sd)
            print(r, sd.name)
            for n, o in [("prior", v["prior"])] + list(v["options"].items()):
                fam = " ".join(f"{f}: {d['share']:.2f} intact {d['intact']:.2f} breakup {d['breakup']:.2f}" for f, d in o["families"].items() if d)
                print(f"  {n:26s} intact {o['intact']:.3f} partial {o['partial']:.3f} breakup {o['breakup']:.3f} n>2.5g {o['n_max_above_2.5g']:.3f} | {fam}")
    json.dump(res, open(sys.argv[1], "w"), indent=1)
