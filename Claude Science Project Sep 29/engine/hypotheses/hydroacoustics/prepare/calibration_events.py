"""PRE-REGISTRATION: near-surface calibration events, stage 1 (architecture audit fix 3; audit F3, F5, coverage G-H1).
Committed before any received level was read from a figure for this purpose and before any TL was computed on these
paths. Implementation follows in this file; any change after a level is read is an amendment with its own commit.

PURPOSE. The impact source is calibrated on ONE event (the F-35A, near-vertical, ~19 t, H11). Two questions:
  Q1 (G-H1, coupling vs kinematics): does a different impact type couple a similar fraction of its kinetic energy into
      the 5-40 Hz band? Shallow-angle and stalled "belly" impacts of airliners are the regime MH370 most often samples.
  Q2 (F3, propagation incl. < 12.5 Hz): does the module's TL reproduce received levels from a near-surface source of
      known energy, band by band, including 5-12.5 Hz?

EVENTS (stage 1; fixed now). Selection rule: deep-water impact or source (> 1,000 m at the source), received at an IMS
hydrophone triad, with an official or peer-reviewed source of the kinematics or yield.
  A. Air France 447, A330-203, 1 Jun 2009 02:14:28 UTC, 3.0658 N 30.5617 W (Wikipedia site coordinates; to be replaced
     by the BEA final report position before scoring). BEA final report (5 Jul 2012) and interim report (27 May 2011):
     mass about 205 t; last recorded vertical speed -10,912 ft/min (55.4 m/s), ground speed 107 kt (55.0 m/s),
     pitch +16.2 deg, roll 5.3 deg L; intact at impact. Receiver H10S (Kadri 2024 Fig. 3: 2,211 km).
  B. Yemenia 626, A310-324, 29/30 Jun 2009 ~22:50 UTC, 11.3715 S 43.2250 E (to be checked against the Comoros final
     report, 25 Jun 2013). Stalled from about 1,000 ft; last FDR values at 65 ft: 15 deg nose up, bank 21 deg R,
     185 kt (SKYbrary summary of the final report; the mass and vertical speed must come from the final report itself,
     else the event is scored with a declared mass range 120-150 t). Receivers H08S, H08N (Kadri Fig. 2: 3,225 /
     3,186 km). H08N is scored only after the audit's N x 2D blockage check (F11) or labelled "blockage unverified".
  C. ARA San Juan calibration charge, 1 Dec 2017 ~20:04:30 UTC, 45.666 S 59.240 W, 108 kg TNT equivalent at 33 m
     (Vergoz et al. 2021, PAGEOPH 178:2527, pp. 2528 and 2548: planned 38 m, raised to 33 m from the bubble period).
     Receivers H10N (Kadri Fig. 8 / Nielsen et al. 2021 Fig. 5c), H04S (Fig. 5d). Vergoz pp. 2529 and 2532: peak
     overpressure 130 dB re 1 uPa (H10N) and 122 dB (H04S).
  Not in stage 1 (declared, with reason): Sriwijaya 182, Lion Air 904, AirAsia 8501 (shallow Java/Bali seas, < 100 m:
  shelf coupling the adiabatic model cannot represent); Transair 810, Asiana 991, AB Aviation 1103 (shallow source
  water or small aircraft); they are a later stage with RAM.

OBSERVABLES (fixed now).
  - Aircraft (A, B): received PEAK pressure in Kadri's band (traces high-passed at 5 Hz, 2-40 Hz, Kadri 2024 p. 11),
    read from the right-hand time-series panels of Kadri Figs. 4b and 5a (raster; scale factor printed on the axis).
    Rule: column-wise extremes of the trace colour; peak = max |p| inside Kadri's box; noise = the 99th percentile of
    the column extremes outside the box. Uncertainty: axis calibration +/- 1 px plus the noise floor (the peak is
    reported as a value with its SNR; SNR < 2 is "upper limit only").
  - San Juan (C): per-band received spectral levels from Nielsen et al. 2021 Fig. 5c/5d (signal and noise curves),
    digitised by the same rule as Blackman App. B (colour trace, axis calibration), third-octave means 5-40 Hz;
    plus the printed peak levels as a cross-check.
MODEL (the module's chain, unchanged): SE_1m = eta * E * rho c / 2 pi in 5-40 Hz with the band fraction S_b(tau) and
  source depth z_s in {2, 10, 30 m}; received SE = sum_b SE_1m S_b 10^(-TL_b/10); peak^2 = R * SE with R = 3.013 /s
  (template T_C2), as for the F-35A. TL_b: KRAKEN, hard bottom, on GEBCO_2026 + WOA23 sections for each event-
  receiver path (ocean transport path products: REQUESTED; out-of-grid Atlantic paths need ocean transport's global
  grids). For C the source is an explosive: z_s = 33 m, E_src from a published explosive source spectrum (to be cited
  with pages before scoring; if none is verifiable, C is scored on the station difference H10N - H04S only, which
  cancels the source).
INVERSION (Q1). eta_event = peak_obs^2 / (R * E * rho c / 2 pi * sum_b S_b 10^(-TL_b/10)), on the same tau and z_s grid
  as eta_cal (F-35A), for E = total KE and E = vertical KE separately. Delta = 10 log10(eta_event / eta_cal) at matched
  (tau, z_s); reported as median and range over the grid.
VERDICTS (fixed now).
  Q1: |Delta| <= 6 dB for both A and B under an energy convention -> "per-joule coupling transfers within the declared
      +/-10 dB under <convention>"; 6 < |Delta| <= 10 -> "transfers within the declared allowance only"; |Delta| > 10 ->
      "coupling depends on impact type beyond the allowance: G-H1 must be modelled, not allowed for". The convention
      (total vs vertical KE) with the smaller max |Delta| over A, B and the F-35A is reported as preferred, with both
      shown.
  Q2 (C): the audit's C1/C2 criteria (criteria.md, 940f1a3) per station and for the station difference, inside the span
      of bands with observed SNR >= 3 dB.
CAVEATS declared now: Kadri's figure peaks include noise and an unknown display filter; one hydrophone per panel (not
  triad-summed); the peak-to-exposure ratio R is the IMOS template, not measured for these events; AF447 H10S noise is
  high at 18-28 Hz (Kadri 2024, text on Fig. 5a).
AMENDMENT 1 (11 Oct 2026 ~04:30 UTC, before any level was read from Kadri's figures):
  (i) A SAME-FIGURE RATIO is added and becomes the primary Q1 statistic: the F-35A peaks at H11N and H11S are read
      from Kadri Fig. 4a by the same rule, and Delta_ratio = 10 log10[(p_e/p_F)^2 * (E_F/E_e) * G_F/G_e], with
      G = sum_b S_b 10^(-TL_b/10) on each path. Display filter, band and peak-reading biases common to Kadri's panels
      cancel. E_F = 900 MJ (Brown 2026). The eta_cal comparison above is kept as secondary.
  (ii) Event positions: Kadri 2024 Supplementary S1 (the positions behind his ranges): Yemenia 626 11 40'29.4"S
      43 16'39.6"E; AF447 3 03'57"N 30 33'42"W. S1 impact speeds: Yemenia about 480 km/h, AF447 about 282 km/h
      (consistent with BEA's 107 kt ground and 10,912 ft/min vertical). The BEA values are primary for AF447; for
      Yemenia the angle is unknown and is bracketed: vertical KE between 5 % and 50 % of total (declared).
  (iii) Figures are rasters (669 px wide); a reading resolution of about 1 px (~3 % of full scale) is declared.
AMENDMENT 2 (11 Oct 2026 ~05:00 UTC, after the peaks were read; position only, independent of the levels): Kadri S1's
  Yemenia 626 position (11 40'29.4"S 43 16'39.6"E) lies ON LAND in GEBCO_2026 (+224 m, near Moroni). The event is
  placed at the Wikipedia / ASN crash site 11.3715 S 43.2250 E (1,303 m water; ASN: "6 km NW off Mitsamiouli").
INTERIM RESULT (11 Oct ~05:00 UTC; results-data/calibration_events/kadri_peaks.csv):
  - F-35A peaks 1.15 Pa (H11N) and 1.22 Pa (H11S), SNR 3.2-3.3 against the 99th percentile outside Kadri's box.
  - AF447 H10S: 0.91 Pa, SNR 1.32 -> upper limit only. Yemenia H08S 0.78 Pa (SNR 1.07), H08N 0.25 Pa (SNR 0.87) ->
    upper limits only; Kadri's panels show no peak above the noise.
  - Yemenia NOT SCORABLE with the adiabatic model: the H08S path crosses Saya de Malha Bank (9.4-9.6 S, 59.6-60.8 E,
    19-75 m) and the Grande Comore shelf (3 m); the H08N path crosses land at 51.1 E and 0 m at 60.2 E. KRAKEN finds
    no modes. Needs the audit's N x 2D / 3D method (F11). Reported as not scorable, not as a non-detection.
  - AF447 waits for an Atlantic path section (ocean transport request).
Status: PRE-REGISTRATION + INTERIM. Outputs to results-data/calibration_events/ when run.
"""
# ------------------------------------------------------------------ implementation (11 Oct 2026, after amendment 1)
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
import air9_tl_validation as A  # noqa: E402
import f35a_eta_calibration as F  # noqa: E402
import imos_stageB_map as B  # noqa: E402
import kraken_tl as K  # noqa: E402
import shared_paths as SP  # noqa: E402

