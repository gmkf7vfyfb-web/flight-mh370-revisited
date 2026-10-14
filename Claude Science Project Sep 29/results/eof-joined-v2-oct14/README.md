# Joined V2 at 00:11 — production run, core run I, waypoints stratum (14 Oct 2026)

**Label for every figure below:** V2 joined at 00:11: onsets before 00:11 scored in-stage, after 00:11 in the filter; conditional on
symmetric single-engine flight (item 1 not landed); uncontrolled-arm dynamics not yet calibrated (item 2 gate open).

Binary mh370-eof-o13d (sha256 bf18d786…). Core run I, stratum `next-i-waypoints` (core P(family) 0.9982). Seeds 1–8: each is an independent replicate of the whole pipeline, core included. 00:11 arm: run-i-dive recipe + exact fuel-cue truncation + all four deliberate control outcomes, N = 8 children × 4 descents per parent. 22:41 arm: the same recipe, deliberate onsets only (mechanism weights [1, 1, 0]; the V2 prior's factor 2/3 applied exactly in the join), scored candidate selection aimed at m0011 (K = 8, defensive share 0.2; test 6 passed at pilot scale), N = 8 × 4. Join (smoke/joined_v2.py; Pete's ruling 14 Oct): deliberate onsets before 00:11 scored in-stage from the 22:41 arm, everything else from the 00:11 arm with the filter's 22:41→00:11 increment; families A1/A2 entirely from the 00:11 arm.

## Results by 00:19 data treatment (cause total, q = 1/3, C2 silent)

| treatment | ln Z (log-mean-exp over seeds) | seed s.d. of ln Z | ESS, smallest seed | A1 share | A2 share | B share | outside B (code 6) | B ESS, smallest seed | share from onsets before 00:11 |
|---|---|---|---|---|---|---|---|---|---|
| D0: 23:15 and 00:11 only (no 00:19 data) | -23.994 | 0.572 | 3800 | 0.267 ± 0.025 | 0.612 ± 0.051 | 0.107 ± 0.068 | 0.014 | 282 | 0.075 |
| D1: R600 BTO | -29.526 | 0.621 | 6515 | 0.263 ± 0.018 | 0.661 ± 0.030 | 0.066 ± 0.041 | 0.010 | 105 | 0.026 |
| D2: R600 BTO + BFO | -35.685 | 0.648 | 2005 | 0.447 ± 0.033 | 0.479 ± 0.023 | 0.059 ± 0.030 | 0.016 | 330 | 0.001 |
| D3: both BFOs, raw | -45.233 | 0.585 | 111 | 0.257 ± 0.034 | 0.690 ± 0.033 | 0.040 ± 0.024 | 0.013 | 35 | 0.000 |
| D4: both BFOs, start-up offset (Holland H1) | -45.379 | 0.637 | 664 | 0.235 ± 0.016 | 0.714 ± 0.028 | 0.040 ± 0.023 | 0.011 | 180 | 0.000 |

Shares are the seed posteriors pooled with weights Z_k; ± is the seed standard deviation. ESS is Kish's, per seed, never pooled.

### Per seed (ln Z; B share; B ESS)

| treatment | seed 1 | seed 2 | seed 3 | seed 4 | seed 5 | seed 6 | seed 7 | seed 8 |
|---|---|---|---|---|---|---|---|---|
| D0 | -24.08; 0.109; 437 | -24.60; 0.185; 332 | -24.56; 0.202; 371 | -25.00; 0.254; 282 | -23.86; 0.096; 474 | -23.66; 0.079; 324 | -24.08; 0.108; 308 | -23.22; 0.062; 590 |
| D1 | -29.58; 0.070; 569 | -30.31; 0.117; 105 | -30.10; 0.130; 301 | -30.63; 0.146; 186 | -29.26; 0.058; 480 | -29.03; 0.040; 219 | -29.66; 0.073; 299 | -28.89; 0.045; 675 |
| D2 | -35.73; 0.073; 330 | -36.40; 0.062; 743 | -36.14; 0.102; 1050 | -36.81; 0.119; 521 | -35.84; 0.082; 884 | -34.74; 0.021; 1329 | -36.10; 0.080; 995 | -35.27; 0.058; 655 |
| D3 | -45.05; 0.037; 58 | -46.07; 0.050; 57 | -45.70; 0.098; 55 | -46.26; 0.070; 58 | -45.06; 0.034; 169 | -44.88; 0.033; 35 | -45.30; 0.033; 122 | -44.63; 0.028; 122 |
| D4 | -45.36; 0.043; 256 | -46.21; 0.047; 223 | -45.91; 0.080; 352 | -46.54; 0.089; 180 | -45.21; 0.044; 429 | -44.84; 0.020; 344 | -45.52; 0.044; 303 | -44.75; 0.032; 396 |

