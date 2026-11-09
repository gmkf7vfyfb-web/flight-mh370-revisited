# Windage prior, wide-windage run and simulation-based calibration smoke test (9 November 2026, night)

Author: Claude Science (ocean drift thread). Status: working record. Nothing here is a ruling by Pete unless marked so.
Related: `README.md` sections 9 and 10 (Mossel Bay item), `scripts/` (`smoke_*`, `arrivals_*`), `scripts/sbc/` (this note), `runs/wide-2026-11-09/` in the module branch.

## 1. Summary

- The sampled windage range of the exterior class is a provisional choice. It is **not** shown to cover the feasible physical bounds. Its centre has some support (one replica trial by CSIRO). Its spread has no measurement.
- A replica trial of the Mossel Bay cowling ("Roy") exists. CSIRO Part I, p. 8: single 48-hour deployment, about 20 kt wind, open ocean off Maria Island. The effective windage of the fairing replica and of the Roy replica was "slightly less" than that of undrogued drifters. An earlier statement of mine, that no object-specific test existed, was wrong. It is withdrawn.
- The same trial shows an attitude effect: the fairing replica floated in two stable attitudes. One attitude behaved like the drifters. The other (concave up) drifted away fast. A range of 0.5 to 2.0 % does not represent such a second mode.
- Published assumptions for the flaperon before the CSIRO measurement ranged from 0 to 5 % (tracer ranges) with best single values from 0.8 % to 3.3 %. The measured value is an extra leeway of about 10 cm/s above undrogued drifters at an angle of about 16° to the left of the wind.
- Trinanes et al. (2016) state that dispersion is likely underestimated where the submesoscale field is energetic. The module addresses part of that with eddy diffusivity (100 to 1000 m²/s) and a transport-error field. The error-field length scale (100 km) is assumed and its effect on the early tail is untested.
- The wide-windage run was built, checked and launched on deskstar (job 27b6e292). Estimated duration is 4 to 5 hours, not the 3 hours first stated.
- Simulation-based calibration, smoke test (code-path check, not evidence): the statistic code reproduces the headline p = 0.1091 and runs 20,000 synthetic datasets per second. In Gaussian toy worlds the nominal χ² p-value is close to calibrated when the toy width matches the posterior width and anti-conservative when it matches the effective dimension. The module's own synthetic-recovery coverage test gives 58/60 (0.967) with calibration ratio 1.056.

## 2. Is the windage range defensible? (question 1)

Run setting (production configuration, exterior class `low_exposure_exterior`): `c_wind` normal, mean 1.2 %, standard deviation 0.3 %, truncated to 0.5 to 2.0 % by rejection; wind angle normal(0°, 10°); no extra leeway. Marked PROVISIONAL in the configuration; source named there: CSIRO Part III p. 6 (items at 1.2 % "subject to Stokes drift but not direct wind forcing"). The GlobCurrent leg subtracts a product offset, uniform on [−0.75 %, −0.60 %] per particle, floored at zero; its extra windage therefore has mean 0.53 % and maximum 1.39 %.

What supports the centre:
- CSIRO Part I (p. 8) gives the undrogued drifter effective windage as 1.2 % (BRAN2015 current; mostly Stokes drift; the direct windage is much smaller).
- The CSIRO replica trial (above) puts the Roy and fairing replicas just below the drifters in one attitude, one deployment.

What does not support the spread:
- Nothing measured gives a distribution. The replicas are not the real parts (no barnacles, no weathering, no damage, unknown density).
- The trial shows two stable attitudes for the fairing replica. A mixture distribution would be the honest description.
- Literature ranges for debris windage are wider: 0 to 5 % in earlier modelling (CSIRO Part I, p. 8), 0 to 2.5 % in 0.5 % steps (Jansen et al. 2016), 0 to 5 % tracers (Maximenko and Hafner, IPRC, 2015; 0 to 4 % in the Trinanes et al. paper).
- Order-of-magnitude physics (my own estimate, not from a reference; air-to-water drag ratio taken as 1): a flat panel in edgewise drift, with relative density d, has a direct leeway of about 3.46 % × sqrt((1 − d)/d). That gives 0.8 % for d = 0.95, 1.15 % for 0.90, 1.7 % for 0.80 and about 5 % for 0.30. The assumed range corresponds to d of about 0.75 or more. A buoyant sandwich panel, or a tilted attitude, lies outside it.

