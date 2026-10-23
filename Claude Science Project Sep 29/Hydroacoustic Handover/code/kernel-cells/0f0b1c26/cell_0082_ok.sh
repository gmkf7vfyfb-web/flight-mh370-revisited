cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; cat > calibration_events_stage1b.py <<'EOF'
"""PRE-REGISTRATION (stage 1b of calibration_events.py; correction track, 22 Oct 2026). Committed to hypothesis/hydroacoustics
BEFORE any module TL or RAM value on these two paths is computed and before any residual is formed. PREDICTIVE, NOT CALIBRATED:
caveats C1 (propagation slope misfit; now a source-term caveat after the EW0112 result) and C2 (coupling efficiency not
calibrated; eta swept over four decades, F-35A upper anchor 2.1e-4) travel with every number.

WHAT IS NOT BLIND (disclosed). The architecture stand-in ran the module's KRAKEN recipe on both paths on 11 Oct
(results/hydroacoustics-calibration-events-stage1-standin.md): AF447 Delta_ratio upper bound +16 to +21 dB; San Juan implied
source 209-215 dB re 1 uPa^2 m^2/Hz, slope -1.83 dB/oct. The KRAKEN half below is therefore a reproduction, not a blind test.
The RAM half and the Gaspin & Shuler (1971) absolute source for the charge are BLIND (no RAM value on these paths and no G&S
spectrum at 108 kg has been computed by anyone in the project).

PATHS. Ocean transport exports /Users/pete/Downloads/mh370-exchange/ocean-transport/paths-calibration/ (READY, dafb0d1):
  af447-H10S (3.07 N 30.56 W -> H10S, 2,209.9 km; WOA23 2005-2014 June), receiver 860.0 m (FDSN H10S triad mean);
  sanjuan-charge-H10N (45.67 S 59.24 W -> H10N, 5,989.0 km; WOA23 2015-2022 December), receiver 847.3 m (FDSN H10N mean).
  Read directly in stub schema (calibration_events.path_tl, stub_dir; the length-1 index bug is fixed there).
MODELS (bands: third octaves 5-40 Hz, F.BANDS).
  K: KRAKEN adiabatic incoherent modes (kraken_tl.py), profiles every 5 km (air9_tl_validation.build_profiles), HARD bottom
     (cp 1650, rho 1.9, 0.5 dB/lambda), Francois-Garrison, spherical correction. z_s: AF447 {2, 10, 30} m; charge {33, 38, 47} m.
  R: RAM (pyram split-step Pade; tl_recal_block9.ram_job settings: 9 frequencies across the third octave, dr = 2 lambda,
     dz = lambda/20, intensity mean over the last 500 m, same hard bottom), PLUS Francois-Garrison added along the path length
     (imos_ram_grid.fg_db_per_km, the KRAKEN parameters), spherical correction. z_s: AF447 10 m; charge 33 and 47 m.
     RAM is the coupled-mode reference for the Rio Grande Rise crossing (2,590-2,672 km, 674 m on the track), which the
     adiabatic model cannot represent (stand-in: only 2-4 modes survive below 10 Hz).
CHARGE (Q2, absolute received level). Source: Gaspin & Shuler (1971) NOLTR 71-160 construction as re-implemented by the
  audit (results/hydroacoustics-audit/gaspin-shuler/gs_reconstruct.py; route B of sus_absolute.py: kappa 4, sin^2 negative
  phases), W = 108 kg TNT = 238.1 lb (Vergoz et al. 2021 p. 2528; Nielsen et al. 2021 give 102 kg: -0.25 dB shock,
  sensitivity only). Depth: 33 m primary (Vergoz p. 2548, bubble period); 38 m (planned); 47 m (the depth at which G&S's
  own T1 = 4.34 W^1/3 / Z^5/6 equals Vergoz's cepstral delay 0.345 s, Table 2). The charge is FAR outside G&S's stated range
  ("up to a few lb", section 8.1): the source uncertainty is declared as +/-3 dB (G&S's own agreement) plus an extrapolation
  allowance, so the LEVEL thresholds are those of audit C4 (PASS <= 4 dB, PARTIAL <= 7 dB). SL(1 m) [dB re 1 uPa^2 s/Hz] =
  G&S band level + 191.1 dB (audit conversion). Model received ESD_b = SL_b - TL_b.
  Observed: results-data/calibration_events/nielsen_fig5cd_bands.csv, H10N (Nielsen et al. 2021 Fig. 5c, digitised; PSD,
  dB re 1 uPa^2/Hz, three-hydrophone mean), noise removed in power. PSD -> ESD: + 10 log10(T_sig), T_sig = 10 s (Vergoz
  p. 2529: "signals ... last about 10 s" at H10N); 5 and 20 s reported as the range (-3/+3 dB on LEVEL only).
  Residual r_b = observed ESD - model ESD (RL convention of criteria.md). LEVEL / SLOPE / SHAPE / SPAN exactly as
  criteria.md C1 (bands with observed SNR >= 3 dB: all ten). Verdict per model (K, R) and depth, primary = R at 33 m.
  Secondary, descriptive only: the model peak pressure from R_pk = 3.013 /s (stage A template) against the printed 130 dB re
  1 uPa peak (Vergoz p. 2529) and the digitised Kadri Fig. 8 H10N peak (3.44 Pa).
AF447 (Q1). Delta_ratio as calibration_events amendment 1 (same-figure ratio with the F-35A, Kadri Figs. 4a/5a), tau grid
  0.05-10 s, slope 2, E total and vertical KE; computed with K (F-35A from results-data/f35a_cal/f35a_tl.csv) and with R
  (AF447 RAM at 10 m; F-35A from results-data/ram_check/h11_tl_ramcorr.csv at 10 m). Kadri's AF447 peak is an UPPER LIMIT
  (SNR 1.32, re-traced 22 Oct: SNR 1.22), so every Delta is an upper bound; verdict rule as prereg (not testable unless the
  upper bound is below +6 dB).
TIMING (descriptive). Observed H10N peak of the charge from three papers (digitised 22 Oct, waveform-rasters/), origin
  20:04:30 +/- 14 s (Vergoz) -> apparent group speed on the 5,989 km geodesic; compared with the module's SOFAR speed
  prior c ~ N(1.482, 0.006) km/s.
Usage: python calibration_events_stage1b.py tl <paths_dir> <out_dir> <at_bin>
       python calibration_events_stage1b.py ram <paths_dir> <out_dir> [nproc]
       python calibration_events_stage1b.py score <out_dir> <gs_dir>
"""
import json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import calibration_events as CE  # noqa: E402
import f35a_eta_calibration as F  # noqa: E402
import imos_stageB_map as B  # noqa: E402

