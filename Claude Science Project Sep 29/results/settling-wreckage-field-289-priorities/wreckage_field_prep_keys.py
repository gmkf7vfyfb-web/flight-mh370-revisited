"""(Env: WF_RUN_PATTERN default eof-289-full-s{s}, WF_SEED_PATTERN default bto-bfo/seed-{s}, WF_SEEDS default 1,2,3,4.)
Resample impacts for chosen 00:19 options (settling wreckage-field maps; settling module, 9 Oct 2026).

    python3 wreckage_field_prep_keys.py <end-of-flight smoke dir> <end-of-flight engine/runs> <tag> <key,key,...> <n per seed> <rng seed>

Weights: end of flight's option_posteriors (imported). Systematic resampling per seed, seeds 1-4 pooled with equal weight,
one numpy Generator(<rng seed>) consumed in seed order then option_posteriors order. A repeated impact gets successive
settling draws 0, 1, 2, ... Writes field/<tag>_impacts.f64 (14 f64 columns: the input of settling::tests::wreckage_field)
and field/<tag>_draws.npz (per key: input row and draw index of every resampled impact; pooled ESS).
"""
import sys, os, json, pathlib, numpy as np
from collections import Counter
SM, E, TAG, KEYS, NPER, SEED = sys.argv[1], pathlib.Path(sys.argv[2]), sys.argv[3], sys.argv[4].split(","), int(sys.argv[5]), int(sys.argv[6])
sys.path.insert(0, SM)
from displacement_hist import option_posteriors
VCOLS = ['unix_s', 'latitude_deg', 'longitude_deg', 'velocity_east_mps', 'velocity_north_mps', 'velocity_up_mps', 'flight_path_angle_deg',
         'mass_kg', 'kinetic_energy_j', 'vertical_kinetic_energy_j', 'parent', 'latent:debris_class']
rng = np.random.default_rng(SEED); tab, out = [], {}
RUN = os.environ.get("WF_RUN_PATTERN", "eof-289-full-s{s}"); SEEDDIR = os.environ.get("WF_SEED_PATTERN", "bto-bfo/seed-{s}")
SEEDS = [int(x) for x in os.environ.get("WF_SEEDS", "1,2,3,4").split(",")]
ESS = {k: 0.0 for k in KEYS}; rows = {k: [] for k in KEYS}; draws = {k: [] for k in KEYS}
for s in SEEDS:
    run = E / RUN.format(s=s); sd = run / SEEDDIR.format(s=s)
    meta = json.loads((run / "run.json").read_text()); cols = {c: i for i, c in enumerate(meta["impact_columns"])}
    picks = {}
    for k, p, c in option_posteriors(run, sd):
        if k not in KEYS: continue
        p = p / p.sum(); ESS[k] += float(1 / np.sum(p ** 2))
        u = (rng.random() + np.arange(NPER)) / NPER; picks[k] = np.minimum(np.searchsorted(np.cumsum(p), u), len(p) - 1)
    assert set(picks) == set(KEYS), f"missing options: {set(KEYS) - set(picks)}"
    need, occ = {}, {}
    for k in KEYS:
        seen = Counter(); occ[k] = []
        for i in picks[k].tolist():
            occ[k].append((i, seen[i])); seen[i] += 1
        for i, m in seen.items(): need[i] = max(need.get(i, 0), m)
    X = np.load(sd / "impacts.npy", mmap_mode="r"); ii = np.array(sorted(need)); A = np.asarray(X[ii][:, [cols[c] for c in VCOLS]], float)
    base = len(tab); where = {i: base + j for j, i in enumerate(ii.tolist())}
    for r, i in zip(A, ii): tab.append(np.r_[r, need[i], s])
    for k in KEYS:
        rows[k] += [where[i] for i, _ in occ[k]]; draws[k] += [d for _, d in occ[k]]
pathlib.Path("field").mkdir(exist_ok=True); np.array(tab).astype("<f8").tofile(f"field/{TAG}_impacts.f64")
np.savez(f"field/{TAG}_draws.npz", keys=np.array(KEYS), ess=np.array([ESS[k] for k in KEYS]),
         **{f"rows_{j}": np.array(rows[k]) for j, k in enumerate(KEYS)}, **{f"draws_{j}": np.array(draws[k]) for j, k in enumerate(KEYS)})
print(TAG, len(tab), int(np.array(tab)[:, 12].sum()), {k: round(ESS[k]) for k in KEYS})
