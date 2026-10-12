Hydroacoustics on end of flight run I (binary mh370-eof-ri1), all four strata. Written 2026-10-12 ~19:45Z.

WHAT IS HERE
  <stratum>/seed-k/hydro-lnL.npy  (row, parent, lnL_gated, lnL_soft, lnL_soft_imos, lnL_soft_h01w, not_computed), row-aligned with
  end-of-flight/run-i/<stratum>/seed-k. Per-stratum README.txt (labels + COVERAGE + per-seed checks), README_module.txt (column
  definitions), READY. Writer prepare/per_impact_lnl.py amendments 1-7 (hypothesis/hydroacoustics a0964d0); reader end of flight
  smoke/compact_impacts.py at e3f0f88. Run detached, 2 threads, outside the lock; about 7 min per stratum.

  stratum                 READY    rows         not_computed  seeds failing checks  lnL_soft q01 / q50 / q99
  next-i-waypoints        18:19Z   25,599,936   0             0                     -12.55 / 0 / +2.93
  next-i-free             18:26Z   25,600,000   0             0                     -11.92 / 0 / +2.77
  next-i-descent-climb    18:33Z   25,600,032   0             0                     -12.12 / 0 / +2.86
  next-i-repro-radar      18:46Z   25,599,936   0             0                     -12.26 / 0 / +2.78
  Checks per seed: rows equal end of flight's rows; row = 0..n-1; lnL_gated = 0.0 in every row.

COMPOSER USE
  lnL_gated = 0.0 is the module likelihood (predictive mode; the P_D gate is not passed: no raw IMS triad data are held).
  lnL_soft and its two parts are a labelled SENSITIVITY only: "hydroacoustics low-power, NOT CALIBRATED; IMS P_D borrowed".
  This module adds no weights; the survival factor and the 00:19 option weights are applied by the composer.

LABELS (carry into any product that uses lnL_soft)
  TL not calibrated (audit C6; K3 over-predicts the A11 SUS level at H08S by about 8 dB; air9 reference NOT SUPPORTED).
  IMS P_D borrowed (IMOS 3274 + 4.8 dB). H08S: periodic impulses every ~10-15 s on 8 Mar 2014. H08N blocked for MH370 impacts
  (Chagos, K4): its non-detection is uninformative. Ridge paths that cut the sound-channel axis are a reach gap (G-N2).
  In-flight breakup rows carry the intact impact point: levels are an intact-impact upper bound (G-bf).
  tau: run I latent:energy_transfer_tau90_s is NaN in all rows (checked), so tau comes from the scenario prior (G-H1 open).

COVERAGE
(a) FEASIBLE SET: every end of flight impact for the four run I strata, i.e. every 00:19 treatment D0-D5 crossed with the log-on
    cause C1 / C2 (silent, unpowered) and families A1, A2, B, as end of flight samples them (its note results/eof-run-i-oct12/README.md,
    with sources for its bounds). The hydroacoustic feasible set adds: any surface impact of a 777-200ER radiates into the sound
    channel; in-flight breakup and AGW at < 0.25 Hz are physically possible.
(b) MODEL'S REACH: SOFAR branch only, intact single impact, source depth 2/10/30 m, KRAKEN TL tables (stage B), 5-40 Hz, N x 2-D
    corridors for blockage. NOT reachable (declared gaps): fragmentation spectra (G-bf), AGW branch below ~0.25 Hz (G-N1, no
    detector), 3-D diffraction over ridges (G-N2), EoF tau (G-H1). Every result that uses lnL_soft names these in its label.
