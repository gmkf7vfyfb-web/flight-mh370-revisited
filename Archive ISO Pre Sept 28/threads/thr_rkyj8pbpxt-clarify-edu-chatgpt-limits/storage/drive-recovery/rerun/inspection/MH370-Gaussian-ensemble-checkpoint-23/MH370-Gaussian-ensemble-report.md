# MH370 checkpoint 23 — Gaussian ensemble runs

Completed 19 September 2026. These are new executed ensembles, not another bridge-boundary implementation checkpoint. The frozen checkpoint-20 core executable is unchanged. The new powered-continuation/waypoint adapter is experimental and is not promoted to the stable release.

## Main finding

Four independent core runs completed with 5,000 initial particles each (20,000 total), using Gaussian BTO/BFO likelihoods. Explicit powered continuations then conditioned fuel exhaustion to 00:16–00:19 UTC. The four runs broadly concentrate in the same southern region, but each retains only about 11 effective initial ancestors. This is a diagnostic ensemble, not a calibrated wreckage-location probability or validated replacement estimator.

Two 5,000-draw waypoint experiments, following a 1,000-draw pilot, also completed. Both larger experiments have ESS approximately one. More candidate trajectories alone did not produce a usable waypoint posterior. Their best available routes still have substantial SATCOM residuals. Neither their concentration nor their endpoint location is evidence that the waypoint hypothesis is established or excluded.

## How Gaussian weighting works

For a residual r with fixed standard deviation sigma, its likelihood relative to a perfect fit is exp(-0.5*(r/sigma)^2). At 1, 2 and 3 sigma this is about 0.607, 0.135 and 0.011. There is no 2-sigma rejection boundary. Likelihood factors are combined across contacts, together with the declared priors and the exact proposal corrections used by the historical sampler.

BFO uses a sequentially marginalized common bias, not independent raw residuals with a fixed offset. The measurement noise is 7 Hz, and the innovation variance also includes the current bias uncertainty. Its initial bias prior is 150 +/- 25 Hz (one standard deviation).

The user correction applies to SATCOM residual scoring. The fuel window and route hypothesis remain explicit conditions. Contacts are evaluated at their recorded timestamps; the code does not select a better-fitting point from a +/-60-second search. No additional timing-uncertainty distribution has been invented.

Standard BTO noise is 29 microseconds; the inherited anomalous 18:25 BTO has 43 microseconds. The anomalous 18:25 BFO remains excluded. Calls at 18:39:55 and 23:15:02 contribute their inherited BFO means. Baseline SATCOM ends at 00:10:59. **00:19 observations have not been assimilated**: they require a separately declared post-exhaustion trajectory and BFO transient model. These results are therefore not a completed all-arcs impact posterior. Hydroacoustics remains excluded.

## Core results

| Seed | Initial particles | 00:11 row ESS | Root ESS | Largest-root weight | Exhaustion row ESS |
|---|---:|---:|---:|---:|---:|
| 37230001 | 5,000 | 107.9 | 11.00 | 17.9% | 114.4 |
| 37230002 | 5,000 | 108.3 | 11.50 | 17.9% | 112.2 |
| 37230003 | 5,000 | 111.3 | 11.78 | 13.7% | 98.6 |
| 37230004 | 5,000 | 78.2 | 11.19 | 15.9% | 68.2 |

The row ESS counts effective weighted rows; the root ESS aggregates descendants of the same initial candidate. These are not interchangeable. The fuel continuation samples use a common random-number seed for a controlled comparison, so they are not four extra independent ensembles. Root counts refer to their original core ancestry.

The explicit fuel continuation multiplies each saved weight by P(exhaustion window | propagated continuation)/P(checkpoint fuel envelope). It replaces the previously consumed conservative envelope factor, avoiding double conditioning. Zero-compatible continuations receive zero weight. Fuel and flow-scale uncertainty remain integrated/sampled under the existing model. This is exact weighting for that declared numerical model, not a claim of exact aircraft performance.

## Configurable operating assumptions

| Setting | Core run | Waypoint pilot |
|---|---|---|
| Mach command range | 0.73–0.84, continuous | Same |
| Altitude target grid | 25,000–43,000 ft, 1,000-ft spacing | Same |
| Mach transition limit | 0.10 Mach/min | Same |
| Climb/descent transition limit | 4,000 ft/min | Same |
| Turn dynamics | 15-degree bank; commands up to 180 degrees | Same bounded-bank dynamics |
| Turn/count limits | 16 turns, 8 Mach changes, 8 altitude changes counted from 18:25:34 | Waypoint steering, then uniformly sampled 0–4 free turns; 8 Mach and 8 altitude changes counted from MEKAR |
| Earlier core segment | Historical 18:01:49 source/process retained; changes before 18:25:34 are outside those later count caps | Replaced by an explicitly conditional MEKAR source |
| Manoeuvre timing | Existing marginalized variable-rate process, original 0.1–10-hour range | Same Mach/altitude process; free turn times uniform from release to 00:16 |
| Navigation | Five inherited modes with equal prior masses | Ground-track waypoint steering, then free true-track commands |
| Fuel anchor | 18:28:05.9; uniform 32,524.10488196–34,524.10488196 kg | Same |
| Flow-scale range | 0.9–1.1; nine inherited quadrature points | Same |
| Exhaustion condition | 00:17:30 +/-90 seconds | Same |
| Jettison | None | None |

