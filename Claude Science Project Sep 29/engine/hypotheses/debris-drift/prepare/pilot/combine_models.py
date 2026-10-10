"""Equal-weight ocean-model SENSITIVITY MIXTURE surface, for diagnostics only.

The deliverable is the per-model surfaces: `ocean-model` is an alternative shared with Pleiades, and the composer
marginalises it jointly, L(x) = sum_m pi_m L(x | m) (brief rule 7-8). This script writes the mixture of two merged
runs on the SAME grid, node by node and column by column, ln(0.5 e^a + 0.5 e^b), so that the scoring diagnostics
can show what the combination does. A node is a value only if it is a value in both models (otherwise the
mixture is undefined there and the node is unresolved); land if land in either.

Usage: python combine_models.py <merged run A> <merged run B> <out dir>
"""
import json
import os
import sys
import tomllib

import numpy as np
import pandas as pd

COLS = ["ln_l", "ln_l_half_a", "ln_l_half_b", "ln_l_h25", "ln_l_h100", "ln_l_h200"]


def main(a, b, out):
    A = pd.read_csv(f"{a}/nodes.csv").set_index("node")
    B = pd.read_csv(f"{b}/nodes.csv").set_index("node")
    assert set(A.index) == set(B.index), "the runs cover different nodes"
    sa, sb = (tomllib.load(open(f"{d}/summary.toml", "rb")) for d in (a, b))
    assert sa["grid"] == sb["grid"], "the runs are on different grids"
    B = B.loc[A.index]
    M = A[["lat_deg", "lon_deg", "component"]].copy()
    land = (A.state == "land") | (B.state == "land")
    for c in [c for c in COLS if c in A and c in B]:
        x, y = A[c].values, B[c].values
        with np.errstate(invalid="ignore"):
            M[c] = np.where(np.isfinite(x) & np.isfinite(y), np.logaddexp(x, y) - np.log(2.0), np.nan)
    M["state"] = np.where(land, "land", np.where(np.isfinite(M["ln_l"]), "value", "unresolved"))
    M["ln_l_model_a"], M["ln_l_model_b"] = A["ln_l"].values, B["ln_l"].values
    os.makedirs(out, exist_ok=True)
    M.reset_index().to_csv(f"{out}/nodes.csv", index=False)
    with open(f"{out}/summary.toml", "w") as f:
        f.write(f"mode = \"sensitivity-mixture (diagnostic; composer marginalises ocean-model)\"\n")
        f.write(f"ocean_model = {json.dumps(sa['ocean_model'] + ' | ' + sb['ocean_model'] + ' (equal weight)')}\n")
        f.write(f"runs = {json.dumps(str(a) + ' | ' + str(b))}\n")
        f.write(f"nodes_scored = \"{int((M.state == 'value').sum())}\"\n")
        f.write("grid = { " + ", ".join(f"{k} = {v}" for k, v in sa["grid"].items()) + " }\n")
    print(f"{len(M)} nodes, {(M.state == 'value').sum()} valued -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
