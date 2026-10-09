"""Negative control (brief section 3, amended sequence item 1): does the model explain why Blackman's
air8 shots were NOT detected at H01, when air9's were?

Blackman et al. (2004), section 4.1: air9 was recorded at H01 at 1,665 km, the "only shots ... clearly
visible in the VLF band at Cape Leeuwin". air8 was not observed at H01, and "blockage of air8 shots is
not known to be significant and H01 noise levels during those shots were similar". air8 WAS recorded
at H08S (Fig. 23 DGS panel), with TL close to air9's.

PROVISIONAL: the environment is the WOA23 + GEBCO_2026 stub (data/stub/, rulings item 5 and H3). The
model construction is identical to air9_tl_validation.py (profiles every 5 km, hard bottom
alternative as the one not rejected by air9, Francois-Garrison, incoherent adiabatic modes, source
at 10 m). The soft bottom is also reported, for completeness.

WHY A DIFFERENCE. The air9 validation found a frequency-dependent residual common to both stations
(r = 0.988), attributed to near-source coupling that the flat half-space does not represent. Within a
station, the difference TL(air8) - TL(air9) cancels that term to the extent that the two shot sites
couple alike. air8 lies in 2,985-3,240 m of water and air9 in 2,710-2,845 m, both on the
Broken-Ridge/Ninetyeast region. Whether they couple alike is NOT known, and this caveat travels with
the result.

PRE-REGISTERED CRITERIA (fixed before the first run; do not edit after looking). Bands: third-octave
centres 16-50 Hz, where air9 was observed at H01 above 3 dB SNR.
  Delta_H01  = median over bands of TL_model(air8 -> H01W) - TL_model(air9 -> H01W)
  Delta_H08S = median over bands of TL_model(air8 -> H08S) - TL_model(air9 -> H08S)
  NEGATIVE CONTROL at H01:
    FOLLOWS        Delta_H01 >= 10 dB  (enough to bury a "clearly visible" stacked air9 arrival)
    DOES NOT       Delta_H01 <= 3 dB
    INCONCLUSIVE   otherwise
  POSITIVE CONTROL at H08S (air8 was detected there, with TL near air9's):
    CONSISTENT     |Delta_H08S| <= 5 dB
    INCONSISTENT   otherwise
  If the negative control "follows" but the positive control is "inconsistent", the model is
  over-predicting loss generally, and the negative control does NOT count as explained.
  A blockage attribution is made only if Delta_H01 is concentrated at the ridge crossing in TL vs
  range: a TL step >= 6 dB across 1,100-1,250 km on the air8 -> H01W path.

Run: python prepare/air8_negative_control.py <stub_dir> <at_bin> <out_dir>
"""

import json
import pathlib
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import air9_tl_validation as V  # noqa: E402
import kraken_tl as K  # noqa: E402

BANDS = [16.0, 20.0, 25.0, 31.5, 40.0, 50.0]
SOURCES = ["air9", "air8"]


def run(stub, at_bin, out):
    rows, curves, wall = [], [], {}
    for src in SOURCES:
        for st, rd in V.RCV.items():
            bathy = pd.read_csv(stub / f"bathy_{src}_{st}.csv")
            ssp = pd.read_csv(stub / f"ssp_{src}_{st}.csv")
            rprof, profiles = V.build_profiles(bathy, ssp)
            L = rprof[-1]
            rr = np.append(np.arange(V.DR_KM, L, V.DR_KM), L)
            for bname, bot in V.BOTTOMS.items():
                t0 = time.time()
                for fc in BANDS:
                    root = f"f{fc:g}".replace(".", "p")
                    wd = out / "work" / f"{src}_{st}_{bname}"
                    K.tl_path(wd, root, fc, profiles, rprof, rr, [10.0], [rd], bot, at_bin, fg=V.FG)
                    s = K.read_shd(wd / f"{root}.shd")
                    x = s["rr_m"] / 1000.0 / 6371.0
                    tl = -20 * np.log10(np.abs(s["p"][0, 0, 0])) + 10 * np.log10(x / np.sin(x))
                    rows.append(dict(source=src, station=st, bottom=bname, fc_hz=fc, range_km=float(L), tl_db=float(tl[-1])))
                    curves.append(pd.DataFrame(dict(source=src, station=st, bottom=bname, fc_hz=fc,
                                                    range_km=s["rr_m"] / 1000.0, tl_db=tl)))
                wall[f"{src}_{st}_{bname}_s"] = round(time.time() - t0, 1)
    return pd.DataFrame(rows), pd.concat(curves), wall


def main(stub, at_bin, out_dir):
    stub, out = pathlib.Path(stub), pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    m, c, wall = run(stub, at_bin, out)
    m.to_csv(out / "air8_control_model.csv", index=False)
    c.to_csv(out / "air8_control_tl_vs_range.csv", index=False)
    res = {}
    for bname in V.BOTTOMS:
        p = m[m.bottom == bname].pivot_table(index=["station", "fc_hz"], columns="source", values="tl_db")
        d = (p["air8"] - p["air9"]).unstack(0)
        dh01, dh08 = float(np.median(d["H01W"])), float(np.median(d["H08S"]))
        neg = "FOLLOWS" if dh01 >= 10 else ("DOES NOT FOLLOW" if dh01 <= 3 else "INCONCLUSIVE")
        pos = "CONSISTENT" if abs(dh08) <= 5 else "INCONSISTENT"
        cc = c[(c.bottom == bname) & (c.source == "air8") & (c.station == "H01W")]
        step = []
        for fc in BANDS:
            g = cc[cc.fc_hz == fc]
            a = g[(g.range_km >= 1050) & (g.range_km <= 1100)].tl_db.mean()
            b = g[(g.range_km >= 1250) & (g.range_km <= 1300)].tl_db.mean()
            spread = 10 * np.log10(1275.0 / 1075.0)
            step.append(b - a - spread)
        res[bname] = dict(delta_H01_by_band=d["H01W"].round(2).to_dict(), delta_H08S_by_band=d["H08S"].round(2).to_dict(),
                          delta_H01_median_db=round(dh01, 2), delta_H08S_median_db=round(dh08, 2),
                          negative_control=neg, positive_control=pos,
                          explained=(neg == "FOLLOWS" and pos == "CONSISTENT"),
                          ridge_step_db_by_band=dict(zip(BANDS, np.round(step, 2))),
                          ridge_step_median_db=round(float(np.median(step)), 2),
                          blockage_attribution=bool(np.median(step) >= 6))
    res["wall_s"] = wall
    res["total_wall_s"] = round(time.time() - t0, 1)
    json.dump(res, open(out / "air8_control_verdict.json", "w"), indent=1, default=float)
    print(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main(*sys.argv[1:4])
