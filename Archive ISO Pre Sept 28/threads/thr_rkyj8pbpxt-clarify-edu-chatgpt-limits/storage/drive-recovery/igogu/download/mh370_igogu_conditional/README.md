# MH370 conditional IGOGU posterior

This run conditions on the aircraft reaching IGOGU; it does not estimate the probability that MH370 reached IGOGU or validate the radar-to-IGOGU segment. It produces the smoothed spatial probability density at five later BTO epochs and at modeled fuel exhaustion.

Times are UTC on 7-8 March 2014. The full numerical prior is recorded in `inputs/prior_config.json`, and each final independent ensemble has its executed configuration under `output/refined_*/config.json`. Check the PDF's sampling status and `output/summary.json` before interpreting any contour as numerically stable.

## Result and numerical limitation

**The final approximation is provisional; it did not meet the declared convergence checks.** The run used 8,388,608 fresh final proposals (8,200,842 physical trajectory evaluations), following 51,834,910 exploratory and proposal-training evaluations. Its pooled importance ESS is only 345.3, and one draw at approximately 31.552°S, 95.400°E carries 4.63% of the total weight. The two final ensembles differ by 9.43 percentage points in their one-turn probability and by up to 10.31 percentage points in an endpoint-coordinate cumulative distribution.

The sampled exhaustion-position coordinate medians are approximately **34.063°S, 93.768°E**. The two final ensembles agree closely on those medians but disagree materially on the northern tail. The 50/90/99% contours describe the weighted, smoothed numerical approximation, not a demonstrated converged location posterior or a search recommendation.

Applying the older extra nominal-arc-centre crossing rule (every crossing within ±60 seconds) retains only 1.38294×10⁻⁷ of the weighted mass, or 0.0000138294%, and has effective sample size approximately **2.0**. This run does not support a reliable separate PDF under that stricter selection. The primary maps instead evaluate the noisy range measurements at their exact logged transmission times, as described below.

Numerical integration checks are a separate matter: all 384 selected trajectories retain their consistency checks at a 30-second step; maximum BTO/BFO changes are 0.143 microseconds and 0.000417 Hz. Accurate evaluation of a trajectory does not cure inadequate exploration of the posterior.

## User-specified conditions

- Start at IGOGU at an uncertain arrival time around the earlier revised estimate.
- Start the required southerly turn immediately and satisfy the southerly condition by the 18:40 call.
- Give 0, 1, 2, 3 and 4 **additional** turns equal prior probability, 20% each.
- Give constant altitude and normal cruise step climbs equal prior probability, 50% each.
- Weight trajectories using satellite range/frequency measurements and fuel exhaustion during 00:15-00:19, with peak at 00:17:30.

The ten combinations each have prior mass 0.1. These are prior weights; their posterior weights are obtained from their estimated marginal likelihoods, not by equal pooling or by counting survivors.

## Additional modeling choices

The IGOGU arrival prior is normal with mean 18:38:00, standard deviation 60 seconds and support 18:36-18:40. The earlier corrected radar-speed extrapolations ranged approximately from 18:37 to 18:39. This declared conditional prior replaces the old non-robust 18:44-18:46 estimate, not a validated arrival-time posterior.

Initial geometric altitude is uniform 31,000-37,000 ft. The step-climb class makes two 1,000-2,000 ft climbs, with timing windows 1-2.5 and 3-4.5 hours after IGOGU. Vertical speed reaches 600 ft/min through 30-second ramps. The maximum possible altitude is 41,000 ft. There are no arbitrary descents.

Initial Mach is uniform 0.76-0.85. Six later knots at 19:40, 20:40, 21:40, 22:40, 23:40 and 00:17:30 follow a truncated-normal random walk with standard deviation 0.015 and bounds 0.74-0.86. Mach changes continuously between these knots. The source and navigation priors, the turn-angle prior and the speed-history prior are modeling assumptions, not independently calibrated aircraft-control distributions.

The first turn is the short left turn from the inbound N571 course, starting at IGOGU and finishing before 18:39:55.354. Its southerly ground course is truncated normal with mean 180 degrees, standard deviation 15 degrees, bounded 150-210 degrees. Each trajectory shares a commanded bank drawn uniformly from 20-25 degrees across its turns; roll and actual bank are physically checked. Additional turn times are ordered independent uniforms between the end of the first call and 00:15. Signed angles are uniform -180 to +180 degrees. Overlapping turns and turns unfinished at exhaustion are excluded. Between maneuvers, course evolves along a WGS-84 geodesic; this natural course evolution is not counted as another commanded turn. Winds determine crab and groundspeed at the selected Mach.

