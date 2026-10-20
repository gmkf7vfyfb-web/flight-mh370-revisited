# Achievements, improvements and remaining work

**The work is recoverable from Google Drive.** The original four archives
remain intact. A fifth archive adds the latest FIR-intercept and waypoint
study. The scheduled 22:00 UTC checkpoint will refresh the handoff with any
subsequent completed work.

## Achieved and improved

- Recovered and preserved the original model, raw importance measures and
  all **1,710,701 positive-weight survivors**, rather than relying on chart
  images or a display resample. Original independent runs and failures remain.
- Tested every survivor against the separately authorized **R600 seventh arc**.
  The old 4.6% draw fails; about **95.2%** of the original weight passes.
  The reweighted median is about **34.07°S, 93.75°E**. Importance ESS improves
  from roughly 345 to 1000, although convergence is still insufficient.
- Preserved the **equal-thirds BRAN2016, OSCAR and GLORYS12** source mixture
  and comparison chart without treating it as independent flight evidence.
- Diagnosed the original due-south question with 100 physically/fuel-feasible
  cases and a conservative geometric bound. All 100 fail first at the 19:41
  BTO. This applies to a turn starting at IGOGU, not the new anticipated turn.
- Built a separate **turn-before-IGOGU model**. A reference Mach 0.82/FL350
  case starts turning 15.3 NM before IGOGU and rolls out due south on the FIR
  meridian at about 7.260°N before the 18:40 call.
- Compared a free second-turn time with a turn at the **6°N FIR corner**.
  The free reference case fits both 19:41 observables essentially exactly.
  At 6°N, constant Mach 0.82 gives a 186.34° course and -5.32 Hz BFO residual;
  allowing late Mach 0.74 reduces the residual to about -1.07 Hz.
- Demonstrated why a perfect early fit is insufficient: the free reference
  course fails the next BTO if continued without another turn. A third-turn
  optimized example passes the original full-flight checks and the separate
  R600 sensitivity, ending near **35.396°S, 92.199°E** at 00:17:30. Its speed
  changes are extreme under the original prior, so it has no assigned weight.
- Screened **1,276 published waypoints**, then computed exact weighted sums
  for a ten-point shortlist over all survivors. With R600 weighting, **99.11%**
  passes within 5 NM of BULVA and **99.46%** within 5 NM of ISBIX; median
  distances are about **0.7 NM** and **1.1 NM**. The original evidence scope
  gives similarly high fractions.
- Added direct numerical checks: early-fit refinement changes BFO by less
  than 0.00001 Hz in tested cases; the full example is rechecked at 5-second
  steps; 372 independent ellipsoidal proximity comparisons differ by at most
  0.0007 NM. These verify calculations, not the real-aircraft model's validity.

## Not yet established

- A converged, calibrated wreckage or impact-location PDF.
- A Bayesian posterior or model probability for the anticipated FIR turn.
- A typical-cruise full continuation for the exact early BFO optimum. The
  passing example has Mach changes 5-8 original prior standard deviations;
  three smoother local searches failed BFO gates, without proving exclusion.
- Complete March 2014 waypoint coordinate validity or a calibrated chance-
  coincidence test. BULVA's name/route is independently attested in 2010,
  but the detailed coordinates used here come from later official listings.
- A validated unpowered terminal-flight model, joint drift likelihood, or
  integration of hydroacoustic evidence into this conditional analysis.

The archive preserves these limits and the failed attempts so another
instance can continue without mistaking an optimization result or numerical
check for a calibrated probability statement.
