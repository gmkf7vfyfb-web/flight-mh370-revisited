# End of flight: the three diagnostic smokes for the 00:19 push-over (10 Oct 2026)

Pete approved these at ~18:10 UTC, from the architecture study `results/burst-0019-plausibility-architecture.md` §6. They are **diagnostics only**:
no default changed, and no large run was made.

**Labels:**
- SMOKE; one seed; core (b), split-half NOT converged;
- two-tank bookkeeping only (no one-engine phase flown);
- descent idle floor ON; dive class (b), PROVISIONAL (divergent spiral weight 0.5, bank cap 90°);
- built from `3c6319f` plus the new switch below; Mac, 2 threads.

**Option names** follow the ruling of ~16:30:
- **00:19 Holland H2** = both bursts at face value, log-on not from fuel exhaustion (`both_no-offset` × other);
- **00:19 Holland H1** = both bursts with Holland's start-up offset, fuel-exhaustion log-on (`both_startup-offset` × fuel-exhaustion).

Every option here carries the existence constraint "airborne at 00:19:37" (`+alive`).

**Input:** hand-off `next-run/next-free`, seed 1 (100,000 parents). The baseline is the stand-in sweep's
`end-of-flight/next-run/next-free/seed-1` (N = 8 children x 4 descents = 32 descents per parent). It has the same recipe as these smokes.

## Smoke 1: trim referenced to the state at loss of control

- **New switch:** `envelope.trim_reference_at_loss` (default false; unit test added; 96 tests pass).
  - With it on, a maintained-then-lost descent flies its fixed trim at the level lift coefficient of the state **at the loss**, plus the same
    drawn offset.
  - With it off (the earlier behaviour), the trim is referenced to the takeover state.
  - The draws are the same either way.
  - Defaults are byte-identical to the previous build (N = 1 check, `cmp` of `impacts.npy`).
- **Run:** `runs/bfree-trimloss-s1`, same seed and recipe, N = 8 (990 s).

| quantity | trim from takeover state (baseline) | trim from state at loss |
|---|---|---|
| prior P(Δv ≤ −10,450 ft/min), airborne at both bursts | 0.274 % | **0.222 %** (−19 %) |
| prior P(Δv ≤ −8,000 ft/min) | 0.775 % | 0.652 % |
| 00:19 Holland H2: ln Z, effective parents, effective impacts | −23.97, 8.3, 19.5 | −24.53, **3.0**, 8.1 |
| 00:19 Holland H2: posterior share maintained-then-lost | 0.91 | 0.85 |
| 00:19 Holland H1: ln Z, effective parents, effective impacts | −31.25, 13.2, 15.7 | −32.64, **3.4**, 10.7 |
| 00:19 Holland H1: posterior share maintained-then-lost | 0.79 | 0.16 (ditching 0.85) |
| 00:19 R600 BTO + Raw BFO: ln Z, effective parents | −12.50, 21,500 | −12.49, 21,690 |

**Reading.**
- The well-estimated result is the prior tail: the takeover-state reference adds about **19 %** to the push-over tail at the Δv that the observed
  −184 Hz requires.
- H2's effective parents fall by 64 %, which meets the study's ">half" criterion. But at 3-13 effective parents, the posterior counts and
  shares are not estimable (smoke 2 shows why).
- No other option moves.
- The ruling of ~18:45 (item 3) already adopts trim at loss for the base; it will take effect at the next announced re-sweep.

## Smoke 2: does within-parent sampling limit H1 and H2?

**Step 1.**
- The top 200 parents per option (352 together, holding more than 99.99 % of each 32-descent posterior) were written to a reduced hand-off
  (`smoke/top_parent_handoff.py`), with weights unchanged.
- They were re-run at **1,024 descents per parent** (`runs/top-free-n256`, 197 s).
- Check: per-parent impact weight sums match the hand-off row weights to 1e-15.

