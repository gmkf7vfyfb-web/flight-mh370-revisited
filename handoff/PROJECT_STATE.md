# Project state at migration

## Research objective

Develop an integrated Bayesian estimator for MH370 that combines BTO, BFO,
received power/aircraft antenna gain, aircraft performance and trajectory,
ocean-drift evidence, conditional imagery evidence, and probabilistic search
non-detection—without imposing a prespecified end-of-flight scenario.

The current first-stage estimator begins near the 18:11 UTC radar position and
ends at the 00:11 UTC satellite arc. The 00:19 exchange and subsequent terminal
trajectory are reserved for a second stage.

## Completed work

### Integrated estimator through 00:11

Primary artifact: `outputs/mh370_stage1_0011/`.

- Seed: 3,700,011.
- 900,000 airborne augmentations and 1.2 million terminal propagations in the
  main run.
- Equal one-third prior across the principal control families.
- Model-averaged Davey-smooth and 12-study meta-analysis drift likelihood.
- No 00:19 likelihood.

Primary impact result after model-averaged drift:

- mode: about 37.26°S, 89.24°E;
- median: about 37.03°S, 89.71°E;
- 95% latitude interval: about 33.22°S–39.15°S;
- probability south of 36°S: about 0.729.

The result is broad and multimodal. A secondary/northern component occurs near
roughly 35°S, 92–93°E. These are posterior features, not unique crash points.

### Refined BFO random-noise analysis

Primary artifact: `outputs/mh370_refined_bfo_0011_airborne/`.

The pooled within-cluster successive-difference estimator, after removing
cluster difference means, gives fast random BFO sigma approximately 0.995 Hz,
with a reported 95% interval of approximately 0.859–1.183 Hz. Slow or
intermittent bias is not added to this random-noise estimate.

At 00:11, the reconstructed airborne posterior without drift has a mode near
36.50°S, 89.29°E. Backward smoothing of the marginalized drift likelihood shifts
and reweights the density but does not replace the satellite/RF solution.

### Received power and antenna gain

The project tests whether the terminal precompensated transmit power for antenna
gain. MH371 heading changes and known-position phases of MH370 are used as a
natural experiment. The project preserves both a marginalized compensation
model and a no-precompensation sensitivity.

Artifacts include:

- `mh370_power_compensation_hypothesis_results.csv`;
- `mh370_power_compensation_phase_data.csv`;
- associated profile-likelihood and sensitivity graphics;
- `mh370_refined_gain_validation.png`;
- received-power/HGA explanatory graphics under `output/graphics/`.

### Conditional Pleiades/BRAN analysis

Primary artifact: `outputs/mh370_pleiades_bran_diagnostic/`.

This is an along-arc BRAN-anchor diagnostic, not a complete two-dimensional
BRAN rerun. When the selected Pleiades objects are assumed to be MH370 debris,
the diagnostic impact mode is approximately 35.29°S, 92.59°E, with median
approximately 35.35°S, 92.54°E. A published three-origin sensitivity is also
retained. No search-area mask was applied and no probability is assigned to the
imagery premise.

### No-power-precompensation sensitivity

Artifacts are under `library_no_precomp/MH370/` and
`library_materialized/MH370/`.

Removing power precompensation reweights and sharpens components but does not
eliminate the southern mode without Pleiades. Conditional Pleiades/BRAN runs
remain concentrated in the northern component. The carried-forward script is
not currently executable because a required imported module is missing; see
`REPRODUCIBILITY_STATUS.md`.

### Pulau Perak descent/re-climb sensitivity

Primary artifact: `outputs/mh370_pp_descent_climb_sensitivity/`.

The analysis tests a reported low-altitude branch near Pulau Perak followed by
re-climb. Median incremental fuel effects are small: about 0.029 t for the
PP-only case and about 0.168 t for the broader high-altitude-plus-PP case. The
conditional 00:11 latitude changes by less than about 0.003° in the primary
cases. The practical conclusion is energy-equivalence/compensation: this
scenario makes little difference to the principal posterior under the tested
trajectory anchoring, while remaining a legitimate historical uncertainty.

### Search-area evidence

Primary artifact: `outputs/mh370_search_evidence/`.

The package inventories the 2014 surface search, Bluefin-21, ATSB bathymetric
and high-resolution sonar campaigns, Ocean Infinity 2018 work, Ocean Infinity
post-contract work, and 2025–2026 contracted/pre-contract activity. Published
areas and source grades are separated from reconstructed geometry. Bathymetry
is not treated as wreckage-detection coverage; sonar non-detection is strong
but non-binary and footprint-uncertain.

### Manuscript development

Primary artifacts: `outputs/paper_draft/`.

- Working title: *Flight MH370 Revisited: Integrated Bayesian Estimation
  without a Prespecified End-of-Flight Scenario*.
- Sections 1–2 first pass: 1,614 words.
- Whole-paper target: approximately 7,200–7,600 words and 18–20 pages.
- Separate end-of-flight/radar/Pleiades evidence note completed in draft form.
- Paper distinguishes established facts, published findings, reproduced
  results, reconstructed analyses and new analyses.

## Interpretive conclusions currently supported

1. The integrated evidence supports a broad, multimodal southern Indian Ocean
   density, not a single deterministic point.
2. High-altitude near-level flight is not required by the model; descent-open
   families remain material.
3. Drift evidence changes weights and width but does not independently dictate
   the solution.
4. The conditional Pleiades hypothesis selects the lower-prior northern spike;
   it should be presented beside, not averaged into, the unconditional result.
5. The Pulau Perak descent/re-climb scenario has little practical posterior
   effect in the tested model because its net fuel/energy effect is small.
6. Search non-detection must be assimilated probabilistically and only where
   detection-capable coverage is defensible.

