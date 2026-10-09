# Early-flight families: configuration notes

Moved from `engine/config/sensitivity/early-families/README.md` (engine/ holds only three markdown files).


Overlays on `davey2016.toml` + `sensitivity/no-exhaustion-prior.toml` that sample the flight
after 18:01:49 under three exclusive families, each run as its own configuration. With
equal family prior weights, P(family | data) is proportional to exp(logZ_family) (each logZ
already marginalises the five autopilot modes), so separate runs give exactly what a single
run with families as strata would give.

| file | family |
|---|---|
| `scale.toml` | smoke scale: 100,000 particles per mode, seeds 1-2 |
| `track-289.toml` | prior track 289.7 deg (Davey Fig. 4.2 at 18:02) instead of 295.66 |
| `free.toml` | F1 free cruise: early Mach 0.45-0.87 clipped to 210-330 KCAS until 18:40, half the trajectories turn at 18:22:12 to a track uniform on 270-340 deg |
| `descent-climb.toml` | F2: F1 plus a descent after 18:01:49 to 2,000-10,000 ft and a climb back to cruise ending 18:13-18:18 (radar re-acquisition 18:15:25) |
| `waypoints.toml` | F3: a route skeleton (48 declared: 6 x 8) flown on true track from 18:01:49, then the free model |

Run as: `mh370 config/davey2016.toml config/sensitivity/no-exhaustion-prior.toml
config/sensitivity/early-families/scale.toml [track-289.toml <family>.toml] <out>`.
Smoke results check code paths and give first indications; they are not conclusions.
Known approximations: fuel below FL060 is priced at FL060 (tables end there); the BFO
uses the scripted vertical rate during the excursion only when `bfo_vertical_rate` is on
(it is, in no-exhaustion-prior); winds below the lowest ERA5 level are taken at that level.

## Overnight 9-10 Oct 2026


Ruled by architecture (coordination/architecture.md, ~02:10 and ~02:50 UTC 9 Oct) and Pete.
Each stratum is a separate invocation in the existing output schema (no family column yet;
request 13's native axis is later). Strata are independent by construction (same seeds,
own RNG streams), so any can be switched off; P(family | data) is computed from logZ within
the radar set only.

Phase A (runs/reference-289): davey2016 (track 289.7) + no-exhaustion-prior +
reference-snapshots, seeds 1-8, 7M per seed: identical to runs/reference-snapshots except
the prior track. Seed-matched A/B against that run.

Phase B (runs/families-<name>), all + radar-full.toml, seeds 1-4, then each family file here:
free (free.toml), repro-radar (no family), routes (waypoints.toml), descent-climb.
