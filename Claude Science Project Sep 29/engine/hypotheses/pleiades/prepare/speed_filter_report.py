"""Weight removed by the infeasible-speed filter (architecture ruling 20:35 -0600 10 Oct, 1(C)): impacts with contact speed above
1.25 VMO = 212 m/s, per stratum and per end-of-flight family code, without H (flight posterior) and under H (Pléiades + all four COSMO,
both ocean models, v2 columns), for each 00:19 option.

    python speed_filter_report.py <impacts root> <v2 columns dir> <out csv> [stratum ...]
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import compact_eval as ce  # noqa: E402
from hydro_sources import option_weights  # noqa: E402

VMAX = 212.0
OPTIONS = ["none+unpowered", "r600-bto+unpowered", "r600/no-offset+unpowered"]
FAMILY = {1: "A1 onset at exhaustion, uncontrolled", 2: "A2 onset at exhaustion, controlled", 3: "B deliberate, ditching approach",
          4: "A controlled then lost", 5: "B control lost en route", 6: "deliberate then no intervention"}


def main(imp, cols, out, strata):
    imp, cols = Path(imp), Path(cols)
    strata = strata or sorted(d.name for d in imp.iterdir() if d.is_dir() and ce.seed_dirs(d))
    rows = []
    for st in strata:
        for sd in ce.seed_dirs(imp / st):
            c, g, n = ce.seed_reader(sd)
            spd = np.sqrt(g("velocity_east_mps") ** 2 + g("velocity_north_mps") ** 2 + g("velocity_up_mps") ** 2)
            fam = g("family_code").astype(int) if "family_code" in c else np.zeros(n, int)
            R = np.load(cols / st / sd.name / "pleiades-lnL.npy", mmap_mode="r")
            LH = np.where(R["not_computed"].astype(bool), 0.0, np.exp(np.asarray(R["lnL_both_mean"], float)))
            fast = spd > VMAX
            for o in OPTIONS:
                w = option_weights(sd, o)
                for f in sorted(set(fam.tolist())) + ["all"]:
                    sel = np.ones(n, bool) if f == "all" else fam == f
                    rows.append(dict(stratum=st, seed=sd.name, option=o, family_code=f, family=FAMILY.get(f, "all" if f == "all" else str(f)),
                                     share_of_option_weight=float(w[sel].sum()), removed_without_H=float(w[sel & fast].sum() / max(w[sel].sum(), 1e-300)),
                                     removed_under_H=float((w * LH)[sel & fast].sum() / max((w * LH)[sel].sum(), 1e-300))))
            print(st, sd.name, flush=True)
    T = pd.DataFrame(rows); T.to_csv(out, index=False)
    S = T.groupby(["stratum", "option", "family_code", "family"])[["share_of_option_weight", "removed_without_H", "removed_under_H"]].mean().reset_index()
    S.to_csv(str(out).replace(".csv", "-mean.csv"), index=False)
    print(S[S.family_code.astype(str) == "all"].to_string(index=False))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
