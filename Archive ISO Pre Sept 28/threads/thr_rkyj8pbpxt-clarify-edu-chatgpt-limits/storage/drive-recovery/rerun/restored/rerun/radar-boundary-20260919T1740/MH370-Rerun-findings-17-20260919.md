# MH370 Rerun checkpoint 17 findings

Created: 2026-09-19T17:40:53Z

## Result

The recovered 18:22:12 boundary has now been reconciled sufficiently to prevent an invalid physical bridge target.

Official sources authenticate three facts: a final positive radar-playback fix existed at 18:22:12 UTC; the aircraft was tracking northwest along the Malacca Strait; and the earlier radar series had ended at 18:01:19, leaving a 20 minute 53 second gap to the final point. The reviewed official reports do not publish the exact final latitude/longitude or a covariance supporting the recovered configuration's 2 NM position and 2 degree direction scales.

The exact recovered point, 6.578 N / 96.340 E, is instead geometrically diagnostic of the bundled N571 route model:

- It is 10.0509 NM after MEKAR on the MEKAR–NILAM leg.
- It is 29.3607% of the way along that leg.
- Its cross-track distance from the WGS84 MEKAR–NILAM geodesic is only 0.00533 NM, about 9.9 metres.
- The leg's initial true bearing is 296.162 degrees; the recovered configuration uses 296.0 degrees, a difference of 0.162 degrees.

This near-exact alignment is strong evidence that the numeric locus and heading were constructed as an N571 airway interpolation or model boundary. It is not evidence that the point is wrong; it is evidence that it must not be labelled a directly published radar measurement.

## Source reconciliation

The official Boeing performance appendix states that one final position point was determined from radar playback at 18:22:12 UTC, after a 20:53 gap from the preceding radar series. It also gives the first post-radar BTO epoch as 18:28:05.90 UTC:

https://www.mot.gov.my/my/Laporan%20Siasatan%20Mh370/02-Appendices/Appendices%20Set%201%20-%207%20Appendices%201.1A%20to1.9A/Appendix-1.6E-Aircraft-Performance-Analysis-MH370-(9M-MRO).pdf

The ATSB flight-path update calls the 18:22 return the final positive fix and describes the aircraft as tracking northwest. It explicitly notes the large number of possible manoeuvre scenarios between 18:22 and 19:41:

https://www.atsb.gov.au/sites/default/files/investigation-reports/AE-2014-054_MH370%20-FlightPathAnalysisUpdate.pdf

Neither reviewed source publishes 6.578 N / 96.340 E or derives the 2 NM / 2 degree scales. The recovered values occur in a downstream estimator configuration whose display context contains the N571 waypoints.

## Boundary implementation

An isolated Rust candidate now has a typed `RadarBoundarySpecification` with two mutually distinct roles:

1. `PrimarySourcedMeasurement`, which fails validation unless both coordinate and uncertainty derivations are authenticated.
2. `ConditionalAirwayInterpolation`, which fails unless the conditional-hypothesis status is explicitly acknowledged.

The current 6.578 / 96.340 / 2 NM / 296 degree / 2 degree configuration passes only under the second role. Attempting to relabel it a primary-sourced radar measurement returns `UnauthenticatedRadarMeasurementClaim`.

This is a source/target guard, not a likelihood. It does not add a radar factor, choose an endpoint, or alter the already validated endpoint/path/fuel-time ratios.

## Validation

- 89 `mh370-end-of-flight` Rust tests passed, including the two new fail-closed boundary tests.
- Five independent Python reconciliation/source-contract tests passed.
- The modified Rust file passes `rustfmt --check`.
- The first workspace-wide formatting check is retained as a non-scientific failure because inherited unrelated source files are not rustfmt-clean. No scientific run failed.
- Exact ERA5 and IGRF inputs remain hash-verified; no sampler lane was occupied.

## Consequence for the physical bridge

A first aircraft bridge may now use the 6.578 N / 96.340 E state only as an explicit conditional hypothesis. It must not silently replace the broad historical 18:01:49 source or inherit the old final-radar branch's 4 Hz BFO setting. Adoption requires sensitivity to a broader N571/radar boundary, such as along-leg uncertainty and inflated cross-track/direction scales.

The next implementation unit is the physical source adapter: initialize the full powered-flight state at the conditional 18:22:12 boundary, map its uncertain radar fuel to the canonical 18:28:05.9 anchor using the exact path-dependent affine mass map, and expose both 00:15–00:17 and 00:15–00:19 bridge hypotheses without applying the fuel or SATCOM factors twice.

## Limitations

- Raw military radar returns and their covariance are not publicly available in the reviewed sources.
- The N571 relationship is a reproducible inference from recovered configuration geometry, not a claim about how the investigators created their final fix.
- No full-aircraft backward or two-ended bridge was run in this checkpoint.
- No calibrated location probability or solved location is claimed.
- Hydroacoustic evidence remains excluded.

