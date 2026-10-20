# MH370 Rerun checkpoint 7 — 200-history physical coverage validation

Created 2026-09-19T08:41:29Z.

## Outcome

Checkpoint 6's single-history concentration is reproducible across independent physical proposal batches, but it is not invariant to proposal budget. Two hundred new full histories were evaluated in ten isolated batches of twenty, crossing forty declared seed vectors with all five navigation modes. All 200 initial states are distinct, all 200 strict initialization replays pass, all 400 independently reconstructed BFO factors match, and no history loses support at 18:39 or 19:41.

At 19:41:

- eight of ten twenty-history batches put more than 90% of their joint diagnostic weight on one history;
- four of ten exceed 95%;
- median batch maximum weight is 92.58%, with a maximum of 99.94%;
- median batch ESS is 1.162;
- pooling all 200 histories raises ESS to 4.305 and lowers the maximum weight to 33.52%.

This is the clearest result so far: the physical target is genuinely narrow, but the extreme single-history percentage is strongly dependent on finite proposal coverage. Pooling independent candidate coverage recovers alternatives; it does not converge to a unique initial trajectory at the tested budget.

## Matched proposal-budget comparison

The fixed ten batches were pooled without changing any path or weight:

| Histories pooled | Groups | Median joint ESS at 19:41 | Median maximum weight |
|---:|---:|---:|---:|
| 20 | 10 | 1.162 | 92.58% |
| 40 | 5 | 2.075 | 60.82% |
| 100 | 2 | 2.185 | 65.95% |
| 200 | 1 | 4.305 | 33.52% |

The 100-history median has only two groups and is not monotone; the complete group records are retained. Nevertheless, the 20-to-200 contrast shows that additional independent proposals materially recover distinct weighted histories. ESS remains only 4.3 out of 200, so brute-force budget alone is inefficient.

## Contact attribution

### 18:39

Across all 200 histories, incoming ESS is 13.09. BFO-only weighting reduces it to 9.34; proposal correction alone gives 3.37; joint weighting gives 9.69 with maximum weight 17.81%. No support is lost.

The 101 histories within two log-likelihood units of the best 18:39 measurement fit have proposal corrections spanning 16.22 log units—approximately 11.1 million-fold. The guide reaches many measurement-compatible states, but with extremely uneven proposal ratios.

### 19:41

Incoming ESS is 9.69. Measurement-only ESS is 2.485; proposal-only ESS is 2.489; joint ESS is 4.305. The pooled maximum is 33.52%, but small batches are usually nearly singular. Twenty-seven histories lie within two measurement log units of the best fit, and their proposal corrections span 12.74 log units—approximately 342,000-fold.

No support rejection occurs. Concentration is caused by narrow measurement compatibility combined with very uneven proposal–target overlap, then amplified by finite candidate coverage and any subsequent genealogy.

## Marginal instability

Leave-one-batch-out weighted CDF comparisons at 19:41 remain very large. Median maximum CDF differences are:

- latitude: 0.722;
- longitude: 0.842;
- altitude: 0.844;
- initial Mach: 0.787;
- initial altitude: 0.745.

These are diagnostic discrepancies, not calibrated uncertainty bands. They show that smooth-looking marginals from one small proposal batch would be unstable. The pooled joint weight is shared mainly by constant-magnetic-heading and constant-true-track cases (39.2% and 55.9% respectively), demonstrating more than one surviving control family, but those masses are not posterior mode probabilities.

## Estimator conclusion

The user's alternatives are not mutually exclusive:

- early SATCOM constraints are genuinely selective;
- 19:41 sharply narrows the compatible physical set;
- the existing guide assigns proposal ratios differing by five to seven orders of magnitude even among similarly good fits;
- finite proposal budgets often leave only one well-weighted representative;
- resampling then turns this overlap failure into genealogical concentration.

The ordinary prior/proposal correction is required and was previously validated; removing it would bias the target. The improvement should instead generate several independent, jointly guided 18:39–19:41 continuations per incoming ancestor and defer resampling until after both contacts. The exact measure and validation gates are recorded in `candidate-20260919T0837/JOINT-BLOCK-PROPOSAL-SPEC.md`.

## Ownership and boundaries

No sampler lane was acquired and no existing population experiment was duplicated. The shared workspace was absent after pruning, which was not treated as permission to take a lane. The work used the independent precompiled single-history probe only. Original source and the separate Resolution workspace were not modified.

The historical 18:01:49 source and 18:28:05.9 fuel anchor remain distinct from the unresolved 18:22:12 radar target. No endpoint was treated as observed, no backward bridge was run, and hydroacoustics remains excluded.

## Reproduction

```bash
python candidate-20260919T0837/prepare_extended_probe.py
python candidate-20260919T0837/run_extended_probe.py
python candidate-20260919T0837/analyze_extended_probe.py
```

Probe outputs must be fresh; the runner fails closed rather than overwrite them. The checkpoint retains all raw contact states, RNG transcripts, factor rows, configs, seeds, hashes, and journals.

## Limitations

- The seed grid is declared, not a random sample from the archived population.
- No population resampling, root genealogy, evidence comparison, or synthetic coverage test was run here.
- Pooling is an exact post-run importance comparison, not an implemented production bridge.
- No replacement estimator, calibrated probability, or solved location is claimed.