What the early Mossel Bay arrivals say about the range (stored beachings): arrivals before day 655 from release points south of 33° S have mean windage 1.40 % (GLORYS12 leg; class mean 1.20 %; 94 % of the mass above 1.0 %) and 0.77 % (GlobCurrent leg; class mean 0.53 %). The early arrivals come from the upper part of the sampled range, and the range ends at 2.0 % (GLORYS12) and 1.39 % (GlobCurrent).

Conclusion: not defensible as a physical bound. Defensible only as a provisional central prior. Action: the wide-windage run (section 5), and a sensitivity of the Mossel Bay result to it.

## 3. Published windage assumptions for the flaperon before measurement, and the measured values (question 2)

| Source | Assumption or value | Note |
|---|---|---|
| DGA / Pengam (2016), numerical modelling | 3.3 % (tail to wind), 2.8 % (nose to wind); drift angle 18° and 32° to the left (28° in CSIRO Part II) | Nesterov (2018) describes these as experimentally established. They are numerical. Discrepancy to flag. |
| Jansen et al. (2016) | wind drag 0 to 2.5 % in 0.5 % steps | scenario range |
| Trinanes et al. (2016); Maximenko and Hafner (IPRC, 2015) | tracers 0 to 5 % (paper: 0 to 4 %); best estimate 0.8 % | a retrieval from drifter statistics; the IPRC page says no windage assessment was available |
| CSIRO Part I (replica trials), as assumed for the flaperon | extra leeway 10 cm/s downwind up to 10 m/s wind, declining linearly above, added to the undrogued-drifter 1.2 % | assumption before the genuine part was tested |
| Eichhorn (comment) | Gao et al. up to 1.8 %; Jansen 2.5 %; Nesterov 3.39 % (the Nesterov paper states 3.29 %) | the 3.39 % figure does not match the paper |
| ATSB fact sheet | Griffin effective leeway about 1.5 % | consistent with CSIRO |
| **Measured** (CSIRO Part II, genuine cut-down Boeing 777 flaperon) | extra leeway about 10 cm/s above undrogued drifters, apparently constant with wind speed; mean leeway angle 16° to the left (0 to 30°; replica 4°) | modelling with 20° left and 10 cm/s over Stokes explains the July 2015 arrival for impact points between 40° S and 30.5° S |

Order-of-magnitude conversion (my arithmetic): 1.2 % of 8 m/s is 0.096 m/s; adding 0.10 m/s gives about 0.2 m/s, or 2 to 3 % effective windage at 8 m/s.

Page numbers are from the local copies of the CSIRO reports read in this session; they should be rechecked against the printed pages before citation in the paper.

## 4. Trinanes et al. (question 3)

Statement (J. Oper. Oceanogr. 9(2):126–138, p. 6): dispersion is likely underestimated, especially where the submesoscale field is energetic. Meaning: the synthetic particles are advected by smooth analysed fields (SCUD, 1° analysis). Real drifters are also moved by eddies and filaments of 10 to 50 km that the fields do not contain. The ensemble spread is then too narrow, and the fast and off-mean tails are under-represented. For the Mossel Bay item the tail is exactly what matters.

In this module the same issue is handled by (a) eddy diffusivity, log-uniform 100 to 1000 m²/s per ocean sample; (b) a transport-error field with σ = 0.0869 m/s, time scale 10 days, length scale 100 km (measured by a replay of undrogued drifters in the search box: σ east/north 0.115/0.118 m/s; the length scale is assumed; the configuration asks for 50 and 200 km sensitivities); (c) importance splitting at Mossel Bay (factor 100 within 500 km; exterior and interior classes) so that the tail is sampled. Not yet done: sensitivity of the Mossel Bay arrival probability to the length scale and σ, and a check of the splitting estimator in the tail.

