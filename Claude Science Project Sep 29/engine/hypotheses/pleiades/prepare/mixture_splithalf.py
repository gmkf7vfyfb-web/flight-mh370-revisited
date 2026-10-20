"""Split-half Monte Carlo check of the Pléiades conditional on a stratified core run (run C: 8 seeds per stratum).

For each option the strata are mixed by end of flight's 00:19-re-weighted P(family) (ruling C), for the whole run and for each half of
the seeds, over three 4 + 4 partitions (1-4 / 5-8, odd / even, {1,2,5,6} / {3,4,7,8}). Reported: the full value and the split-half
sigma = rms over partitions of (half A - half B) / 2, for the 90 % / 50 % areas under H, the mean under H, the share the searches
leave under H, and the tension (ln S, mean shift). After all searches (Phase 2 + Bluefin-21 + OI 2018 + 2025-26), P + all four COSMO,
both ocean models at equal weight (and GLORYS12 only).

    python mixture_splithalf.py <impacts root> <branch root> <surface dir> <family-evidence json> <out csv> <option> [...]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import branch_eof289 as b  # noqa: E402
import closeup_figure as cf  # noqa: E402
import closeup_styles as cs  # noqa: E402
from branch_figure import hdr_level  # noqa: E402
from rerun_reference import tension  # noqa: E402

PARTS = [((0, 1, 2, 3), (4, 5, 6, 7)), ((0, 2, 4, 6), (1, 3, 5, 7)), ((0, 1, 4, 5), (2, 3, 6, 7))]


def summ(pre, post, L, area, lat, lon):
    LAT, LON = np.meshgrid(lat, lon, indexing="ij")
    m = post * L; s = cf.stats(m, area, LAT, LON, {}); dn = (m / m.sum()) / area
    z = np.zeros_like(area, dtype=bool); t = tension(post, L, area, lat, lon, z, z, z)
    return dict(hdr90_km2=s["hdr90_km2"], hdr50_km2=float(area[dn >= hdr_level(dn, m / m.sum(), 0.5)].sum()),
                mean_lat=s["mean_lat"], mean_lon=s["mean_lon"], search_retains_under_H=float(m.sum() / (pre * L).sum()),
                ln_S=t["ln_S"], mean_shift_nm=t["mean_shift_nm"])


def main(imp, root, surf, fam, out, options):
    imp, root, surf = Path(imp), Path(root), Path(surf)
    mp, models, P, Cm = b.load_fields(surf)
    br = b.build_branch(models, P, Cm)["P+C4"]
    Ls = {"both models": np.nan_to_num(br["both models"]), "GLORYS12 only": np.nan_to_num(br[models[0]])}
    F = json.loads(Path(fam).read_text()); pcore = F["p_core"]
    strata = sorted(pcore)
    rows = []
    for o in options:
        pf = cs.reweighted_pfam(fam, o) or pcore
        H = {}
        for s in strata:
            seeds, pre, post, _, elat, elon = b.histograms(imp / s, root / s / "eval-oi2018-2025", mp, o)
            assert len(seeds) == 8, (s, seeds)
            H[s] = (pre, post)
            print(o, s, flush=True)
        lat = 0.5 * (elat[1:] + elat[:-1]); lon = 0.5 * (elon[1:] + elon[:-1]); area = b.area_km2(np.meshgrid(lat, lon, indexing="ij")[0])

        def mix(idx):
            return (sum(pf[s] * H[s][0][list(idx)].mean(0) for s in strata), sum(pf[s] * H[s][1][list(idx)].mean(0) for s in strata))
        for ln, L in Ls.items():
            full = summ(*mix(range(8)), L, area, lat, lon)
            halves = [(summ(*mix(A), L, area, lat, lon), summ(*mix(B), L, area, lat, lon)) for A, B in PARTS]
            r = dict(option=o, option_name=cs.describe_option(o, short=True), ocean_models=ln,
                     strata=("reweighted-0019" if pf is not pcore else "fixed"), family_key=cs.eof_family_key(o, F["mixtures"]))
            for k, v in full.items():
                d = np.array([(a[k] - bb[k]) / 2 for a, bb in halves])
                r[k] = v; r[f"{k}_splithalf_sd"] = float(np.sqrt((d ** 2).mean()))
                r[f"{k}_half_range"] = float(max(max(a[k], bb[k]) for a, bb in halves) - min(min(a[k], bb[k]) for a, bb in halves))
            rows.append(r)
            print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if not k.endswith("range")}), flush=True)
        pd.DataFrame(rows).to_csv(out, index=False)


if __name__ == "__main__":
    main(*sys.argv[1:6], sys.argv[6:])
