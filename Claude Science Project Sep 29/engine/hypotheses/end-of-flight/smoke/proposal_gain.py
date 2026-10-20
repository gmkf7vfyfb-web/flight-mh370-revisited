"""Offline estimate of what an onset-window defensive mixture would do to effective parents (brief section 8).

    python3 proposal_gain.py <terminal-out-dir> <out.json> [--logon fuel-exhaustion] [--children-target 16]

Proposal under test: onset ~ q = alpha * p + (1 - alpha) * p( . | onset in [T - W, T)), with T the 00:19:37 burst
and p the plain onset prior of the parent. The exact weight is p/q = 1 / (alpha + (1 - alpha) 1[window] / P_w),
with P_w the parent's prior mass of the window. The per-parent single-draw variance of the likelihood is
  plain:    E_p[L^2] - Lbar^2,
  targeted: E_p[L^2 p/q] - Lbar^2,
both estimated from the plain-proposal rows already run. With n draws per parent, the observed denominator
is sum pi^2 (Lbar^2 + Var/n); the Lbar^2 term is the split-half product (ess_limit.py). The predictor is
checked by reproducing the observed effective parents with q = p. P_w is estimated from the parent's rows
here; in the implementation it is exact (the onset prior's CDF).
"""
import argparse, json, pathlib
import numpy as np
from scipy.special import gammaln

T0019B = 1394237977.443


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out_dir"); ap.add_argument("out_json")
    ap.add_argument("--logon", default="other", choices=["other", "fuel-exhaustion"])
    ap.add_argument("--children-target", type=int, default=16)
    a = ap.parse_args()
    d = pathlib.Path(a.out_dir); run = json.loads((d / "run.json").read_text())
    cols = {c: i for i, c in enumerate(run["impact_columns"])}
    children = run["terminal"]["children"]; per_child = run["config"]["hypotheses"]["end-of-flight"]["descents_per_child"]
    rows_per = children * per_child
    opts = ["r600/startup-offset", "r1200/inflated", "r1200/no-offset", "r1200/startup-offset",
            "both/inflated", "both/no-offset", "both/startup-offset"]
    designs = [(W, al) for W in (120, 300, 600) for al in (0.2, 0.3, 0.5)]
    res = {"source": str(d), "logon": a.logon, "children": children, "children_target": a.children_target, "seeds": {}}
    for sd in sorted((d / "bto-bfo").glob("seed-*")):
        X = np.load(sd / "impacts.npy", mmap_mode="r")
        parent = np.asarray(X[:, cols["parent"]], int); n_par = parent.max() + 1
        w = np.asarray(X[:, cols["weight"]], float)
        on = np.asarray(X[:, cols["latent:onset_unix_s"]], float)
        half = np.empty(len(X), int); order = np.argsort(parent, kind="stable")
        half[order] = np.tile(np.repeat([0, 1], rows_per // 2), n_par)
        extra = 0.0
        if a.logon == "fuel-exhaustion":
            p = run["config"]["hypotheses"]["end-of-flight"]["logon"]
            fo = np.asarray(X[:, cols["latent:realised_flameout_unix_s"]], float); lag = p["logon_unix_s"] - fo
            with np.errstate(divide="ignore", invalid="ignore"):
                extra = (p["lag_shape"] - 1) * np.log(lag) - lag / p["lag_scale_s"] - p["lag_shape"] * np.log(p["lag_scale_s"]) - gammaln(p["lag_shape"])
            extra = np.where(np.isfinite(fo) & (lag > 0), extra, -np.inf)
        bc = lambda v: np.bincount(parent, weights=v, minlength=n_par)
        W0 = bc(w); pi = W0 / W0.sum()
        out = {}
        for o in opts:
            ll = np.asarray(X[:, cols["loglik:" + o]], float); ll = np.where(np.isfinite(ll), ll, -np.inf) + extra
            L = np.exp(ll - ll[np.isfinite(ll)].max())
            mean = lambda v: np.divide(bc(w * v), W0, out=np.zeros(n_par), where=W0 > 0)
            def half_mean(h):
                sel = half == h
                num_h = np.bincount(parent[sel], weights=(w * L)[sel], minlength=n_par)
                den_h = np.bincount(parent[sel], weights=w[sel], minlength=n_par)
                return np.divide(num_h, den_h, out=np.zeros(n_par), where=den_h > 0)
            hA, hB = half_mean(0), half_mean(1)
            lbar = 0.5 * (hA + hB)                               # as ess_limit.py
            sq = hA * hB                                         # unbiased Lbar^2 (independent halves)
            m2 = mean(L * L)
            num = (pi * lbar).sum() ** 2
            def ess(var, n):
                return float(num / (pi ** 2 * (sq + var / n)).sum())
            var_p = m2 - sq                                      # E[L^2] - Lbar^2, unbiased; not clipped
            r = {"observed": float(num / (pi ** 2 * lbar ** 2).sum()), "predicted_plain_N": ess(var_p, rows_per),
                 "limit": float(num / (pi ** 2 * sq).sum()),
                 "plain_at_target": ess(var_p, a.children_target * per_child), "designs": {}}
            for W, al in designs:
                inw = ((on >= T0019B - W) & (on < T0019B)).astype(float)
                Pw = np.clip(mean(inw), 1e-3, 1.0)[parent]
                pq = 1.0 / (al + (1 - al) * inw / Pw)
                m2q = mean(L * L * pq)
                r["designs"][f"W{W}_a{al}"] = {"at_target": ess(m2q - sq, a.children_target * per_child),
                                               "max_weight_ratio": float(1 / al)}
            out[o] = r
        res["seeds"][sd.name] = out
    pathlib.Path(a.out_json).write_text(json.dumps(res, indent=1))
    for s, out in res["seeds"].items():
        for o, r in out.items():
            best = max(r["designs"].items(), key=lambda kv: kv[1]["at_target"])
            print(f"{s} {o:22s} obs {r['observed']:7.0f} pred(q=p) {r['predicted_plain_N']:7.0f} lim {min(r['limit'],1e9):9.0f} "
                  f"plain@N{a.children_target} {r['plain_at_target']:7.0f} best {best[0]} {best[1]['at_target']:7.0f}")


if __name__ == "__main__":
    main()
