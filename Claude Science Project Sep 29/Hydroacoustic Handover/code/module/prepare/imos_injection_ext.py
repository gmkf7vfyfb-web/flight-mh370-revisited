"""EXTENSION of item 3 stage A (imos_injection.py, pre-registered eb83b31), NOT pre-registered: the same design
on an SNR grid of 22.5-40 dB (step 2.5), because the pre-registered grid (-5..20 dB) ended below the
alpha = 0.005 transition at 3376 and 3250 (P_D <= 0.02 up to 17.5 dB), leaving the logistic fit unidentified.
Same background, templates, detectors, thresholds, window, N_INJ; seed 20261010 (independent draws). The
logistic fits are then refitted on the union of both grids. The pre-registered results stand as reported.
Usage: python imos_injection_ext.py <stageA_dir> <out_dir> <background_root>"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).parent))
import imos_injection as I  # noqa: E402


def refit(res):
    fits = {}
    for (cid, tn, det, a), g in res.groupby(["logger", "template", "detector", "alpha"]):
        def nll(th):
            z = np.clip(-(g.snr_db.values - th[0]) / max(th[1], 0.05), -50, 50)
            p = np.clip(1 / (1 + np.exp(z)), 1e-9, 1 - 1e-9)
            return -np.sum(g.k * np.log(p) + (g.n - g.k) * np.log(1 - p))
        best = min((minimize(nll, [x0, 2.0], method="Nelder-Mead") for x0 in [5.0, 15.0, 25.0, 35.0]), key=lambda r: r.fun)
        th = best.x
        top = g[g.snr_db == g.snr_db.max()].pd.iloc[0]
        fits[f"{cid}|{tn}|{det}|{a}"] = dict(snr50=float(th[0]), snr90=float(th[0] + np.log(9) * max(th[1], 0.05)),
                                             identified=bool(top >= 0.9 and g.pd.min() <= 0.1), pd_at_max_snr=float(top))
    return fits


def main(stageA, out, bg):
    I.SNRS = np.arange(22.5, 40.01, 2.5)
    I.SEED = 20261010
    I.main(out, bg)
    a = pd.read_csv(Path(stageA) / "pd_vs_snr.csv")
    b = pd.read_csv(Path(out) / "pd_vs_snr.csv")
    u = pd.concat([a, b], ignore_index=True).sort_values(["logger", "template", "detector", "alpha", "snr_db"])
    u.to_csv(Path(out) / "pd_vs_snr_union.csv", index=False)
    fits = refit(u)
    s = json.loads((Path(stageA) / "summary.json").read_text())
    s["fits"] = fits
    s["note"] = "fits refitted on the union of the pre-registered grid (-5..20 dB) and the extension (22.5..40 dB)"
    (Path(out) / "summary_union.json").write_text(json.dumps(s, indent=1, default=str))
    f = pd.DataFrame([dict(key=k, **v) for k, v in fits.items()])
    print(f.round(2).to_string(index=False))


if __name__ == "__main__":
    main(*sys.argv[1:4])
