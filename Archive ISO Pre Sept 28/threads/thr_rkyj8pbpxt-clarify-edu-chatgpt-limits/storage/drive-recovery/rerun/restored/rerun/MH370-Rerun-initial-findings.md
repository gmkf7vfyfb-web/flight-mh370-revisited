# MH370 Rerun: first diagnostic checkpoint

19 September 2026. This is the start of the requested overnight investigation. The scheduled 12-hour report is due at approximately 14:34 UTC. These are completed checkpoint analyses and methodological controls; a replacement aircraft estimator has not yet been validated.

## What the concentration means

The 95.63% and 98.19% largest-ancestor weights belong to two difficult **synthetic** runs with the same generated observations and truth, each starting with 500,000 candidates. They do not describe every MH370 production run. The six authenticated real-flight production runs have largest-ancestor weights of 2.99%–17.51% and ancestor-weight effective sizes of 20.95–152.41. Those are still small relative to their 85,000–255,000 initial populations, but the distinction matters.

Tracing the saved checkpoints identifies a common bottleneck: **18:28:14 to the block ending 19:41:02**. In the synthetic pair, effective ancestry falls from 49,116.72 to 4.1483, and from 49,060.41 to 1.5026. This is an 11,840-fold and 32,650-fold reduction. That block contains the 18:39:55 BFO-only call and the 19:41:02 BTO/BFO observation. The same block has the largest relative decline in all six production runs, by factors of 165–4,900.

| Run type | Seed | Initial candidates | Final ancestor-weight ESS | Largest ancestor mass |
|---|---:|---:|---:|---:|
| Synthetic, shared truth | 37111900 | 500,000 | 1.0925 | 95.6297% |
| Synthetic, shared truth | 37111901 | 500,000 | 1.0370 | 98.1889% |
| MH370 production | 37091631 | 85,000 | 20.9514 | 17.5116% |
| MH370 production | 37091640 | 85,000 | 48.6812 | 9.1838% |
| MH370 production | 37091711 | 255,000 | 94.2120 | 7.6666% |
| MH370 production | 37091712 | 255,000 | 152.4098 | 2.9861% |
| MH370 production | 37091713 | 170,000 | 84.6259 | 6.4024% |
| MH370 production | 37091714 | 170,000 | 29.2934 | 17.2482% |

The raw configurations and checkpoint files were copied only after matching their full hashes and sizes to the supplied package manifest. The table uses archived diagnostics, not new aircraft simulations. An effective size is a concentration statistic, not an independent sample count. It can rise later if surviving roots receive more even weights; that does not mean lost roots were recovered.

The exact historical synthetic source applies its exhaustion-compatibility likelihood only at the final observation. Thus that final nine-node fuel factor is **not directly being applied at the 19:41 collapse**. Fuel propagation, model support and environmental boundaries still require checks; the known fuel quadrature defect remains important for the final distribution. Source evidence is retained in `source-evidence/cruise_filter.rs` and its archive/hash record.

The remaining causal split is unresolved. Aggregate checkpoints cannot tell how much of this collapse is due to the 18:39 BFO, the 19:41 BTO or BFO, proposal-correction tails, initial Mach/altitude coverage, shared bias, or environmental support. The next physical diagnostic must record these factors and the actual initial states before and after the block. Tight initial position uncertainty alone does not establish narrow uncertainty in heading, speed, altitude, modes, manoeuvre history, wind, bias or fuel.

The earlier independent analysis found synthetic latitude and longitude CDF disagreements of 64.83 and 63.19 percentage points between seeds. These show that the two finite estimates cannot both be close to the same target CDF. They do not prove which run is closer, identify the true posterior, or establish a repeated-data calibration rate from one synthetic truth.

## Backward and two-ended inference

The proposed approach is worth testing. For a Markov state with an evaluable transition law, the backward kernel is proportional to the saved filtering weight times the **forward** transition probability to the next state. It is not obtained simply by reversing time in the forward dynamics. It can select from earlier filtering populations instead of following only the final population's surviving parent links. [Lindsten, Jordan and Schön, 2014](https://jmlr.org/papers/volume15/lindsten14a/lindsten14a.pdf).

