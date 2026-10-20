"""Per-option evidence and parent-level convergence diagnostics for an end-of-flight terminal sweep.

For each data option x log-on cause, per seed:
- log evidence ln Z = ln sum_i w_i L_i, w the impact weight normalised over the seed (the hand-off posterior
  through 00:11 times the within-parent proposal correction) and L the 00:19 likelihood of that option (times
  the section 6 lag density for fuel-exhaustion). Z is the predictive probability of the 00:19 data given the
  cruise data under that option, so options scoring the SAME data are comparable (Holland H1 vs H2 is
  both/startup-offset vs both/no-offset). Options scoring different data (r600 vs both) and the two log-on
  causes (`other` has no log-on likelihood, absolute_scale false) are NOT comparable and are not compared.
- effective impacts 1/sum p^2, effective parents 1/sum P^2 (P = posterior summed per parent), the posterior
  share of the top 100 parents, and the share of Z from the top 10 parents;
- a parent-bootstrap standard error of ln Z (resampling parents with their children).
Across seeds: mean and spread of ln Z. The bootstrap understates the error when a handful of parents carry Z
(the top-10 share says when); the between-seed spread is the honest check. Architecture fix 2 (~19:30 UTC,
9 Oct) asked for the per-option effective parents / impacts / top-100 share; this is where they live.

Usage: python option_evidence.py OUT.json RUN_DIR [RUN_DIR ...]   (each RUN_DIR holds run.json, bto-bfo/seed-k/)
"""
import json, pathlib, sys
import numpy as np
from scipy.special import gammaln, logsumexp

from displacement_hist import OPTIONS, derived_logliks


def seed_dirs(run):
    return sorted((run / "bto-bfo").glob("seed-*"))


def analyse(run, seed_dir, n_boot=200, rng=None):
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    logon = meta["config"]["hypotheses"]["end-of-flight"]["logon"]
    X = np.load(seed_dir / "impacts.npy", mmap_mode="r")
    g = lambda k: np.asarray(X[:, cols[k]], float)
    w = g("weight"); w = w / w.sum(); lw = np.log(w)
    par = g("parent").astype(np.int64); _, par = np.unique(par, return_inverse=True); n_par = par.max() + 1
    lag = logon["logon_unix_s"] - g("latent:realised_flameout_unix_s")
    with np.errstate(divide="ignore", invalid="ignore"):
        lfe = (logon["lag_shape"] - 1) * np.log(lag) - lag / logon["lag_scale_s"] - logon["lag_shape"] * np.log(logon["lag_scale_s"]) - gammaln(logon["lag_shape"])
    lfe = np.where(np.isfinite(lag) & (lag > 0), lfe, -np.inf)
    present = [c[len("loglik:"):] for c in meta["impact_columns"] if c.startswith("loglik:")]
    derived = derived_logliks(meta, g, present)
    out = {}
    for o in [o for o in OPTIONS if o in present] + [o for o in present if o not in OPTIONS] + list(derived):
        base = derived[o] if o in derived else g("loglik:" + o); base = np.where(np.isfinite(base), base, -np.inf)
        for cause, extra in (("other", 0.0), ("fuel-exhaustion", lfe)):
            a = lw + base + extra                       # ln(w_i L_i)
            lz = logsumexp(a)
            p = np.exp(a - lz)
            P = np.bincount(par, weights=p, minlength=n_par)
            Ps = np.sort(P)[::-1]
            # parent bootstrap of ln Z: Z = sum over parents of z_j, resample parents
            z = np.bincount(par, weights=np.exp(a - a.max()), minlength=n_par)
            boots = []
            for _ in range(n_boot):
                idx = rng.integers(0, n_par, n_par)
                s = z[idx].sum()
                boots.append(np.log(s) + a.max() if s > 0 else -np.inf)
            boots = np.array(boots)
            out[f"{o.replace('/', '_')}__{cause}"] = {
                "ln_evidence": float(lz),
                "ln_evidence_boot_se": float(np.std(boots[np.isfinite(boots)])) if np.isfinite(boots).sum() > 2 else None,
                "boot_zero_fraction": float(np.mean(~np.isfinite(boots))),
                "effective_impacts": float(1.0 / np.sum(p ** 2)),
                "effective_parents": float(1.0 / np.sum(P ** 2)),
                "top100_parent_share": float(Ps[:100].sum()),
                "top10_parent_share": float(Ps[:10].sum()),
                "rows": int(len(w)), "parents": int(n_par),
            }
    return out


def main():
    out_path = pathlib.Path(sys.argv[1]); runs = [pathlib.Path(r) for r in sys.argv[2:]]
    rng = np.random.default_rng(20261009)
    per_seed = {}
    for run in runs:
        for s in seed_dirs(run):
            key = f"{run.name}/{s.name}"; per_seed[key] = analyse(run, s, rng=rng); print(key, flush=True)
    arms = list(next(iter(per_seed.values())).keys())
    pooled = {}
    for k in arms:
        lz = np.array([per_seed[s][k]["ln_evidence"] for s in per_seed])
        pooled[k] = {"ln_evidence_mean_over_seeds": float(np.mean(lz)), "ln_evidence_sd_over_seeds": float(np.std(lz, ddof=1)) if len(lz) > 1 else None,
                     "ln_evidence_pooled": float(logsumexp(lz) - np.log(len(lz))),
                     "effective_impacts_sum": float(sum(per_seed[s][k]["effective_impacts"] for s in per_seed)),
                     "effective_parents_sum": float(sum(per_seed[s][k]["effective_parents"] for s in per_seed)),
                     "top100_parent_share_max": float(max(per_seed[s][k]["top100_parent_share"] for s in per_seed))}
    # Holland H1 (startup-offset) vs H2 (no-offset) on the same data, per burst set and cause
    bf = {}
    for burst in ("r600", "r1200", "both"):
        for cause in ("other", "fuel-exhaustion"):
            a, b = f"{burst}_startup-offset__{cause}", f"{burst}_no-offset__{cause}"
            if a in pooled and b in pooled:
                d = np.array([per_seed[s][a]["ln_evidence"] - per_seed[s][b]["ln_evidence"] for s in per_seed])
                bf[f"{burst}__{cause}"] = {"ln_BF_H1_over_H2_pooled": pooled[a]["ln_evidence_pooled"] - pooled[b]["ln_evidence_pooled"],
                                           "per_seed": [float(x) for x in d], "sd_over_seeds": float(np.std(d, ddof=1)) if len(d) > 1 else None}
    json.dump({"runs": [str(r) for r in runs], "per_seed": per_seed, "pooled": pooled, "holland_h1_vs_h2": bf}, open(out_path, "w"), indent=1)


if __name__ == "__main__":
    main()
