# End of flight: the full-scale 00:11 smoke contract and the children-per-parent pilot, 9 October

**Measured on `hypothesis/end-of-flight` at `2923512`, which predates core requests 2 and 3 (`52ce1ca`).**
So the onset mechanism is still recomputed from the core-propagated state, and powered flight still
burns this module's swept TSFC (5,033 kg/h against the core's 5,764 at the fixture state). The
importance weights and the descent integrator do not read the mechanism, so the effective-parent
counts below are valid for **sizing N**. The burn model does change the physics, so every number here
is re-measured after requests 2 and 3 are adopted, and the difference is reported. **No family
attribution is quoted.**

Hand-off: `reference-snapshots`, `seed-{1..8}/handoff-m0011/`, read through a symlinked run tree and
`smoke/snapshot-m0011.toml` (`exclude_epochs = ["m0019a","m0019b"]`), as ruled. SHA-256 of every
`handoff.toml` is in `handoff-m0011.sha256`. 20,000 parents per seed (one seed 19,999), 160,000
in total. All numbers are read from the JSON files in this directory: `contract-n4*.json` (N = 4, all 8
seeds), `pilot-*-summary.json` and `pilot-ess-parents.json`.

## The six-item contract at full scale (N = 4, all 8 seeds)

Pooled with equal weight per seed; brackets give the range across the 8 seeds.

| item | result |
|---|---|
| 2. every parent has an impact | **Pass.** 0 of 159,999 |
| 3. dry rows take the no-thrust branch; flame-out derived in-stage; condition on nothing | **Pass, after a fix.** 85 rows per seed are dry at 00:11 (18–131; 0.42% as core reported). On the first run about 2/3 of their descents were labelled thrusting and given powered profiles. Fixed at `2923512`: dry at takeover means `NeitherThrusting`. Re-run: **0 dry-parent descents labelled thrusting on every seed.** No fallback fired on any seed |
| 4. full `ImpactView`; latents present, finite except declared hooks | **Pass.** 44 latents (`sinks_not_floats` retired), no unexpected NaN on any seed, declared hooks all NaN |
| 5. spread per family | Propulsion × control spreads computed; 16 families flagged beyond the 103.4 NM glide bound of the arc, none collapsed. **Mechanism axis not quoted** until request 2 is adopted |
| 6. quoted as plumbing | This page |

Proposal self-check, mean correction per seed: 0.9987–1.0007, standard error 0.0007–0.0008.

**The burn gap inside the stage:** 50.2% of the weight (49.0–51.0%) was flown powered by the core
after its own tanks were dry, median 42 s (37–48 s). Request 3 should remove this; it is re-measured
after adoption.

