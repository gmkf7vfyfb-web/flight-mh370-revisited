# End of flight: first smoke run on real dynamics, 9 October

**SMOKE SCALE. PLUMBING, NOT EVIDENCE.** Every number below comes from one seed, a hand-off rebuilt at
20k particles per mode, and N = 4 children per parent, and is read from `contract-n4.json` (produced
by `engine/hypotheses/end-of-flight/smoke/analyse.py`). It is the first `impacts.npy` produced by this
module's own dynamics; earlier smoke impacts came from the `arc-kernel` placeholder.

## What was run

| | |
|---|---|
| hand-off | `davey2016 + no-exhaustion-prior + handoff-smoke + smoke/seed1 + smoke/particles-20k`, stop at 00:11, 2,000 rows (1,999 distinct particles), fuel_kg median 641.8 kg, **no row dry at 00:11** |
| terminal stage | `mh370 terminal` with `smoke/terminal.toml` + `smoke/children-4.toml`; module `end-of-flight` confirmed in `run.json` |
| code | `hypothesis/end-of-flight` at `d5936a6` (the binary was built from that tree; `run.json` records `ddee1b5-dirty`) |
| scale | 2,000 parents × 4 children × 4 descents = 32,000 impacts, 22.3 s at `RAYON_NUM_THREADS=2` |

**Why not core's configuration.** The rebuild began at core's 200k per mode, the scale core used for
its measured seed-1 hand-off (2,001 rows, 687 kg median, 9 rows dry). It was stopped under the
01:58 UTC CPU rule and redone at the project's smoke scale. The 20k hand-off therefore does **not**
reproduce core's measurement: it has 641.8 kg median fuel and no dry rows.

## The smoke contract

| item | result |
|---|---|
| 1. scope; smoke completes | **Pass.** 9 + 2 module files only, checked by hand against the working branch (core request 11 still open) |
| 2. every parent has an impact | **Pass.** 0 of 2,000 without one; the stage refuses an empty descent |
| 3. dry rows take the no-thrust branch; the rest derive flame-out in-stage; condition on nothing | **Partly assessed.** This hand-off has no dry rows, so the dry-row check was **not assessed at this depth**. The same branch was exercised by children the core flew dry before takeover (below). No fallback fired (0 fuel, 0 mass). |
| 4. full `ImpactView`; latents present, finite except declared hooks | **Pass.** 45 latents; none unexpectedly NaN; every declared hook NaN; impact fields finite |
| 5. spread per family; flag collapse or scatter beyond the glide bound | **Fails on the mechanism axis**, a defect described below. Propulsion × control spreads reported; 8 families flagged beyond the 103.4 NM glide bound of the arc, none collapsed |
| 6. quoted as plumbing | This page |
| 7. children per parent | **N = 4 only.** The N = 64 pilot is deferred to the morning by the 01:58 UTC rule |
| 8. measured cost | 32,000 descents in 22.3 s at 2 threads, about 1,430 descents/s or 360 children/s |

Proposal self-check: mean correction 0.9997 ± 0.0025 against an expected 1.

### Effective parents per data option at N = 4

| option | no-offset | startup-offset (Holland) | inflated |
|---|---|---|---|
| none | 2,000 | – | – |
| R600 | 503.9 | 374.3 | 1,483.1 |
| R1200 | 4.9 | 12.1 | 54.6 |
| both | 1.0 | 1.1 | 14.4 |

Everything below about 1,000 effective parents is **not resolved**: every R1200 and both cell, and
R600 raw and Holland. This is the collapse to 1–4 effective samples that the brief warned of with both
BFOs. It sets the target for the N = 64 pilot; it is not a result.

## The defect: the onset mechanism is mislabelled

**No flame-out-associated family appears.** About 53.1% of the weight is labelled anticipatory with
**zero** prior weight, which is an impossible label.

The cause is in this module and was introduced by the fuel-state fix (`7413c8d`). `takeover_time`
draws the onset against the exhaustion predicted from the **hand-off** state. Between the two hooks
the **core** propagates the aircraft on its own calibrated burn (5,764 kg/h against this module's
5,033) and its own stochastic manoeuvres. `descend` then recomputes the lead from the **takeover**
state. `classify` recovers the flame-out-associated mechanism only for a lead of exactly zero, and
after propagation the lead is never exactly zero:

