"""PRE-REGISTRATION (committed before any Fig. 23 curve other than air9 is digitised and before any TL for these
paths is computed): CONFIRMATORY test of the post-hoc airgun source model found on air9 (air9_ew0112 amendment 1,
results deb70727), on independent Blackman (2004) airgun sites.

MODEL M* (fixed from air9, nothing re-fitted): Blackman's "observed TL" used a FLAT source level; the true far-field
  notional source spectrum is S0(f) = Ball(f)@1m - Delta_ref(f) (air9 Ball near-source spectrum, EW0112 Fig. 2 as
  digitised at 5b522802; Delta_ref at the nominal Ball geometry x_h 30 m, z_h 15 m, the OFR 95-228 layout, V^(1/3)
  strengths); the array has the far-field factor AF(f, phi) toward each station, phi = station bearing minus ship
  heading. Predicted residual shape: r_b = C - S0_b - AF_b, C free. Same array, same tow-depth range (EW0112 p. 5:
  all 2001 lines), DECLARED: one source spectrum for all sites.
SITES and HEADINGS (EW0112 p. 5 shot-line end points, READ; ledger airgun_lines_ew0112.csv): air1 (shots 100-108),
  air2 (130-148), air3 (155-165), air4 (196-202), air5 (215-229), air7 (255-270 and 275-287), air8 (290-300 and
  305-311). Heading = WGS84 forward azimuth start -> end of the segment; a site with two segments uses each segment's
  own heading and the shot-count-weighted mean AF.
PAIRS (stations with an observed-TL curve in Fig. 23 per blackman_receiver_observations.csv): air1-air5 -> H08N;
  air7, air8 -> H08S. (air9 is the training case and excluded.)
TL MODEL: the module's KRAKEN chain unchanged (air9_tl_validation.build_profiles + kraken_tl.tl_path, hard bottom,
  z_s in {9, 10, 12} m, receiver at the hydrophone depth), on sections from the audit path builder
  (results/hydroacoustics-audit/scripts/paths.py; GEBCO_2026, WOA23 decade 95A4, October), from the segment midpoint
  to the station. A pair whose path is BLOCKED in a band has no model TL there.
OBSERVATION: Fig. 23 (p23_img0.png, artifact 99b55187) curves, digitised by the module's rule
  (digitise_blackman_fig23.py: panel calibration unchanged) extended to the other curves by legend style. A curve
  that cannot be traced uniquely (crossing curves of the same grey, legend ambiguity) is NOT TESTABLE, said so.
SCORING per pair, at z_s 10 m (9 and 12 m reported): residual r_b = TL_obs - TL_model in bands with both; corrected
  r*_b = r_b + S0_b + AF_b - median; graded with C1 (criteria.md 940f1a3) for SLOPE and SHAPE (level not tested: C is
  free). A pair is TESTABLE if it has >= 4 bands spanning >= 1 octave inside the Fig. 2 readable bands.
  Control: the same without AF (H-flat only), and uncorrected r_b.
VERDICT (fixed now): with N testable pairs (N >= 3 required, else NOT TESTABLE):
  CONFIRMED if >= 2/3 of pairs have slope PASS or PARTIAL under M* AND M* reduces |slope| relative to the
  uncorrected residual in >= 2/3 of pairs; REFUTED if < 1/3 of pairs pass/partial under M*; otherwise INCONCLUSIVE.
  If CONFIRMED, the airgun tilt is explained at source, and the station-independent TL is calibrated in slope at
  the tested bands; if not, the tilt stays unexplained and air9 stays uncalibrated in slope.
AMENDMENT 1 (11 Oct 2026, after viewing Fig. 23 for curve identity only; before any curve is traced or any TL
  computed). (i) The Fig. 23 CL panel legend shows air7 as well as air9, so the pair air7 -> H01W is added
  (blackman_receiver_observations.csv omits it). (ii) Curve tracing rule per site: the curve's grey level and line
  weight are sampled from its own legend swatch (DGN: air1 thin black, air2 thick dark grey, air3 dotted, air4 thick
  light grey, air5 thin light grey; DGS: air7 thick light grey, air8 dotted, air9 thin black; CL: air7 light grey,
  air9 black); in each pixel column the curve is the pixel cluster within +/- 20 grey levels of the swatch value,
  continuity as digitise_blackman_fig23.py (max jump 30 px); a column with two candidate clusters of the same class
  more than 3 px apart is dropped; a band keeps a value only if >= 50 % of its columns are traced. Pairs then follow
  the TESTABLE rule as registered. Panel calibration: as the module digitiser (3.6 px/dB, 2.875 px/Hz, 0 Hz at
  x = 51.5); DGN 150 dB at y = 8.5 (the same 140-px panel pitch as DGS 148.5 and CL 288.5), DECLARED.
LABELS: predictive audit, not a likelihood; hydroacoustics stays PREDICTIVE.
"""