Trinanes works found (completeness not guaranteed): the 2016 Journal of Operational Oceanography paper with Olascoaga, Goni, Maximenko, Griffin and Hafner (published and submitted manuscript R1); the IPRC web pages of Maximenko and Hafner (2015) used in the paper; the AOML and IPRC news items (Denny Medal 2016). A further web page listing "Trinanes" on a 2021 analysis is a related-work link on a paper by Eichhorn, not a Trinanes work. Olascoaga's group has other MH370 work (a Markov-chain approach, arXiv 1903.06165) that is not by Trinanes and was not reviewed here.

## 5. Wide-windage run (question 5; Pete approved the design as proposed)

Design (unchanged from the proposal): exterior class only, `c_wind` log-normal, median 1.2 %, σ(log) 0.5, truncated to 0.3 to 5 % by rejection (the proposal named 0.3 % and 5 %; 95 % range 0.45 to 3.2 %), wind angle normal(0°, 10°), same nodes (84 arc points in stage 1; 42 southern points in stage 2), same environment seeds (201 to 232), same seed 21, both ocean models, same GlobCurrent product offset. Class name `wide_windage_exterior`.

Code change (module `hypothesis/debris-drift`, `lib.rs`): default-off option `restrict_to_classes` (list of class names). Finds of other classes are not scored, so those classes are not transported. Validation rejects unknown names. Diff: `runs/wide-2026-11-09/lib-restrict-to-classes.diff` (3 hunks, 13 added lines).

Checks (deskstar job c6865ecd; smoke configuration, 3 nodes, 4 environments, 100 particles, same input for old and new binary):
1. Old binary (`bin-arr`, sha 256 prefix f86b14178c00df8b) and new binary (`bin-wide`, 0674397ec1996884), default configuration: `nodes.csv` (md5 3b52c7cec6d238f7873ae9bedfcbc538), `coefficients.jsonl`, `coefficients-meta.json`, `responses.json` and `arrivals.bin` identical byte for byte. `summary.toml` differs only in `wall_s` and `particle_steps_per_s` (job b4ad619e).
2. New binary with `restrict_to_classes = ["low_exposure_exterior"]` and the production class definitions: all 288 coefficient records of the exterior class equal the unrestricted run exactly; classes 0 and 2 empty.
3. Unit tests of the module: 30 passed, 0 failed, 4 ignored.
4. The wide-class draws were checked in the run output (`responses.json`, 6250 per model): GLORYS12 median 1.20 %, 95th percentile 2.66 %, 5 % of draws below 0.53 %; GlobCurrent (after offset) median 0.53 %, 95th percentile 2.00 %, 12 % at zero. `tables/wide-class-windage-draws.csv`.

Timing (smoke with production settings, 2 nodes × 2 environments, 6250 particles): GlobCurrent 14.0 s, GLORYS12 11.6 s of transport; peak memory 12.2 GB and 18.7 GB. The production run took 11.45 h for 18 legs. The new run transports one class. Estimate from particle steps: 4 to 5 h in total (stage 1 about 3 to 3.5 h, stage 2 about 1 to 1.5 h); the measured smoke rate alone would give 3.6 h of transport, and the southern legs cost more because of splitting. The first estimate of 3 h was too low because importance splitting dominates the cost and the exterior class carries most of it.

Run: job 27b6e292, started 9 Nov 2026 23:44 UTC, sequential legs under the shared lock, resumable. Output: `runs/wide-<model>-N/` on deskstar (`nodes.csv`, `coefficients.jsonl`, `arrivals.bin`, `responses.json`), progress in `runs/wide-chain.log`.

Next steps after the run: (1) rescore the exterior items with the arrivals-based scorer, take classes 0 and 2 from the production run (same nodes, same environment seeds), rerun smoothing and tension; (2) report the Mossel Bay arrival probability and the tension p-value with and without the wide class. Flaperon and interior-class results are not changed by this run.

## 6. Simulation-based calibration, smoke test (question 4)

Rule of the project: a smoke run is a code-path check and never evidence about the model. The results below are labelled accordingly.