- If the core ran the tanks dry before takeover, the lead is negative (53.1% of the weight). No
  mechanism can produce it, so the child is reported as anticipatory with prior zero.
- Otherwise the lead is small and positive (15.6% of the weight between 0 and 120 s), and the child
  is relabelled anticipatory.

Before the fix both hooks measured against the configured 00:17:30 constant, which made the recovery
exact by accident. That constant was the anchor that had to go.

**What it affects.** The mechanism label, the `family_prior` latent, and, through `draw_axes`, which
propulsion cells are legal for the child. Neither the impact weights nor the descent integrator read
the mechanism. The **control axis is unaffected**, which is why the Pléiades numbers below are given
by control.

**Fix.** No module-side recomputation can be exact while the two hooks see different states. The fix
is **core request 2**: pass `takeover_time`'s draw into `descend`. It is now a blocker, and is pinned
by the ignored test `the_flameout_mechanism_survives_the_cores_propagation`, which fails today.

## The burn gap, measured in the stage

53.1% of the weight was flown **powered by the core after its own tanks were dry**, between the
hand-off and this module's takeover. Among those children the duration is 4.8 / 43.4 / 70.2 s at the
5th / 50th / 95th percentile (`powered_after_core_exhaustion_s`). This happens because the module's
predicted exhaustion comes later than the core's real one. At a 00:11 hand-off it amounts to seconds.
At 22:41 it scales with the time to onset, roughly 0.145 × Δt, so up to about 14 minutes for a
96-minute onset window. **Core request 3 is on the critical path for V2.**

## Breakup family (settling's candidate rule), provisional

Implemented at `d5936a6` from `results/breakup-field-candidate.md`, drawn once per impact sample, with
settling's three fixtures reproduced. Under option `none`: intact 29.0%, broken 24.5%,
fragmented 46.4%; the rule refused none of the impacts.

## Pléiades section 11: displacement from the 00:19:37 position

The position at 00:19:37 is the module's own state when it flew through the burst (74.9% of the
weight). Where the takeover came after 00:19:37 (25.0%) it is a straight-line back-extrapolation from
the takeover position and ground velocity, which is approximate. Impacts already down by then (0.2%)
are counted as zero displacement. "North-west" is a bearing in [270°, 360°). "Inside the arc" is
`arc_distance_nm` ≤ −30 or −50 against the 00:19a arc, Pléiades' own table metric. Option `none`:
the 00:19 bursts are held out.

| | all | ditching attempt | maintained then lost | no intervention | upset then recovery |
|---|---|---|---|---|---|
| weight | 1.000 | 0.248 | 0.248 | 0.255 | 0.249 |
| NW ≥ 30 NM | 0.066 | 0.005 | 0.011 | 0.048 | 0.201 |
| NW ≥ 50 NM | 0.034 | 0.005 | 0.005 | 0.019 | 0.106 |
| inside arc ≥ 30 NM | 0.187 | 0.014 | 0.032 | 0.319 | 0.380 |
| inside arc ≥ 50 NM | 0.071 | 0.010 | 0.013 | 0.046 | 0.216 |

Displacement in any direction is 44.6 / 106.7 / 164.0 NM at the 50th / 90th / 99th percentile.

How to read this. The reach that Pléiades needs, 30–50 NM inside the arc, comes mostly from
**upset-then-recovery** and, for ≥ 30 NM, from **no-intervention**. Ditching attempts barely reach it.
The equal control weights are a statement of indifference, not a prior anyone has argued for, so the
"all" column is only as good as that choice. Under `both`, effective parents fall to about 1, so the
conditioned version is **not resolved** and is not given here. A rerun with a different random stream
moved NW ≥ 30 NM from 0.064 to 0.066, which shows the Monte Carlo noise at this scale.

## What changes in the morning

When core posts DELIVERED: the same contract on `handoff-m0011` at 20,000 rows per seed, with the N = 64
pilot. The snapshot directories are `seed-N/handoff-m0011/`, which `mh370 terminal` does not find
(it reads `seed-N/handoff.toml` and takes its later bursts from `exclude_epochs`). So the morning run
needs a symlinked run tree plus `exclude_epochs = ["m0019a", "m0019b"]` in the override, or a small
core change. The family attribution stays invalid until core request 2 lands.
