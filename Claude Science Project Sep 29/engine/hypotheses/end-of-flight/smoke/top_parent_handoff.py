"""Diagnostic smoke 2 (Pete, 10 Oct ~18:10 UTC): within-parent saturation of the two-burst options.

Selects the top-K parents by posterior mass under each named option x cause from a finished end-of-flight seed,
and writes a reduced hand-off (handoff.toml only: the terminal stage reads nothing else) holding just those rows,
weights UNCHANGED (so they sum to < 1 and each parent's contribution to Z is directly comparable). The terminal
stage is then re-run on it with many more descents per parent; compare ln Z_top = ln sum_i w_i Lbar_i between the
original 32 descents per parent and the new count. Writes parents.json (selected rows, their original index, and
per-option Z_top from the source run).

Usage (from engine/): python top_parent_handoff.py SRC_SEED_DIR HANDOFF_TOML OUT_DIR K OPTION [OPTION ...]
  e.g. ... next-free/seed-1 .../handoff-m0011/handoff.toml runs/top-free/bto-bfo/seed-1 200 both_no-offset__other both_startup-offset__fuel-exhaustion
"""
import json, pathlib, sys
import numpy as np
from scipy.special import logsumexp
from displacement_hist import option_posteriors


def log_ztop(run, sd, options, keep_parents):
    """ln sum_i w_i Lbar_i over the given parents, per option, from a seed's impacts (log-space)."""
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(sd / "impacts.npy", mmap_mode="r"); par = np.asarray(X[:, cols["parent"]], np.int64)
    out = {}
    for key, p, _ in option_posteriors(run, sd):
        if key in options:
            out[key] = p, par
    return out


def main(src, handoff, outdir, k, options):
    src = pathlib.Path(src); outdir = pathlib.Path(outdir)
    post = log_ztop(src, src, set(options), None)
    chosen = set(); info = {"source": str(src), "k": k, "options": {}}
    for o in options:
        p, par = post[o]
        mass = np.bincount(par, weights=p)
        top = np.argsort(mass)[::-1][:k]
        info["options"][o] = {"top_parents": top.tolist(), "share_of_posterior_in_top": float(mass[top].sum()),
                              "effective_parents": float(mass.sum() ** 2 / (mass ** 2).sum())}
        chosen.update(top.tolist())
    chosen = sorted(chosen); keep = set(chosen)
    outdir.mkdir(parents=True, exist_ok=True)
    head, rows, cur, idx = [], [], None, -1
    with open(handoff) as f:
        for line in f:
            if line.startswith("[[row]]"):
                if cur is not None and idx in keep: rows.append(cur)
                idx += 1; cur = [line]
            elif cur is None:
                head.append(line)
            else:
                cur.append(line)
    if cur is not None and idx in keep: rows.append(cur)
    assert len(rows) == len(chosen), (len(rows), len(chosen))
    with open(outdir / "handoff.toml", "w") as f:
        f.writelines(head)
        for r in rows: f.writelines(r)
    info["rows_written"] = len(rows); info["original_index_of_new_row"] = chosen; info["handoff_rows_total"] = idx + 1
    (outdir / "parents.json").write_text(json.dumps(info, indent=1))
    print(json.dumps({o: {k2: v for k2, v in d.items() if k2 != "top_parents"} for o, d in info["options"].items()}), len(rows))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5:])
