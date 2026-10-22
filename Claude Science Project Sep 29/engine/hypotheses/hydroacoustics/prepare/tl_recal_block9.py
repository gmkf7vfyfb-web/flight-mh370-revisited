"""PRE-REGISTRATION (committed before any number below is computed): transmission-loss recalibration, work order
2026-10-21 block 9 = brief Refresh v2 section 9 steps (a), (b), (d). Hydroacoustic Module, overnight track, 22 Oct 2026.

DISCLOSURE (not blind). The author of this file has read air9_ew0112.py and its results (verdicts_amendment1.json):
  the H-ref and H-flat rescoring were NOT SUPPORTED, and an EXPLORATORY post hoc model "H-flat + near-field Ball
  factor + far-field array factor" gave slopes +2.33 (H01W) and -0.43 dB/oct (H08S) at the nominal geometry and
  passed the slope grade on 0.778 of the geometry grid (label POST HOC). The confirmatory test on independent sites
  (airgun_sites_confirm.py) was NOT TESTABLE (2 testable pairs, 3 required). Route 1 below is therefore a
  CONFIRMATORY RE-SCORING of a model fixed in advance, in the forward (source + TL -> received level) form the work
  order asks for, under the audit's C1 criteria (criteria.md 940f1a3), with the decision rule fixed here. A pass is
  fit-consistency on the training case (air9), NOT an independent confirmation; it cannot lift caveat C1 on its own.
  Nothing in the model is fitted to Fig. 23; every parameter comes from EW0112, OFR 95-228 or geometry.

ROUTE 1 - EW0112 near-source calibrated recordings (step a, first route).
  Observation. Blackman et al. (2004) Fig. 23 "observed TL" (digitised, +/-2 dB; air9 third-octave band means at
    H01W 12.5/16-63 Hz and H08S 5-63 Hz as in results/hydroacoustics-audit/data/air9_residuals.csv, model M1) is
    TL_obs,b = SL_B - RL_obs,b with a FLAT source level SL_B. Blackman quote the array as 230-240 dB re 1 uPa at 1 m.
    Hence RL_obs,b = SL_B - TL_obs,b with SL_B = 235 dB (midpoint; 230 and 240 reported as the range).
  Source. Ball(f) = dB mean over the two Fig. 2 shots of the third-octave Ball spectrum at the receiver
    (results-data/air9_ew0112/ew0112_fig2_ball_spectra_bands_DIGITISED.csv), scaled to 1 m by 20 log10 R1m with
    R1m = 25.75 m (ew0112_fig2_scaling.json). A band is used only if BOTH shots are READABLE (so 40 Hz is excluded).
    Delta_ref,b = 10 log10 <|sum_g w_g (e^{ik r1g}/r1g - e^{ik r2g}/r2g) / sum_g w_g|^2>_b R1m^2, the near-field
    reference factor at the Ball for the OFR 95-228 20-gun layout (ewing_20gun_layout_ofr95228.csv) with weights
    w_g proportional to V_g^(1/3) (primary) and equal (sensitivity); r1g/r2g = direct/surface-image paths from gun g
    to the Ball; band mean over 200 log-spaced frequencies inside f_b 2^(+/-1/6); c = 1500 m/s.
    S0,b = Ball,b + 20 log10 R1m - Delta_ref,b: the far-field notional MONOPOLE source spectrum level
    (dB re 1 uPa^2/Hz at 1 m) which KRAKEN's point source at z_s (free surface included) then propagates.
    AF_b(station) = 10 log10 of the band-mean |sum_g w_g e^{-i k u.x_g}|^2 / (sum_g w_g)^2 at elevation 0 deg toward
    the station (bearing from the air9 midpoint minus the ship heading 111.2 deg; across-track sign +1 primary,
    -1 reported), the module's air9_farfield_array_factor.csv values.
  Geometry prior (unchanged from air9_ew0112.py): z_s in {9, 10, 12} m (10 nominal), Ball x_h in {20, 30, 40} m
    ahead of the array centre (30 nominal), Ball depth z_h in {5, 10, 15, 20, 30} m (15 nominal): 45 grid points.
  Propagation. TL_model,b recomputed here with the module chain unchanged (air9_tl_validation.build_profiles +
    kraken_tl.tl_path: profiles every 5 km, hard bottom cp 1650 / rho 1.9 / 0.5 dB per wavelength, Francois-Garrison,
    incoherent adiabatic modes, spherical correction, receiver at the triad centroid depth H01W 1,055 m, H08S 1,376 m)
    on the SHARED ocean-transport sections (products/hydro-paths-2001-10, GEBCO_2026 + WOA23 95A4 October),
    converted by shared_paths.convert, for z_s in {9, 10, 12} m, third octaves 5-80 Hz. Pipeline check: the 10 m
    values must agree with the audit's M1 model_tl_db to within 1.0 dB in every band (else STOP and report).
  Prediction and residual. RL_pred,b = S0,b + AF_b - TL_model,b.  r_b = RL_obs,b - RL_pred,b  (dB; r > 0 means the
    model under-predicts the signal). Over the bands in both the Fig. 23 span at the station and the readable Fig. 2
    set: H01W 12.5-63 Hz without 40 (8 bands), H08S 5-63 Hz without 40 (11 bands).
  Statistics (criteria.md definitions): LEVEL = median r_b (graded at SL_B = 235; also given at 230 and 240);
    SLOPE = OLS slope of r_b on log2 f_b, dB/oct, with standard error; SHAPE = RMS of r_b after the level-and-slope fit.
    Grades: LEVEL PASS <= 3, PARTIAL <= 6; SLOPE PASS <= 1.5, PARTIAL <= 3; SHAPE PASS <= 3, PARTIAL <= 5.
  Common-mode removal (the second view the work order asks for): over the bands shared by both stations
    (12.5-63 without 40, 7 bands), c_b = mean of r_b over the two stations; r~_b = r_b - c_b. LEVEL/SLOPE/SHAPE of r~_b
    per station (= half the station difference, the path-only view, audit C2), and LEVEL/SLOPE/SHAPE of c_b itself
    (what remains on the shared, source-side term after the EW0112 source is applied).
  Sensitivities, reported, not graded: each Fig. 2 shot alone as Ball(f); equal gun weights; across-track sign -1;
    the retired stub sections in place of the shared sections.
  DECISION RULE (route 1), at z_s = 10 m, nominal geometry (x_h 30, z_h 15), V^(1/3) weights, sign +1, SL_B = 235:
    EXPLAINED        SLOPE PASS or PARTIAL at BOTH stations AND SHAPE PASS or PARTIAL at both AND LEVEL not FAIL at
                     both for at least one SL_B in {230, 235, 240}; AND the slope condition holds on >= 2/3 of the 45
                     geometry grid points (z_s x x_h x z_h).
    PARTLY EXPLAINED the nominal conditions hold but the grid fraction is < 2/3, OR slope passes at one station only
                     with the other station's slope <= 4.5 dB/oct (half-way to the uncorrected tilt).
    NOT EXPLAINED    otherwise.
  Consequence fixed now. EXPLAINED -> the air9 absolute received-level chain is labelled "PARTLY CALIBRATED in
    slope, conditional on the EW0112 source model (training case; no independent site)"; caveat C1 stays on every
    MH370 number, re-worded to name the remaining common-mode slope c_b, until an independent airgun site or the
    F-35A route confirms. PARTLY / NOT EXPLAINED -> C1 unchanged, the tilt stays attributed to near-source coupling.

ROUTE 2 - F-35A spectral shape (step a, second route; Brown et al. 2026, arXiv:2604.12723).
  Purpose. An independent near-surface source of a different kind (an aircraft impact, 9 Apr 2019, 40.64 N 142.96 E)
    seen at H11 (3,341 km). If the module's engine tilts the spectrum of a near-surface source (near-source coupling
    the flat half-space cannot represent), the F-35A implied source spectrum will show a tilt of the same sign as the
    air9 common mode; if the air9 tilt was the airgun source, the F-35A implied source will sit inside the module's
    impact source-shape envelope.
  Data. The F-35A received spectrum (PSD or spectrogram slice at H11) digitised from the Brown et al. 2026 figure by
    the Digitisation track (results-data/digitised/brown2026/, polled every 30 min); if absent by hour 3 (05:20 UTC),
    digitised here from the arXiv PDF (declared as a substitution; the module branch has no papers folder).
    Third-octave band means over 5-40 Hz where the trace is readable and the paper's noise floor is exceeded by 3 dB.
  Implied source. S_F35,b = RL_b + TL_model,b, TL from results-data/f35a_cal/f35a_tl.csv (H11S and H11N, z_s 10 m,
    the same chain), RAM-corrected TL (ram_check/h11_tl_ramcorr.csv) as a sensitivity.
  Expectation. The module's impact source shape 10 log10 S_b(tau, slope) (imos_stageB_map.band_fraction) over
    tau in the F-35A grid (0.05-10 s, 25 log-spaced points) and slope in {2, 4}: envelope [s_min, s_max] of its OLS
    slopes on log2 f over the same bands.
  Statistic. s_F35 = OLS slope of S_F35,b on log2 f (dB/oct) with standard error; excess e = distance from s_F35 to
    the envelope (0 if inside).
  DECISION RULE (route 2): CONSISTENT if e <= 3 dB/oct (the PARTIAL slope threshold); INCONSISTENT otherwise, and
    then e is the lower bound of the engine-side tilt for a near-surface source and C1 is re-stated with it.
    Route 2 is DESCRIPTIVE: one event, one receiver, a figure-read PSD whose band and processing Brown may not state;
    it cannot by itself lift or confirm C1. If no usable figure exists in the paper, route 2 is reported as NOT
    AVAILABLE with the reason.

STEP (b) - air8 negative control under the same source model (only if route 1 is EXPLAINED or PARTLY EXPLAINED;
  otherwise reported as not re-run and why).
  The source spectrum S0 is common to air8 and air9 (same array, same tow-depth range; EW0112 p. 5), so it cancels in
  the within-station difference; only the array factor changes with heading. Heading of air8 from
  data/blackman/blackman_shot_lines.csv (two segments, shot-count weighted). Predicted received-level difference
  D_st,b = [AF_air8,b - TL_air8,b] - [AF_air9,b - TL_air9,b] at each station, TL on sections built by the audit path
  builder (results/hydroacoustics-audit/scripts/paths.py; GEBCO_2026 3x3 median, WOA23 95A4 October) for BOTH sites
  (same builder on both sides of the difference), z_s 10 m, bands 16-50 Hz (the air8 pre-registered set).
  Rule (unchanged from air8_negative_control.py, in received-level form): H01W FOLLOWS if median D <= -10 dB;
  DOES NOT if >= -3 dB; INCONCLUSIVE between. H08S CONSISTENT if |median D| <= 5 dB. Verdict "still holds" if
  H01W FOLLOWS and H08S CONSISTENT.

STEP (d) - air7 -> H01W, the ridge path (gap G22).
  Source: air7 shot-weighted mean position of the two EW0112 segments (data/blackman/blackman_shot_lines.csv:
    segment 1, 16 shots, 22 55.5 S 87 02.8 E to 22 54.6 S 87 00.7 E; segment 2, 14 shots, to 22 54.3 S 87 00.0 E).
    Receiver H01W triad centroid (-34.890303, 114.142637), depth 1,055 m. z_s = 10 m only (budget; declared).
  (d1) N x 2D: nx2d.py unchanged (17 Fresnel-corridor members, u in -2..2 step 0.25, weights exp(-u^2), GEBCO_2026
    3x3 median at 0.5 km, sound speed from the geodesic's own section built by the audit path builder), bands
    16, 20, 25, 31.5, 40, 50, 63 Hz (the observed air7 span at H01W is 31.5-80 Hz; 16-25 Hz are carried for the air9
    comparison; 80 Hz is omitted as the Fig. 2 source is unreadable there and the cost is highest).
  (d2) 3-D proxy (horizontal refraction around the 1,190 m feature at 28.8-29.0 S, 98.0-98.5 E): single-section TL
    along paths displaced laterally from the geodesic by d(s) = d_max sin(pi s / R), d_max in {-20, -10, -5, 0, +5,
    +10, +20} km (positive = to the right of the forward azimuth), same bands; the least-loss corridor is the minimum
    TL over d_max per band (an optimistic bound: it assumes the energy finds the deepest corridor within +/-20 km).
  (d3) If wall time allows after (d1)-(d2) (budget: 4 processes, finish by 09:00 UTC): a RAM (pyram) coupled
    solution on the geodesic at 31.5, 40 and 63 Hz, ram_tl_check.py settings (dr 2 lambda, dz lambda/20, 9
    frequencies per band, no absorption in either model), as a mode-coupling cross-check; reported, not graded.
  Observation: Fig. 23 CL air7 and air9 digitised band means (results-data/airgun_sites_confirm/
    fig23_CL_air7_bands_DIGITISED.csv, fig23_CL_air9_bands_DIGITISED.csv): the observed difference
    dTL_obs,b = TL_obs(air7) - TL_obs(air9) at H01W (about 0 +/- 2 dB at 31.5-63 Hz), which cancels the flat source.
  Statistic: dTL_model,b = TL(air7 -> H01W) - TL(air9 -> H01W) per band, for the geodesic, the N x 2D corridor and the
    least-loss corridor; the primary is the MEDIAN over 31.5, 40, 50, 63 Hz of dTL_model - dTL_obs.
  DECISION RULE (step d): REPRODUCED if |median| <= 10 dB for the N x 2D corridor; REPRODUCED AS AN UPPER BOUND if
    only the least-loss corridor is within 10 dB; NOT REPRODUCED otherwise. The absolute comparison with the module
    source model (S0 + AF - TL against SL_B - TL_obs) is reported beside it.
  G22 status text proposed to the architect: REPRODUCED -> "explained (lateral corridor, N x 2D)"; UPPER BOUND ->
    "explained only as an upper bound (3-D proxy); 3-D model needed"; NOT -> "still open: single-section, corridor and
    +/-20 km proxy all exceed the observation by > 10 dB; mode-coupling (PE/3-D) is the next test".

OUTPUTS. results-data/tl_recal_block9/: route1_tl_model.csv, route1_residuals.csv (per station, z_s, geometry,
  weights, sign, SL_B, band: RL_obs, RL_pred, r, r~), route1_grades.csv, route1_verdict.json; route2_*.csv/json;
  air8_recal.csv + air8_recal_verdict.json; air7_corridor.csv, air7_offsets.csv, air7_verdict.json; wall.json.
  Charts (PNG + PDF, two footnotes) and the addendum go to results/ on claude-science-sep29. Caveats C1 and C2 on
  every number. KRAKEN scratch under /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-tlrecal/ (deleted
  after use). Thread budget 4 processes (one KRAKEN/FIELD run per process).
"""
# IMPLEMENTATION is appended after the pre-registration commit (method exactly as registered; any change is an
# amendment with its own commit and reason).
