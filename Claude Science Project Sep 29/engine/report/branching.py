"""Compare branching runs against the fixed-population resampler, epoch by epoch.

Davey's scheme lets the population float, so a raw effective sample size is not comparable
across runs: 6,000 out of 100,000 and 6,000 out of 2,000,000 are very different states. Every
figure here is therefore an ESS *fraction* of the live population at that epoch, which is what
the project's other diagnostics already report and what the published threshold discussion is
framed in.

Usage: python report/branching.py <run-dir> [<run-dir> ...]
"""

import json
import pathlib
import sys


def modes(run):
    """Yield every mode record in a run.json, whatever the nesting."""
    stack = [run]
    while stack:
        node = stack.pop()
        if isinstance(node, dict):
            if "mode" in node and "epochs" in node:
                yield node
            stack.extend(node.values())
        elif isinstance(node, list):
            stack.extend(node)


def load(path):
    path = pathlib.Path(path)
    files = sorted(path.glob("**/run.json"))
    if not files:
        raise SystemExit(f"{path}: no run.json")
    return json.loads(files[0].read_text())


def table(run, start_n):
    """Per-epoch ESS fraction and population, pooled over modes and seeds."""
    rows = {}
    for m in modes(run):
        for e in m["epochs"]:
            pop = e.get("population") or start_n
            rows.setdefault(e["epoch"], []).append((e["ess_after_update"] / pop, pop))
    return {k: (sum(f for f, _ in v) / len(v), sum(p for _, p in v) / len(v)) for k, v in rows.items()}


def evidence(run):
    """Total log evidence, log-sum-exp pooled over modes within each seed."""
    import math

    per_seed = {}
    for m in modes(run):
        per_seed.setdefault(m.get("seed", 0), []).append(m["log_evidence"])
    out = []
    for lz in per_seed.values():
        top = max(lz)
        out.append(top + math.log(sum(math.exp(x - top) for x in lz)))
    return out


def main(dirs):
    runs = {pathlib.Path(d).name: load(d) for d in dirs}
    start = {}
    for name, run in runs.items():
        cfg = run.get("config", {})
        ppm = cfg.get("particles_per_mode") or [0]
        start[name] = max(ppm)
    tables = {n: table(r, start[n]) for n, r in runs.items()}
    epochs = list(next(iter(tables.values())).keys())

    width = max(len(n) for n in runs) + 2
    print(f"{'epoch':>8} " + "".join(f"{n:>{width}}" for n in runs))
    print(f"{'':>8} " + "".join(f"{'ESS%  pop':>{width}}" for _ in runs))
    for ep in epochs:
        line = f"{ep:>8} "
        for n in runs:
            frac, pop = tables[n].get(ep, (float("nan"), 0))
            line += f"{frac * 100:>6.2f} {pop / 1000:>6.0f}k".rjust(width)
        print(line)
    print()
    for n, r in runs.items():
        lz = evidence(r)
        span = f" span {max(lz) - min(lz):.3f}" if len(lz) > 1 else ""
        print(f"{n:>{width}}  logZ {' '.join(f'{x:.3f}' for x in lz)}{span}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1:])