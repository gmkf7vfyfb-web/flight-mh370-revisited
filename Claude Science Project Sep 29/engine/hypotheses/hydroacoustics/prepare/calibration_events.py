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
Status: PRE-REGISTRATION ONLY. Outputs to results-data/calibration_events/ when run.
"""