The public aircraft/fuel model is inherited from the saved project: ERA5 weather, an OpenAP B772/Trent895 thrust proxy with multiplier 1.25, and an affine BSM Trent892 LRC fuel approximation with log-uniform flow factor 0.9-1.1. It is a public-data sensitivity model, not a calibrated manufacturer performance deck. Maximum Mach is 0.87, CAS 330 kt, actual bank 30 degrees, roll rate 3 degrees/second, CL 1.5 and stall margin 1.2. Geometric altitude is used as a pressure-height proxy when evaluating this inherited performance model.

## Measurements and two corrections

`inputs/observations.csv` lists every selected measurement, timestamp, carrier identifier and uplink/downlink frequency. The five R1200 epochs are 19:41:02.906, 20:41:04.904, 21:41:26.905, 22:41:21.906 and 00:10:59.928. The calls contain 51 and 29 receive BFOs, each predicted at its own timestamp. The fixed oscillator calibration is 152.5 Hz, with the inherited satellite AFC curve. Satellite positions and velocities use the pinned Hermite interpolation of the supplied public-workbook transcription, not independently authenticated operator ephemeris.

The inherited observation model uses WGS-84 aircraft coordinates, ground-station ECEF coordinates (-2368.8, 4881.1, -3342.0) km, the R1200 timing offset -495,679 microseconds, and carrier base frequencies 1,646,652,500 Hz uplink / 3,615,152,500 Hz downlink. Carrier offsets are `(hexadecimal carrier - 0x36ED) * 2500 Hz`. The AES compensation model retains the saved nominal longitude 64.5°E and radius `(6378.137 + 36210.12) km`; this is an explicit inherited model parameter, not an independently recalibrated orbit parameter. The actual satellite position/velocity used in the propagation calculation comes from the separate pinned ephemeris. Oscillator bias, compensation constants and AFC interpolation are held fixed, so their systematic uncertainty is not marginalized in these maps.

The Gaussian errors are 29 microseconds for R1200 BTO and 4.3 Hz for BFO. Each correlated call contributes one mean-residual likelihood with 4.3 Hz scale, while every raw call burst is checked individually. The final consistency selection requires every BTO within 58 microseconds and every BFO within 8.6 Hz. Residuals mean predicted minus observed.

1. The inherited parser incorrectly read the trailing `21000` bitrate in C-channel names as the carrier code. The new code reads `3730`, `373E` or `3737` from the actual carrier field. The R1200 carrier remains `36ED`.
2. Each BTO is evaluated at its exact logged transmission time. An additional requirement to cross the *nominal arc centre* within 60 seconds is not imposed. Near the 19:41 tangency, that old condition can effectively demand roughly 1 microsecond agreement even though the measurement uncertainty is 29 microseconds. It is a second, unjustifiably tight constraint on the same noisy range observation. The old centre-crossing result remains recorded only as a diagnostic; a value of 1e9 seconds denotes no centre crossing found within the diagnostic window.

All observations before IGOGU and all 00:19 BTO/BFO are outside this conditional likelihood. WSPR, hydroacoustics, drift/debris and search coverage are not included. Fuel-exhaustion position is not an impact or wreckage position; no subsequent glide/descent is inferred.

## Fuel timing without a missing importance weight

The fuel anchor at 18:28:05.904 is uniform 32,524.10488196-34,524.10488196 kg, with zero-fuel mass 174,369 kg and 15 kg unusable residual. No jettison is assumed. The short prefix from 18:28 to IGOGU uses the initial level-cruise fuel coefficients; it is a fuel allowance, not a reconstructed early trajectory.

The desired likelihood on computed exhaustion time is triangular, zero outside 00:15-00:19, with mode 00:17:30. For efficient sampling, exhaustion time is drawn from this same triangular proposal. The affine fuel map is inverted to obtain the required anchor fuel. Its prior support is checked and the change-of-variable factor `abs(dM_anchor/dT_exhaustion) / 2000` is retained. This avoids silently replacing the fuel-mass prior with a forced exhaustion time. Climb, speed and turn schedules are defined independently of the sampled exhaustion time, so the endpoint derivative is available from the fuel map.

