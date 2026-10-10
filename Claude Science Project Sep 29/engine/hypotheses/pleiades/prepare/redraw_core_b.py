"""Redraw the standard close-ups (colour + seabed, faint points) on core (b) for the three existence constraints:
`alive` (a, earlier reference), `unpowered` (b, reference per ruling ~19:10 UTC B), `silent` (c, declared variant beside (b))."""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams.update({"font.size": 6, "axes.titlesize": 6.5, "axes.labelsize": 6, "xtick.labelsize": 5.5, "ytick.labelsize": 5.5})
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import closeup_styles as cs  # noqa: E402

EXCH = Path("/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run")
FE = EXCH / "summary" / "family-evidence-next-run-b.json"
PF = {"next-free": 0.6948, "next-repro-radar": 0.1527, "next-descent-climb": 0.1376, "next-routes": 0.0149}
BASE = ("core (b): request-17 sampler fix IN, split-half NOT converged; two-tank bookkeeping only; internal-v1 fuel (one-engine flow 2x its "
        "tables); Inmarsat ephemeris; descent idle floor ON; EoF sweep run by an architecture stand-in; PROVISIONAL-OVERNIGHT")
SETS = {"alive": "next-run-b-core", "unpowered": "next-run-b-unpowered", "silent": "next-run-b-silent"}
RUNS, RES = HERE.parents[2] / "runs" / "pleiades", HERE.parents[3] / "results" / "pleiades"
geom, gebco = sys.argv[1], "/Users/pete/Downloads/mh370-ocean-data/gebco/grid/gebco_2026.json"
for con in (sys.argv[2:] or SETS):
    tag = SETS[con]
    T = cs.standard(RUNS / tag, EXCH, geom, gebco, RES / tag / "closeups", plt, PF,
                    [f"none+{con}", f"r600-bto+{con}", f"r600/no-offset+{con}"], BASE, fam_json=str(FE))
    print(con, len(T), flush=True)
