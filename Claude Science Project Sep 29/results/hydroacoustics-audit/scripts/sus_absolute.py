"""Audit C4, absolute part (SUS 2003): predicted source spectra from Gaspin & Shuler (1971) scored against the
audit's traced received spectra (data/sus_bands.csv, from sus_score.py) and the module's propagation
(data/sus_tl.csv, from sus_tl.py with the module's KRAKEN wrapper). Pre-registered criteria: criteria.md (940f1a3).

Source routes (both declared before scoring; neither is fitted to SUS or hydrophone data):
  A (primary)  time-similitude scaling of G&S Table 3 1.8-lb 800-ft spectrum (the depth correction G&S themselves
               apply to the Squaw shots, para 7.5): E(f; Z) = E800(f s) + 20 log10 s, s = ((800+33)/(z+33))^(5/6).
               Bands with f s below the 11-14 Hz band are extrapolated at the slope of the two lowest bands (flagged).
  B (check)    re-implementation of the G&S Table 2 construction at the SUS depth (gs_reconstruct.py),
               shape option kappa = 4, sin^2 negative phases (best reproduction of Table 3 at 800 ft).
Conversion: SL(1 m) [dB re 1 uPa^2 s/Hz] = E [dB re 1 erg/cm^2/Hz at 100 yd] + 10 log10(rho c * 1e10) + 20 log10(91.44).

Residual r_b = implied_sl_db - SL_pred_b  (= observed RL - model RL).  C4 LEVEL thresholds 4 / 7 dB, SLOPE 1.5 / 3,
SHAPE 3 / 5.  Detection consistency uses predicted S/N_b = SL_pred - TL - 10 log10(6 s) - noise_b (signal-to-noise).

Usage: python sus_absolute.py <audit_dir> <gs_dir> <out_dir>
"""
import json
import sys

import numpy as np
import pandas as pd

AUD, GSD, OUT = sys.argv[1:4]
sys.path.insert(0, f"{AUD}/scripts"); sys.path.insert(0, GSD)
from air9_audit import stats, grade  # noqa: E402  (audit helpers, unchanged)
import gs_reconstruct as G  # noqa: E402

BANDS = [5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 31.5, 40.0, 50.0, 63.0]
CONV = 10 * np.log10(G.RHOC * 1e10) + 20 * np.log10(91.44)
FT = 1 / 0.3048
# 1.8-lb shots at sites A6-A11 (Blackman Table 5); detection status read from App. B Figs B6-B10 (printed pp. 28-31)
SHOTS = {"A6sus2": ("A6", 610.0, {"H01W": "ND?", "H08S": "D"}), "A6sus3": ("A6", 915.0, {"H01W": "D", "H08S": "D"}),
         "A7sus2": ("A7", 610.0, {"H01W": "D", "H08S": "D"}), "A7sus3": ("A7", 915.0, {"H01W": "D", "H08S": "D"}),
         "A8sus2": ("A8", 610.0, {"H01W": "D", "H08S": "D"}), "A8sus2b": ("A8", 610.0, {"H01W": "D", "H08S": "D"}),
         "A9sus3": ("A9", 915.0, {"H01W": "D", "H08S": "D"}), "A10sus3": ("A10", 915.0, {"H01W": "D", "H08S": "D"})}
NOISE_SUB = {("A6sus3", "H01W"): "A6sus2", ("A7sus2", "H08S"): "A7sus3"}   # panel not traced: sibling shot's noise
T3 = pd.read_csv(f"{GSD}/gs1971_table3_third_octave.csv")
LF = np.log10(T3.fc_nominal_hz.values); E800 = T3.e_1p8lb_800ft.values
LOW_SLOPE = (E800[1] - E800[0]) / (LF[1] - LF[0])


def sl_route_a(fc, z_m, low_slope=LOW_SLOPE):
    s = ((800 + 33) / (z_m * FT + 33)) ** (5 / 6); x = np.log10(fc * s)
    e = np.interp(x, LF, E800) if x >= LF[0] else E800[0] + low_slope * (x - LF[0])
    return e + 20 * np.log10(s) + CONV, ("extrap" if x < LF[0] else "interp"), fc * s


_B = {}


def sl_route_b(fc, z_m, kappa=4.0, neg="sin2"):
    k = (z_m, kappa, neg)
    if k not in _B:
        _B[k] = G.pulse(1.8, z_m * FT, kappa=kappa, neg=neg)
    t, x, p = _B[k]
    return G.band_db(t, x, fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 40) + CONV


def c4_verdict(s):
    g = dict(level=grade(s["level_median"], 4, 7), slope=grade(s["slope_db_per_oct"], 1.5, 3),
             shape=grade(s["shape_rms"], 3, 5))
    return g, ("FAIL" if "FAIL" in g.values() else ("PASS" if all(v == "PASS" for v in g.values()) else "PARTIAL"))