## Sampling and diagnostics

Adaptive-tempering sequential Monte Carlo runs separately in every prior cell. Every cell starts from 131,072 independent prior proposals, including failed physical/fuel proposals in its evidence denominator, and retains a population of 4,096 particles. Random-walk Metropolis moves in logit-transformed prior coordinates rejuvenate the entire parameter history, including arrival time, speed history, turns and altitude parameters. The uniform-coordinate Jacobian is included in those moves. A gradual constraint penalty guides particles toward the final hard consistency set; that penalty is exactly zero on the retained set and is removed by the final indicator selection. This changes the sampling path, not the target posterior.

Those initial SMC ensembles disagreed materially in evidence and in the branches they occupied. Their measures are therefore **not** the final posterior measure. They serve only to initialize proposal training. Their initial-family ancestry and unique-parameter counts are diagnostics, not claims of independent samples.

The final sampler makes independent draws from a **frozen, full-support proposal**: 10% from the original unit-coordinate prior, and 90% from a mixture of multivariate Student-t distributions (8 degrees of freedom) in logit prior coordinates. Proposal components initially use both SMC populations and local sensitivity covariances. Four rounds of 65,536 independent importance proposals refine the mixture for each cell with sampled support. Training stops early if it finds no consistency survivor. Two larger importance pilot batches then make 1,048,576 proposals per cell. Because those pilots still had concentrated weights, their posterior display populations train a further empirical mixture of up to 24 clusters, with local-sensitivity covariance floors. The refined mixture gives 75% of its non-prior mass to the new empirical clusters and retains 25% of the previous mixture. Zero-support cells keep their original full-support proposals. The final `refined_a` and `refined_b` ensembles use fresh seeds and 1,048,576 proposals per one-additional-turn cell, and 262,144 per other cell. This allocation concentrates computation on the classes with greatest pilot evidence; every class still has the same 0.1 prior and its evidence is divided by its own proposal count. None of the earlier training or large-pilot draws is reused as final evidence.

Additional-turn time coordinates are sorted to a canonical representation, without changing their associated ordered-turn angles. On that ordered domain the original prior has density `k!`. The exact importance weight includes this factor, the logit-coordinate Jacobian, the full Student-t-plus-prior proposal density, the fuel-time change of variable, the observation likelihood and all physical/consistency indicators. Out-of-order Student-t draws and failed trajectories have zero weight and remain in the evidence denominator. Sampling does not silently relax the physical model or the original declared priors.

A numerical guard rejects coordinates with absolute logit magnitude at least 28; those draws also remain in the denominator. This excludes less than approximately 4×10⁻¹¹ of the original unit-coordinate prior mass per cell, before any likelihood conditioning. The saved parameters and weights expose the exact implemented calculation.

For a cell with `N` proposals, its evidence estimate is `sum(w_i)/N`, including zero-weight proposals. Posterior mass is proportional to this evidence times the cell's 0.1 prior. Pooling the two independent unnormalized estimates is equivalent to averaging their evidence estimates, not equally pooling accepted trajectories. The saved `importance_measure_*.npz` files retain every positive final weight, the corresponding endpoint, and the original proposal count. Importance ESS is `(sum(w_i))²/sum(w_i²)` and is computed **before** display resampling. The standard error of evidence uses the independent importance weights, conditional on the frozen learned proposal.

The report flags the approximation as provisional if pooled importance ESS is below 1,000, a single normalized weight exceeds 1%, independent evidence estimates differ by more than three estimated standard errors, or a turn-count probability or endpoint-coordinate cumulative distribution differs by more than five percentage points between ensembles. Passing these numerical diagnostics does not prove complete coverage of remote modes. A cell with no retained sample has **zero sampled support**, not a proof that every path in that class is impossible. No zero-support cell is removed from the prior or silently reassigned to another class.

The final raw importance records also retain the former nominal-centre crossing-time diagnostic. The report gives the weighted fraction and effective sample size that would survive an additional requirement to cross every nominal arc centre within 60 seconds of its logged epoch. This sensitivity is distinct from the primary exact-epoch noisy-range likelihood. Its centre crossings are bracketed/interpolated on the numerical path and are not a second independent measurement.

