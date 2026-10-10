"""Per-impact drift log-likelihood, row-aligned with end of flight's impacts.npy (end-to-end milestone, architecture
15:20 -0600 10 Oct; the same layout as Pleiades' `pleiades-lnL.npy`).

For each <stratum>/seed-<k>/impacts.npy under <eof next-run dir>, writes <out>/<stratum>/seed-<k>/drift-lnL.npy, a numpy
structured array with one row per impact row:
  row (uint32), parent (int32, copied);
  lnL_<model>_h<bw> (float32): ln L(recovered debris | impact at this point, model), interpolated in likelihood exactly as
      interpolate.rs (bilinear over the four corners, land renormalised out, never extrapolated); NaN where not scored;
  state_<model>_h<bw> (uint8): 1 scored, 0 outside the drift surface's support, 2 Monte Carlo unresolved;
  lnL_mean_h<bw> (float32): ln of the equal-weight mean of the two models' likelihoods, ln(0.5 e^a + 0.5 e^b), relative
      scale preserved (normalisation rule 2); NaN unless both are scored.
Models: glorys12 (`<run>/debris-drift-production-glorys12/merged`) and globcurrent (`...-globcurrent/merged`, AS RUN:
GlobCurrent windage not product-relative, audit F1). Bandwidths 50 (default), 25, 100, 200 km.
Absolute scale: each value carries the recovery model's normalising constants; it cancels in every posterior. Unscored rows
are NOT impossible: exclude and count them, never treat as zero likelihood (normalisation rule 3).

Usage: python export_per_impact.py <drift runs dir> <eof next-run dir> <out dir> [--strata next-free,...] [--seeds 1,2,3,4]
"""
import argparse
import hashlib
import json
import os
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from score_impacts import lookup, surface_arrays  # noqa: E402

MODELS = {"glorys12": "debris-drift-production-glorys12/merged", "globcurrent": "debris-drift-production-globcurrent/merged"}
BW = {"h50": "ln_l", "h25": "ln_l_h25", "h100": "ln_l_h100", "h200": "ln_l_h200"}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def main(runs, nextrun, out, strata, seeds):
    surfs = {(m, b): surface_arrays(os.path.join(runs, d), c) for m, d in MODELS.items() for b, c in BW.items()}
    fields = [("row", "u4"), ("parent", "i4")]
    for b in BW:
        for m in MODELS:
            fields += [(f"lnL_{m}_{b}", "f4"), (f"state_{m}_{b}", "u1")]
        fields.append((f"lnL_mean_{b}", "f4"))
    summary = {}
    for st in strata:
        for k in seeds:
            d = pathlib.Path(nextrun) / st / f"seed-{k}"
            meta = json.loads((d / "run.json").read_text())
            cols = {c: i for i, c in enumerate(meta["impact_columns"])}
            X = np.load(d / "impacts.npy", mmap_mode="r")
            n = X.shape[0]
            lat = np.asarray(X[:, cols["latitude_deg"]], float)
            lon = np.asarray(X[:, cols["longitude_deg"]], float)
            A = np.zeros(n, dtype=fields)
            A["row"] = np.arange(n, dtype=np.uint32)
            A["parent"] = np.asarray(X[:, cols["parent"]]).astype(np.int32)
            s = {}
            for b in BW:
                vals = {}
                for m in MODELS:
                    flag, ll = lookup(*surfs[(m, b)], lat, lon)
                    A[f"lnL_{m}_{b}"] = np.where(flag == 1, ll, np.nan).astype(np.float32)
                    A[f"state_{m}_{b}"] = flag.astype(np.uint8)
                    vals[m] = np.where(flag == 1, ll, np.nan)
                    s[f"{m}_{b}"] = {"scored": int((flag == 1).sum()), "outside_support": int((flag == 0).sum()), "mc_unresolved": int((flag == 2).sum())}
                a, c = vals["glorys12"], vals["globcurrent"]
                with np.errstate(invalid="ignore"):
                    A[f"lnL_mean_{b}"] = np.where(np.isfinite(a) & np.isfinite(c), np.logaddexp(a, c) - np.log(2.0), np.nan).astype(np.float32)
            o = pathlib.Path(out) / st / f"seed-{k}"
            o.mkdir(parents=True, exist_ok=True)
            tmp = o / "drift-lnL.npy.tmp"
            with open(tmp, "wb") as f:
                np.save(f, A)
            os.replace(tmp, o / "drift-lnL.npy")
            (o / "COLUMNS.txt").write_text("\n".join(f"{nm}\t{dt}" for nm, dt in fields) + "\n")
            (o / "SHA256SUMS").write_text(f"{sha256(o / 'drift-lnL.npy')}  drift-lnL.npy\n")
            summary[f"{st}/seed-{k}"] = {"rows": n, "impacts_sha256_listed": (d / "SHA256SUMS").read_text().split()[0] if (d / "SHA256SUMS").exists() else None, **s}
            print(f"{st} seed-{k}: {n} rows", flush=True)
    (pathlib.Path(out) / "summary.json").write_text(json.dumps(summary, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("runs"); ap.add_argument("nextrun"); ap.add_argument("out")
    ap.add_argument("--strata", default="next-free,next-repro-radar,next-descent-climb,next-routes")
    ap.add_argument("--seeds", default="1,2,3,4")
    a = ap.parse_args()
    main(a.runs, a.nextrun, a.out, a.strata.split(","), [int(x) for x in a.seeds.split(",")])
