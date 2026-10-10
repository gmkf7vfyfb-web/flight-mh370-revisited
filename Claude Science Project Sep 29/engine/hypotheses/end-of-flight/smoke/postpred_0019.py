"""Posterior-predictive consistency of the two 00:19 BFOs (Pete's intent, 10 Oct 2026: which 00:19 observations are
consistent with the feasible trajectory space selected by the other evidence, or anomalous).

Options that use DIFFERENT data cannot be ranked by a Bayes factor; instead each observation is checked against the
trajectories selected without it:
  R600 BFO   | data to 00:11 + R600 BTO (+ airborne at 00:19:37):         posterior = 00:19 R600 BTO Only +alive
  R1200 BFO  | data to 00:11 + R600 BTO + R600 BFO (+ airborne):          posterior = that BFO model's R600 option +alive
under each BFO model the run carries: no offset (sd 7 Hz), inflated (sd 34 Hz), Holland's start-up offset (R1200 offset
U[17,130] Hz, R600 = R1200 offset + U[0,6] Hz). The bias is the hand-off's (mean in the innovation column, variance from
handoff.npy), updated by the R600 BFO for the R1200 check exactly as the terminal stage does (Kalman, shared bias).
Statistic: the Bayesian (posterior-predictive) p-value of density type, P(f(rep) <= f(obs)), where f is each row's
predictive density for the burst; small means the observation is in the tail of what the selected trajectories
predict. Also reported: the posterior-predictive median and 5-95 % of the innovation.
Usage: python postpred_0019.py EXCHANGE_RUN_DIR OUT_JSON stratum ...    (core hand-offs read from core's next-run tree)
"""
import json, sys, pathlib
import numpy as np
from scipy.stats import norm
from displacement_hist import option_posteriors
from compact_impacts import open_seed

CORE = pathlib.Path(__import__("os").environ.get("EOF_CORE_RUN", "/Users/pete/Downloads/mh370-exchange/core/next-run"))
SD = 7.0
RNG = np.random.default_rng(20261010)


def nodes(model, n_b=24, n_d=4):
    if model == "startup-offset":
        b = np.linspace(17, 130, n_b); d = np.linspace(0, 6, n_d)
        B, D = np.meshgrid(b, d, indexing="ij"); return (B + D).ravel(), B.ravel(), np.full(B.size, 1.0 / B.size)
    return np.zeros(1), np.zeros(1), np.ones(1)


def pvalue(mean_nodes, var_nodes, w_nodes, obs, ndraw=1):
    """Density-type posterior-predictive p for each row: P(f(rep) <= f(obs)) under a Gaussian mixture per row.
    mean/var/w_nodes: (rows, k). Monte Carlo with ndraw replicates per row (unbiased for the weighted mean)."""
    rows, k = mean_nodes.shape
    f = lambda x: (w_nodes * norm.pdf(x[:, None], mean_nodes, np.sqrt(var_nodes))).sum(1)
    fobs = f(np.full(rows, obs) if np.ndim(obs) == 0 else obs)
    out = np.zeros(rows)
    for _ in range(ndraw):
        j = (w_nodes.cumsum(1) > RNG.random(rows)[:, None]).argmax(1)
        rep = mean_nodes[np.arange(rows), j] + np.sqrt(var_nodes[np.arange(rows), j]) * RNG.standard_normal(rows)
        out += f(rep) <= fobs
    return out / ndraw


def seed_check(sd, core_sd):
    meta, g = open_seed(sd, sd)
    ia = g("bfo_innovation_hz:m0019a"); ib = g("bfo_innovation_hz:m0019b"); par = g("parent").astype(np.int64)
    H = np.load(core_sd / "handoff-m0011" / "handoff.npy"); P = H[par, 9]          # bfo_bias_variance_hz2 per row
    sd_by = {"no-offset": SD, "startup-offset": SD, "inflated": float(meta["config"]["terminal"]["bfo_models"]["inflated"]["sd_hz"])}
    post = {}
    for key, p, c in option_posteriors(sd, sd, constraints=("alive",)):
        if key in ("r600-bto__other+alive", "r600_no-offset__other+alive", "r600_inflated__other+alive", "r600_startup-offset__other+alive"):
            post[key] = p
    out = {}
    # rows with real mass only (speed); weights renormalised over the kept rows
    def keep(p, q=1 - 1e-6):
        o = np.argsort(p)[::-1]; c = np.cumsum(p[o]); k = o[: np.searchsorted(c, q) + 1]; return k, p[k] / p[k].sum()
    for model in ("no-offset", "inflated", "startup-offset"):
        s = sd_by[model]; offa, offb, wn = nodes(model)
        # R600 BFO given R600 BTO: innovation_a - offset_a ~ N(0, s^2 + P)  (innovation already has the bias mean removed)
        k, w = keep(post["r600-bto__other+alive"]); m = np.broadcast_to(offa, (len(k), len(offa))); v = (s ** 2 + P[k])[:, None] + 0 * m
        pa = float((w * pvalue(m, v, np.broadcast_to(wn, m.shape), ia[k])).sum())
        rep_med = np.average(offa, weights=wn)
        # R1200 BFO given R600 BTO + R600 BFO under this model: update the shared bias with the R600 BFO (node by node)
        k, w = keep(post[f"r600_{model}__other+alive"])
        Pk = P[k][:, None]; xa = ia[k][:, None] - offa[None, :]
        lik = wn[None, :] * norm.pdf(xa, 0, np.sqrt(s ** 2 + Pk))           # node weights given the R600 BFO
        wnode = lik / lik.sum(1, keepdims=True)
        K = Pk / (Pk + s ** 2); mu = K * xa; Pp = Pk * (1 - K)
        mb = offb[None, :] + mu; vb = s ** 2 + Pp + 0 * mb
        pb = float((w * pvalue(mb, vb, wnode, ib[k])).sum())
        out[model] = {"p_R600_BFO_given_R600_BTO": pa, "p_R1200_BFO_given_R600_BTO_and_BFO": pb,
                      "R1200_innovation_posterior_median_hz": float(np.median(ib[k])), "rows_used": [int(len(k))]}
    return out


def main(root, outp, strata):
    res = {}
    for st in strata:
        seeds = sorted(d for d in (pathlib.Path(root) / st).glob("seed-*") if (d / "impacts.npy").exists() or (d / "impacts32.npy").exists())
        r = [seed_check(d, CORE / st / "bto-bfo" / d.name) for d in seeds]
        res[st] = {m: {k: [x[m][k] for x in r] for k in r[0][m]} for m in r[0]}
        for m in res[st]:
            print(st, m, "p(R600 BFO | R600 BTO)", np.round(res[st][m]["p_R600_BFO_given_R600_BTO"], 4), "p(R1200 BFO | R600)", np.round(res[st][m]["p_R1200_BFO_given_R600_BTO_and_BFO"], 5), flush=True)
    pathlib.Path(outp).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:])
