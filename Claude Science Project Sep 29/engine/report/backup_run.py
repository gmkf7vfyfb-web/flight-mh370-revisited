"""Checkpoint a long run as each replicate lands, so an interruption costs at most one seed.

Runs are expensive — the fuel-plus-tempering configuration is about ten hours — and the harness
can lose a detached process without warning when the session is torn down (observed 5 October:
a six-tempered-epoch run died at seed 2 of 8 when the app restarted). The engine already writes
each replicate's `final.npy`, `routes.npy` and `diagnostics.json` as that replicate completes, so
the *data* survives; what does not survive is anything held only in memory, and `final.npy` at
504 MB per seed is too large to push anywhere as a routine backup.

This writes a thinned, portable copy instead: a stride-sampled subset of the final particle
columns that matter for the posterior, plus every replicate's diagnostics verbatim. At stride 10
and twelve columns that is 82 MB for eight seeds (measured on best-model-6temper) — small enough to save as an artifact
and mirror to Drive after every seed.

`diagnostics.json` is byte-identical to the corresponding entry of `run.json`'s `replicates`
array (verified), so the per-seed diagnostics collected here are also exactly what is needed to
rebuild a `run.json` for a run that was interrupted before it could write one. See
`rebuild_manifest`.

Usage:  python report/backup_run.py runs/<name> out/<name>-partial.npz [--stride 10] [--watch]
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np

# Columns of final.npy worth keeping for a posterior checkpoint: position, weight, the
# autopilot/mode bookkeeping and the fuel state. Indices follow FINAL_COLUMNS in run.json.
KEEP = ("weight", "latitude_deg", "longitude_deg", "altitude_ft", "mach", "tau_h",
        "turns", "mode", "bias_mean_hz", "origin", "stratum", "fuel_kg")


def seed_dirs(run_dir, case="bto-bfo"):
    """Completed replicates, in seed order. A seed is complete when final.npy exists."""
    base = Path(run_dir) / case
    if not base.is_dir():
        return []
    out = []
    for d in sorted(base.glob("seed-*"), key=lambda p: int(p.name.split("-")[1])):
        if (d / "final.npy").is_file() and (d / "diagnostics.json").is_file():
            out.append(d)
    return out


def columns_of(run_dir):
    """FINAL_COLUMNS from run.json, or from any sibling run that has one."""
    p = Path(run_dir) / "run.json"
    if p.is_file():
        return json.loads(p.read_text())["final_columns"]
    for sib in sorted(Path(run_dir).parent.glob("*/run.json")):
        return json.loads(sib.read_text())["final_columns"]
    raise SystemExit("no run.json anywhere under runs/; cannot resolve final column names")


def thin(run_dir, out_path, stride=10, case="bto-bfo"):
    """Write a thinned npz plus a diagnostics sidecar for every completed replicate."""
    cols = columns_of(run_dir)
    idx = [cols.index(c) for c in KEEP if c in cols]
    names = [c for c in KEEP if c in cols]
    arrays, diags = {}, {}
    for d in seed_dirs(run_dir, case):
        a = np.load(d / "final.npy", mmap_mode="r")
        arrays[d.name] = np.asarray(a[::stride][:, idx], dtype=np.float32)
        diags[d.name] = json.loads((d / "diagnostics.json").read_text())
    if not arrays:
        return []
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out_path, columns=np.array(names), stride=np.int32(stride), **arrays)
    out_path.with_suffix(".diagnostics.json").write_text(json.dumps(diags, indent=1) + "\n")
    return sorted(arrays)


def rebuild_manifest(run_dir, case="bto-bfo", seeds=None):
    """Replace run.json's `replicates` with every completed seed's diagnostics, in seed order.

    For a run assembled from more than one launch — e.g. seed 1 from an interrupted attempt and
    seeds 2-8 from the resume — the final launch's run.json lists only its own seeds. Each
    diagnostics.json is exactly the replicate record the summariser expects, so this reassembles
    the full set from the engine's own per-seed output rather than editing anything by hand.
    Run `mh370 summarise <run-dir>` afterwards.
    """
    run_dir = Path(run_dir)
    manifest = json.loads((run_dir / "run.json").read_text())
    reps = []
    for d in seed_dirs(run_dir, case):
        r = json.loads((d / "diagnostics.json").read_text())
        if seeds is None or r["seed"] in seeds:
            reps.append(r)
    manifest["replicates"] = reps
    manifest["config"]["seeds"] = [r["seed"] for r in reps]
    (run_dir / "run.json").write_text(json.dumps(manifest, indent=1) + "\n")
    return [r["seed"] for r in reps]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("run", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--stride", type=int, default=10)
    ap.add_argument("--case", default="bto-bfo")
    ap.add_argument("--watch", action="store_true",
                    help="keep checkpointing every --every seconds until summary.json appears")
    ap.add_argument("--every", type=int, default=300)
    args = ap.parse_args()

    seen = None
    while True:
        done = thin(args.run, args.out, args.stride, args.case)
        if done != seen:
            print(f"{time.strftime('%H:%M:%S')} checkpointed {len(done)}: {' '.join(done)}",
                  flush=True)
            seen = done
        if not args.watch or (args.run / "summary.json").is_file():
            break
        time.sleep(args.every)


if __name__ == "__main__":
    main()