def main():
    sb = pd.read_csv(f"{AUD}/data/sus_bands.csv"); tl = pd.read_csv(f"{AUD}/data/sus_tl.csv")
    rows = []
    for variant, depth_override in (("base", {}), ("A8sus2b_915m", {"A8sus2b": 915.0})):
        for shot, (site, z, det) in SHOTS.items():
            z = depth_override.get(shot, z)
            for st in ("H01W", "H08S"):
                src = NOISE_SUB.get((shot, st), shot)
                obs = sb[(sb.shot == shot) & (sb.station == st) & (sb.status == "ok")].set_index("fc_hz")
                noi = sb[(sb.shot == src) & (sb.station == st) & (sb.status == "ok")].set_index("fc_hz").noise_db
                g = tl[(tl.site == site) & (tl.station == st) & np.isclose(tl.src_depth_m, z)].set_index("fc_hz").tl_db
                for fc in BANDS:
                    a, flag, fs = sl_route_a(fc, z)
                    a6 = sl_route_a(fc, z, low_slope=6.0 / np.log10(2))[0]
                    a12 = sl_route_a(fc, z, low_slope=12.0 / np.log10(2))[0]
                    b = sl_route_b(fc, z)
                    t_ = g.get(fc, np.nan); n_ = noi.get(fc, np.nan)
                    o = obs.loc[fc] if fc in obs.index else None
                    impl = o.implied_sl_db if o is not None else np.nan
                    snr_obs = o.snr_db if o is not None else np.nan
                    pred_sig = a - t_ - 10 * np.log10(6.0)
                    rows.append(dict(variant=variant, shot=shot, site=site, src_depth_m=z, station=st,
                                     reported=det[st], fc_hz=fc, scaled_fc_800ft_hz=fs, route_a_flag=flag,
                                     sl_pred_a_db=a, sl_pred_a_lo6_db=a6, sl_pred_a_lo12_db=a12, sl_pred_b_db=b,
                                     model_tl_db=t_, noise_db=n_, noise_from=src, obs_snr_db=snr_obs,
                                     implied_sl_db=impl, resid_a_db=impl - a, resid_b_db=impl - b,
                                     pred_rl_psd_db=pred_sig, pred_sn_db=pred_sig - n_,
                                     pred_sn_b_db=b - t_ - 10 * np.log10(6.0) - n_))
    df = pd.DataFrame(rows); df.to_csv(f"{OUT}/sus_absolute_bands.csv", index=False)
    summ = {}
    for variant in ("base", "A8sus2b_915m"):
        dv = df[df.variant == variant]
        for route in ("a", "b"):
            col = f"resid_{route}_db"
            for (shot, st), gdf in dv.groupby(["shot", "station"]):
                v = gdf.dropna(subset=[col])
                if len(v) >= 3:
                    s = stats(list(v.fc_hz), list(v[col])); s["grades"], s["verdict"] = c4_verdict(s)
                    summ[f"{variant}|{route}|{shot}|{st}"] = s
                elif len(v):
                    summ[f"{variant}|{route}|{shot}|{st}"] = dict(n=len(v), level_median=float(np.median(v[col])),
                                                                 f_lo=float(v.fc_hz.min()), f_hi=float(v.fc_hz.max()),
                                                                 verdict="not graded (< 3 bands)")
            for key, sel in (("H01W", dv.station == "H01W"), ("H08S", dv.station == "H08S"),
                             ("610m", dv.src_depth_m == 610.0), ("915m", dv.src_depth_m == 915.0), ("all", dv.station != "")):
                v = dv[sel].dropna(subset=[col])
                if len(v) >= 3:
                    s = stats(list(v.fc_hz), list(v[col])); s["grades"], s["verdict"] = c4_verdict(s)
                    s["pairs"] = int(v.groupby(["shot", "station"]).ngroups); summ[f"{variant}|{route}|pooled|{key}"] = s
            # detection consistency
            sncol = "pred_sn_db" if route == "a" else "pred_sn_b_db"
            det = []
            for (shot, st), gdf in dv.groupby(["shot", "station"]):
                sn = gdf[sncol].dropna(); rep = gdf.reported.iloc[0]
                if sn.empty:
                    det.append(dict(shot=shot, station=st, reported=rep, scored=False)); continue
                mx = float(sn.max()); nd = rep.startswith("ND")
                inc = (nd and mx >= 6.0) or ((not nd) and mx <= -6.0)
                det.append(dict(shot=shot, station=st, reported=rep, scored=True, max_pred_sn_db=mx,
                                band_of_max=float(gdf.loc[sn.idxmax(), "fc_hz"]), inconsistent=bool(inc),
                                noise_substituted=bool((shot, st) in NOISE_SUB)))
            dd = pd.DataFrame(det); sc = dd[dd.scored]
            frac = float(sc.inconsistent.mean()) if len(sc) else float("nan")
            summ[f"{variant}|{route}|detection"] = dict(pairs=det, n_scored=int(len(sc)), n_inconsistent=int(sc.inconsistent.sum()),
                                                        fraction=frac, verdict=("PASS" if frac <= 0.10 else "PARTIAL" if frac <= 0.25 else "FAIL"))
    # frequency extent validated: bands with observed SNR >= 3 dB (the audit's signal definition)
    v = df[(df.variant == "base")].dropna(subset=["implied_sl_db"])
    summ["extent"] = dict(f_lo=float(v.fc_hz.min()), f_hi=float(v.fc_hz.max()),
                          bands_by_pair={f"{a}|{b}": sorted(g.fc_hz.tolist()) for (a, b), g in v.groupby(["shot", "station"])})
    summ["route_b_params"] = {f"{z}m": {k: (float(v_) if np.isscalar(v_) else v_) for k, v_ in _B[(z, 4.0, "sin2")][2].items()
                                        if k not in ("impulse_balance",)} for z in (610.0, 915.0)}
    summ["conversion_db"] = CONV
    json.dump(summ, open(f"{OUT}/sus_absolute_summary.json", "w"), indent=1, default=float)
    return df, summ


if __name__ == "__main__":
    df, summ = main()
    for k, s in summ.items():
        if k.startswith("base|") and "verdict" in s and "pairs" not in s or k.endswith("pooled|all"):
            print(k, s.get("n"), s.get("f_lo"), s.get("f_hi"), round(s.get("level_median", np.nan), 2),
                  round(s.get("slope_db_per_oct", np.nan), 2), round(s.get("shape_rms", np.nan), 2), s.get("verdict"))
    for k, s in summ.items():
        if k.endswith("detection"):
            print(k, s["n_scored"], s["n_inconsistent"], s["verdict"])
