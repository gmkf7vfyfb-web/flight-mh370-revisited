#!/usr/bin/env python3
"""noise_caveat_imos_gain_check.py - fix C2 (26 Oct 2026): do the IMOS band levels in hydro_data.sqlite include the
frequency-dependent logger gain?

Recomputes the per-record Welch band levels of one or more IMOS records with the module's own reader and calibration
(prepare/imos_noise.py: read_volts, decimate, welch, gain_db, band_mean; sensitivity from data/imos/preregistration.json)
in two ways:
  per_bin   gain G(f) from the logger's calibration record applied per frequency bin (what imos_noise.py line 117 does);
  flat100   one flat gain equal to G(100 Hz) for all bins (what a missing frequency-dependent gain would give).
and compares both with results-data/imos1d/noise_per_recording.csv. Pass (pre-registered): per_bin equals the file within
0.05 dB in every band. Reads the raw .DAT records read-only from the IMOS inputs folder (imos_preregistration.IMOS).

Usage: python noise_caveat_imos_gain_check.py --out <dir> [--files MH370/3315_PerthCanyon/531A728A.DAT ...]
"""
import argparse, json, sys
from pathlib import Path
import numpy as np, pandas as pd

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import imos_noise as N, imos_preregistration as P  # noqa: E402

DEFAULT = ["MH370/3315_PerthCanyon/531A728A.DAT"]


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--files", nargs="*", default=None)
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    pre = json.loads((HERE.parent / "data/imos/preregistration.json").read_text())
    PR = pd.read_csv(HERE.parent / "results-data/imos1d/noise_per_recording.csv")
    files = a.files
    if not files:   # one background record per logger plus the CMST Fig. 1 record
        files = DEFAULT + [PR[PR.logger == lg].file.iloc[len(PR[PR.logger == lg]) // 2] for lg in sorted(PR.logger.unique())]
    rows = []
    for fn in files:
        r = PR[PR.file == fn]
        if r.empty:
            continue
        r = r.iloc[0]; L = pre["loggers"][str(r.logger)]
        calp = next(P.IMOS.glob(f"*/*alibration/{L['cal_file']}")); fg, G = N.gain_db(calp)
        g100 = float(np.interp(100, fg, G))
        f, p = N.welch(N.decimate(N.read_volts(P.IMOS / fn)))
        for mode, cal in (("per_bin", 10 ** ((np.interp(f, fg, G) + L["sens_db"]) / 10)), ("flat100", 10 ** ((g100 + L["sens_db"]) / 10) * np.ones_like(f))):
            pu = p / cal
            for lo, hi in N.BANDS:
                k = f"{lo}-{hi}"; v = float(10 * np.log10(N.band_mean(f, pu, lo, hi)))
                rows.append(dict(logger=int(r.logger), file=fn, mode=mode, band=k, recomputed_db=round(v, 3), file_db=float(r[k]),
                                 diff_db=round(v - float(r[k]), 3)))
    D = pd.DataFrame(rows); D.to_csv(out / "imos_gain_check.csv", index=False)
    pb = D[D["mode"] == "per_bin"]; fl = D[D["mode"] == "flat100"]
    res = dict(n_records=int(pb.file.nunique()), per_bin_max_abs_diff_db=float(pb.diff_db.abs().max()),
               pass_per_bin_within_0_05_db=bool(pb.diff_db.abs().max() <= 0.05),
               flat100_minus_file_by_logger_band={f"{lg} {b}": float(g.diff_db.median()) for (lg, b), g in fl.groupby(["logger", "band"])})
    (out / "imos_gain_check.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