The Mach interval is a command/set-point interval; inherited OU fluctuations perturb instantaneous Mach, track and wind. The count-cap timing clarification above corrects the abbreviated progress update: the historical core does not impose an eight-change cap over its entire 18:01-start history.

## Waypoint experiment and MEKAR timing

The numerical boxes were given precedence over the word “east”: 94–96 E lies west of MEKAR (96.491111 E). The early box is 94–96 E, 6–8 N through 18:40. MEKAR itself lies outside it, so the initial entry segment is exempt until first entry; thereafter the box is enforced. At 18:40 the route must be in 91–95 E, 14 S–7 N and remains within it until waypoint release.

Release latitude is uniform from 14 S to the equator. Steering ceases upon crossing the sampled latitude, including during a leg; any unfinished target is not recorded as a passed waypoint. The post-release turn count is uniform on integers 0–4. Targets need not be waypoints, turn times are sorted independent uniform times before 00:16, and headings are uniform over 0–360 degrees. The route arrival radius is 2 NM. Bank-limited propagation is used rather than instantaneous heading changes.

The first waypoint is uniform among catalogue fixes in the early box. Subsequent choices are an explicit prior mixture: 80% uniform over unvisited fixes progressing westward in the early box or southward in the later box, and 20% uniform over all unvisited in-box fixes; if the progressive set is empty the full set is used. This is a declared conditional route prior, not an established pilot-behaviour distribution. It excludes repeat visits. Proposal and prior are identical for this experimental full-path sampler, so no artificial likelihood or omitted proposal ratio is added. No Bayes factor between these differently normalized hypothesis models is claimed.

MEKAR passage is estimated at about 18:20:55 UTC, approximately 18:20:45–18:21:04 over these sampled operating states. The estimate subtracts the MEKAR-to-(6.578 N, 96.340 E) travel time from 18:22:12 using sampled speed, altitude and local atmosphere. **The latter point is the previously identified conditional airway interpolation, not an authenticated radar coordinate.** The short range is a conditional kinematic spread; it excludes radar-locus uncertainty and does not certify the subsequent trajectory through that point. This source construction requires refinement before using the waypoint output for scientific model comparison.

The catalogue carries historical_2014_verified flags. Several southern fixes are later-source catalogue entries whose 2014 presence remains unverified. The pilot includes them provisionally and does not relabel them as authenticated 2014 navigation data. Its guidance cadence is 10 seconds; route geometry and timing have not passed a step-refinement/convergence study.

| Run | Draws | Route and fuel supported | ESS |
|---|---:|---:|---:|
| waypoint-pilot | 1,000 | 108 | 1.00 |
| waypoint-37231002 | 5,000 | 538 | 1.00 |
| waypoint-37231003 | 5,000 | 535 | 1.00 |

Both larger pilots end with essentially one effective trajectory despite hundreds of route/fuel-supported candidates. Gaussian normalization only ranks the proposed candidates; it cannot make a poorly fitting or poorly explored proposal population reliable. The saved analysis includes the dominant trajectories' actual standardized residuals.

## Verification and continuation

The independent Python audit reconstructs Gaussian contact factors from residuals and bias variance, verifies normalized finite nonnegative weights, independently aggregates root ESS, checks the powered-continuation weight ratio, and checks every retained exhaustion time against the requested window. It passed. Saved illustrative core histories with BTO residuals above 2 sigma retain positive weight, demonstrating that the hard cutoff is absent. Illustrative histories are selected for coverage and are not an unbiased sample for estimating the fraction beyond 2 sigma.

See Gaussian-ensemble-diagnostics.png, analysis.json and independent-audit.json. Source configs, frozen core executable, experimental adapter source/executable, all run outputs and reproducibility scripts are included in the continuation ZIP. The large ERA5/IGRF grids and offline Rust runtime remain in the previously verified full-core handoff; their required hashes are included here. Use rebase.py to point this supplemental bundle at that recovered environment.

Next priorities: improve the waypoint proposal using staged likelihood information with a correct prior/proposal ratio; reconcile its MEKAR source law with radar uncertainty; validate catalogue history and route integration; run larger independent core populations or valid rejuvenation to test the observed ancestry collapse; then add the declared end-of-flight treatment and 00:19 likelihood without duplicate conditioning. The checkpoint-22 full-aircraft bridge work remains experimental and is not replaced or claimed completed by these forward runs. Hydroacoustic work remains behind core adequacy.
