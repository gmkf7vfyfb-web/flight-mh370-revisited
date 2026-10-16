# Run J (core) — definition, 16 October 2026

**Status:** Pete pre-approved run J (16 Oct 2026 ~02:15Z) to start once the final smoke passes.
Source pinned to git tag `run-j`. Job script `engine/scripts/job-run-j.sh` (one stratum per job, fixed order,
heavy lock, gates checked by every job, manifest written by every job).

## What changes from run I

| Item | Run I | Run J | Basis |
|---|---|---|---|
| BFO sd, every BFO epoch | 7 Hz | **4.3177 Hz** (Davey Table 5.1) | results/bfo-sd-check-2026-10-15/ (data favour 4.32 Hz by 0.56 nat in the pure reproduction) |
| 18:25:27 R600 burst | not used | **not used (held out)**; companion predictive check on the repro family | Pete 15 Oct; results/r600-1825-holdout-2026-10-15/ |
| Fuel flow on extrapolated steps | no extra factor | **kappa_x ~ N(1.0, 0.046)**, PROVISIONAL | core request 21; results/request21-2026-10-16/ |
| Seeds (7M free/waypoints, 3.5M descent-climb/repro) | 8 / 8 / 8 / 8 | **free 18, waypoints 24, descent-climb 16, repro 16** | Pete 15–16 Oct; results/islands-check-2026-10-15/ |
| Everything else | — | unchanged: same stack, same step sizes (F3 passed), F4 bias drift OFF, hand-off look-ahead D, trace 18:22–18:42:40 | results/step-check-2026-10-15/ |

Not in run J: core request 20 (the both-burst arms are descent-limited: an end-of-flight remedy), the islands
layout, the evidence-tilted proposal, a latitude-band proposal, F4 drift. Request 9 is end of flight's.

## Chains (config order; `S=config/sensitivity`, `X=$S/fuel-fixes`, `F=$S/early-families`, `RJ=$S/run-j`)

COMMON = davey2016-inmarsat, no-exhaustion-prior, s1-factor, s2-temperature, s3-internal, s4-ceiling,
s5-hard-reject, s6-tanks, reference-snapshots, radar-full. CX = s7-single-engine, s8-hold-taper, inop-flow-fix.

| Job order | Stratum (output name) | Chain after COMMON CX | Seeds | Particles per seed |
|---|---|---|---|---|
| 1 | waypoints (`run-j-waypoints`) | speed-envelope, handoff-lookahead-d, RJ/obs-bfo432, RJ/kx, F/route-sampler, RJ/size-sampler | 1–24 | 7M |
| 2 | free (`run-j-free`) | same, F/free, RJ/size-free | 1–18 | 7M |
| 3 | descent-climb (`run-j-descent-climb`) | same, F/descent-climb, RJ/size-dc | 1–16 | 3.5M |
| 4 | repro (`run-j-repro-radar`) | handoff-lookahead-d, RJ/obs-bfo432, RJ/kx, RJ/size-repro (no speed envelope: Davey speeds) | 1–16 | 3.5M |
| 5 | companions (`run-j-repro-r600`, `run-j-repro-r600bfo`) | repro chain, then RJ/size-repro-r600(bfo), RJ/companion-r600(bfo) LAST | 1–8 each | 3.5M |

Companion: ln p(18:25:27 R600 | all other data) = ln Z(companion) − ln Z(run-j-repro-radar), seed by seed,
seeds 1–8. `r600bfo` scores the BFO only; `r600` scores BTO and BFO. BFO sd 4.3177 Hz as production.

## Time, memory, disk

- Deskstar at 88 threads, from run I per-seed times: waypoints 24 × 23.4 min = 9.4 h; free 18 × 12.5 min
  = 3.8 h; descent-climb 16 × 6.9 min = 1.8 h; repro 16 × 6.0 min = 1.6 h; companions 16 × 6.0 min = 1.6 h.
  Each job adds about 8 min (gates, preflight, compaction, hashing). **Total about 18.5 h.**
- Memory per process as run I (seeds run one after another; particles per seed unchanged), within the 36 GiB cap.
- Disk after compaction (run I per-seed sizes): waypoints 46 GiB, free 22, descent-climb 10, repro 7,
  companions 3; **about 88 GiB.** Deskstar volume 99 GB. Each job waits until there is room
  (waypoints 74, free 38, descent-climb 20, repro 16, companions 10 GiB free). The core thread copies each
  finished stratum to `~/Downloads/mh370-exchange/core/run-j/<name>/`, checks SHA256SUMS, then deletes it
  on deskstar. Mac free space before run J: 125 GiB.

## Predictions (written before the run)

1. Waypoints keeps more than 99% of the posterior across families.
2. The 4.32 Hz BFO sd raises the 34.5–36.5 S shoulder. In the pure reproduction it went 0.078 → 0.150; the
   production stack should move by a similar amount. Run J ln Z is not comparable with run I (other BFO sd).
3. kappa_x moves the fuel-exhaustion median by less than 1 min (smoke: −25 s); the shifted prior
   N(1.027, 0.043) is a declared sensitivity (smoke: −4.8 min).
4. Split-half overlap meets the floor for each family's seed count, or the shortfall is reported with it.
5. Pooled northern effective lineages north of 33 S: waypoints about 450, free about 420.
6. The held-out R600 burst scores close to the best attainable value, as in the 12 Oct smoke.

## Declared sensitivities (not in this run)

BFO sd 7 Hz (run I is the nearest comparison, but it also lacks kappa_x); kappa_x N(1.027, 0.043); 18:25:27
BFO sd 5–6 Hz (only relevant if that burst were used); F4 drift (end-of-flight terminal rerun only).