Spatial PDFs pool the independent final importance measures using equal class priors. The fuel-exhaustion map uses every positive original importance weight. For maps at the five BTO epochs, 4,096 stratified display samples per supported cell/replicate are traced and weighted by the estimated component mass. Those repeated display points are not independent samples. Each map is a **smoothing** density using all selected later observations and the exhaustion condition, not a forward-filter density at that time. Display contours use a 5 km equal-area grid with a 5 km Gaussian display kernel and enclose 50%, 90% and 99% of the sampled normalized spatial probability. Neither the display kernel nor the contour probabilities incorporate model misspecification or unlocated posterior branches. Contour area is sensitive to display resolution and is not a search recommendation.

## Reproduce

Python and a C++17 compiler with OpenMP are required. Install the pinned Python packages in `requirements.txt`. `inputs/weather.bin` must contain the supplied full ERA5 grid; its expected SHA-256 is in `inputs/weather_manifest.json`. The binary shared library is compiled automatically from the supplied C++ source.

```bash
python model.py
python verify_engine.py
OPENBLAS_NUM_THREADS=1 python run_smc.py --particles 4096 --moves 8 --threads 4 --seed 370260919 --output run_a
OPENBLAS_NUM_THREADS=1 python run_smc.py --particles 4096 --moves 8 --threads 4 --seed 470260919 --output run_b
OPENBLAS_NUM_THREADS=1 python train_importance.py --cells all --draws 65536 --rounds 4 --threads 4
OPENBLAS_NUM_THREADS=1 python importance.py --draws 1048576 --threads 4 --seed 970260919 --output importance_a --proposal-dir proposals_final
OPENBLAS_NUM_THREADS=1 python importance.py --draws 1048576 --threads 4 --seed 1070260919 --output importance_b --proposal-dir proposals_final
OPENBLAS_NUM_THREADS=1 python refine_proposals.py --cells '0,0;0,1;1,0;1,1;2,0;2,1;3,0;3,1;4,0;4,1'
OPENBLAS_NUM_THREADS=1 python importance.py --cells '1,0;1,1' --draws 1048576 --threads 4 --seed 1270260919 --output refined_a --proposal-dir proposals_refined
OPENBLAS_NUM_THREADS=1 python importance.py --cells '1,0;1,1' --draws 1048576 --threads 4 --seed 1370260919 --output refined_b --proposal-dir proposals_refined
OPENBLAS_NUM_THREADS=1 python importance.py --draws 262144 --threads 4 --seed 1270260919 --output refined_a --proposal-dir proposals_refined
OPENBLAS_NUM_THREADS=1 python importance.py --draws 262144 --threads 4 --seed 1370260919 --output refined_b --proposal-dir proposals_refined
python assemble_results.py refined_a refined_b
python make_report.py
```

Completed cells are reused on rerun; choose a new output name to generate a new ensemble. Saved frozen proposals can be used directly to reproduce independent final draws without repeating exploratory SMC and proposal training. Cell seeds are the specified ensemble seed plus `1000*k + 100*altitude_class`. The `reference/` directory preserves the independent Python model used for observation/weather/fuel cross-checks, including the old carrier parser whose carrier field is explicitly bypassed in the numerical comparison.

The independent checks cover 8,500 BTO/BFO predictions, weather interpolation, fuel mass integration, the fuel-time Jacobian, and 120-second versus 30-second integration. Adaptive 10-second steps are used during turns and climbs. Every observation time is an integration boundary. Additional fine-resolution checks use selected posterior samples.

## Sources

- [Released SATCOM log](https://www.atsb.gov.au/sites/default/files/media/5772619/public_mh370-data-communication-logs.pdf).
- [Historical Malaysia AIP ENR 3.3, 3 June 2010](https://aip.caam.gov.my/aip%20pdf/AIP%20AMDT%202_2010/ENR/Enr3_3.pdf).
- [Davey et al., Bayesian Methods in the Search for MH370](https://link.springer.com/content/pdf/10.1007/978-981-10-0379-0.pdf).
- ERA5 grid provenance, source object identities, coverage and SHA-256: `inputs/weather_manifest.json`.
- Full pinned SATCOM transcription: `inputs/satcom_source.csv`; selected observations: `inputs/observations.csv`.
- Satellite-state workbook transcription: `inputs/satellite_ephemeris.csv`.
- [Natural Earth public-domain coastline](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_50m_land.geojson).
