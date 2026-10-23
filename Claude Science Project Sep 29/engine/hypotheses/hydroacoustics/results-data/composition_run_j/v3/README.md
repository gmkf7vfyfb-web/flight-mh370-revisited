# Hydroacoustic composition term, product v3 (amendment A6): coupling prior bound 1 and sensitivities (23 Oct 2026)

*ASD-STE100 for work-specific text; standard statistical terms as they are. PREDICTIVE, NOT CALIBRATED (caveats C1, C2).*

Columns: `mh370-exchange/hydroacoustics/run-j-gated-v3/` (74 seeds, 4 strata, 313,599,968 rows, 0 not computed; 8,471 s wall, 6 workers;
README.txt there corrected after generation, see its [CORRECTED] note). Reductions here: `ub1/` (coupling prior log-uniform on [1e-6, 1],
ruling X03, 61 grid points), `ub0.1/` and `ub0.01/` (prior upper bound 1e-1 and 1e-2: sensitivities). Code: prepare/composition_run_j
(prereg.py A6, worker, reduce.py with B11_V3=1 B11_IMOS_RAMGRID=1 B11_ETA_UB=<bound>). Summary table: `bounds_comparison_D0_p0.5_a0.05.csv`.

## Regression checks (all pass)
1. `ub0.01/` against `../v2/` (the v2 product, bound 1e-2): all tables equal to rounding (relative difference <= 5e-12), EXCEPT the
   columns "at anchor" (`pnd_at_anchor`, `L_at_anchor` in upper_limits.csv; `pd_*_at_anchor_*` in coincidence_locus.csv). These change by
   design: v2 used the old anchor 2.1e-4; v3 uses the F-35A value 2.26e-3 (X02, Pete has not given an explicit ruling; registry
   PENDING_RULING).
2. reduce.py in v2 mode on the v2 statistics reproduces `../v2/` (max difference 2e-16); v3 adds columns eta_prior_ub and pnd_at_ub.
3. Column margeta-ub1e-2 is byte-identical to the v2 default column: independent verifier, 8 random seeds over all 4 strata (2 per
   stratum); all 74 seeds have identical NaN patterns across the 6 columns and valid checksums; 0 NaN in the default column. The
   independent verifier also recomputed ln Z hydro and eta95 from the accumulators for all three bounds (D0/p0.5/alpha 0.05, IMOS gated).
4. In v3 mode the upper-limit column is named for the bound used (eta95_bayes_nondetection_logu_1e-6_<bound>); in v2 the name said 1e-2.

## Result (option D0, dive probability 0.5, alpha 0.05)

| prior bound | receivers | ln Z hydro | median latitude core -> combined | shift (deg, + = north) | KL (nats) | eta95 full likelihood (all latitudes) | eta95 prior alone |
|---|---|---|---|---|---|---|---|
| 1e-2 (= v2) | IMOS gated | -0.034 | 37.081 S -> 37.035 S | +0.046 | 0.008 | 0.0067 | 0.0063 |
| 1e-1 | IMOS gated | -0.060 | 37.081 S -> 37.013 S | +0.068 | 0.014 | 0.057 | 0.056 |
| 1 | IMOS gated | -0.090 | 37.081 S -> 36.983 S | +0.098 | 0.020 | 0.48 | 0.50 |
| 1 | IMS proxy + IMOS | -0.483 | 37.081 S -> 37.055 S | +0.026 | 0.007 | 0.075 | 0.50 |
| 1 | IMOS gated, amplitude-weighted | -0.180 | 37.081 S -> 37.035 S | +0.046 | 0.008 | 0.37 | 0.50 |

Reading (plain words): for every prior bound the hydroacoustic term changes the end-of-flight distribution only a little (median at most
0.10 deg; KL at most 0.02 nats). With IMOS only, the 95 % coupling limit is almost the prior limit: the IMOS data do not constrain the
coupling (at bounds 1e-2 and 1e-1 eta95 is even slightly above the prior-alone value). The non-detection-only form gives 0.116 (bound 1),
0.032 (1e-1), 0.0056 (1e-2). The IMS proxy column constrains it more (0.075), but that column uses stand-in noise at Cape Leeuwin and Diego Garcia (D06), so
it is a sensitivity only. A higher bound gives more weight to amplitude-blind matches (G11-1); the amplitude-weighted column shows that
part of the bound-1 shift (0.098 vs 0.046 deg) comes from that. No column is ruled for the composer.

## Limits
D05 detector not validated on real long-range arrivals (X06: M1b detected 6 of 37 real arrivals against 19.8 predicted); D06 IMS
stand-in noise; G11-1 amplitude-blind matching except in the -amp- column; D25 source depth 10 m; coupling not calibrated. Monte Carlo:
streamed ESS D0/p0.5 1.33e6 (summary.json).
