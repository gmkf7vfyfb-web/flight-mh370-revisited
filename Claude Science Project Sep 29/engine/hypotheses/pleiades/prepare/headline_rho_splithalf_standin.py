"""STAND-IN (11 Oct 2026): mixture_splithalf.py with the likelihood set replaced by the rulings' variants (ρ 0 / 0.25 / 0.5 x
GLORYS12 only; ρ 0.25 both models) plus the module's hook 'both models' for a reproduction check against its splithalf.csv.
Everything else is mixture_splithalf.main unchanged (same seeds, partitions, re-weighted strata, summ()). For the module to review.

    python headline_rho_splithalf_standin.py <impacts root> <branch root> <surface dir> <family-evidence json> <out csv> <option> [...]
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import branch_eof289 as b  # noqa: E402
import closeup_styles as cs  # noqa: E402
from mixture_splithalf import PARTS, summ  # noqa: E402
from headline_rho_standin import VARIANTS, rho_L  # noqa: E402


def main(imp, root, surf, fam, out, options):
    imp, root, surf = Path(imp), Path(root), Path(surf)
    mp, models, P, Cm = b.load_fields(surf)
    br = b.build_branch(models, P, Cm)["P+C4"]
    Ls = {"hook both models (check)": np.nan_to_num(br["both models"])}
    Ls.update({k: rho_L(surf, r, mo) for k, r, mo in VARIANTS})
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
            r = dict(option=o, option_name=cs.describe_option(o, short=True), variant=ln,
                     strata=("reweighted-0019" if pf is not pcore else "fixed"), family_key=cs.eof_family_key(o, F["mixtures"]))
            for k, v in full.items():
                d = np.array([(a[k] - bb[k]) / 2 for a, bb in halves])
                r[k] = v; r[f"{k}_splithalf_sd"] = float(np.sqrt((d ** 2).mean()))
                r[f"{k}_half_range"] = float(max(max(a[k], bb[k]) for a, bb in halves) - min(min(a[k], bb[k]) for a, bb in halves))
            rows.append(r)
            print(json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if not k.endswith("range")}), flush=True)
        del H
        pd.DataFrame(rows).to_csv(out, index=False)


if __name__ == "__main__":
    main(*sys.argv[1:6], sys.argv[6:])