HERE = Path(__file__).parent.parent
PATHS = {"af447-H10S": (860.0, [2.0, 10.0, 30.0], [10.0]), "sanjuan-charge-H10N": (847.3, [33.0, 38.0, 47.0], [33.0, 47.0])}
W_KG, W_LB = 108.0, 108.0 / 0.45359237
CONV = 191.1


def cmd_tl(paths_dir, out, at_bin):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); CE.AT_BIN = at_bin; dfs = []
    for name, (rd, zk, _) in PATHS.items():
        t0 = time.time(); d, h = CE.path_tl(None, name, rd, out, src=zk, stub_dir=paths_dir); d["source_water_depth_m"] = h; dfs.append(d)
        print(name, f"{time.time() - t0:.0f} s", flush=True)
    pd.concat(dfs).to_csv(out / "event_tl_kraken.csv", index=False)


def _ram(a):
    import tl_recal_block9 as T, imos_ram_grid as I
    name, bathy, ssp, fc, zs, rd = a
    r = T.ram_job((name, bathy, ssp, fc, zs, rd)); L = float(pd.read_csv(bathy).range_km.iloc[-1])
    r.update(path=name, rcv_depth_m=rd, range_km=L, fg_db=float(I.fg_db_per_km(fc) * L), tl_db=r["tl_ram_db"] + float(I.fg_db_per_km(fc) * L))
    print(name, fc, zs, f"{r['wall_s']:.0f} s", flush=True); return r


