"""Merge a chunked pilot (node_stride = n, node_offset = 0..n-1) into one run directory.

The chunks share the grid, the environment seeds and the response draws (common random numbers
are keyed by environment seed, not by node), so their node rows concatenate into the surface one
unchunked run would have produced. Summary counts are summed; fractions are weighted by
trajectories; throughput is total particle-steps over total chunk wall time, with the per-chunk
values and thread counts kept, since chunks may have run at different thread counts.

Usage: python merge_chunks.py <pilot-dir> [<out-dir>]   (default out-dir: <pilot-dir>/merged)
"""
import os
import sys
import tomllib

import pandas as pd


def main(pilot, out=None):
    out = out or os.path.join(pilot, "merged")
    chunks = sorted(d for d in os.listdir(pilot) if d.startswith("chunk-"))
    frames, sums = [], []
    for c in chunks:
        with open(os.path.join(pilot, c, "summary.toml"), "rb") as f:
            sums.append(tomllib.load(f))
        frames.append(pd.read_csv(os.path.join(pilot, c, "nodes.csv")))
    df = pd.concat(frames).sort_values("node")
    assert not df.node.duplicated().any(), "a node appears in two chunks"
    s0 = sums[0]
    for s in sums[1:]:
        for k in ("segments", "classes", "grid", "finds", "diffusivity_m2_s", "ocean_model", "level_draws", "env_realisations"):
            assert s[k] == s0[k], f"chunks disagree on {k}"
    traj = [int(s["trajectories"]) for s in sums]
    steps = [float(s["particle_steps"]) for s in sums]
    wall = [float(s["wall_s"]) for s in sums]
    m = dict(s0)
    for k in ("nodes_released", "nodes_scored", "nodes_unresolved", "trajectories"):
        m[k] = str(sum(int(s[k]) for s in sums))
    # Land counts in a chunk summary include nodes the chunk never released; recount from rows.
    m["nodes_land"] = str(int((df.state == "land").sum())) if "state" in df else "n/a"
    for k in ("model_error_fraction", "left_domain_fraction"):
        m[k] = f"{sum(float(s[k]) * t for s, t in zip(sums, traj)) / max(sum(traj), 1):.6f}"
    m["particle_steps"] = f"{sum(steps):.4e}"
    m["wall_s"] = f"{sum(wall):.1f}"
    m["particle_steps_per_s"] = f"{sum(steps) / sum(wall):.4e}"
    m["threads"] = ";".join(str(s["threads"]) for s in sums)
    m["chunks"] = ";".join(f"{c}: {w:.0f} s at {s['threads']} threads, {float(s['particle_steps_per_s']):.3e} steps/s" for c, w, s in zip(chunks, wall, sums))
    os.makedirs(out, exist_ok=True)
    df.to_csv(os.path.join(out, "nodes.csv"), index=False)
    with open(os.path.join(out, "summary.toml"), "w") as f:
        for k, v in m.items():
            if k == "grid":
                f.write("grid = { " + ", ".join(f"{a} = {b}" for a, b in v.items()) + " }\n")
            elif isinstance(v, list):
                f.write(f"{k} = {v!r}\n".replace("'", '"'))
            else:
                f.write(f'{k} = "{v}"\n')
    print(f"{len(chunks)} chunks, {len(df)} node rows -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
