"""Spiral (dive-class) weight sensitivity, brief section 7 / Pete's ruling (50/50 with 25/75 and 75/25).

    python3 spiral_sensitivity.py <out.json> <label>=<terminal-out-dir> ...

Per run and per data option x log-on cause (seed 1 only): ESS, posterior share of divergent-spiral descents,
weighted median impact latitude/longitude, and the weighted median and 90% radius of displacement from the own
00:19:37 position. Weights come from displacement_hist.option_posteriors, so the histograms and this table share
one definition.
"""
import json, pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from displacement_hist import option_posteriors


def wq(x, p, q):
    m = np.isfinite(x); o = np.argsort(x[m]); c = np.cumsum(p[m][o]); c = c / c[-1]
    return float(np.interp(q, c, x[m][o]))


def main():
    out = pathlib.Path(sys.argv[1]); res = {}
    for arg in sys.argv[2:]:
        label, d = arg.split("=", 1); run = pathlib.Path(d)
        meta = json.loads((run / "run.json").read_text())
        seed = sorted(p for p in (run / "bto-bfo").glob("seed-*") if (p / "impacts.npy").exists())[0]
        rec = {"run": str(run), "seed": seed.name, "children": meta["terminal"]["children"],
               "code_revision": meta.get("code_revision"), "options": {}}
        for key, p, c in option_posteriors(run, seed):
            r = np.hypot(c["dn"], c["de"])
            rec["options"][key] = {
                "ess": float(1.0 / np.sum(p ** 2)),
                "divergent_share": float(p[c["spiral_divergent"] > 0.5].sum()),
                "median_lat_deg": wq(c["lat"], p, 0.5), "median_lon_deg": wq(c["lon"], p, 0.5),
                "displacement_nm_50_90": [wq(np.where(c["has"], r, np.nan), p, q) for q in (0.5, 0.9)],
            }
        res[label] = rec
    out.write_text(json.dumps(res, indent=1)); print("wrote", out)


if __name__ == "__main__":
    main()
