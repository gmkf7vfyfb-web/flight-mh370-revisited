# Fuel-table extrapolation in run I (run-J item 7 check, 15 October 2026)

**Source.** Every `final.npy` of run I in `~/Downloads/mh370-exchange/core/run-i/`: 4 families × 8 seeds, all rows.
- Rows are pooled as weight × mode probability / mode weight sum, with the seeds equally weighted.
- `fuel_extrapolated_s` is the flight time on steps whose flow was not interpolated inside the tables. In
  `flight/src/fuel.rs` and `lib.rs` such a step has a Mach outside the bracketing speed schedules (above M0.84
  or below the holding Mach), a single schedule, or a fit fallback or weight clamp.
- The share of flight is that time divided by the time from 18:01:49 to fuel exhaustion, or to 00:19:37 if earlier.
- Output: `fuel_extrapolation_run_i.json` in this folder.

| family | mass with any extrapolation | median share of flight | mean share | 90% quantile share | median minutes | mean minutes |
|---|---|---|---|---|---|---|
| free | 0.958 | 0.285 | 0.318 | 0.749 | 107 | 119 |
| waypoints | 0.877 | 0.019 | 0.189 | 0.604 | 7 | 71 |
| descent-climb | 0.973 | 0.335 | 0.370 | 0.859 | 126 | 139 |
| repro-radar | 0.952 | 0.273 | 0.320 | 0.741 | 102 | 120 |

No mass flies below the tables or above the ceiling (both are imposed in run I).

## Reading
- **Extrapolation is not an edge effect.** 88–97% of the posterior uses it, and on average 19–37% of each
  path's flight time is flown on extrapolated flow. Waypoints is the exception at the median (2%): its routes
  hold Mach inside the schedules more often. Its mean is still 19%.
- **This uncertainty is not in the posterior.** The fuel audit (F6, quoted in `fuel.rs`) validates extrapolated
  steps against Boeing's figures at −11.5% to +3.7%, against 1.8% (sd) inside the schedules. The per-path factor
  κ carries only the in-table calibration.
- **Rough size, for scale only (not a computation):** 30% of a 6 h flight at a few per cent of flow error
  moves the fuel-exhaustion time by of order ±5–15 min. That is comparable to the 8.5 min between arcs 6 and 7.

## Recommendation (for Pete; a fuel-model and core change, not done here)
- Carry the extrapolation uncertainty explicitly: a second per-path factor κ_x, applied only on extrapolated
  steps, with a prior from the F6 validation (centre and spread of the −11.5% to +3.7% residuals).
- Report run J with κ_x on, and with κ_x at its point value as a sensitivity.
- As a first step, the fuel session states the F6 residual set and splits extrapolation by cause (Mach high,
  Mach low, single schedule, fallback). This check did not split it.