(c) PROPOSAL COVERAGE: this module scores every row (not_computed 0 of 102,399,904). Its ESS per option and family is end of flight's.
    Gaps below the 1,000 gate, from end of flight's 19:05Z COVERAGE: D3 x C2 silent (Holland's Hypothesis 2) 275; D5 x C2 silent 833;
    D4 x C2 silent per family A1 219, A2 544, B 780; A1 under D3 / D5 x C1 352 / 253; B under D3 x C1 697. These cells are NOT
    ESTIMABLE at this depth for any hydroacoustic summary; end of flight's aimed-proposal fix is in progress.
    End of flight's per-cell table (summary/table-0019-mixture.txt; its ESS column uses its own definition), D x C rows:
      D0xC1                              lnZ   -7.036 ESS     817767 A1/A2/B 0.19/0.41/0.40 A1 ESS  168733 lat [-38.45, -37.06, -34.22]
      D0xC2 silent                       lnZ  -11.567 ESS     343057 A1/A2/B 0.32/0.10/0.58 A1 ESS  165924 lat [-38.61, -37.14, -33.519999999999996]
      D0xC2 unpowered                    lnZ   -8.505 ESS    7150422 A1/A2/B 0.14/0.34/0.52 A1 ESS  995097 lat [-38.94, -37.15, -33.99]
      D1xC1                              lnZ  -12.554 ESS     827660 A1/A2/B 0.17/0.42/0.41 A1 ESS  162876 lat [-38.56, -37.23, -34.96]
      D1xC2 silent                       lnZ  -17.126 ESS     350356 A1/A2/B 0.38/0.11/0.51 A1 ESS  205778 lat [-38.75, -37.35, -34.36]
      D1xC2 unpowered                    lnZ  -14.106 ESS    6800355 A1/A2/B 0.14/0.35/0.51 A1 ESS 1123267 lat [-39.13, -37.48, -34.83]
      D2xC1                              lnZ  -18.560 ESS      63592 A1/A2/B 0.25/0.32/0.43 A1 ESS   15681 lat [-38.25, -37.1, -34.66]
      D2xC2 silent                       lnZ  -23.923 ESS      10251 A1/A2/B 0.43/0.08/0.49 A1 ESS    4781 lat [-38.21, -37.11, -34.06]
      D2xC2 unpowered                    lnZ  -20.892 ESS     193236 A1/A2/B 0.18/0.27/0.55 A1 ESS   38215 lat [-38.4, -37.21, -34.480000000000004]
      D3xC1                              lnZ  -28.219 ESS       2171 A1/A2/B 0.16/0.40/0.43 A1 ESS     352 lat [-38.24, -37.42, -35.14]
      D3xC2 silent                       lnZ  -33.751 ESS        275 A1/A2/B 0.18/0.22/0.59 A1 ESS      34 lat [-38.24, -37.4, -34.1]
      D3xC2 unpowered                    lnZ  -30.605 ESS       1516 A1/A2/B 0.14/0.36/0.51 A1 ESS     408 lat [-38.28, -37.42, -34.87]
      D4xC1                              lnZ  -28.382 ESS      10845 A1/A2/B 0.15/0.41/0.44 A1 ESS    1363 lat [-38.17, -37.44, -35.08]
      D4xC2 silent                       lnZ  -33.881 ESS       1426 A1/A2/B 0.20/0.22/0.58 A1 ESS     219 lat [-38.18, -37.41, -34.49]
      D4xC2 unpowered                    lnZ  -30.814 ESS      18651 A1/A2/B 0.12/0.36/0.51 A1 ESS    1395 lat [-38.22, -37.42, -34.9]
      D5xC1                              lnZ  -28.828 ESS       4060 A1/A2/B 0.15/0.39/0.47 A1 ESS     253 lat [-38.14, -37.37, -35.01]
      D5xC2 silent                       lnZ  -34.415 ESS        833 A1/A2/B 0.16/0.22/0.62 A1 ESS     137 lat [-38.18, -37.44, -34.51]
      D5xC2 unpowered                    lnZ  -31.224 ESS      12103 A1/A2/B 0.11/0.37/0.52 A1 ESS    1090 lat [-38.19, -37.39, -34.92]