Part A (statistic only; `scripts/sbc/`). `tension_lib.py` is the tension function of the smoothing script, unchanged, on the same bins, prior and core. Check: on the real headline curve it returns ln S = −0.705, d = 0.864, p = 0.1091, 1.60σ (reported earlier: −0.71, 0.109, 1.6σ). Toy worlds: truth drawn from the ruled core posterior; synthetic drift data y = x + noise; likelihood Gaussian in latitude (case A), or Gaussian with smooth random departures (case B). Rate: about 20,000 datasets in 1.2 s.

| Case | width s (°) | median d | P(p ≤ 0.05) | P(p ≤ 0.10) | P(p ≤ 0.1091) | P(ln S ≤ −0.705) |
|---|---|---|---|---|---|---|
| A, matched to the real posterior width (3.76°) | 3.91 | 1.22 | 0.043 | 0.095 | 0.103 | 0.121 |
| A, matched to the real effective dimension (0.864) | 6.09 | 0.85 | 0.053 | 0.169 | 0.181 | 0.115 |

Reading (toy only): the real curve cannot be matched in both width and effective dimension by a Gaussian, so the real likelihood is not Gaussian. For a nominal p of 0.1091 the false-alarm rate in the toy lies between 0.10 and 0.18, and the fraction with ln S at or below the observed value is about 0.12 in both. Where d is below 1 the χ² reference with d degrees of freedom becomes anti-conservative. The paper should therefore quote a simulated p-value from the real generator, with the χ² value as a nominal figure.

Module test (existing; `synthetic_recovery_coverage`, analytic field, 21 nodes, 60 trials, finds from independent ensembles, module scorer): 90 % highest-posterior-density coverage 58/60 = 0.967 (standard error 0.039 at 0.90), calibration ratio 1.056. This checks the module's generator–scorer consistency in a simplified world. Output: `tables/module-synthetic-coverage.txt`.

Part B (real generator and module scorer; not built). Requirements: sample truth from the core posterior; sample ocean sample, level draw and finds from the stored beachings (arrival chosen with probability proportional to weight × detection level, delay from the exponential model, place displaced along the coast by the kernel, segment from the place); score with the same pipeline; compute ln S, d and p; repeat 200 to 1000 times. Cost estimate: coefficients for synthetic finds need one pass over the 165 million stored beachings per batch of finds (24 s for 12 finds on 12 processes). Open design points: kernel displacement needs coast geometry; the generator must match the scorer in segments, periods and class totals, or the test measures the mismatch. What it can show: whether the tension p-value is calibrated for this likelihood. What it cannot show: physical errors (windage, delay, identity), because the same assumptions generate and score the data; the timing check against the real find dates (section 10.3 of the README) addresses that part.

## 7. Key assumptions and modelling choices

| Item | Value | Status |
|---|---|---|
| Core | final 7 Nov end-of-flight model with fuel, D0, `eof-final-handoff-df.npz` | Pete's ruling |
| Wide exterior class windage | log-normal, median 1.2 %, σ(log) 0.5, truncated 0.3 to 5 % | Pete approved the design as proposed; the numbers are my proposal; PROVISIONAL |
| Wind angle | normal(0°, 10°) | provisional (unchanged) |
| Production exterior class | normal(1.2 %, 0.3 %) truncated 0.5 to 2 % | provisional (CSIRO Part III p. 6) |
| GlobCurrent product offset | uniform [−0.75 %, −0.60 %], floored at zero | provisional (unchanged) |
| Ocean-error length scale | 100 km | assumed (provisional) |
| Eddy diffusivity | log-uniform 100 to 1000 m²/s | provisional |
| Importance splitting at Mossel Bay | factor 100 within 500 km | provisional |
| Items for wide run | six stringent exterior items; thirteen exterior shadow finds; flaperon and interior items taken from the production run | my choice |
| Identity weights, detection prior in time (0.1/0.5/1/1), delay (exponential, 60 d), kernel (50 km) | as in README | my choices / provisional (not Pete's rulings) |
| SBC toy worlds | Gaussian likelihood; truth from the ruled core | my choice; smoke test only |