def cmd_ram(paths_dir, out, nproc=4):
    out = Path(out); out.mkdir(parents=True, exist_ok=True); pdir = Path(paths_dir); jobs = []
    for name, (rd, _, zr) in PATHS.items():
        for fc in sorted(F.BANDS, reverse=True):
            for zs in zr:
                jobs.append((name, pdir / f"bathy_{name}.csv", pdir / f"ssp_{name}.csv", fc, zs, rd))
    with Pool(int(nproc)) as P:
        rows = list(P.imap_unordered(_ram, jobs))
    pd.DataFrame(rows).to_csv(out / "event_tl_ram.csv", index=False)


def stats(fc, r):
    x = np.log2(np.asarray(fc)); r = np.asarray(r); A = np.vstack([np.ones_like(x), x]).T
    c, res, *_ = np.linalg.lstsq(A, r, rcond=None); resid = r - A @ c
    se = np.sqrt(np.sum(resid ** 2) / max(1, len(r) - 2) / np.sum((x - x.mean()) ** 2))
    return dict(level_median=float(np.median(r)), slope_db_per_oct=float(c[1]), slope_se=float(se), shape_rms=float(np.sqrt(np.mean(resid ** 2))))


def grade(v, p, q):
    v = abs(v); return "PASS" if v <= p else ("PARTIAL" if v <= q else "FAIL")


def verdict(s, lv=(4, 7)):
    g = dict(level=grade(s["level_median"], *lv), slope=grade(s["slope_db_per_oct"], 1.5, 3), shape=grade(s["shape_rms"], 3, 5))
    return g, ("FAIL" if "FAIL" in g.values() else ("PASS" if all(v == "PASS" for v in g.values()) else "PARTIAL"))


