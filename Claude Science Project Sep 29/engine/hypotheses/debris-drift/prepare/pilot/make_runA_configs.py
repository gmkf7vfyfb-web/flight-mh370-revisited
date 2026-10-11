"""Generate run A chunk configs (architecture decision 18:35 -0600, 10 Oct, option A).

GlobCurrent: planned 367 production nodes + extension nodes, windage offset drawn per particle U(-0.75 %, -0.60 %).
GLORYS12: extension nodes only (its 367 production nodes are unaffected by audit F1).
Both: same grid, same everything else as production; node_subset with node_subset_outside_extent = true.
Usage: python make-runA-configs.py <extension-nodes.csv> <out dir> [--chunk 96]
"""
import re
import sys

import pandas as pd

ext_csv, out = sys.argv[1], sys.argv[2]
chunk = int(sys.argv[4]) if len(sys.argv) > 4 else 96
planned = sorted(pd.read_csv("repo/Claude Science Project Sep 29/engine/runs/debris-drift-production-glorys12/merged/nodes.csv").node.astype(int))
ext = sorted(pd.read_csv(ext_csv).node.astype(int))
assert not set(ext) & set(planned)
plan = {"globcurrent": sorted(planned + ext), "glorys12": ext}
import os
os.makedirs(out, exist_ok=True)
n = 0
for model, nodes in plan.items():
    base = open(f"prod-cfg2/{model}-0.toml").read()
    base = re.sub(r"^node_stride = .*\n", "", base, flags=re.M)
    base = re.sub(r"^node_offset = .*\n", "", base, flags=re.M)
    parts = [nodes[i:i + chunk] for i in range(0, len(nodes), chunk)]
    for k, part in enumerate(parts):
        extra = f"node_subset = {part}\nnode_subset_outside_extent = true\n"
        if model == "globcurrent":
            extra += "c_wind_product_offset_range = [-0.0075, -0.0060]\n"
        cfg, m = re.subn(r'^output_dir = "\.\./runs/debris-drift-production-' + model + r'/chunk-0"\n',
                         f'output_dir = "../runs/debris-drift-runA-{model}/chunk-{k}"\n' + extra, base, flags=re.M)
        assert m == 1, (model, k)
        open(f"{out}/{model}-{k}.toml", "w").write(f"# run A ({model}, chunk {k} of {len(parts)}): {len(part)} nodes\n" + cfg)
        n += 1
    print(model, len(nodes), "nodes in", len(parts), "chunks")
print(n, "configs")