Filter increment 22:41→00:11 by seed: -15.718, -16.393, -15.836, -16.030, -15.649, -15.851, -15.862, -15.387 nat.

## Onset-boundary statistic (22:41 arm: weight within 60 s of the 22:41 hand-off), largest over seeds

| cell | all | B | outside B (6) |
|---|---|---|---|
| prior (nothing scored) | 4.94 % | 4.95 % | 4.91 % |
| D0 (23:15+00:11 only) x cause total | 0.00 % | 0.00 % | 0.00 % |
| D1 R600 BTO x cause total | 0.00 % | 0.00 % | 0.00 % |
| D2 R600 BTO+BFO x cause total | 0.00 % | 0.00 % | 0.00 % |
| D3 both BFO raw x cause total | 0.00 % | 0.00 % | 0.00 % |
| D4 both BFO start-up offset x cause total | 0.00 % | 0.00 % | 0.00 % |

Contract threshold 5 %. Support truncation is populated (finite fraction per seed: 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000).

## COVERAGE

**(a) Feasible set.** A 777-200ER from the core's 22:41/00:11 states to the sea: descent onset anticipatory, fuel-cue or flame-out-associated; 0, 1 or 2 engines thrusting; control ditching, maintained-then-lost, no intervention or upset; rates up to the structural limits (VMO/MMO 330 kt / M0.87, TCDS T00001SE); piloted turns; single-engine flight with or without thrust-asymmetry compensation.

**(b) Model reach.** Gaps, each named in the label: (1) single-engine flight is a symmetric point mass in this run (item 1 code landed after, off here); (2) the uncontrolled-arm dynamics are not calibrated (item 2 gate open; smoke shows a glide-phugoid and a dive-chord misfit against Boeing); (3) deliberate onsets earlier than 22:41 are not reachable from this hand-off. Status: closed in practice — the boundary statistic is 0.00 % in every scored cell of every seed (gate 5 %), so no supported mass presses on 22:41 and a 21:41 checkpoint is not indicated; (4) A-family flame-out timing differs by about 2.6 min between the 22:41- and 00:11-based hand-offs (V1a/V1b effect, ~0.36 nat), carried by taking A from the 00:11 arm.

**(c) Proposal coverage.** ESS per treatment and family in the table above (smallest seed). D5 (R600 BTO + R600 BFO + R1200 BFO with offset) is NOT estimable from this sample set at 22:41: the bias variance after the in-stage updates is not emitted — a coverage gap, fix proposed (emit it, or its own log-likelihood column). In seed 1 the 22:41 arm carries 648 rows labelled flame-out mechanism with prior 0 (parents with no deliberate support after 22:41); the join excludes them by construction (weight share 6e-5); those parents' flame-out onsets come from the 00:11 arm.

**Coverage gaps by ESS (smallest seed; sum over seeds in joined-v2-summary.json):** B under D3 (35) and D1 (105); A1 under D3 (10) and D4 (57); code 6 under D3 (8), D4 (15) and D0 (137). These cells are estimable but imprecise; the between-seed spread is the larger error for B (D0 B share 0.062–0.254 over seeds, against the within-seed ESS of 282–590), which indicates that the B fraction is limited by the core's cruise parents (which differ by seed) rather than by this stage's descents. Fix proposed: more core seeds (or parents) for the B family rather than more children here.

**Parameter bounds with sources:** as in the run-i-dive recipe (hypotheses/end-of-flight/full/*.toml, each with its source line).


## What this is and is not

Production scale, all gates run (gate 3 ESS at 00:11 and 22:41, gate 4 boundary statistic and truncation, test 6 at pilot scale for the
aimed proposal). It is the V2 joined estimate for the waypoints stratum only, labelled as above. It is not yet an impact-distribution result
for the paper: item 1 (asymmetry) is off and item 2 (calibration of the uncontrolled arm) is open, so no impact energy, attitude or
flight-path angle from it may be quoted as a physical prediction (§8). Rule 11: this run is the "before" for item 1.

Files: `joined-v2-summary.json/.csv` (aggregate), `joined-sK.json` (per-seed join), `gate4-sK.json` (22:41-arm onset statistics).
Code: `hypotheses/end-of-flight/full/run_joined_v2.sh`, `full/summarise_joined_v2.sh`, `smoke/joined_v2.py`, `smoke/joined_v2_summary.py`,
`smoke/joined_v2_note.py`. Data: `mh370-exchange/end-of-flight/run-i-joined-v2/` (slim float32 per seed and arm, sha256 per file).

Correction made before publication: the first 8-seed summary read seed 1's samples for every seed (the join's `--seed` was not passed); the
driver was fixed and every number here is from the rerun (s1/s2 row counts now differ by seed).