def cmd_score(out, gs_dir):
    out = Path(out); sys.path.insert(0, gs_dir); import gs_reconstruct as G
    K = pd.read_csv(out / "event_tl_kraken.csv"); R = pd.read_csv(out / "event_tl_ram.csv")
    obs = pd.read_csv(HERE / "results-data/calibration_events/nielsen_fig5cd_bands.csv"); obs = obs[obs.station == "H10N"].set_index("fc_hz")
    sig = 10 * np.log10(10 ** (obs.signal_db / 10) - 10 ** (obs.noise_db / 10))
    res = {"charge": {}, "af447": {}}; rows = []
    for z in (33.0, 38.0, 47.0):
        t, x, p = G.pulse(W_LB, z / 0.3048, kappa=4.0, neg="sin2")
        sl = {fc: float(G.band_db(t, x, fc * 2 ** (-1 / 6), fc * 2 ** (1 / 6), 40) + CONV) for fc in F.BANDS}
        for mname, T in (("KRAKEN", K), ("RAM", R)):
            tt = T[(T.path == "sanjuan-charge-H10N") & np.isclose(T.src_depth_m, z)].set_index("fc_hz").tl_db
            if len(tt) < len(F.BANDS):
                continue
            for Tsig in (10.0, 5.0, 20.0):
                o = sig + 10 * np.log10(Tsig); m = pd.Series({fc: sl[fc] - tt[fc] for fc in F.BANDS}); r = o - m
                s = stats(F.BANDS, r.values); g, v = verdict(s)
                key = f"{mname}|z{z:g}|T{Tsig:g}"; res["charge"][key] = dict(stats=s, grades=g, verdict=v)
                if Tsig == 10.0:
                    for fc in F.BANDS:
                        rows.append(dict(model=mname, src_depth_m=z, fc_hz=fc, sl_gs_db=sl[fc], tl_db=float(tt[fc]), model_esd_db=float(m[fc]),
                                         obs_esd_db=float(o[fc]), residual_db=float(r[fc])))
            # descriptive peak: p_pk^2 = R_pk * SE (5-40 Hz), SE from the model ESD integrated over bands
            se = sum(10 ** ((sl[fc] - tt[fc]) / 10) * fc * (2 ** (1 / 6) - 2 ** (-1 / 6)) for fc in F.BANDS) * 1e-12   # Pa^2 s
            res["charge"][f"{mname}|z{z:g}|peak_model_db_re_1uPa"] = float(10 * np.log10(3.013 * se) + 120)
    pd.DataFrame(rows).to_csv(out / "charge_h10n_residuals.csv", index=False)
    res["charge"]["peak_observed_db_re_1uPa"] = {"vergoz_p2529": 130.0, "kadri_fig8_digitised": float(20 * np.log10(3.44e6))}
    # AF447 Delta_ratio upper bound, K and R
    pk = pd.read_csv(HERE / "results-data/calibration_events/kadri_peaks.csv").set_index("panel")
    pF = {"H11N": pk.loc["F-35A H11N", "peak_Pa"], "H11S": pk.loc["F-35A H11S", "peak_Pa"]}; pe = pk.loc["AF447 H10S", "peak_Pa"]
    taus = np.exp(np.linspace(np.log(0.05), np.log(10), 25))
    Ftl = {"KRAKEN": pd.read_csv(HERE / "results-data/f35a_cal/f35a_tl.csv"), "RAM": pd.read_csv(HERE / "results-data/ram_check/h11_tl_ramcorr.csv")}
    for mname, T in (("KRAKEN", K), ("RAM", R)):
        e = T[T.path == "af447-H10S"]
        for conv, Ee in (("total", CE.EVENTS["AF447"][2][0]), ("vertical", CE.EVENTS["AF447"][3][0])):
            ds = []
            for z in sorted(set(e.src_depth_m)):
                te = e[np.isclose(e.src_depth_m, z)].set_index("fc_hz").tl_db
                Ge = np.array([sum(B.band_fraction(fc, np.array([1 / tau]), 2)[0] * 10 ** (-te[fc] / 10) for fc in F.BANDS) for tau in taus])
                for stn in ("H11N", "H11S"):
                    tf = Ftl[mname]; tf = tf[(tf.station == stn) & np.isclose(tf.src_depth_m, z)].set_index("fc_hz").tl_db
                    if len(tf) < len(F.BANDS):
                        continue
                    GF = np.array([sum(B.band_fraction(fc, np.array([1 / tau]), 2)[0] * 10 ** (-tf[fc] / 10) for fc in F.BANDS) for tau in taus])
                    ds += list(10 * np.log10((pe / pF[stn]) ** 2 * (CE.E_F35 / Ee) * GF / Ge))
            if ds:
                res["af447"][f"{mname}|{conv}"] = dict(upper_bound_median=float(np.median(ds)), min=float(np.min(ds)), max=float(np.max(ds)), n=len(ds),
                                                      verdict="not testable (upper bound >= +6 dB)" if np.min(ds) >= 6 else "upper bound below +6 dB")
    # timing
    tpk = pd.Timestamp("2017-12-01T21:12:04Z"); t0 = pd.Timestamp("2017-12-01T20:04:30Z"); L = 5989.0
    res["timing"] = dict(observed_peak_utc=str(tpk), origin_utc=str(t0), apparent_speed_km_s=L / (tpk - t0).total_seconds(),
                         range_km=L, note="peak from Kadri Fig. 8 21:12:06, Vergoz Fig. 2 21:12:04, Nielsen Fig. 3 21:12:03-06 (digitised)")
    (out / "stage1b_summary.json").write_text(json.dumps(res, indent=1)); print(json.dumps(res, indent=1))


if __name__ == "__main__":
    c = sys.argv[1]
    if c == "tl": cmd_tl(*sys.argv[2:5])
    elif c == "ram": cmd_ram(*sys.argv[2:5])
    elif c == "score": cmd_score(*sys.argv[2:4])
EOF
python -c "import ast;ast.parse(open('calibration_events_stage1b.py').read());print('ok')"; grep -n "SRC\b" calibration_events.py | head -3; grep -n "def G\|F.SRC" calibration_events.py | head