# End of flight on core run J, waypoints stratum: production pass — 16 Oct 2026

**Status (core run J: split-half convergence accepted as a pass by project ruling, 16 Oct 2026): complete for one stratum (waypoints, core prior share 0.9982 on run I; run J's stratum shares are not yet posted by core).**
These are per-stratum figures, not the four-stratum mixture. The free, descent-climb and repro strata are still to be run (disk).
The both-burst cells D3 and D4 are thin in this pass. The supplementary pass (section 4) is running for them.

## 1. What was run
- **Input:** core run J, `run-j-waypoints`, 24 seeds, the m0011 hand-offs (sha256 verified against core's COMPACT.txt).
- **Recipe:** run-i-dive (C2-silent aim, dive branch p = 0.5, children 16, so 64 descents per parent), with the **round-3 descent
  laws** and the **divergent-spiral bank limit drawn uniformly on [52, 90] deg** (`full/bank-cap-uniform.toml`; Pete, 16 Oct about
  16:40Z). Binary `/tmp/mh370-eof-rj1`, sha256 19031f41748ecb0c, built from 16f2eb1.
- **Output:** `mh370-exchange/end-of-flight/run-j/run-j-waypoints/` (24 x 2.8 GB, the run-i-dive compact format, README and READY).
  It ran from 16:54Z to 20:59Z, including a 1.4 h pause for disk.
- **Check:** the drawn limit is uniform, with 1.60M rows in each quarter of 52-90 deg (seed 1).

## 2. The 00:19 two-factor table (q = 1/3, cause C2 silent; transmission imposed; this stratum only)

`table-0019-run-j-waypoints.json/.txt` (`smoke/option_table_0019.py`, unchanged). Run I is the run-i-dive waypoints table: production
laws, 90 deg cap, 8 seeds, BFO noise 7 Hz. The two runs differ in the core inputs (24 seeds, BFO 4.32 Hz, fuel factor kx) **and** in
the descent laws, so the differences below are not attributable to either change alone. Item 8 and order (b) item 3 measured the
law changes on run I.

| 00:19 treatment | run J: ln Z | run J: A1 / A2 / B | run J: latitude 5 / 50 / 95 % | run J: ESS | run I: A1 / A2 / B | run I: median latitude |
|---|---|---|---|---|---|---|
| D0' held out | −7.525 | 0.17 / 0.34 / 0.48 | −38.40 / −37.12 / −33.87 | 1.94M | 0.19 / 0.41 / 0.40 | −37.07 |
| D1 R600 BTO | −12.934 | 0.20 / 0.35 / 0.45 | −38.48 / −37.21 / −34.57 | 2.14M | 0.17 / 0.42 / 0.41 | −37.24 |
| D2 R600 BTO + BFO | −19.120 | 0.24 / 0.23 / 0.53 | −38.16 / −37.12 / −34.34 | 92k | 0.25 / 0.31 / 0.43 | −37.11 |
| D3 both BFOs raw | −28.581 | 0.09 / 0.41 / 0.50 | −38.04 / −37.29 / −34.42 | 4.7k (A1 368) | 0.17 / 0.38 / 0.45 | −37.31 |
| D4 both, transient bias | −28.512 | 0.25 / 0.35 / 0.40 | −37.98 / −37.21 / −34.39 | 21k (A1 1.9k) | 0.14 / 0.42 / 0.44 | −37.32 |
| D5 R1200 offset | −29.168 | 0.06 / 0.42 / 0.52 | −37.99 / −37.27 / −34.47 | 26k | 0.14 / 0.39 / 0.47 | −37.29 |

**Reading.**
1. **The latitude is stable.** The median moves by at most 0.11 deg between the runs in every treatment. The 5-95 % interval
   widens to the north, towards −34 deg, in run J.
2. **The A1/A2/B split moves.** Under D0', A2 falls from 0.41 to 0.34 and B rises from 0.40 to 0.48. Under D4, A1 rises from 0.14 to
   0.25. This D4 change matches the direction measured on run I for a wider bank limit (order (b) item 3: A1 0.10 at 52.5 deg, 0.21
   sampled, 0.58 at 90 deg).
3. **D3 rests on 368 effective A1 impacts.** Its A1 share (0.09 against run I's 0.17) is **not yet estimable at this sampling depth: an end-of-flight coverage gap (low ESS)**. This is about end of flight's own descent sampling, not core's run J, whose split-half convergence was accepted as a pass by project ruling, 16 Oct 2026. This is the cell the
   supplementary pass is for.

## 3. The bank-limit prior: exact re-weightings (raw 00:19 columns, seed means ± standard error, 24 seeds)

`bank-prior-variants-run-j-waypoints.json` (`smoke/bank_prior_variants.py`). These are the raw per-cell columns, not the two-factor
totals of section 2, so the values differ from that table. They show what the prior on the limit does.

| 00:19 column | prior on the bank limit | A1 | A2 | B | steeper than 45 deg | ln Z | ESS per seed (min) |
|---|---|---|---|---|---|---|---|
| none (held out) | uniform 52-90 (headline) | 0.214 ± 0.001 | 0.244 | 0.543 | 0.088 | 0 | 1.34M (1.24M) |
| none | Boeing-weighted 0.8/0.2 | 0.208 ± 0.001 | 0.249 | 0.543 | 0.035 | 0 | 589k (539k) |
| none | limit 80-90 only | 0.217 ± 0.001 | 0.240 | 0.543 | 0.223 | 0 | 355k (321k) |
| both, start-up offset (D4 column) | uniform 52-90 | 0.132 ± 0.008 | 0.305 | 0.564 | 0.090 | −22.11 ± 0.02 | 615 (197) |
| both, start-up offset | Boeing-weighted 0.8/0.2 | 0.078 ± 0.004 | 0.319 | 0.603 | 0.031 | −22.19 ± 0.03 | 399 (36) |
| both, start-up offset | limit 80-90 only | 0.217 ± 0.012 | 0.289 | 0.494 | 0.228 | −22.00 ± 0.03 | 217 (51) |
| both raw (D3 column) | uniform 52-90 | 0.047 ± 0.005 | 0.329 | 0.624 | 0.024 | −22.02 ± 0.02 | 131 (30) |

**Reading.**
1. **Without 00:19 data, the bank-limit prior changes the impact angle and not the families.** The steep share runs from 0.035 to
   0.223; A1 moves by 0.01.
2. **With both frequencies and the start-up offset, the prior changes the family.** A1 runs from 0.078 to 0.217, and the evidence
   favours high limits by 0.19 nat.
3. These repeat, on run J, the run-I finding of order (b) item 3. The paper must give D4 as a range over the bank-limit prior.

## 3b. Both-burst supplementary pass (8 seeds, 256 descents per parent, thinned) — complete 03:00Z 17 Oct

- **Method.** Same hand-offs as production seeds 1-8. Recipe: the production laws (round-3 + bank limit U[52, 90]) with children 64.
  The output is Poisson-thinned to 1M rows per seed over the cells r600/no-offset, both/no-offset, both/startup-offset and
  both/inflated (`smoke/both_burst_thin.py`; ln Z normalised by the unthinned total).
- **Output:** `run-j-both-burst/run-j-waypoints/` (8 x 0.43 GB).
- **Scope:** valid for D2-D5 only. The held-out D0' and D1 cells are not represented, and their rows in the table are not results.

| 00:19 treatment (q = 1/3, C2 silent) | production, 24 seeds: ln Z / ESS / A1 ESS / A1-A2-B | supplementary, 8 seeds: ln Z / ESS / A1 ESS / A1-A2-B | median latitude, production / supplementary |
|---|---|---|---|
| D2 | −19.120 / 92k / 48k / 0.24-0.23-0.53 | −19.142 / 112k / 55k / 0.21-0.22-0.57 | −37.12 / −37.17 |
| D3 | −28.581 / 4.7k / 368 / 0.09-0.41-0.50 | −28.596 / 6.3k / 409 / 0.08-0.37-0.55 | −37.29 / −37.31 |
| D4 | −28.512 / 21k / 1.9k / 0.25-0.35-0.40 | −28.509 / 44k / 4.6k / 0.25-0.32-0.43 | −37.21 / −37.23 |
| D5 | −29.168 / 26k / 2.2k / 0.06-0.42-0.52 | −29.220 / 27k / 1.8k / 0.05-0.38-0.57 | −37.27 / −37.31 |

**Reading.**
1. **The two passes are independent sets of descent draws, and they agree.** ln Z differs by at most 0.05 nat in D2-D5. Family
   shares differ by at most 0.05, and median latitude by at most 0.05 deg. This is a direct check of both the thinning and the
   production numbers.
2. **D4 is now well sampled:** ESS 44k, of which 4.6k is A1. Its family split, 0.25 / 0.32-0.35 / 0.40-0.43, is robust.
3. **D3 overall is well sampled (6.3k), but its A1 sub-population is not:** about 400 effective impacts in each pass, even at
   256 descents per parent. A no-input spiral rarely gives both frequency values as recorded. The D3 A1 share is 0.08-0.09 in two
   independent passes, and run I's round-3 arm gave 0.06 (item 8), so **the share is stable**. The **shape** of the D3 A1 impact
   distribution is still a coverage gap.
4. **Bank-limit prior, D4 raw column** (`bank-prior-variants-supplementary-8.json`, ESS 2,064 per seed under the uniform prior):
   - A1 is 0.081 (Boeing-weighted), 0.132 (uniform) and 0.206 (limit 80-90 only).
   - ln Z is −22.16, −22.07 and −21.95.
   - These match the production pass (0.078 / 0.132 / 0.217) at three times the ESS.

## 3c. D3-aimed selection smoke (17 Oct, 11:32-12:02Z; run J waypoints seed 1; SMOKE, not evidence)

- **Config:** `smoke/score-select-0019-raw.toml`. Aimed candidate selection (K = 8) with the proposal target's BFO-model mixture tilted
  to the no-offset model (0.98 / 0.01 / 0.01). These priors are used only for the proposal target. The stored per-model loglik
  columns do not depend on them.
- **Comparison on the same hand-off** (two-factor totals, q = 1/3, C2 silent):

| arm | D3 ESS | D3 A1 ESS | D3 A1 / A2 / B | D4 ESS | D4 A1 ESS |
|---|---|---|---|---|---|
| production (64 descents per parent) | 236 | 7 | 0.08 / 0.38 / 0.54 | 1,596 | 130 |
| supplementary (256 per parent, thinned) | 919 | 41 | 0.07 / 0.36 / 0.57 | 6,569 | 573 |
| D3-aimed selection (K = 8, 64 kept) | 1,360 | 58 | 0.06 / 0.40 / 0.54 | 6,191 | 563 |

**Reading.**
1. **Aiming raises D3 overall by 5.8 times against production. It barely raises the A1 sub-population** (7 → 58).
2. No-input spirals almost never produce the raw 00:19 pair. The A1 share under D3 is consistent across all arms and both passes
   (0.06-0.09). **The shape of A1's impact distribution under D3 is not estimable** with any proposal now in the module. It is a
   declared coverage gap, and it carries about 0.07 of D3's weight.
3. **Prior recovery: no evidence of a defect (corrected 17 Oct, about 12:20Z; an earlier version of this item said "suspected defect").** The largest deviations are push-over hold 0.0067 and push-over rate 0.0036, against the fixed 0.0030 standard. But the two-sample 95 % band, from parent-level effective sizes, is 0.0108 for the push-over quantities: aiming concentrates push-overs, so they rest on 24k effective parents in the aimed arm against 46k in production. The band is 0.0081 for the rest. Every deviation is at most 0.63 of its band. The fixed 0.0030 standard does not scale with ESS, so thin arms fail it from noise alone. The same holds for the earlier run-I repro value (0.0105 against a band of 0.0108 or more). **Recommendation: replace the fixed standard with the ESS-scaled band.** The decision to use the unaimed children-64 pass stands on other grounds: it improves every cell, and aiming for D4 hurt D3 on the run-J smoke.

## 4. Running and queued (heavy lock, one queue)
- **Supplementary both-burst pass: done** (section 3b).
- **Joined V2, waypoints seeds 1-8**, with the clock-time onset window in J2241 (Pete's item 4 ruling). Output: `run-j-joined-v2/`.
- **Free-stratum production pass**, 18 seeds.
- **Descent-climb and repro passes:** waiting for disk (`run-i-dive` must be moved first).

## 5. COVERAGE
**(a) Feasible set.**
- Bank limits up to 90 deg in an uncontrolled spiral. Overbank is physically possible but not modelled.
- Dives and level-offs after a push-over (p = 0.5).
- Planned descents at any time before exhaustion (pre-00:11 starts come from joined V2, section 4).
- Impacts only after the 00:19:37 transmission.

**(b) Model's reach.**
- The bank limit covers [52, 90] deg, which closes the reach gap of the fixed 52.5 deg cap.
- **Overbank above 90 deg is a declared reach gap.**
- Round-3 laws: the Boeing leave-one-out gate failed in all three rounds.

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.

**(c) Proposal's coverage (this stratum).**
- D0', D1 and D2 are well covered (92k-2.1M effective impacts).
- D4: 21k in production and **44k in the supplementary pass (4.6k for A1): covered.**
- D3: 4.7k in production and 6.3k in the supplementary pass. **The A1 sub-population under D3 stays at about 400 effective impacts.** Its share is stable across two independent passes (0.08-0.09), but the shape of its impact distribution is a declared end-of-flight coverage gap. A dedicated A1-aimed proposal would be needed to close it.
- The "limit 80-90 only" variant rests on 217 effective impacts per seed under D4, so treat it as indicative.
- The B-uncontrolled family (share about 0.001) is not estimable in D3 or D4.
- Pre-00:11 planned descents come from joined V2 (queued); they are not in this pass.

**Bounds and sources.**
- Bank limit U[52, 90] deg. The lower end is the Boeing traces' 53-60 deg rounded outward; the upper end is the model's knife-edge
  limit. This is a declared choice (Pete).
- Dive probability p = 0.5 (Decision 4).
- Log-on cause mixture q = 1/3 with C2 silent (12 Oct rulings).
