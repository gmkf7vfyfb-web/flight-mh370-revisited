# Run datasheet: `no-exhaustion-prior`

Written in simple English. Short sentences. One idea in each sentence.

This is the project's new reference run. It is the first full-scale run on the corrected fuel
model. It also removes the 00:17:30 exhaustion term completely. It supersedes
`6temper-realloc` for every result.

## 1. What changed from `6temper-realloc`

Two changes, and nothing else. The particle allocation, the tempering, the priors, the
observations and the seeds are the same.

| Change | Reason |
|---|---|
| The fuel-flow tables no longer give coincident speed schedules two separate points | A defect. The two-point drag fit became unstable. Some steps burnt no fuel at all. See `results/fuel-burn-gap.md`. |
| `exhaustion_target_utc = 00:17:30` and `exhaustion_sd_s = 300` are removed | The term forced a disputed hypothesis on the ensemble. It was worth only 0.168 nats. See `results/exhaustion-prior-is-nearly-inert.md`. |

`require_power_until = "m0011"` is kept. That is an observation, not a hypothesis. The
aircraft transmitted at 00:11. A path whose tank ran dry before then contradicts the data.

## 2. Run statistics

| Item | Value |
|---|---|
| Replicates | 8 |
| Particles for each replicate | 7,000,000 |
| Particles in total | 56,000,000 |
| Allocation across the five modes | 1.0 M / 0.5 M / 2.5 M / 0.5 M / 2.5 M |
| Wall-clock time | 15.52 h |
| Time for each replicate | 1.71 h to 2.48 h |
| Peak memory | 12,749 MiB |
| Log evidence | −98.420 |

The run is 1.65 times slower per replicate than `6temper-realloc`. The reason is the fix. More
paths stay alive, because fewer run out of fuel early and get rejected. A denser population
costs more work in the endurance proposal.

## 3. Convergence

| Item | Value |
|---|---|
| Split-half overlap, mean over all 35 balanced partitions | **0.9020** |
| Range across those partitions | 0.8188 to 0.9495 |
| Floor for 8 replicates | 0.924 |
| Verdict | **FAILS**, by 0.022 |
| Replicate median span | 0.339° |

`6temper-realloc` reached 0.9109 with a median span of 0.216°. So this run is less stable, not
more. Do not read that as the fix making the sampler worse. The two runs sample different
posteriors. The correct reading is that the corrected posterior is harder to sample
consistently, and that the convergence problem for fuel runs is still open.

The quantities below should be read against this. Report each one at the precision its own
agreement supports, not against one verdict for the whole run.

## 4. Posterior at 00:19:37

| Item | Value | `6temper-realloc` |
|---|---|---|
| Median | **−37.225°** | −37.643° |
| 50 % interval | [−37.85, −37.00], width **0.85°** | width 1.10° |
| 90 % interval | [−38.35, −35.50], width **2.85°** | width 3.70° |
| Shoulder mass, −36.5 to −34.5 | **0.1739**, which is 72 % of Davey's 0.2406 | 0.1018, 42 % |
| Overlap with Davey Fig. 10.3 | 0.6748 | 0.7879 |
| Mode probabilities | True track 0.589, lateral navigation 0.165, true heading 0.151, magnetic track 0.075, magnetic heading 0.020 | 0.596 / 0.250 / 0.100 / 0.044 / 0.011 |

Three points about this table.

The posterior is **tighter**, not wider. Both intervals narrow. The defect had kept slow
southern paths alive on fuel they never burnt, and those paths were widening the distribution.

The median moves 0.42° north. It is now 0.31° south of Davey's −37.532°.

The overlap with Davey falls. **That is expected and is not a fault.** Davey assumes infinite
fuel. Once a real fuel constraint acts, agreement with a model that has no such constraint
stops being a measure of quality. The same argument was already written down for the
conditioned posteriors.

The mode mixture moves weight out of lateral navigation and into the two heading modes.

## 5. Fuel state, and the post hoc test of the flame-out window

`fuel_no_flow_s` is **0.000 s** for every particle in every replicate. That column is now a
permanent assertion in the output. Any value above zero is a defect.

| Item | Value | Replicate range |
|---|---|---|
| Mean burn over the 18:01 to 00:19 leg | 36,293 kg, which is **5,764 kg/h** | — |
| Runs dry by 00:19:37 | **56.86 %** of the posterior | 52.4 % to 62.2 % |
| Runs dry between the 6th and 7th arcs | **51.01 %** of all mass | — |
| The same, as a share of what runs dry | **89.73 %** | 86.7 % to 91.9 % |

The burn rate is now inside the tabulated cruise band. At FL350 and about 192 t the tables give
5,395 to 6,241 kg/h. The defective model gave 4,788 kg/h, which was below the whole band at a
weight lighter than the flight started with.

**This is the test of the flame-out hypothesis, and the model does not assume it.** The
00:17:30 term is absent. Exhaustion time is an output. Half of the posterior runs dry inside
the 8.5-minute window between the two arcs, and nine tenths of everything that runs dry at all
lands in that window.

The replicate range on that share is 5.2 points. The density shape disagrees between halves by
about 9 points. So this quantity is better converged than the posterior shape, which is the
usual pattern: mass fractions converge faster than shape.

Selecting the window moves the median from −37.225° to −37.428° and narrows the 50 % interval
from 0.85° to 0.75°.

## 6. Limits

1. The run fails the convergence floor. Quote the median and the 50 % interval. Do not quote
   the shoulder mass or the mode probabilities as converged.
2. `fuel_exhausted_unix_s` is a `float32`. Its ulp at this epoch is exactly 128 s. Only about
   21 exhaustion times can be represented. The histogram in
   `results/no-exhaustion-prior-window.pdf` shows the representable times, not the true
   distribution. Store the value as an offset from a run-level epoch before this figure goes in
   the paper.
3. The latitude at exhaustion is not recorded. The figures use the latitude at 00:19:37.
4. The size of each manoeuvre is not recorded, only the count.
