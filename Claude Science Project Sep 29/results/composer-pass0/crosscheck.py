"""Composer pass 0: independent cross-check of compose() on one seed with plain numpy.

PIPELINE TEST - core (b) unconverged; EoF physics provisional; hydro L_hyd stand-in; GlobCurrent F1; Holland H1/H2 not estimable.

Recomputes from the same input columns, without the composer library:
  P1  w1 = w exp(l_terminal) / sum                                    (flight + EoF)
  G   w2 = w1 L / sum, L = exp(l_drift + l_hyd); a row with NaN in any factor carries the (mode) mean likelihood
      ratio D_m = sum_{computed rows of m} w1 L / sum_{computed rows of m} w1   (composer.md ruling 1)
  Ga  w3 = w2 exp(l_seabed) / sum
  H   as G with l_pleiades added (NaN rows carried the same way)
and the per-mode evidence increments ln D_m, then compares with the composer's f32 weights and products.json.
Usage: python crosscheck.py <input dir> <rust out dir> <seed> <out json>
"""
import json, pathlib, sys
import numpy as np
from scipy.special import logsumexp

G12 = "glorys12v1+era5-wind10"


def step(w, mode, ll):
    """One composition: returns new weights and ln D per mode."""
    nan = np.isnan(ll); lnd = np.full(5, np.nan); out = np.zeros_like(w)
    for m in range(5):
        sel = (mode == m) & (w > 0)
        if not sel.any():
            continue
        c = sel & ~nan
        lnd[m] = logsumexp(np.log(w[c]) + ll[c]) - np.log(w[c].sum())
        l = np.where(nan, lnd[m], ll)
        out[sel] = np.log(w[sel]) + l[sel]
    pos = w > 0
    out[pos] = np.exp(out[pos] - out[pos].max()); out[~pos] = 0.0
    out /= out.sum()
    return out, lnd


def main(ind, rout, k, outp):
    ind, rout = pathlib.Path(ind), pathlib.Path(rout)
    h = json.loads((ind / f"seed-{k}.json").read_text()); c = h["columns"]
    X = np.memmap(ind / f"seed-{k}.f64", dtype="<f8", mode="r", shape=(h["rows"], len(c)))
    g = lambda n: np.array(X[:, c.index(n)])
    w = g("weight"); w = w / w.sum(); mode = g("mode").astype(int)
    P = {p["id"]: p for p in json.loads((rout / "products.json").read_text())["products"]}
    res = {"seed": k, "rows": int(w.size), "cases": {}}
    for tag, term in (("r600", "loglik:r600-bto+alive"), ("heldout", "loglik:none+alive")):
        w1, d1 = step(w, mode, g(term))
        drift, hyd, sea = g(f"debris-drift:loglik:{G12}"), g("hydroacoustics:loglik"), g("seabed-search:loglik")
        ple = g(f"pleiades:loglik:H/rho4-0/equal/{G12}")
        w2, d2 = step(w1, mode, drift + hyd)            # NaN propagates through the sum: a row is computed only if all are
        w3, d3 = step(w2, mode, sea)
        wh, dh = step(w1, mode, drift + hyd + ple)
        for pid, wn, dn in ((f"{tag}-P1", w1, d1), (f"{tag}-G", w2, d2), (f"{tag}-Ga", w3, d3), (f"{tag}-H", wh, dh)):
            wr = np.fromfile(rout / "weights" / pid / f"seed-{k}.f32", dtype="<f4").astype(float)
            rep = [r for r in P[pid]["replicates"] if r["seed"] == k][0]
            lr = np.array([np.nan if v is None else v for v in rep["log_evidence_increment"]])
            diff = np.abs(wr - wn); big = wn > 1e-12
            res["cases"][pid] = {"max_abs_diff_weight": float(diff.max()), "max_rel_diff_weight": float((diff[big] / wn[big]).max()),
                                 "f32_storage_rel_precision": float(np.finfo(np.float32).eps / 2),
                                 "max_abs_diff_ln_D_per_mode": float(np.nanmax(np.abs(lr - dn))),
                                 "numpy_ln_D_per_mode": dn.tolist(), "composer_ln_D_per_mode": lr.tolist(),
                                 "numpy_mean_lat": float((wn * g("latitude_deg")).sum()), "composer_mean_lat_from_f32": float((wr * g("latitude_deg")).sum() / wr.sum())}
            print(pid, res["cases"][pid]["max_abs_diff_weight"], res["cases"][pid]["max_rel_diff_weight"], res["cases"][pid]["max_abs_diff_ln_D_per_mode"], flush=True)
    pathlib.Path(outp).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4])