HERE = Path(__file__).parent.parent
E_F35 = 900e6
# Kadri Fig. 4a / 4b / 5a peaks read by the pre-registered rule (results-data/calibration_events/kadri_peaks.csv)
EVENTS = {   # name: (receiver, path name, E_total J (lo, hi), E_vertical J (lo, hi))
    "AF447": ("H10S", "af447-H10S", (0.5 * 205e3 * (55.4 ** 2 + 55.0 ** 2),) * 2, (0.5 * 205e3 * 55.4 ** 2,) * 2),
    "Yemenia626-H08S": ("H08S", "yem626-H08S", (0.5 * 120e3 * 133.3 ** 2, 0.5 * 150e3 * 133.3 ** 2),
                        (0.05 * 0.5 * 120e3 * 133.3 ** 2, 0.50 * 0.5 * 150e3 * 133.3 ** 2)),
    "Yemenia626-H08N": ("H08N", "yem626-H08N", (0.5 * 120e3 * 133.3 ** 2, 0.5 * 150e3 * 133.3 ** 2),
                        (0.05 * 0.5 * 120e3 * 133.3 ** 2, 0.50 * 0.5 * 150e3 * 133.3 ** 2)),
}


def path_tl(exp, name, rd, out):
    stub = out / "stubschema"; stub.mkdir(parents=True, exist_ok=True)
    SP.convert(Path(exp), stub, name)
    tag_ = name.replace("-", "_")
    bathy = pd.read_csv(stub / f"bathy_{tag_}.csv"); ssp = pd.read_csv(stub / f"ssp_{tag_}.csv")
    rprof, profiles = A.build_profiles(bathy, ssp)
    rows = []
    for fc in F.BANDS:
        tag = f"f{fc:g}".replace(".", "p")
        K.tl_path(out / "work" / name, tag, fc, profiles, rprof, np.array([rprof[-1]]), F.SRC, [rd], A.BOTTOMS["hard"],
                  AT_BIN, fg=A.FG)
        s = K.read_shd(out / "work" / name / f"{tag}.shd"); x = s["rr_m"] / 1000.0 / 6371.0
        sph = 10 * np.log10(x / np.sin(x))
        for js, zs in enumerate(s["sz"]):
            rows.append(dict(path=name, fc_hz=fc, src_depth_m=float(zs), rcv_depth_m=rd, range_km=float(rprof[-1]),
                             tl_db=float(-20 * np.log10(np.abs(s["p"][0, js, 0])) + sph[-1])))
    return pd.DataFrame(rows), float(bathy.depth_m.iloc[0]) if "depth_m" in bathy else np.nan


