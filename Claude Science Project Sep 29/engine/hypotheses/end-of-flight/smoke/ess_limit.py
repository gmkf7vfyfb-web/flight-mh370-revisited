"""How many effective parents could ANY terminal-stage proposal reach? The N -> infinity limit.

    python3 ess_limit.py <terminal-out-dir> <out.json> [--logon fuel-exhaustion]

For a data option with per-impact likelihood L, a parent j's contribution to the posterior is
pi_j * Lbar_j, where pi_j is its hand-off weight and Lbar_j the mean likelihood over its descents.
The effective number of parents is (sum pi Lbar)^2 / sum (pi Lbar)^2. With finitely many children,
Lhat_j is an ESTIMATE of Lbar_j and its noise inflates the denominator, so the reported ess_parents
understates what a perfect proposal would reach - but only by the Monte Carlo part.

Split each parent's children into two independent halves A and B and estimate Lbar from each. Then
E[Lhat_A Lhat_B] = Lbar^2 exactly (independence), so

    ESS_inf = (sum pi Lbar_hat)^2 / sum pi^2 Lhat_A Lhat_B

estimates the limit with the Monte Carlo noise removed from the denominator. If ESS_inf is far
below a target, the shortfall is the posterior itself - the data concentrate on few parents - and
no proposal inside the terminal stage can lift it; only more parents can. If ESS_inf is far above
the observed ess_parents, the shortfall is Monte Carlo and a targeted proposal is the remedy.

Rows of one parent are child-major (the stage writes each child's descents in turn), so the first
half of a parent's rows are the first half of its children.
"""
import argparse, json, pathlib
import numpy as np
from scipy.special import gammaln


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir"); ap.add_argument("out_json")
    ap.add_argument("--logon", default="other", choices=["other", "fuel-exhaustion"])
    a = ap.parse_args()
    d = pathlib.Path(a.out_dir)
    run = json.loads((d / "run.json").read_text())
    cols = {c: i for i, c in enumerate(run["impact_columns"])}
    children = run["terminal"]["children"]
    per_child = run["config"]["hypotheses"]["end-of-flight"]["descents_per_child"]
    ll_cols = [c for c in run["impact_columns"] if c.startswith("loglik:")]
    result = {"source": str(d), "children": children, "descents_per_child": per_child, "logon": a.logon, "replicates": []}
    for rep in run["replicates"]:
        X = np.load(d / rep["case"] / f"seed-{rep['seed']}" / "impacts.npy", mmap_mode="r")
        w = np.array(X[:, cols["weight"]], float)
        parent = np.array(X[:, cols["parent"]], int)
        n_par = parent.max() + 1
        rows_per = children * per_child
        assert len(X) == n_par * rows_per, "every parent must have children x descents rows"
        order = np.argsort(parent, kind="stable")
        assert (np.diff(parent[order]) >= 0).all()
        half = np.tile(np.repeat([0, 1], rows_per // 2), n_par)          # first half of each parent's rows -> A
        half_sorted = np.empty_like(half); half_sorted[order] = half      # map back to file order
        extra = 0.0
        if a.logon == "fuel-exhaustion":
            p = run["config"]["hypotheses"]["end-of-flight"]["logon"]
            fo = np.array(X[:, cols["latent:realised_flameout_unix_s"]], float)
            lag = p["logon_unix_s"] - fo
            with np.errstate(divide="ignore", invalid="ignore"):
                extra = (p["lag_shape"] - 1) * np.log(lag) - lag / p["lag_scale_s"] - p["lag_shape"] * np.log(p["lag_scale_s"]) - gammaln(p["lag_shape"])
            extra = np.where(np.isfinite(fo) & (lag > 0), extra, -np.inf)
        pi = np.bincount(parent, weights=w, minlength=n_par)
        cols_out = {}
        for c in ["none"] + ll_cols:
            ll = np.zeros(len(X)) if c == "none" else np.array(X[:, cols[c]], float)
            ll = np.where(np.isfinite(ll), ll, -np.inf) + extra
            m = ll[np.isfinite(ll)].max() if np.isfinite(ll).any() else 0.0
            L = np.exp(ll - m)
            est = {}
            for h in (0, 1):
                sel = half_sorted == h
                num = np.bincount(parent[sel], weights=(w * L)[sel], minlength=n_par)
                den = np.bincount(parent[sel], weights=w[sel], minlength=n_par)
                est[h] = np.divide(num, den, out=np.zeros(n_par), where=den > 0)
            lbar = 0.5 * (est[0] + est[1])
            post = pi * lbar
            ess_obs = post.sum() ** 2 / (post ** 2).sum()
            cross = (pi ** 2 * est[0] * est[1]).sum()
            ess_inf = post.sum() ** 2 / cross if cross > 0 else float("inf")
            # Share of posterior mass held by the top 1% / top 100 parents: concentration, directly.
            srt = np.sort(post)[::-1] / post.sum()
            cols_out[c.replace("loglik:", "")] = {"ess_parents_observed": float(ess_obs), "ess_parents_limit": float(ess_inf),
                                                   "top_100_parent_share": float(srt[:100].sum()),
                                                   "top_1pct_parent_share": float(srt[: max(1, n_par // 100)].sum())}
        result["replicates"].append({"seed": rep["seed"], "parents": int(n_par), "columns": cols_out})
    pathlib.Path(a.out_json).write_text(json.dumps(result, indent=1))
    print("wrote", a.out_json)


if __name__ == "__main__":
    main()
