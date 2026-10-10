"""Score end of flight's per-stratum impacts against a merged drift surface, pooled by P(family).

For every option x cause (end of flight's recipe, read-only, plain and with any declared constraints) this
pools all strata and seeds into one mixture: weight P(family)_s / n_seeds x the seed's normalised option
posterior. It reports, per drift bandwidth column:
  - scored / outside_support / mc_unresolved mass, classified exactly as interpolate.rs (score_impacts.lookup);
  - the impact median latitude and 5-95% of the whole mixture, and of the scored part before and after
    multiplying by the drift likelihood (q = p x L on scored mass only; the unscored mass is EXCLUDED, never
    renormalised in silently: report the scored fraction beside every number);
  - the effective-sample-size ratio of the drift weighting on the scored mass.
Quantiles come from a 0.001 deg weighted latitude histogram (end of flight's convention).

Usage: python score_mixture.py <merged-drift-run> <eof next-run dir> <out.json> --recipe <eof smoke dir>
         [--constraints alive] [--pfamily free=0.6948,repro-radar=0.1527,descent-climb=0.1376,routes=0.0149]
         [--seeds 1,2,3,4]
"""
import argparse
import json
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from score_impacts import lookup, surface_arrays  # noqa: E402

EDGES = np.arange(-60.0, 0.0 + 1e-9, 0.001)


def quantiles(h, qs=(0.05, 0.5, 0.95)):
    c = np.cumsum(h)
    if c[-1] <= 0:
        return [None] * len(qs)
    return [round(float(EDGES[min(np.searchsorted(c, q * c[-1]) + 1, EDGES.size - 1)]), 3) for q in qs]


def main(drift_run, nextrun, out, recipe, constraints, pfamily, seeds):
    sys.path.insert(0, recipe)
    from displacement_hist import option_posteriors  # end of flight's recipe, read-only

    import pandas as pd
    cols = [c for c in ("ln_l", "ln_l_h25", "ln_l_h100", "ln_l_h200") if c in pd.read_csv(f"{drift_run}/nodes.csv", nrows=1).columns]
    surfs = {c: surface_arrays(drift_run, c) for c in cols}
    lref = {c: float(np.nanmax(surfs[c][4])) for c in cols}  # one constant per surface, so strata pool on one scale
    acc = {}
    for stratum, pf in pfamily.items():
        for k in seeds:
            d = pathlib.Path(nextrun) / f"next-{stratum}" / f"seed-{k}"
            cache = {}
            kw = {"constraints": tuple(constraints)} if constraints else {}
            for key, p, c in option_posteriors(d, d, **kw):
                w = pf / len(seeds) * p
                lat = c["lat"]
                a = acc.setdefault(key, {"all": np.zeros(EDGES.size - 1), "mass": 0.0, "by": {}})
                ok = np.isfinite(lat)
                a["all"] += np.histogram(lat[ok], EDGES, weights=w[ok])[0]
                a["mass"] += float(w.sum())
                for col in cols:
                    if col not in cache:
                        cache[col] = lookup(*surfs[col], lat, c["lon"])
                    flag, ll = cache[col]
                    b = a["by"].setdefault(col, {"scored": 0.0, "outside_support": 0.0, "mc_unresolved": 0.0,
                                                 "before": np.zeros(EDGES.size - 1), "after": np.zeros(EDGES.size - 1),
                                                 "sw": 0.0, "sw2": 0.0, "sq": 0.0, "sq2": 0.0})
                    for name, f in (("scored", 1), ("outside_support", 0), ("mc_unresolved", 2)):
                        b[name] += float(w[flag == f].sum())
                    s = flag == 1
                    q = w[s] * np.exp(ll[s] - lref[col])
                    b["before"] += np.histogram(lat[s], EDGES, weights=w[s])[0]
                    b["after"] += np.histogram(lat[s], EDGES, weights=q)[0]
                    b["sw"] += float(w[s].sum()); b["sw2"] += float((w[s] ** 2).sum())
                    b["sq"] += float(q.sum()); b["sq2"] += float((q ** 2).sum())
            print(f"{stratum} seed-{k} done", flush=True)
    res = {"label": "Drift likelihood scored on end-of-flight impacts, strata pooled by P(family). Unscored mass excluded; "
                    "report the scored fraction beside every number.",
           "drift_run": str(drift_run), "impacts": str(nextrun), "constraints": list(constraints),
           "pfamily": pfamily, "seeds": seeds, "options": {}}
    for key, a in acc.items():
        r = {"mixture_lat_p05_p50_p95": quantiles(a["all"]), "by_bandwidth": {}}
        for col, b in a["by"].items():
            m = {n: b[n] / a["mass"] for n in ("scored", "outside_support", "mc_unresolved")}
            m["scored_lat_p05_p50_p95_before"] = quantiles(b["before"])
            m["scored_lat_p05_p50_p95_after"] = quantiles(b["after"])
            m["ess_ratio_drift_weighting"] = (b["sq"] ** 2 / b["sq2"]) / (b["sw"] ** 2 / b["sw2"]) if b["sq2"] > 0 and b["sw2"] > 0 else None
            r["by_bandwidth"][col] = m
        res["options"][key] = r
    pathlib.Path(out).write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("drift_run"); ap.add_argument("nextrun"); ap.add_argument("out")
    ap.add_argument("--recipe", required=True); ap.add_argument("--constraints", default="")
    ap.add_argument("--pfamily", default="free=0.6948,repro-radar=0.1527,descent-climb=0.1376,routes=0.0149")
    ap.add_argument("--seeds", default="1,2,3,4")
    a = ap.parse_args()
    pf = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in a.pfamily.split(",")}
    main(a.drift_run, a.nextrun, a.out, a.recipe, [c for c in a.constraints.split(",") if c], pf, [int(s) for s in a.seeds.split(",")])
