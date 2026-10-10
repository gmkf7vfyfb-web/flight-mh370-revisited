"""Draw settling-wreckage-field-289-priorities.{pdf,png,json} from field/{A,B}_{impacts,draws,elements} (settling, 9 Oct 2026).

    python3 wreckage_field_prep_keys.py <smoke> <runs> A none__other 50000 20261010
    python3 wreckage_field_prep_keys.py <smoke> <runs> B r600_no-offset__fuel-exhaustion,both_startup-offset__fuel-exhaustion,both_no-offset__other 10000 20261011
    SETTLING_FIELD_IN=field/<T>_impacts.f64 SETTLING_FIELD_OUT=field/<T>_elements.f64 cargo test --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored   (T = A, B)
    python3 wreckage_map_priorities_run.py <smoke> <runs> <core runs/reference-289/run.json>
"""
import sys, os, json, pathlib, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
SM, E, ARCS_JSON = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3]
sys.path.insert(0, SM); sys.path.insert(0, str(pathlib.Path(__file__).parent))
from displacement_hist import option_posteriors
KEYS = ["none__other", "r600_no-offset__fuel-exhaustion", "both_startup-offset__fuel-exhaustion", "both_no-offset__other"]
RUN = os.environ.get("WF_RUN_PATTERN", "eof-289-full-s{s}"); SEEDDIR = os.environ.get("WF_SEED_PATTERN", "bto-bfo/seed-{s}")
SEEDS = [int(x) for x in os.environ.get("WF_SEEDS", "1,2,3,4").split(",")]
KEYS = os.environ.get("WF_KEYS", ",".join(KEYS)).split(",")
meta0 = json.loads((E / RUN.format(s=SEEDS[0]) / "run.json").read_text())
TRACK = meta0["config"]["prior"]["track_deg"]; SRCRUN = meta0.get("source_run"); LABEL = os.environ.get("WF_LABEL", "reference-289")
CON = os.environ.get("WF_CONSTRAINT", "")  # "" (plain) or end of flight's "alive" / "silent" (PROVISIONAL-OVERNIGHT)
SUFFIX = f"+{CON}" if CON else ""
full = {k: [] for k in KEYS}; ESS_CON = {k: 0.0 for k in KEYS}
for s in SEEDS:
    run = E / RUN.format(s=s)
    for k, p, c in option_posteriors(run, run / SEEDDIR.format(s=s), constraints=(CON,) if CON else ()):
        if k.endswith(SUFFIX) and k[:len(k) - len(SUFFIX)] in KEYS and (CON or "+" not in k):
            k = k[:len(k) - len(SUFFIX)]
            p = p / p.sum(); nz = np.nonzero(p)[0]; full[k].append((c["lat"][nz], c["lon"][nz], p[nz])); ESS_CON[k] += float(1 / np.sum(p ** 2))
SRC, ESS = {}, {}
for tag in ("A", "B"):
    T = np.fromfile(f"field/{tag}_impacts.f64", "<f8").reshape(-1, 14); EL = np.fromfile(f"field/{tag}_elements.f64", "<f8").reshape(-1, 8)
    z = np.load(f"field/{tag}_draws.npz")
    for j, k in enumerate(z["keys"].tolist()):
        rows, dr = z[f"rows_{j}"], z[f"draws_{j}"]
        if CON == "alive":  # rejection from the plain resample: keep impacts after 00:19:37.443 (end of flight's T_M0019B)
            from displacement_hist import T_M0019B
            keep = T[rows, 0] > T_M0019B; rows, dr = rows[keep], dr[keep]
        elif CON:
            raise SystemExit(f"constraint {CON} needs its own resample (it reweights, not only truncates)")
        SRC[k] = (T, rows, dr, EL); ESS[k] = ESS_CON[k]
ESS_MIN = 1000; SMOOTH = 0.1; OUTSTEM = os.environ.get("WF_OUTSTEM", "settling-wreckage-field-289-priorities")
TITLES_W = {"none__other": "(a) Held out: no 00:19 BFO; no log-on cause",
            "r600_no-offset__fuel-exhaustion": "(b) R600 as observed, no offset (as Ashton); fuel-exh.",
            "both_startup-offset__fuel-exhaustion": "(c) Holland H1: both bursts, start-up offset; fuel-exh.",
            "both_no-offset__other": "(d) Holland H2: both bursts, no offset; other"}
TITLE = f"Seabed wreckage PDF under the four 00:19 priority hypotheses ({LABEL}{', ' + SUFFIX + ' (PROVISIONAL-OVERNIGHT)' if CON else ''})"
RUNLABELS = os.environ.get("WF_RUN_LABELS", "uncorrected fuel (fuel-model audit F1-F14 open)") + (f"; {SUFFIX}: airborne at 00:19:37.443 (end of flight, PROVISIONAL-OVERNIGHT), applied by rejection to the plain resample" if CON == "alive" else "")
SAMPLES = os.environ.get("WF_SAMPLES", "(200,000 in a; 40,000 in b-d).")
SUB = ("Grey: seabed wreckage PDF, weighted by settled mass (afloat pieces have no seabed position and are excluded). Dashed orange: impact PDF, every impact at full weight. Before any seabed-search evidence.\n"
       f"Impacts: end of flight {RUN.format(s='{'+','.join(map(str,SEEDS))+'}')} ({LABEL}, prior track {TRACK}°, source {SRCRUN}), seeds pooled with equal weight; weights = option_posteriors (hand-off × 00:19 burst likelihood,\n"
       "× log-on lag density for fuel-exhaustion). Dive class and Boeing-calibrated glide PROVISIONAL-OVERNIGHT. Settling (hypothesis/settling 9823b4e): real ocean, GLORYS12V1 column (TEOS-10 density) and\n"
       "surface current, ERA5 wind, AusSeabed then GEBCO_2026; breakup table PROVISIONAL; implosion and occupants alternatives off. Systematic resampling, one settling draw per resampled impact\n"
       f"{SAMPLES} Impacts north of 18° S lie outside the ocean window: not computed, excluded (counted in the JSON). 0.02° grid, Gaussian 0.1° (6 NM), HPD on the smoothed density.\n"
       f"NOT ESTIMABLE: pooled impact ESS below {ESS_MIN:,}; such a panel shows where a few dozen impacts lie, not a posterior. Platform: Mac, 2 threads.\nRun labels: {RUNLABELS}.")
exec(open(pathlib.Path(__file__).with_name("wreckage_map_priorities.py")).read())
