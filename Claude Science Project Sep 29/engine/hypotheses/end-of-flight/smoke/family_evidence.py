"""The 00:19 evidence factor per core family (stratum) and per 00:19 option, with Monte Carlo error, and the
re-weighted family mixture (architecture ruling C, ~19:10 UTC 10 Oct 2026):

    P(family | all data, option) = P_core(family) x Zhat_0019(family, option) / sum over families,

where P_core(family) is core's posterior family probability through 00:11 and
Zhat_0019(family, option) = E_handoff[ L_0019(option) x existence constraint ] is this module's evidence for the
00:19 data given that family's 00:11 hand-off. Per seed: ln Zhat_k = ln sum_rows w L c - ln sum_rows w. The factor is
the mean over seeds of Zhat_k (equal weight per seed); its MC error is the seed-to-seed s.e. of that mean, also
given in log units (s.e./mean). Held out (no 00:19 data) has factor 1 without constraints; with the `alive`
constraint it is P(airborne at 00:19:37 | family), reported as such.

Also writes per-stratum posterior latitude histograms (0.001 deg; seeds equal weight) and the fixed-weight and
re-weighted mixture medians and 5-95 % ranges, so the two mixtures can be shown side by side.

Usage: python family_evidence.py EXCHANGE_RUN_DIR OUT_JSON  [P_core as stratum=value ...]
"""
import json, sys, pathlib
import numpy as np
from scipy.special import logsumexp, gammaln
from displacement_hist import derived_logliks, constraint_log_factor

CORE = [("00:19 Held Out", "none", "other"), ("00:19 R600 BTO Only", "r600-bto", "other"),
        ("00:19 R600 BTO + Raw BFO", "r600/no-offset", "other"),
        ("00:19 Holland H1", "both/startup-offset", "fuel-exhaustion"), ("00:19 Holland H2", "both/no-offset", "other")]
EDGES = np.arange(-50.0, -15.0 + 1e-9, 0.001)


def per_seed(sd):
    meta = json.loads((sd / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r"); g = lambda k: np.array(X[:, cols[k]], float)
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    w = g("weight"); lw = np.log(w) - np.log(w.sum()); lat = g("latitude_deg"); par = g("parent").astype(np.int64)
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    der = derived_logliks(meta, g, present)
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    out = {}
    for name, o, cause in CORE:
        base = der[o] if o in der else g("loglik:" + o)
        ll = np.where(np.isfinite(base), base, -np.inf) + (lfe if cause == "fuel-exhaustion" else 0.0)
        for con in ("", "alive"):
            l2 = ll + (constraint_log_factor(g, logon, cause, con) if con else 0.0)
            lz = float(logsumexp(lw + l2))
            p = np.exp(lw + l2 - lz); mass = np.bincount(par, weights=p)
            h = np.histogram(lat, EDGES, weights=p)[0]
            out[(name, con)] = {"ln_Z": lz, "eff_parents": float(1 / (mass ** 2).sum()), "eff_impacts": float(1 / (p ** 2).sum()), "hist": h}
    return out


def qs(h, q=(0.05, 0.5, 0.95)):
    c = np.cumsum(h); c = c / c[-1]; mids = 0.5 * (EDGES[1:] + EDGES[:-1])
    return [float(mids[np.searchsorted(c, x)]) for x in q]


def main(root, outp, pcore):
    root = pathlib.Path(root); res = {"p_core": pcore, "strata": {}, "mixtures": {}}
    H = {}
    for s in pcore:
        seeds = sorted(d for d in (root / s).glob("seed-*") if (d / "impacts.npy").exists())
        rows = [per_seed(d) for d in seeds]
        res["strata"][s] = {}
        for key in rows[0]:
            z = np.array([np.exp(r[key]["ln_Z"]) for r in rows]); m = z.mean(); se = z.std(ddof=1) / np.sqrt(len(z))
            hist = np.mean([r[key]["hist"] / r[key]["hist"].sum() for r in rows], axis=0); H[(s, key)] = hist
            res["strata"][s][f"{key[0]}{' +' + key[1] if key[1] else ''}"] = {
                "ln_Zhat": float(np.log(m)), "ln_Zhat_se": float(se / m), "ln_Z_per_seed": [r[key]["ln_Z"] for r in rows],
                "eff_parents_per_seed": [r[key]["eff_parents"] for r in rows], "eff_impacts_per_seed": [r[key]["eff_impacts"] for r in rows],
                "median_lat": qs(hist)[1]}
    for name, _, _ in CORE:
        for con in ("", "alive"):
            k = f"{name}{' +' + con if con else ''}"
            lz = {s: res["strata"][s][k]["ln_Zhat"] for s in pcore}
            fixed = {s: pcore[s] for s in pcore}
            a = np.array([np.log(pcore[s]) + lz[s] for s in pcore]); rw = np.exp(a - logsumexp(a))
            rew = dict(zip(pcore, rw.tolist()))
            mix = lambda wts: sum(wts[s] * H[(s, (name, con))] for s in pcore)
            res["mixtures"][k] = {"p_family_fixed": fixed, "p_family_reweighted": rew,
                                  "lat_q05_q50_q95_fixed": qs(mix(fixed)), "lat_q05_q50_q95_reweighted": qs(mix(rew))}
    pathlib.Path(outp).write_text(json.dumps(res, indent=1))
    for k, v in res["mixtures"].items():
        print(f"{k:34s}", " ".join(f"{s}:{res['strata'][s][k]['ln_Zhat']:.2f}±{res['strata'][s][k]['ln_Zhat_se']:.2f}" for s in pcore),
              "| P rew", {s: round(x, 3) for s, x in v["p_family_reweighted"].items()}, "| median fixed %.2f rew %.2f" % (v["lat_q05_q50_q95_fixed"][1], v["lat_q05_q50_q95_reweighted"][1]))


if __name__ == "__main__":
    pc = dict(a.split("=") for a in sys.argv[3:]); pc = {k: float(v) for k, v in pc.items()}
    main(sys.argv[1], sys.argv[2], pc)
