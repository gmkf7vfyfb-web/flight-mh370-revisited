"""Early check of one run C stratum (on its READY): every seed loads through wf_standard.columns (compact format), carries the columns
settling and the family split need, and yields the five core option posteriors under +unpowered. Prints one line per seed."""
import sys, pathlib, numpy as np
SM, st_dir = sys.argv[1], pathlib.Path(sys.argv[2]); sys.path.insert(0, SM); sys.path.insert(0, str(pathlib.Path(__file__).parent))
from wf_standard import columns, VCOLS, OPTS, CON
from displacement_hist import option_posteriors
from compact_impacts import family_labels
need = VCOLS + ["latent:onset_mechanism", "latent:control_realised", "latent:recovery_attempted"]
for sd in sorted((p for p in st_dir.glob("seed-*") if p.is_dir()), key=lambda p: int(p.name.split("-")[1])):
    meta, g = columns(sd); n = g("latitude_deg").size
    miss = [c for c in need if c not in meta["impact_columns"] and c not in ("kinetic_energy_j", "vertical_kinetic_energy_j", "unix_s")]
    v = {c: g(c) for c in need}; bad = {c: int((~np.isfinite(v[c])).sum()) for c in VCOLS[:7]}
    f4 = family_labels(v["latent:onset_mechanism"], v["latent:control_realised"], v["latent:recovery_attempted"])["family4_code"]
    keys = {k: float(1 / np.sum((p / p.sum()) ** 2)) for k, p, c in option_posteriors(sd, sd, constraints=(CON,))}
    want = [k + "+" + CON for _, k, _ in OPTS]; got = {k: round(keys[k]) for k in want if k in keys}
    print(sd.name, n, "missing", miss, "nonfinite", {k: x for k, x in bad.items() if x}, "family4", {c: int((f4 == c).sum()) for c in (1, 2, 3, 6)},
          "nan-family", int(np.isnan(f4).sum()), "ESS", got, "absent", [k for k in want if k not in keys], flush=True)
