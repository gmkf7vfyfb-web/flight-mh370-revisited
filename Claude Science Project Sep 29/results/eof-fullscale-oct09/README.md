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
