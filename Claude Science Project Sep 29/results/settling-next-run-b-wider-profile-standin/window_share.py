"""Stand-in analysis (not module code): weight share of impacts outside settling's old ocean window
[80,112]E x [-45,-18] and outside the wider one [75,115]E x [-45,-10], per stratum, seed and option, full option-posterior weights."""
import sys, json, pathlib, numpy as np
SM = sys.argv[1]; E = pathlib.Path(sys.argv[2]); sys.path.insert(0, SM)
from displacement_hist import option_posteriors
KEYS = ["none__other", "r600-bto__other", "r600_no-offset__other", "r600_no-offset__fuel-exhaustion"]
OLD = (80.0, 112.0, -45.0, -18.0); NEW = (75.0, 115.0, -45.0, -10.0)
def out(lat, lon, w): return ~((lon >= w[0]) & (lon <= w[1]) & (lat >= w[2]) & (lat <= w[3]))
res = {}
for f in ["free", "repro-radar", "descent-climb", "routes"]:
    for s in [1, 2, 3, 4]:
        run = E / f"next-{f}" / f"seed-{s}"
        for k, p, c in option_posteriors(run, run, constraints=("alive",)):
            base = k.split("+")[0]
            if base not in KEYS: continue
            p = p / p.sum(); lat, lon = c["lat"], c["lon"]
            o1, o2 = out(lat, lon, OLD), out(lat, lon, NEW)
            nz = p > 0
            res.setdefault(k, {}).setdefault(f, []).append({"seed": s, "w_out_old": float(p[o1].sum()), "w_out_new": float(p[o2].sum()),
                "n_out_old_nonzero": int((o1 & nz).sum()), "n_out_new_nonzero": int((o2 & nz).sum()), "n_nonzero": int(nz.sum()),
                "max_lat_out_old": float(lat[o1 & nz].max()) if (o1 & nz).any() else None})
        print(f, s, flush=True)
json.dump(res, open(sys.argv[3], "w"), indent=1)
