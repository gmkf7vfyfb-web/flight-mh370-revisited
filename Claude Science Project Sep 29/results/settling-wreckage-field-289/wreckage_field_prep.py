"""Resample impacts per 00:19 option for the settling wreckage-field map (settling module, 9 Oct 2026).

Weights: end of flight's option_posteriors (hand-off weight x burst likelihood x log-on lag density for
fuel-exhaustion), imported from hypotheses/end-of-flight/smoke/displacement_hist.py, not reimplemented.
Systematic resampling per seed (seeds pooled with equal weight): 50,000 per seed for none__other, 10,000
per seed otherwise (rng seeds 20261009 / 20261010). Writes field/impacts_in.f64 (14 f64 columns, the input
of settling::tests::wreckage_field). Each repeated impact gets successive settling draws 0, 1, 2, ...
Then: SETTLING_FIELD_IN=field/impacts_in.f64 SETTLING_FIELD_OUT=field/elements.f64 cargo test --release
-p mh370-hypotheses settling::tests::wreckage_field -- --ignored; then wreckage_map.py.
"""
import sys, json, pathlib, numpy as np
from collections import Counter
SM, E = sys.argv[1], pathlib.Path(sys.argv[2])  # end-of-flight smoke dir; end-of-flight engine/runs dir
sys.path.insert(0, SM)
from displacement_hist import option_posteriors
KEYS = ["none__other", "r600_startup-offset__fuel-exhaustion", "r1200_startup-offset__fuel-exhaustion", "both_inflated__fuel-exhaustion"]
VCOLS = ['unix_s', 'latitude_deg', 'longitude_deg', 'velocity_east_mps', 'velocity_north_mps', 'velocity_up_mps', 'flight_path_angle_deg',
         'mass_kg', 'kinetic_energy_j', 'vertical_kinetic_energy_j', 'parent', 'latent:debris_class']
NPER = {"none__other": 50000}; rng = np.random.default_rng(20261009); rng2 = np.random.default_rng(20261010)
pick = {k: [] for k in KEYS}; full = {k: [] for k in KEYS}; ESS = {k: 0.0 for k in KEYS}
for s in (1, 2, 3, 4):
    run = E / f"eof-289-full-s{s}"; sd = run / "bto-bfo" / f"seed-{s}"
    for k, p, c in option_posteriors(run, sd):
        if k not in KEYS: continue
        p = p / p.sum(); ESS[k] += float(1 / np.sum(p ** 2)); nz = np.nonzero(p)[0]; full[k].append((c["lat"][nz], c["lon"][nz], p[nz]))
        n = NPER.get(k, 10000); r = rng2 if k in NPER else rng
        if k in NPER: rng.random()  # the run drew a 10,000 pass from rng first, then replaced it: keep the stream
        u = (r.random() + np.arange(n)) / n; pick[k].append((s, np.minimum(np.searchsorted(np.cumsum(p), u), len(p) - 1)))
tab, uid2, vd2 = [], {}, {k: [] for k in KEYS}
for s in (1, 2, 3, 4):
    run = E / f"eof-289-full-s{s}"; meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    X = np.load(run / "bto-bfo" / f"seed-{s}" / "impacts.npy", mmap_mode="r"); need = {}
    for k in KEYS:
        seen = Counter()
        for i in [i for (ss, i) in pick[k] if ss == s][0].tolist():
            vd2[k].append(((s, i), seen[i])); seen[i] += 1
        for i, m in seen.items(): need[i] = max(need.get(i, 0), m)
    ii = np.array(sorted(need)); A = np.asarray(X[ii][:, [cols[c] for c in VCOLS]], float)
    for r, i in zip(A, ii): uid2[(s, i)] = len(tab); tab.append(np.r_[r, need[i], s])
T2 = np.array(tab); pathlib.Path("field").mkdir(exist_ok=True); T2.astype("<f8").tofile("field/impacts_in.f64")

# Plot, once the elements exist: python3 wreckage_field_prep.py <smoke> <runs> <core reference-289 run.json>
if len(sys.argv) > 3 and pathlib.Path("field/elements.f64").exists():
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    ARCS_JSON = sys.argv[3]; SMOOTH = 0.1; OUTSTEM = "settling-wreckage-field-289"
    el = np.fromfile("field/elements.f64", "<f8").reshape(-1, 8)
    TITLES_W = {"none__other": "(a) 00:19 bursts held out; no log-on cause",
                "r600_startup-offset__fuel-exhaustion": "(b) R600, Holland offset; fuel-exhaustion",
                "r1200_startup-offset__fuel-exhaustion": "(c) R1200, Holland offset; fuel-exhaustion",
                "both_inflated__fuel-exhaustion": "(d) both bursts, inflated; fuel-exhaustion"}
    TITLE = "Where the wreckage rests on the seabed, under four impact PDFs (reference-289): settling barely widens the impact PDF"
    SUB = ("Grey: seabed wreckage PDF (settled mass-weighted; real ocean: GLORYS12V1 column and surface current, ERA5 wind, AusSeabed/GEBCO). Dashed orange: impact PDF, all impacts at full weight.\n"
           "End of flight eof-289-full-s1..4, prior track 289.7°; dive class and glide PROVISIONAL-OVERNIGHT; breakup table PROVISIONAL. Systematically resampled impacts, one settling draw each\n"
           "(200,000 in a, 40,000 in b-d); 0.02° grid, Gaussian 0.1° (6 NM), HPD levels on the smoothed density. Log-on cause fuel-exhaustion = end of flight's log-on lag density.")
    exec(open(pathlib.Path(__file__).with_name("wreckage_map.py")).read())