**Step 2.**
- Selecting parents on the same draws that estimate them is biased. So **2,000 parents drawn at random from the other 99,647** were run the same
  way (`runs/rand-free-n256`, 1,165 s).
- They give an unbiased estimate of the evidence outside the top set.

| | 00:19 Holland H2 | 00:19 Holland H1 |
|---|---|---|
| ln Z, all parents, 32 descents (unbiased, noisy) | −23.97 | −31.25 |
| ln Z, top parents: 32 → 1,024 descents | −23.97 → **−25.27** (−5.7 s.e.) | −31.25 → **−33.30** (−8.1 s.e.) |
| ln Z, the other 99,647 parents at 1,024 (from the random 2,000) | −23.71 | −31.67 |
| **share of total evidence in parents that scored ~nothing at 32 descents** | **0.83** | **0.84** |
| ln Z, all parents, 1,024 descents: median (90 % bootstrap over the random parents) | −23.55 (−24.05, −23.15) | −31.52 (−33.04, −30.78) |
| ESS of the 2,000 random parents' contributions | 9.9 | 2.2 |
| top parents at 1,024: effective parents / effective impacts / within-run split-half | 3.9 / 136 / 0.62 | 4.4 / 194 / 0.69 |

**Reading.**
- **Within-parent sampling is the binding limit, not the hand-off.**
  - At 32 descents almost every parent scores no two-burst match. The posterior then collapses onto the few parents that were lucky
    (8-13 effective parents).
  - Re-run, those parents fall back (the winner's curse).
  - About 83 % of the evidence sits in parents that 32 descents never reach.
- The total ln Z is consistent between 32 and 1,024 descents, as an unbiased estimator should be. What 32 descents cannot give is a usable
  posterior.
- **Even 1,024 descents per parent is not enough.**
  - Of 2,000 random parents, an effective 10 (H2) and 2 (H1) carry the evidence.
  - Brute force would need well over 1,024 descents per parent across all parents: at least 100 M descents and about 60 GB per seed.
- **The efficient route is an exact within-parent sampler on the burst-time regime** (the study's B2/B3: a defensive mixture or splitting,
  with exact ln(p/q)).
  - It needs core request 9 (unnormalised within-parent weights) first.
  - It is a sampling change, with no change in expectation. **It is not built:** Pete's go is needed, per architecture ~17:30.

## Smoke 3: Boeing 8-s window occupancy against our simulators

- **Estimator.** The fraction of 8-s windows during the descent whose start and end vertical speeds fall inside Holland's H1 or H2 bounds
  (Table IV and Table VI, p. 9).
  - Method: 1-Hz altitude, 3-s moving average, central differences; windows run from 200 ft below the start altitude to the end of the record.
  - Added to `smoke/boeing_calibration.py` (`window_occupancy`). On the ten Boeing cases it **reproduces the study's Table 6 exactly**:
    windows, counts, and the first H2 window's altitude and time before the end.
- **Boeing (no control inputs, ATSB-selected):**
  - mean per-case fraction **H2 0.12 %**, **H1 1.61 %**;
  - H2 windows in cases 3, 4 and 5 (1, 2, 3); H1 windows in all five high-rate cases.
- **Point mass, current base** (the free-dynamics fixture, `free_dynamics_traces_for_calibration`, cap 90°, 114 traces):

| set | traces | high-rate | traces with any H2 window | mean H2 fraction | traces with any H1 window | mean H1 fraction | median of most negative 8-s Δv |
|---|---|---|---|---|---|---|---|
| neutral spiral | 60 | 0 | 0 | 0 | 1 | 0.03 % | −1,810 ft/min |
| divergent spiral | 54 | 37 | **0** | **0** | 52 | 3.37 % | −10,790 ft/min |
| Boeing | 10 | 5 | 3 | 0.12 % | 5 | 1.61 % | (Table 6) |

- **6-DOF fit of 9-10 Oct (NOT converged; shared stage stopped at its evaluation cap), case by case** (`sim/case_by_case.py`; Boeing / 6-DOF):

| case | regime | peak descent, ft/min | peak downward g | high-rate | H2 windows | H1 windows | distance start to end, NM | time to end, s |
|---|---|---|---|---|---|---|---|---|
| 1 | glide | 4,800 / 3,226 | 0.34 / 0.05 | no / no | 0 / 0 | 0 / 0 | 102.9 / 104.1 | 2,503 / 2,522 |
| 2 | glide | 6,300 / 3,242 | 0.34 / 0.05 | no / no | 0 / 0 | 0 / 0 | 103.4 / 105.4 | 2,461 / 2,516 |
| 3 | short | 53,460 / 59,459 | 1.24 / 0.71 | yes / yes | 1 / 0 | 9 / 8 | 36.2 / 33.2 | 577 / 490 |
| 4 | short | 33,600 / 12,509 | 0.87 / 0.39 | yes / **no** | 2 / 0 | 14 / 0 | 22.4 / 30.8 | 453 / 512 |
| 5 | long | 24,180 / 3,314 | 0.90 / 0.05 | yes / **no** | 3 / 0 | 15 / 0 | 107.8 / 94.9 | 1,891 / 1,950 |
| 6 | short | 43,380 / 55,772 | 1.21 / 0.67 | yes / no | 0 / 0 | 11 / 8 | 27.6 / 20.8 | 384 / 382 |
| 7 | glide | 4,920 / 2,699 | 0.31 / 0.05 | no / no | 0 / 0 | 0 / 0 | 104.6 / 102.8 | 2,434 / 2,493 |
| 8 | glide | 7,140 / 3,627 | 0.34 / 0.05 | no / no | 0 / 0 | 0 / 0 | 73.7 / 91.5 | 2,234 / 2,293 |
| 9 | glide | 6,900 / 3,078 | 0.31 / 0.04 | no / no | 0 / 0 | 0 / 0 | 85.5 / 85.7 | 2,249 / 2,308 |
| 10 | short | 58,020 / 13,793 | 1.31 / 0.18 | yes / **no** | 0 / 0 | 9 / 0 | 24.2 / 22.5 | 473 / 532 |

**Reading.**
- **The point mass produces H1-type pairs, but never an H2 pair, in any trace.**
  - H1-type pairs come only through the divergent spiral, already fast at the first burst.
  - An H2 pair (moderate descent, then 0.6 g in 8 s) needs pitch dynamics that can unload. That is structural, and it agrees with the study.
- **The 6-DOF fit does not yet pass the gate** (ruling ~18:45, item 1). Against Boeing it:
  - damps the glide phugoids: peak g 0.05 against 0.31-0.34;
  - reproduces the dive in cases 3 and 6 only (peak g 0.71 / 0.67 against 1.24 / 1.21);
  - misses the dive in cases 4, 5 and 10;
  - has no H2 window in any case.

  The start-to-end distance differs by ≤ 2 NM in five cases (1, 2, 7, 9, 10), by 3-7 NM in cases 3 and 6, and by 8-18 NM in cases 4, 5 and 8.
- **Next step for the gate:** diagnose the shared-stage stall and the phugoid damping. Candidates are the pitch-damping and Mach-tuck shared
  multipliers against the glide cases' phugoid period and amplitude. A refit under the heavy lock would follow, announced first. This is
  item B8 of my ~19:30 plan.

## Files
- `smoke1-trim-reference.json`;
- `smoke2-top-parents.json` and `smoke2-all-parents.json`;
- `smoke3-point-mass-and-boeing-windows.json` and `smoke3-sixdof-case-by-case.json`.

Scripts are in `hypotheses/end-of-flight/smoke/` (`compare_two_burst.py`, `top_parent_handoff.py`, `saturation.py`, `boeing_calibration.py`)
and `sim/case_by_case.py`.

- End of flight