def G(tl, taus):
    """sum_b S_b(tau) 10^(-TL_b/10) for each tau and source depth."""
    out = {}
    for z in F.SRC:
        t = tl[np.isclose(tl.src_depth_m, z)].set_index("fc_hz").tl_db
        out[z] = np.array([sum(B.band_fraction(fc, np.array([1 / tau]), 2)[0] * 10 ** (-t[fc] / 10) for fc in F.BANDS) for tau in taus])
    return out


AT_BIN = None


def run_tl(exp, out, names_rd):
    global AT_BIN
    out = Path(out); out.mkdir(parents=True, exist_ok=True); dfs = []
    for name, rd in names_rd:
        t0 = time.time(); d, h = path_tl(exp, name, rd, out); d["source_water_depth_m"] = h; dfs.append(d)
        print(name, f"{time.time() - t0:.0f} s, source water depth {h:.0f} m", flush=True)
    df = pd.concat(dfs); df.to_csv(out / "event_tl.csv", index=False)
    return df


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "tl":
    AT_BIN = sys.argv[4]
    st = pd.read_csv(HERE / "data/stations.csv", comment="#")
    rdep = lambda t: float(st[st.triad == t].hydrophone_depth_m.mean())  # noqa: E731
    pairs = [(n, rdep(n.split("-")[1]) if n.split("-")[1] in set(st.triad) else float(sys.argv[5])) for n in sys.argv[6:]] \
        if len(sys.argv) > 6 else [(n, rdep(n.split("-")[1])) for n in ("yem626-H08S", "yem626-H08N")]
    run_tl(sys.argv[2], sys.argv[3], pairs)
