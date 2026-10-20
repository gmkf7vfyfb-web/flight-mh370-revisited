# MH370 Rerun checkpoint 6 — bounded physical factor attribution at 18:39/19:41

Created 2026-09-19T07:40:32Z.

## Outcome

This is Rerun's first executed full-aircraft bottleneck diagnostic. It uses an already compiled, independently packaged version of the original physical model and the exact recovered ERA5, MH370 IGRF, SATCOM, satellite, fuel, and guided-initialization inputs. It evaluates twenty declared histories—four fixed seed vectors in each of five navigation modes. It does not run a sampler, branch or resample a population, estimate evidence, or produce a posterior location.

The result directly demonstrates a likelihood/proposal-overlap bottleneck at 19:41:

- all twenty histories retained dynamical/model support through both 18:39 and 19:41;
- measurement weighting alone at 19:41 gives a diagnostic ESS of 2.209;
- proposal-correction weighting alone gives 2.017;
- joint weighting gives ESS 1.053 and assigns 97.40% of this twenty-case diagnostic mass to one history;
- among the five histories within two log-likelihood units of the best 19:41 measurement fit, proposal corrections span 11.675 log units, a factor of approximately 117,600.

This rules out support rejection as the mechanism in these twenty histories. It also shows that neither the measurement factor nor the proposal correction alone explains the local collapse: concentration occurs because only one tested history combines a strong measurement fit, favorable incoming weight, and a favorable proposal ratio.

## Exactness controls

The baseline and instrumented executables were preserved in the prior draw-map development package but had not been physically executed. Their SHA-256 values are recorded in the validation receipt.

- 20/20 baseline initial states equal their instrumented counterparts exactly.
- 20/20 instrumented initializations replay exactly from the captured public RNG-call transcript.
- 40/40 BFO contact factors—two contacts for each history—match an independent predictive-normal reconstruction from the saved innovation and prior bias variance.
- Complete per-contact states, RNG transcripts, failures/work journals, staged config, input hashes, and factor rows are retained.

## Contact-level results

### 18:39:55

This contact contains BFO but no BTO. Across the twenty declared histories, the BFO log factor ranges from −169.86 to −3.06. The proposal correction ranges from −13.30 to +3.00. No support is lost.

The diagnostic ESS is already only 1.821 before 18:39, showing that the earlier contacts and incoming proposal weights have already concentrated this small independent set. Applying only the 18:39 BFO reduces it to 1.427; applying only the proposal correction raises it to 2.734; applying both gives 1.996. In this bounded diagnostic, the 18:39 proposal correction partly counteracts rather than causes concentration.

Even here, proposal overlap is uneven: the eight histories within two log-likelihood units of the best 18:39 fit have proposal corrections spanning 11.253 log units, approximately a 77,000-fold ratio.

### 19:41:02

The BTO term has much greater dispersion over all twenty histories than the BFO term: BTO log factors range from −1704.03 to −4.34, while BFO ranges from −58.60 to −3.03. Those extreme tails mainly show that unguided full histories can miss the arc badly; they are not posterior tail probabilities.

The incoming diagnostic mass is dominated by a history that fits the 19:41 BFO poorly. The 19:41 measurement changes the winner. Measurement alone spreads appreciable mass over several compatible histories, and the proposal correction alone also leaves about two effective histories. Their intersection, however, is almost singular: the joint weighting produces a 97.40% maximum case weight.

This is evidence for poor proposal–target overlap, not evidence that the required `log(prior/proposal)` correction should be removed. Removing it would condition on the guided proposal as though it were the prior and would bias the target. A better estimator should construct proposals that reach the joint 18:39-BFO/19:41-BTO-BFO-compatible region more often while retaining the exact correction.

## Implication for the archived 96–98% ancestry result

The result supports a mixed explanation:

1. the early SATCOM constraints are genuinely selective—the twenty-case ESS is already 1.821 before 18:39;
2. 18:39 BFO is highly selective, but its proposal correction is locally compensatory in this diagnostic;
3. 19:41 exposes a severe overlap problem: multiple measurement-compatible histories exist, but their proposal ratios differ by roughly five orders of magnitude;
4. no support rejection occurs at either contact in these histories.

This does **not** yet prove that proposal overlap quantitatively caused the archived synthetic pair's 96–98% single-root mass. The tested histories are fixed conditional-mode engineering cases, not the archived filtering population. The opt-in population exporter or a matched-budget physical comparison is still required for that attribution.

## Estimator direction

The next implementation should guide the entire 18:39–19:41 block jointly, or introduce a valid block-boundary/bridge proposal, rather than separately aiming at only the terminal BTO. It must:

- retain the exact transition prior divided by proposal density;
- carry BFO bias/calibration state into the joint guide;
- preserve the fact that 18:39 and 19:41 are separate observations in one BTO-terminated block;
- avoid reusing their likelihoods both in the proposal and again without correction;
- compare multiple seeds, matched path-evaluation budgets, actual initial-state diversity, support, row/root ESS, evidence, CDF shifts, and synthetic coverage.

Backward/two-ended flight histories from uncertain exhaustion states remain a later extension after this bottleneck proposal is validated. The 00:15–00:17 window remains a conditional sensitivity against 00:15–00:19. Hydroacoustics remains excluded.

## Reproduction

From the extracted checkpoint root:

```bash
python candidate-20260919T0733/prepare_physical_probe.py
candidate-20260919T0733/bin/baseline-probe candidate-20260919T0733/input/baseline-probe-job.json
candidate-20260919T0733/bin/instrumented-probe candidate-20260919T0733/input/physical-probe-job.json
python candidate-20260919T0733/analyze_physical_probe.py
```

The output directories must be fresh because the binaries fail closed rather than overwrite a prior diagnostic. The portable checkpoint includes the raw outputs and the exact inputs other than the large ERA5 file, which remains recoverable through the authenticated multipart receipt.

## Limitations

- Twenty histories are too few for probability calibration or robust mode-frequency claims.
- No population resampling, root ancestry, evidence, marginal CDF, or coverage estimate is produced.
- The newer factor-export runner remains uncompiled because Rust 1.98.0 is unavailable.
- No replacement estimator, calibrated probability, or solved location is claimed.
