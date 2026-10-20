"""Pléiades per-impact columns (exchange format v2, build_columns.build_seed) for the run J northern supplement (order B2, 20 Oct 2026).

Written: (1) end of flight's reduced rule-B table `reduced/impacts-ruleB.npz` (2,408,038 rows; row-aligned; the file end of flight
tells downstream modules to use); (2) the A1 conditional passes `north-k2-a1branch/seed-1001..1016` and `run-j-a1outside/seed-1..8`.
The full-row folders north-k2, north-k2b and their xd256 groups (about 150 M rows, about 8 GB in this format) are NOT written: over
the 3 GB cap. Their H factor is the same exact cell lookup and is applied on the fly by score_supplement.py.
The format's `seed` field is one byte: supplement seeds are stored as seed - 1000 (1..16); the reduced table stores seed 0 and
parent = handoff_row (use the row index to align).

    python columns_supplement.py OUT_ROOT
"""
import shutil
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[1] / "end-of-flight" / "smoke"))
import build_columns as BC  # noqa: E402
import branch_eof289 as b  # noqa: E402

X = Path("/Users/pete/Downloads/mh370-exchange")
SUP = X / "end-of-flight/run-j-supplement"
SURF = X / "pleiades/run-j/surfaces"
ST = "run-j-waypoints"


def main(out):
    out = Path(out); mp, models, P, Cm = b.load_fields(SURF); lines = []
    z = np.load(SUP / "reduced/impacts-ruleB.npz")
    def g(n):   # reduced table: parent = handoff_row; prior weight (build stats only) = exp(lnw:comb/D0)
        if n == "parent": return np.asarray(z["handoff_row"], np.float64)
        if n == "weight": return np.exp(np.asarray(z["lnw:comb/D0"], np.float64))
        return np.asarray(z[n], np.float64)
    stat, line = BC.build_seed(Path("seed-0"), ST, out / "reduced", (mp, P, Cm), g=g); lines.append((line, "reduced"))
    for folder, seeds, off in (("north-k2-a1branch", range(1001, 1017), 1000), ("run-j-a1outside", range(1, 9), 0)):
        for k in seeds:
            free = shutil.disk_usage("/Users/pete").free / 2 ** 30
            if free < 6:
                print("PAUSED disk", free); return
            sd = SUP / folder / f"seed-{k}"
            from compact_impacts import load   # end of flight's reader (on sys.path through build_columns / compact_eval)
            meta, gg = load(sd)
            fake = Path(f"seed-{k - off}")   # a name only: build_seed reads the seed number from it (rows come from gg)
            stat, line = BC.build_seed(fake, ST, out / folder, (mp, P, Cm), g=gg)
            src = out / folder / ST / f"seed-{k - off}"; dst = out / folder / f"seed-{k}"
            src.rename(dst); lines.append((line, folder)); print(folder, k, stat.get("rows"), flush=True)
        # the now-empty <folder>/run-j-waypoints/ directory is left in place (nothing is deleted under /Users/pete)
    (out / "columns-build-lines.txt").write_text("\n".join(f"{f}\t{l}" for l, f in lines) + "\n")


if __name__ == "__main__":
    main(sys.argv[1])
