"""Drift coverage of end of flight's impacts, and the extension node list that closes the gap (coverage gap G10).

For each <stratum>/seed-<k> present under <eof run dir> (impacts.npy or run C's compact impacts32.npy, read through end
of flight's own recipe, read-only), and each standard 00:19 option under each constraint, it bins the normalised impact
posterior into the drift grid's bilinear cells. A cell is COVERED when all four of its corner nodes are in the node set
(interpolate.rs never extrapolates). Per stratum, option and constraint it reports the weight that is not covered, split
into: off the grid entirely, and on the grid but not covered by the planned nodes.

The extension list is the union, over every stratum x option x constraint, of the corner nodes of the smallest set of
cells (taken in order of mass) that brings the covered weight to >= --target of that stratum's posterior. A union per
stratum guarantees the target for any P(family) mixture. Off-grid weight cannot be covered on this grid; it is reported.

Usage: python coverage_nodes.py <planned nodes.csv> <planned summary.toml> <eof run dir> <recipe dir> <out dir>
         [--target 0.99] [--constraints alive,unpowered]
Writes <out>/coverage.csv (one row per stratum x seed-pool x option) and <out>/extension-nodes.csv.
"""
import argparse
import json
import os
import pathlib
import sys
import tomllib

import numpy as np
import pandas as pd

STANDARD = {"none__other": "00:19 Held Out", "r600-bto__other": "00:19 R600 BTO Only", "r600_no-offset__other": "00:19 R600 BTO + Raw BFO",
            "both_startup-offset__fuel-exhaustion": "00:19 Holland H1", "both_no-offset__other": "00:19 Holland H2"}


def main(nodes_csv, summary_toml, run, recipe, out, target, constraints):
    sys.path.insert(0, recipe)
    from displacement_hist import option_posteriors  # end of flight's recipe, read-only

    g = tomllib.load(open(summary_toml, "rb"))["grid"]
    nlat, nlon = int(g["nlat"]), int(g["nlon"])
    planned = set(pd.read_csv(nodes_csv).node.astype(int))
    ncell = (nlat - 1) * (nlon - 1)

    def corners(c):
        i, j = divmod(int(c), nlon - 1)
        return (i * nlon + j, (i + 1) * nlon + j, i * nlon + j + 1, (i + 1) * nlon + j + 1)

    covered_cell = np.array([all(n in planned for n in corners(c)) for c in range(ncell)])
    acc = {}  # (stratum, option) -> [cellmass, offgrid, seeds]
    run = pathlib.Path(run)
    for st in sorted(d for d in os.listdir(run) if (run / d).is_dir()):
        for sd in sorted(d for d in os.listdir(run / st) if d.startswith("seed-") and (run / st / d / "run.json").exists()):
            D = run / st / sd
            if not ((D / "impacts.npy").exists() or (D / "impacts32.npy").exists()):
                continue
            for key, p, c in option_posteriors(D, D, constraints=tuple(constraints)):
                base, _, con = key.partition("+")
                if base not in STANDARD or (constraints and not con):
                    continue
                lat, lon = c["lat"], c["lon"]
                fi = (lat - g["lat0"]) / g["dlat"]; fj = (lon - g["lon0"]) / g["dlon"]
                ok = (fi >= 0) & (fj >= 0) & (fi <= nlat - 1) & (fj <= nlon - 1) & np.isfinite(fi) & np.isfinite(fj)
                i = np.minimum(np.floor(np.where(ok, fi, 0)).astype(int), nlat - 2)
                j = np.minimum(np.floor(np.where(ok, fj, 0)).astype(int), nlon - 2)
                cm = np.bincount((i * (nlon - 1) + j)[ok], weights=p[ok], minlength=ncell)
                a = acc.setdefault((st, f"{STANDARD[base]} +{con}" if con else STANDARD[base]), [np.zeros(ncell), 0.0, 0])
                a[0] += cm; a[1] += float(p[~ok].sum()); a[2] += 1
            print(f"{st} {sd} done", flush=True)
    rows, need = [], set()
    for (st, opt), (cm, off, ns) in sorted(acc.items()):
        cm, off = cm / ns, off / ns  # equal weight per seed within a stratum
        tot = cm.sum() + off
        order = np.argsort(-cm); cum = np.cumsum(cm[order]) / tot
        reach = min(target, float(cum[-1]) - 1e-12)
        k = int(np.searchsorted(cum, reach)) + 1
        add = {n for c in order[:k] for n in corners(c)} - planned
        need |= add
        rows.append({"stratum": st, "seeds": ns, "option": opt, "off_grid": off / tot, "not_covered_on_grid": float(cm[~covered_cell].sum() / tot),
                     "not_computed_planned": float((off + cm[~covered_cell].sum()) / tot), "nodes_needed_for_target": len(add),
                     "covered_after": float(sum(cm[c] for c in np.nonzero(cm)[0] if all(n in planned | add for n in corners(c))) / tot)})
    os.makedirs(out, exist_ok=True)
    pd.DataFrame(rows).to_csv(f"{out}/coverage.csv", index=False)
    ext = pd.DataFrame({"node": sorted(need)})
    ext["lat_deg"] = (ext.node // nlon) * g["dlat"] + g["lat0"]; ext["lon_deg"] = (ext.node % nlon) * g["dlon"] + g["lon0"]
    ext.round(5).to_csv(f"{out}/extension-nodes.csv", index=False)
    json.dump({"planned_nodes": len(planned), "extension_nodes": len(need), "target": target, "constraints": constraints,
               "strata": sorted({s for s, _ in acc})}, open(f"{out}/summary.json", "w"), indent=1)
    print(f"extension nodes: {len(need)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a in ("nodes_csv", "summary_toml", "run", "recipe", "out"):
        ap.add_argument(a)
    ap.add_argument("--target", type=float, default=0.99); ap.add_argument("--constraints", default="alive,unpowered")
    a = ap.parse_args()
    main(a.nodes_csv, a.summary_toml, a.run, a.recipe, a.out, a.target, [c for c in a.constraints.split(",") if c])
