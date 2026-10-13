"""Effective parents per family cell (within arm), min over seeds, from the stand-in mini.npz files."""
import numpy as np, pathlib, json, re
from scipy.special import logsumexp
W = pathlib.Path(__file__).resolve().parents[1]; res = {}
for f in sorted(W.glob("abd/next-d-*-[AB]-s*/bto-bfo/seed-*/mini.npz")):
    m = re.match(r"(next-d-[a-z-]+)-([AB])-s(\d+)", f.parents[2].name); st, arm = m.group(1), m.group(2)
    z = np.load(f); par = z["parent"].astype(np.int64); fam = z["family_code"]
    for opt in ("none", "m0011", "m0011+r600-bto", "m0011+r600/inflated"):
        a = z["lw"].astype(float) + (0 if opt == "none" else z["ll:" + opt].astype(float))
        for c in ((1, 2, 4) if arm == "A" else (3, 5)):
            b = np.where(fam == c, a, -np.inf)
            if not np.isfinite(b).any(): continue
            p = np.exp(b - logsumexp(b)); P = np.bincount(par, weights=p)
            k = f"{st}|{arm}|{c}|{opt}"; res[k] = min(res.get(k, 1e12), float(1 / (P ** 2).sum()))
json.dump(res, open(W / "abd/family_ess.json", "w"), indent=1)
for k, v in res.items():
    if "|none" not in k: print(k, round(v))
