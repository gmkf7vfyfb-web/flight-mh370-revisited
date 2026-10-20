# Item 8 — the round-3 laws as a labelled sensitivity on the uncontrolled arm (15 Oct 2026)

**Work order:** section 1, Task B of `threads/work-orders/work-order-2026-10-15.md`. **This is not a calibration and the section 8 gate stays FAILED.**

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.

## 1. What was run

One full sweep at run-I scale: the run-i-dive recipe (arm C, aimed pitch-down, piloted turns with the particle's own tau_h, C2-silent push-over component, dive branch) with `full/round3-laws.toml` appended last. Four strata x 8 seeds, 32 seed-runs, 127,999,840 impacts — the same scale and the same core run I m0011 hand-offs as the production arm. Binary `mh370-eof-r3`, sha256 `ed3d757b3b1c6a9211e5c5909db9cdbba03d65fac8eb6c25c475b087a854fa7e`, built from `hypotheses/end-of-flight` at this branch head with the pinned toolchain 1.98.0. Run 05:10:06Z to 07:37:06Z (2 h 27 min) at 12 threads under the heavy lock, driver `full/sweep_round3.sh`.

**Binary identity gate, run first.** The same binary with the production recipe and no round-3 overlay reproduces the stored run-i-dive result to the last bit: on `next-i-free` seed 1 all 42 cells of the 00:19 two-factor table agree with the stored `mh370-eof-ri3` values, maximum difference 0.000e+00 nat. The stored run-i-dive is therefore a valid "before" for rule 11, and the before-and-after below is a change of dynamics only.

## 2. Rule 11 — the reach change, and what it does to the answer

**Physical justification.** Round 3's laws are a lagged lift (lift relaxes towards a dynamic-pressure-dependent target with a time constant), a turn rule that banks towards the dead engine while one engine is still thrusting, and a dive trigger on equivalent airspeed at the loss of control. The lagged lift is the only one of the three fitted rounds that reproduces the Boeing glide phugoid (cases 1, 7 and 8: period and damping inside tolerance), which a fixed-lift point mass cannot do — Lanchester's period at the speed it flies is about 20 s short and its damping is positive where Boeing's is neutral.
**Prompted by a fit failure: YES, explicitly.** Rounds 1 and 2 failed the gate; round 3 was pre-registered after them (`results/eof-item2-fit-oct14/PREREG-v3.md`) and also failed it. Rule 11 requires this to be stated beside every number.

| cell (q = 1/3, C2 silent) | ln Z before | ln Z after | change, nat | latitude median before | after | effective impacts before | after |
|---|---|---|---|---|---|---|---|
| D0 total q=0.333 (C2 silent) | -7.322 | -7.424 | **-0.101** | -37.07 | -37.13 | 891,309 | 754,291 |
| D1 total q=0.333 (C2 silent) | -12.840 | -12.858 | **-0.018** | -37.24 | -37.21 | 857,064 | 812,266 |
| D2 total q=0.333 (C2 silent) | -18.841 | -19.036 | **-0.195** | -37.11 | -37.15 | 71,111 | 62,024 |
| D3 total q=0.333 (C2 silent) | -28.468 | -28.615 | **-0.147** | -37.31 | -37.35 | 4,653 | 5,586 |
| D4 total q=0.333 (C2 silent) | -28.658 | -28.703 | **-0.046** | -37.32 | -37.33 | 33,741 | 33,343 |
| D5 total q=0.333 (C2 silent) | -29.103 | -29.225 | **-0.122** | -37.29 | -37.33 | 10,456 | 9,258 |
| D0xC1 | -7.039 | -7.141 | **-0.102** | -37.07 | -37.13 | 883,620 | 746,905 |
| D4xC1 | -28.374 | -28.419 | **-0.046** | -37.32 | -37.33 | 33,522 | 33,134 |
| D4xC2 silent | -32.880 | -32.932 | **-0.052** | -37.39 | -37.41 | 16,629 | 17,901 |

**The laws change the shape and not the answer.** The held-out log evidence moves by -0.101 nat, well inside the work order's 1-nat stop condition, and no cell moves by more than 0.20 nat. The held-out impact-latitude median moves 0.06 degrees south (−37.07 to −37.13) and the D4 median 0.01 degrees (−37.32 to −37.33); the 90 per cent region is unchanged to within 0.03 degrees at both ends. **Stop condition: not tripped.**

**What does move is the family mixture under the R1200 cells.** A1 falls from 0.168 to 0.062 under D3, from 0.145 to 0.103 under D4 and from 0.141 to 0.057 under D5, with the B families taking the mass (D4: 0.438 to 0.461). The reason is in section 3: the round-3 laws do not produce the near-vertical impacts that carried part of the A1 mass under those cells.

## 3. Impact conditions — the labelled sensitivity this arm exists to make quotable

Both arms measured by the same estimator: a weight-proportional subsample without replacement, 50,000 impacts per seed (400,000 per stratum), strata mixed at the core family prior, 00:19 bursts held out. Effective sample 401,363 in each arm.

| quantity, 00:19 held out | production (run-i-dive) | round-3 laws | 
|---|---|---|
| flight-path angle at contact, q05 / q50 / q95 (deg) | 1.7 / 4.2 / 55.8 | 2.0 / 4.7 / 31.5 |
| share below 10 deg | 0.740 | 0.665 |
| share 10-45 deg (acoustically decisive band) | 0.161 | **0.323** |
| share above 45 deg | 0.100 | **0.012** |
| impact energy, q05 / q50 / q95 (GJ) | 0.35 / 1.23 / 10.98 | 0.35 / 1.81 / 10.99 |
| energy-transfer duration tau90, q05 / q50 / q95 (s) | 0.11 / 3.63 / 11.30 | 0.15 / 3.69 / 12.21 |

**Reading it as flight dynamics.** The round-3 arm all but removes the near-vertical tail — the share above 45 degrees falls from 0.100 to 0.012 — and moves that mass into the 10-45 degree band, which doubles from 0.161 to 0.323. Two features do it: the lagged lift (time constant 3.52 s, gain 0.41) keeps the aircraft flying a Boeing-like phugoid instead of converging on a steep attitude, and the fitted spiral bank cap of 52.5 degrees limits how steep a divergent spiral can become before contact. The median impact energy rises from 1.23 to 1.81 GJ because a shallower, faster arrival carries more speed into the water, while the upper tail is unchanged at about 11 GJ. The duration barely moves (median 3.63 to 3.69 s).

**The caution that must travel with that paragraph.** The bank cap is the parameter doing most of the work on the steep tail, and it is the worst identified number in the fit: the all-data value 52.5 degrees lies outside the range of every leave-one-out fit (57.3 to 62.4 degrees). The single most consequential feature of this arm for the acoustics is therefore also its least identified one.

**Not quotable from this arm: the 00:19-weighted impact conditions.** Applying the D4 likelihood to the prior-side subsample leaves an effective sample of 84, so the energy and angle distributions under the R1200 cells cannot be read from it. The D4-weighted evidence, latitude and family shares in section 2 are unaffected: they come from the full 128-million-impact tables, not from the subsample.

## 4. The round-3 parameters, with the leave-one-out spread beside each value

| parameter | all-data fit (used in this arm) | leave-one-out range | production prior | note |
|---|---|---|---|---|
| `spiral_doubling_s` | 26.4453 | 23.48 to 58.74 | [60, 120] s | **outside** the production band |
| `trim_cl_offset` | -0.0689453 | -0.1406 to -0.02509 | [-0.08, 0.08] | inside the production band (round 1's was not) |
| `windmilling_per_engine` | 0.00140964 | 2.55e-06 to 0.001382 | [0, 0.0015] |  |
| `rat_increment` | 0.000194437 | 0.0001857 to 0.0005063 | [0.0001, 0.0006] |  |
| `spiral_bank_cap_deg` | 52.5332 | 57.3 to 62.42 | 90 deg (fixed) | **outside every leave-one-out fit** (57.3-62.4) |
| `free_lift_lag_s` | 3.51689 | 0.979 to 3.772 | 0 s (law off) |  |
| `free_lift_gain` | 0.412371 | 0.3768 to 0.9774 | 1 (law off) |  |
| `residual_bank_deg` | 9.68529 | 5.728 to 12.82 | [0, 35] deg |  |
| `residual_bank_left_probability` | 0.98 | 0.8326 to 0.98 | 0.8 | on a search bound |
| `residual_bank_toward_dead_probability` | 0.98 | 0.98 to 0.98 | absent (law off) | on a search bound, no spread at all |
| `dive_trigger_eas_mid_kt` | 182.514 | 181.7 to 201.6 | absent (law off) |  |
| `dive_trigger_eas_scale_kt` | 2 | 2 to 2 | absent (law off) | on a search bound |

Three parameters sit on a search bound and one lies outside the range of every leave-one-out fit, so several local optima of similar total are likely. Out of sample the three rounds read −1,282.0, −904.2 and −713.6 nat with 13, 18 and 25 of 62 case-targets inside tolerance; no case passed in any round, and each round is a further fit to the same ten cases, so the out-of-sample claim is weaker with every round. That sentence belongs beside every number from this arm.

## 5. COVERAGE

**(a) Feasible set.** Unchanged from run-i-dive: a 777-200ER after the second flame-out can glide, phugoid, enter a divergent or neutral spiral, be flown in a piloted descent, or be dived into the water; the Boeing engineering-simulator cases are the only aircraft-specific evidence about which of those it does, and five of the ten are dive cases.

**(b) Model's reach — this is the reach change rule 11 is about.** The arm adds three laws the production dynamics do not have (lagged lift, turn towards the dead engine, dive trigger on equivalent airspeed at the loss) and widens the spiral doubling time below its production band (26.4 s against [60, 120] s). It also **narrows** the reach in five dimensions that production samples: the doubling time, trim offset, windmilling increment, RAT increment and bank cap are point values here, not ranges. That is a declared coverage gap of the sensitivity arm, and the leave-one-out spread in section 4 is the honest width of each. The production arm remains the headline for exactly this reason.

**(c) Proposal's coverage.** The proposal is unchanged from run-i-dive (same aims, same defensive mixtures, same exact weights), so the proposal-side coverage statement of run-i-dive carries over; what changed is the dynamics the proposal is aimed at. Effective impacts per cell are in the table in section 2: the worst cell is D3 at 5,586 (it improves on production's 4,653), and every reported cell is above the 1,000-impact gate. The acoustic distributions in section 3 rest on an effective sample of 401,363 with the bursts held out, and are NOT estimable under the R1200 cells from the retained subsample (effective sample 84), which is declared in section 3 rather than worked around.

**Gaps carried over unchanged** from run-i-dive: stepped shapes not push-over eligible; INTERIM parametric pitch-down; no transonic drag rise; turn model PROVISIONAL; B uncontrolled below the gate under the R1200 cells.

## 6. Retention, and what is kept

The work order assumed outputs retained as usual. A second full sweep would need about 56 GB and the machine had 41 GiB free at the start, so this arm was written to the session workspace and **summarised per stratum, after which the per-seed files were removed**. What is kept, on the exchange at `mh370-exchange/end-of-flight/round3-sensitivity/`: the per-stratum 00:19 two-factor tables and their latitude histograms (the full-sample products, 8 seeds per stratum, from which every number in section 2 comes), a weight-proportional subsample of 50,000 impacts per seed per stratum with 27 columns including the `tau90_v1` sidecar fields, the matched production subsample used for section 3, the per-stratum run READMEs, and `round3-report.json` + `sensitivity-distributions.json`. Re-running the arm costs 2 h 27 min at 12 threads, and the driver, the override and the report script are in the repository, so this is a reproducible deletion rather than a lost run.

Two defects in the driver, recorded because the run worked around them rather than being re-run: its sidecar and subsample steps globbed `seed-*`, which matched the `seed-k.convert8.log` files as well as the directories and made both steps fail (fixed to `seed-*/` after the sweep, so the fix is not what produced these outputs — a companion script did those two steps per stratum); and the stratum weights are applied by `smoke/combine_strata_0019.py`, not inside the per-stratum tables, which are conditional. The combiner reproduces the stored run-i-dive mixture exactly — all 42 cells, ln Z, effective impacts and latitude quantiles identical — which is the check that the summary path is sound.

## 7. What this arm licenses, and what it does not

It licenses quoting impact energy, flight-path angle and energy-transfer duration **as a labelled sensitivity on uncalibrated dynamics**, which is what the task was for, with the section 4 identification table beside them. It does not license treating those fields as physical predictions, does not change run.toml, does not supersede run-i-dive, and is not to be pooled with it: the two are different priors over the end-of-flight trajectory, not sampling variants. The gate stays failed.

---

Footnote (ASD-STE100). We ran the descent model again with the laws from the third fit to the Boeing data. The fit did not pass its test, so these laws are an alternative and not a correction. The position answer did not change: the evidence moved by 0.10 nat and the middle latitude by 0.06 degrees. The shape of the impact changed: there are almost no very steep impacts, there are twice as many impacts between 10 and 45 degrees, and the middle energy is higher. You must not use the energy, the angle or the duration as a prediction.

Footnote (technical). Source posterior and prior track: core run I m0011 hand-offs (core NOT CONVERGED: all-partition split-half 0.916 waypoints, 0.830 free flight, against the 8-replicate floor 0.924), end of flight run-i-dive recipe plus `full/round3-laws.toml`, binary mh370-eof-r3 (sha256 ed3d757b...), 4 strata x 8 seeds, 127,999,840 impacts, strata mixed at the core family prior 0.9982 / 0.0011 / 0.0004 / 0.0002. 00:19 cells: D0-D5 x C1/C2 with the competing-cause mixture q = 1/3 (p = 0.75), W = 3,898 s, C2 silent primary, survival factor applied, as `smoke/option_table_0019.py`. Dive probability 0.5 (item 7: the three readings of that prior coincide). Impact energy, peak radiated power and tau90 from the `tau90_v1` sidecar, method 1, joined by row order. Impact conditions from weight-proportional subsamples, 50,000 rows per seed, equal weights thereafter, 00:19 held out; the D4-weighted subsample is not estimable (effective sample 84). Uncontrolled-arm dynamics NOT CALIBRATED: Boeing leave-one-out gate failed in all three rounds (out of sample −1,282.0, −904.2, −713.6 nat; 13, 18, 25 of 62 case-targets inside tolerance; no case passed). Round-3 identification weak: three parameters on a search bound, the all-data bank cap outside every leave-one-out range.
