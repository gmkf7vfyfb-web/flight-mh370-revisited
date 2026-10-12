# Run I proposal (core, 12 Oct 2026): free flight against the reset waypoint family, new speed envelope

Status: **proposal for Pete's GO.** Nothing is submitted. No deskstar deletion without Pete's yes.

## Purpose

The first fair test of free flight against waypoint flight at equal family prior (Pete's ruling, 11 Oct). It uses:
- the reset waypoint family: random routes over the 26 fixes valid in 2014, with break-off, fly-by/fly-over and the equator rule;
- Pete's speed rule: early phase unchanged, then cruise Mach 0.70-0.87 within 210-330 KCAS.

It also supplies the joint posterior that the zoom plot needs.

## Design

| Stratum | Early-phase file | Particles per seed | Notes |
|---|---|---|---|
| free | free.toml | 7M | as run D free |
| waypoints | **route-sampler.toml** (replaces waypoints.toml) | 7M | the discrete route space is large; run D routes had 3.5M |
| descent-climb | descent-climb.toml | 3.5M | as run D |
| repro-radar | none | 3.5M | **choice for Pete**: (a) new cruise speeds like the others, or (b) Davey 0.73-0.84 kept |

Common to all strata:
- the run D stack (davey2016-inmarsat, no-exhaustion-prior, fuel fixes s1-s8, inop-flow-fix, reference-snapshots, radar-full);
- `speed-envelope-throughout.toml`;
- the run C sampler (16 equal tempering stages, resampling 0.5);
- seeds 1-8, so the split-half floor is 0.924;
- look-ahead hand-offs at 22:41 and 00:11 (handoff-lookahead-d.toml, oversample 50, 100k rows), as end of flight reads them;
- trace on: 18:22:00-18:42:40 every 40 s, 2,000 route samples per seed;
- family prior 1/4 per stratum, so free and waypoints have equal weight.

Repro choice: under (a), run D remains the Davey-speed baseline (same stack, old speeds), so the paper can still show what the speed change does. Core recommends (a).

## Compute (deskstar, one stratum at a time at 88 threads)

| Stratum | Estimate |
|---|---|
| free | about 2.0 h |
| waypoints | about 2.2 h |
| repro-radar | about 0.9 h |
| descent-climb | about 0.6 h |
| **Total** | **about 5.5-6 h** |

Estimates are scaled from run D, which ran 4 seeds at 44 threads.

Peak memory: run D free was 21.7 GB. The trace buffer adds about 0.9 kB per live particle (about 4.5 GB at free's largest mode), so about 26 GB against the 36 GiB limit. Hence one stratum at a time.

## Disk (deskstar: 4.9 GB free of 59 GB)

Expected output is about 26-30 GB (run D was 12 GB at 4 seeds). Proposed:
1. Delete the superseded job folders: run G raw 4.9 GB (fly-over, superseded by run H); resample-threshold smoke 4.3 GB; the 10 Oct job a9f01687 1.2 GB; the audit, fly-by, hybrid and sensitivity arms about 0.4 GB in total. Free space becomes about 16 GB.
2. Bring each stratum back to the Mac exchange (116 GiB free) when it finishes, check it, then delete it on deskstar before the next stratum writes.
3. Runs E and F (14.5 GB each) stay, as ruled on 11 Oct, unless Pete releases them. Run H raw (4.9 GB) stays for now.

## Predictions (to be re-posted at submission)

1. **Waypoint family above free flight by 5-9 nats.** Smoke: sampler -128.1 (2 seeds x 420k, mean legs 2.68) against free -135.9 (run D) or -136.1 (speed smoke B). Free smoke and full-scale values agree within 0.7 nat.
2. Free flight under the new speeds within 1.5 nats of run D free (smoke: -0.9).
3. Waypoint posterior led by SAMAK first, fly-by, then south toward ISBIX (smoke 0.89). Break-off at 40-80 % of the first leg below 15 %. ANOKO and IGOGU first legs together below 15 %.
4. Every fly-by route starts its southward turn within 18:37-18:39.
5. 00:19 median within 0.3 deg of run H (-37.18), labelled "core, Davey both-BTO no-BFO 00:19 treatment".
6. Split-half: free at or above 0.924 (run C/F reached 0.912-0.918 at 7M x 8). Waypoints is uncertain; below the floor is possible because the plan space is large.

## What Pete gets

- Family log evidence and posterior shares, with seed spread.
- The zoom plot: posterior paths drawn in proportion to weight, coloured by family and by waypoint turn fix and break-off, with each group's posterior % and split-half.
- 60 s states for the IGO053 and UAE343 separation check, per family.
- Hand-offs (with route plans) for end of flight.
