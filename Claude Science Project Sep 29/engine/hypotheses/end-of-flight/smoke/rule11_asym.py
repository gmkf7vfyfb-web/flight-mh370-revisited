"""Item 1 rule-11 comparison on the 00:11 arm (00:11 hand-off, run-i-dive recipe, N = 8, 8 seeds): BEFORE = joined V2 J0011 (o13d,
symmetric), AFTER = run-i-asym-0011 (o14 + smoke/asymmetry.toml). Same parents and recipe; the stage's own evidence ln sum_i w_i L_i
(weights normalised within each run), impact latitude median and family shares per D cell, and the AFTER arm re-weighted to the
compensation-off prior 0 and 1 (latent:asymmetry_compensation_off, sampled at 0.5). LABEL: "00:11 arm only (onsets after 00:11)".
    python rule11_asym.py BEFORE_DIR AFTER_DIR OUT_JSON"""
import sys, json, numpy as np
from scipy.special import logsumexp
from joined_v2 import load, cells, family, FAMS

def stats(meta, g, extra_lw=None):
    w = g("weight"); lw = np.log(w / w.sum()) + (0 if extra_lw is None else extra_lw)
    C = cells(meta, g, ""); fam = family(g); lat = g("latitude_deg"); out = {}
    for k, ll in C.items():
        x = lw + ll; fin = np.isfinite(x); lz = float(logsumexp(x[fin])); p = np.exp(x[fin] - lz)
        o = np.argsort(lat[fin]); cw = np.cumsum(p[o])
        out[k] = dict(lnZ=lz, lat50=float(lat[fin][o][np.searchsorted(cw, 0.5)]), ess=float(1 / np.sum(p * p)),
                      **{n: float(p[np.isin(fam[fin], codes)].sum()) for n, codes in FAMS})
    return out

B, A, outp = sys.argv[1:4]; res = {}
for k in range(1, 9):
    mb, gb, _ = load(B, k); ma, ga, ixa = load(A, k)
    off = ga("latent:asymmetry_compensation_off")
    r = {"before": stats(mb, gb), "after": stats(ma, ga)}
    for pr in (0.0, 1.0):
        f = np.where(np.isfinite(off), np.where(off == 1, pr / 0.5, (1 - pr) / 0.5), 1.0)
        with np.errstate(divide="ignore"): r[f"after_compoff_{pr:.0f}"] = stats(ma, ga, np.log(f))
    res[k] = r; print(k, {c: round(r["after"][c]["lnZ"] - r["before"][c]["lnZ"], 3) for c in r["before"]})
agg = {}
for v in ("after", "after_compoff_0", "after_compoff_1"):
    agg[v] = {}
    for c in res[1]["before"]:
        d = np.array([res[k][v][c]["lnZ"] - res[k]["before"][c]["lnZ"] for k in res]); dl = np.array([res[k][v][c]["lat50"] - res[k]["before"][c]["lat50"] for k in res])
        agg[v][c] = dict(dlnZ_mean=float(d.mean()), dlnZ_se=float(d.std(ddof=1) / np.sqrt(len(d))), dlat50_mean=float(dl.mean()), dlat50_se=float(dl.std(ddof=1) / np.sqrt(len(dl))),
                         **{f"d_{n}": float(np.mean([res[k][v][c][n] - res[k]["before"][c][n] for k in res])) for n, _ in FAMS})
json.dump({"per_seed": res, "aggregate": agg}, open(outp, "w"), indent=1)
for v, d in agg.items():
    for c, x in d.items(): print(v, c, "dlnZ %+.3f ± %.3f; dlat50 %+.3f ± %.3f deg; dA1 %+.3f dA2 %+.3f dB %+.3f" % (x["dlnZ_mean"], x["dlnZ_se"], x["dlat50_mean"], x["dlat50_se"], x["d_A1"], x["d_A2"], x["d_B"]))