**Breakup family** (settling's rule, drawn once per impact), option `none`: intact 27.1%, broken
25.1%, fragmented 47.8%. The across-seed range is under ±0.2 pp, which says nothing about whether the
rule's constants are right.

## Item 7: effective parents per data option

Effective parents per replicate (20,000 parents), with the 1,000 threshold below which an option is
labelled not resolved.

| option / BFO model | N = 4, s1 | N = 4, s2 | N = 16, s1 | N = 64, s1 | N = 64, s2 | status at N = 64 |
|---|---|---|---|---|---|---|
| none | 20,000 | 19,999 | 20,000 | 20,000 | 19,999 | resolved |
| R600 / inflated | 13,384 | 13,683 | 14,878 | 15,294 | 15,557 | resolved |
| R600 / no-offset | 3,413 | 3,851 | 5,803 | 6,880 | 7,986 | resolved |
| R600 / startup-offset (Holland) | 2,168 | 2,792 | 3,368 | 3,912 | 5,112 | resolved |
| R1200 / inflated | 484 | 629 | 875 | 1,185 | 1,625 | resolved, narrowly |
| R1200 / no-offset | 92 | 92 | 300 | 448 | 401 | **not resolved** |
| R1200 / startup-offset | 148 | 156 | 380 | 582 | 575 | **not resolved** |
| both / inflated | 102 | 99 | 256 | 385 | 325 | **not resolved** |
| both / no-offset | 3.2 | 3.9 | 15.1 | 16.9 | 14.2 | **not resolved** |
| both / startup-offset | 11.5 | 9.4 | 26.5 | 102.7 | 34.4 | **not resolved** |

**By the agreed rule, the smallest adequate N is 16.** The strictest option, `both`/no-offset, stops
gaining effective parents between 16 and 64 (15.1, then 16.9 and 14.2, which is within the spread
between seeds).

**More children will not resolve the strict options. That is the finding, and it is about the
sampler, not about N.** Going from 16 to 64 children multiplies the R600 counts by 1.03–1.19 and the
R1200 and `both` counts by 1.1–1.5 on seed 1, while the strictest settles near 15 per seed. The one
exception, `both`/startup-offset rising from 26.5 to 102.7 on seed 1 against 34.4 on seed 2, is a
count too small to be stable, not a trend. The
binding constraint is how many **parents** can produce the 00:19 BFOs at all under raw or Holland
interpretation, so the effective count is bounded by the hand-off population, not by the descents
drawn from it. Brief §8 already requires a defensive mixture of plain and targeted proposals with
exact weights. These counts are the measured reason it is needed: the targeted component has to place
children where the R1200 and `both` likelihoods have mass. The `both`/startup-offset pair at N = 64,
102.7 on seed 1 against 34.4 on seed 2, shows how unstable a count of this size is.

## Item 8: measured cost

At `RAYON_NUM_THREADS=12` under the heavy-job lock: **about 12,900 descents/s, or 3,200
children/s**, linear in N (N = 4 over 8 seeds 222.6 s; N = 16 one seed 100.9 s; N = 64 one seed
397.2 s and 389.8 s). A full 8-seed sweep therefore takes about 13 min at N = 16 and 53 min at N = 64,
**per data-option configuration** (options and BFO models are columns, so they come free).

**Disk, not CPU, bounds the sweep.** `impacts.npy` is about 600 bytes per impact: 0.77 GB per seed at
N = 16 and 3.0 GB at N = 64, so 6.2 GB and 24 GB for 8 seeds. With the 25 GiB floor and about 30 GiB
free this morning, a full N = 64 sweep cannot be written at all, and N = 16 only seed by seed with
deletion. That is a storage question for the composer and core, raised in the coordination entry, not
solved here.

---

## After core requests 2 and 3 (`ffc3fbe`, then `b3c07f2`)

Requests 2 and 3 were adopted at `ffc3fbe`. The full-scale contract (N = 4, all 8 seeds) and the
pilot at N = 16 and N = 64 on seed 1 were re-run on that commit. Files: `r23-*.json`. The N = 64
replicate on seed 2 was **not run** on the new code: free disk fell to 25 GiB during the sequence
from another session's writing, and the run stopped at its floor check. Seed 2's pre-request N = 64
count stands as the replicate, which is defensible because seed 1's counts move by -12.4% to +3.2%
between the two codes (largest R1200/no-offset, 392 against 448), which is the scale of seed-to-seed
scatter at these counts, not a systematic shift.

**Request 2 works.** In every seed, 100% of samples take their mechanism from the carried draw
(`mechanism_from_draw`), and none needed the dry relabelling. The mechanism split is now physical:
**flame-out-associated 46.3% [45.5, 47.2], anticipatory 45.0% [44.2, 45.5], fuel-cue 8.7% [7.3, 10.3]**.
It was 0 / 96 / 1 when the mechanism was recovered from the propagated state. The former ignored test
passes as the acceptance test, with a control showing that the legacy path still loses the mechanism.

**Request 3 prices the burn.** No second of powered flight went unpriced. 10.3% of the weight spends
some time below FL060, where the tables understate flow (mean 27 s per sample), and 29.7% spends some
time on an extrapolated schedule (mean 128 s). Both are latents.

**The burn gap in the onset trigger is not closed: 50.2% of the weight is still flown dry by the core
before takeover, median 42 s.** That is expected. `takeover()` receives no fuel model, so the
exhaustion prediction that triggers onset is still priced by this module's TSFC. Raised as
**request 3b** (pass `&dyn FuelFlow` to `takeover()`). It amounts to seconds at 00:11 and minutes at
22:41, so it blocks the 22:41 arms, not this 00:11 contract.

**Effective parents are unchanged to within noise:** at N = 64 on seed 1, R600/no-offset 6,896 (6,880
before), R1200/inflated 1,135 (1,185), R1200/no-offset 392 (448), `both`/no-offset 17.4 (16.9). The
item 7 conclusion stands: **N = 16 by the agreed rule; R1200 raw and Holland and `both` are bounded by
the parent population, not by N.**

**One more label fixed at `b3c07f2`:** an already-dry hand-off (0.42%) drew flame-out-associated with
a mechanism prior of zero. Given the aircraft is dry, that mechanism is certain, so its prior is now 1.
This touches the `family_prior` latent only, not the weights. It is not yet re-run at full scale
because the disk is at its floor.

### Pléiades section 11, now by taxonomy axis (option `none`, `ffc3fbe`, 8 seeds pooled [range])

| axis | value | weight | NW ≥ 30 NM | NW ≥ 50 NM | inside arc ≥ 30 | inside arc ≥ 50 |
|---|---|---|---|---|---|---|
| all | | 1.000 | 0.061 [0.060, 0.063] | 0.034 [0.033, 0.034] | 0.227 [0.206, 0.245] | 0.097 [0.089, 0.102] |
| control | upset then recovery | 0.249 | 0.174 [0.169, 0.180] | 0.095 [0.092, 0.098] | 0.389 [0.372, 0.405] | 0.248 [0.230, 0.267] |
| | no intervention | 0.250 | 0.046 [0.044, 0.048] | 0.020 [0.019, 0.021] | 0.421 [0.369, 0.474] | 0.083 [0.072, 0.088] |
| | maintained then lost | 0.250 | 0.016 [0.015, 0.017] | 0.010 [0.009, 0.011] | 0.064 [0.057, 0.073] | 0.030 [0.028, 0.036] |
| | ditching attempt | 0.250 | 0.010 [0.008, 0.012] | 0.010 [0.008, 0.012] | 0.035 [0.031, 0.043] | 0.028 [0.026, 0.033] |
| mechanism | flame-out-associated | 0.463 | 0.056 [0.054, 0.059] | 0.030 [0.029, 0.031] | 0.158 [0.135, 0.181] | 0.070 [0.061, 0.076] |
| | anticipatory | 0.450 | 0.064 [0.063, 0.065] | 0.034 [0.033, 0.035] | 0.264 [0.248, 0.277] | 0.108 [0.102, 0.112] |
| | fuel-cue | 0.087 | 0.072 [0.070, 0.074] | 0.050 [0.049, 0.052] | 0.403 [0.394, 0.410] | 0.187 [0.182, 0.192] |
| propulsion | none thrusting | 0.641 | 0.058 [0.056, 0.060] | 0.029 [0.028, 0.030] | 0.183 [0.161, 0.204] | 0.078 [0.069, 0.083] |
| | one thrusting | 0.179 | 0.067 [0.066, 0.070] | 0.040 [0.040, 0.041] | 0.306 [0.288, 0.316] | 0.131 [0.123, 0.136] |
| | two thrusting | 0.180 | 0.068 [0.066, 0.069] | 0.041 [0.040, 0.042] | 0.306 [0.293, 0.318] | 0.133 [0.127, 0.138] |

**The control axis carries the north-west reach.** An upset that is dynamically recovered reaches
≥ 30 NM north-west 17% of the time; a ditching attempt reaches it about 1% of the time. Mechanism and
propulsion move the north-west reach by a factor of about 1.3, though they matter more for distance
**inside** the arc (powered 31% against unpowered 18% at ≥ 30 NM). Every "all" figure inherits the
equal family priors, which are a statement of indifference. The data are held out (option `none`):
under `both` the effective parents number 2-17 per seed, so no conditioned version is given.