A separate family of bridge methods uses future observations to guide intermediate propagation, with compensating weights that retain the declared target. This can be useful when a long gap ends in a narrow observation. Approximate guidance must be corrected rather than counted as extra data. [Del Moral and Murray, 2015](https://arxiv.org/abs/1405.4081).

I implemented finite-state forward/backward and bridge controls with exactly computable answers. These are **not aircraft simulations**. Across 24 fixed inference seeds for each of two models, median initial-state CDF error was:

| Method | Tight initial distribution | Broad initial distribution |
|---|---:|---:|
| Follow surviving forward parent links | 0.2417 | 0.3321 |
| Backward simulation over saved filter populations | 0.0770 | 0.1344 |
| Bridge using an exact future-information function | 0.0547 | 0.0644 |

The backward method adds computation to the same forward filter. The last method has an exact future-information function unavailable for the aircraft model. This is a feasibility control, not an equal-cost comparison or proof that either method solves MH370. Exhaustive enumeration of all 81 paths in a separate small case agrees with the smoother and bridge law within 1.67e-16. A deterministic-transition control checks that backward steps do not join incompatible states.

An endpoint sampled uniformly is a **proposal**, not an observation or posterior. In these controls, reversing from equally weighted uniform endpoints produces a maximum marginal CDF error of about 0.703. Weighting endpoints by posterior endpoint probability divided by proposal probability recovers the exact finite-model marginals within 2.22e-16. An aircraft implementation needs the corresponding proposal correction, appropriate area/time measures, full nuisance state, and support accounting.

![Archived ancestry and controlled backward tests](results/ancestry-and-backward-controls.png)

## Initial and terminal boundaries need explicit treatment

The archived broad-flight runs initialize at **18:01:49 UTC**, at 5.624829°N, 99.048157°E. Their fuel prior is 32,524.10–34,524.10 kg at **18:28:05.9**. These are the actual configuration values, not a newly verified statement about the aircraft.

A separate supplied final-radar configuration uses 6.578°N, 96.340°E with a 2 NM position scale and 2° direction scale. Its observation offsets imply **18:22:12 UTC**. It uses a different model branch and a 4 Hz BFO override; it cannot be substituted into the broad 7 Hz model without an explicit target/configuration change. The underlying radar-source uncertainty and fuel propagation to this boundary still need reconciliation.

The user's **00:15–00:17 fuel-exhaustion window** will be tested as an explicit conditional hypothesis alongside the preserved 00:15–00:19 baseline. The geometry between the 00:11 and 00:19 arcs is useful for proposal design, but it is not an observed position at the exhaustion time. A continuation after exhaustion is needed to relate that state to 00:19. Using 00:19 range data would be an additional explicitly labelled likelihood/sensitivity relative to the current through-00:11 baseline, which uses later timing only. Time, heading, altitude, speed, wind and remaining usable fuel must be included; a two-dimensional endpoint alone is insufficient.

The physical model has discrete manoeuvre events, persistent/static parameters, memory, and partly deterministic transitions. Simple backward splicing may therefore have zero support. The candidate should retain or augment the necessary state, use conditional trajectory bridges or explicit-innovation moves where appropriate, and derive every proposal ratio. The parallel draw-map development already documents why arbitrary edits to a consumed PRNG word are not automatically valid local posterior moves.

## Next work and handoff

1. Reconcile the 18:01:49 and 18:22:12 radar branches against source evidence and construct a separate, fully specified final-radar target. Carry fuel uncertainty to the correct time; do not relabel an old fuel prior.
2. Instrument the 18:28–19:41 block without changing the original random sequence. Save factor-wise likelihood/proposal changes, support failures, initial physical states, and rejected histories. Authenticate replay before interpreting those diagnostics.
3. Test a corrected future-guided bridge across this block, then extend to an uncertain terminal fuel state. Compare matched model targets and costs; retain failed modes and seeds.
4. Combine valid early-state moves with backward/bridge proposals. Backward re-selection cannot recover regions absent from every saved bank, and late-only moves cannot fix lost initial support.
5. Run prespecified synthetic recovery, known-flight and repeated-seed diagnostics. Improve code and numerical integration separately from changing physical priors. No posterior is adopted solely because its map looks plausible or acceptance is high.
6. Keep hydroacoustic evidence excluded until the core estimator has been built and its adequacy assessed. If those tests fail, report the failure and keep the hydroacoustic update pending.

At the scheduled checkpoint, create or reuse `MH370 Review/Rerun`, publish a summary and a portable continuation bundle, and continue afterward. The hourly execution task is separate from the existing `Resolution` investigation. Existing long-running inference lanes and original sources are not modified by this diagnostic.
