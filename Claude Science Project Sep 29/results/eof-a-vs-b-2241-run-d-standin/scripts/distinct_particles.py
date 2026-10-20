"""Stand-in diagnostic: effective number of DISTINCT core filter particles behind each arm's posterior. Look-ahead hand-off rows can
repeat a filter particle (oversample 50), so 'effective parents' (per hand-off row, end of flight's measure) can exceed the effective
number of distinct trajectories to 22:41. Reads mini.npz (stand-in) and core's handoff.npy columns mode (6) and particle (12)."""
import json, pathlib, re, sys
import numpy as np
from scipy.special import logsumexp
W = pathlib.Path(__file__).resolve().parents[1]; D = W / "abd"; CORE = pathlib.Path("/Users/pete/Downloads/mh370-exchange/core/next-run-d")
res = {}
for f in sorted(D.glob("*-[AB]-s*/bto-bfo/seed-*/mini.npz")):
    run = f.parents[2].name; m = re.match(r"(next-d-[a-z-]+)-([AB])-s(\d+)", run); st, arm, k = m.group(1), m.group(2), m.group(3)
    H = np.load(CORE / st / "bto-bfo" / f"seed-{k}" / "handoff-m2241" / "handoff.npy", mmap_mode="r")
    key = (H[:, 6].astype(np.int64) << 40) + H[:, 12].astype(np.int64); _, inv = np.unique(key, return_inverse=True)
    z = np.load(f); par = z["parent"].astype(np.int64); r = {"distinct_rows_in_handoff": int(inv.max() + 1), "handoff_rows": int(H.shape[0])}
    w0 = H[:, 0] * np.exp(H[:, 13]); r["handoff_ess_rows"] = float(w0.sum() ** 2 / (w0 ** 2).sum())
    q0 = np.bincount(inv, weights=w0 / w0.sum()); r["handoff_ess_distinct"] = float(1 / (q0 ** 2).sum())
    for opt in ("none", "m0011", "m0011+r600-bto", "m0011+r600/no-offset"):
        a = z["lw"].astype(float) + (0.0 if opt == "none" else z["ll:" + opt].astype(float))
        p = np.exp(a - logsumexp(a)); P = np.bincount(par, weights=p, minlength=H.shape[0]); Q = np.bincount(inv, weights=P)
        r[opt] = {"eff_rows": float(1 / (P ** 2).sum()), "eff_distinct_particles": float(1 / (Q ** 2).sum())}
    res[run] = r
json.dump(res, open(D / "distinct_particles.json", "w"), indent=1)
for k, v in res.items(): print(k, v["distinct_rows_in_handoff"], round(v["handoff_ess_distinct"]), {o: (round(v[o]["eff_rows"]), round(v[o]["eff_distinct_particles"])) for o in ("m0011", "m0011+r600-bto")})
