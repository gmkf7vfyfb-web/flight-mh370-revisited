# End of flight on core run J, waypoints stratum: production pass — 16 Oct 2026

**Status: complete for one stratum (waypoints, core prior share 0.9982 on run I; run J's stratum shares are not yet posted by core).**
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
3. **D3 rests on 368 effective A1 impacts.** Its A1 share (0.09 against run I's 0.17) is **not converged**. This is the cell the
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

## 4. Running and queued (heavy lock, one queue)
- **Supplementary both-burst pass**, waypoints seeds 1-8, 256 descents per parent with the same laws, thinned to 1M rows per seed.
  Started 21:00Z, about 3.7 h. Output: `run-j-both-burst/run-j-waypoints/`.
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
- D4 has 21k in total, but only 1.9k for A1, and 197-615 per seed in the raw column.
- **D3 is a coverage gap at this setting:** 4.7k in total, 368 for A1, and 30-131 per seed in the raw column. The supplementary
  pass is under way to close it.
- The "limit 80-90 only" variant rests on 217 effective impacts per seed under D4, so treat it as indicative.
- The B-uncontrolled family (share about 0.001) is not estimable in D3 or D4.
- Pre-00:11 planned descents come from joined V2 (queued); they are not in this pass.

**Bounds and sources.**
- Bank limit U[52, 90] deg. The lower end is the Boeing traces' 53-60 deg rounded outward; the upper end is the model's knife-edge
  limit. This is a declared choice (Pete).
- Dive probability p = 0.5 (Decision 4).
- Log-on cause mixture q = 1/3 with C2 silent (12 Oct rulings).
