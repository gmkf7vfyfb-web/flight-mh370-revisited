# End of flight on core run J: all four strata — the run-J end-of-flight set — 17 Oct 2026

**Status:** complete. Core run J's split-half convergence is accepted as a pass by project ruling (16 Oct 2026). Every stratum has
READY under `mh370-exchange/end-of-flight/run-j/`, and the summaries are complete (`run-j/summary/SUMMARIES-DONE`, 09:55Z).

| stratum | seeds | READY (UTC) | core P(family), run J |
|---|---|---|---|
| run-j-waypoints | 24 | 16 Oct 20:59 | 0.9982 |
| run-j-free | 18 | 17 Oct 02:54 | 0.0013 |
| run-j-repro-radar | 16 | 17 Oct 05:20 | 0.0003 |
| run-j-descent-climb | 16 | 17 Oct 07:23 | 0.0002 |

- **Recipe:** run-i-dive (C2-silent aim, dive branch p = 0.5; children 16 on waypoints, 8 elsewhere), with the **round-3 descent laws**
  and the **bank limit uniform on [52, 90] deg** (Pete, 16 Oct). Binary sha256 19031f41748ecb0c.
- The free, repro and descent-climb strata ran at 6 threads outside the heavy lock (Pete, 17 Oct: the lock is retired for end of
  flight). Thread count does not change the output.
- **Related notes:**
  - `results/eof-run-j-waypoints-oct16/`: waypoints, the bank-limit prior variants, and the both-burst supplementary pass (D3/D4).
  - `results/eof-run-j-joined-v2-oct17/`: joined V2, planned descents before 00:11, and the U1 onset prior.

## 1. The 00:19 two-factor table, four-stratum mixture (q = 1/3, cause C2 silent, transmission imposed)

`table-0019-mixture.json/.txt` (strata mixed by core run J's P(family); seeds pooled by evidence).

| 00:19 treatment | ln Z | ESS | A1 / A2 / B | A1 ESS | impact latitude 5 / 50 / 95 % |
|---|---|---|---|---|---|
| D0' held out | −7.525 | 1.95M | 0.17 / 0.34 / 0.48 | 999k | −38.40 / −37.12 / −33.86 |
| D1 R600 BTO | −12.935 | 2.14M | 0.20 / 0.35 / 0.45 | 1.25M | −38.48 / −37.21 / −34.57 |
| D2 R600 BTO + BFO | −19.121 | 92k | 0.24 / 0.23 / 0.53 | 49k | −38.16 / −37.12 / −34.34 |
| D3 both BFOs raw | −28.582 | 4.7k | 0.09 / 0.41 / 0.50 | 369 | −38.04 / −37.29 / −34.42 |
| D4 both, transient bias | −28.513 | 21k | 0.25 / 0.35 / 0.40 | 1.9k | −37.98 / −37.21 / −34.39 |
| D5 R1200 offset | −29.169 | 26k | 0.06 / 0.42 / 0.52 | 2.2k | −37.99 / −37.27 / −34.47 |

**Reading.**
1. **The mixture equals the waypoints stratum at the precision shown** (ln Z within 0.001; core P(family) 0.9982).
2. The other three strata impact further north: D0' median latitude −36.4 to −37.0, and q95 up to −28.6 (free, D4). They carry
   0.0018 of the weight between them. They matter only for the northern tail of the PDF.
3. **For D3 and D4, use the supplementary pass** (waypoints note, section 3b). It gives D4 an ESS of 44k with the same answer
   (A1/A2/B 0.25 / 0.32 / 0.43).

## 2. Per-stratum D0' and D4 (q = 1/3, C2 silent)

| stratum | D0' A1 / A2 / B | D0' median latitude (q95) | D4 A1 / A2 / B | D4 ESS (A1) | D4 median latitude (q95) |
|---|---|---|---|---|---|
| waypoints | 0.17 / 0.34 / 0.48 | −37.12 (−33.87) | 0.25 / 0.35 / 0.40 | 21k (1.9k) | −37.21 (−34.39) |
| free | 0.12 / 0.29 / 0.60 | −36.42 (−32.01) | 0.21 / 0.29 / 0.49 | 4.4k (271) | −36.67 (−28.63) |
| repro-radar | 0.13 / 0.32 / 0.55 | −36.44 (−30.49) | 0.26 / 0.30 / 0.43 | 3.8k (357) | −36.68 (−29.35) |
| descent-climb | 0.13 / 0.30 / 0.56 | −36.98 (−33.63) | 0.19 / 0.32 / 0.49 | 2.1k (321) | −37.18 (−34.23) |

## 3. Consumer products (in `run-j/summary/`; copied here)

The same set as run I, under run-J names (`*-run-j.json`; the `*-run-c.json` files in `run-j/summary/` are identical copies made by
the shared script):
- impact-time shares and constraints per stratum (`impact-time/`);
- family evidence (`family-evidence-run-j.json`) and family shares (`family-shares-run-j.json`; its own warning applies: the shares
  are "mostly the module prior from the 00:11 hand-off", not an A-against-B test);
- same-data Bayes factors under the alive, unpowered and silent constraints, with the contact-speed ≤ 212 m/s variants;
- the 00:19 posterior predictive (`postpred-0019-run-j.json`);
- the H1/H2 sweep summary;
- the pulse-duration sidecar (`tau-sidecar.log`; waypoints tau90 q50 about 2.7 s, q95 about 10.2 s per seed).

## 4. COVERAGE

**(a) Feasible set.**
- Uncontrolled spiral bank limits up to 90 deg. Overbank is possible but not modelled.
- Dive or level-off after a push-over.
- Planned descents at any time before exhaustion.
- Impacts only after the 00:19:37 transmission.

**(b) Model's reach.**
- Bank limit [52, 90] deg; **overbank above 90 deg is a declared reach gap.**
- Pre-00:11 planned descents come only from joined V2, not this set.

> The uncontrolled-arm dynamics are not calibrated: the Boeing leave-one-out gate failed in all
> three rounds. Impact energy, attitude, flight-path angle and energy-transfer duration from
> this arm are a labelled sensitivity on uncalibrated dynamics, not a physical prediction.

**(c) Proposal's coverage.**
- D0', D1 and D2 are well covered (92k-2.1M).
- D4: 21k here and 44k in the supplementary pass.
- **D3's A1 sub-population is about 400 effective impacts in both passes:** the share is stable, but the shape of its distribution
  is a declared end-of-flight coverage gap.
- The non-waypoints strata have A1 ESS of 271-357 under D4. Their weight is 0.0018, so they matter only in the northern tail.
- Pre-00:11 B is parent-limited (joined V2 note, section 3).

**Bounds and sources.**
- Bank limit U[52, 90] (Pete).
- p = 0.5 (Decision 4).
- q = 1/3, C2 silent (12 Oct rulings).
- Strata mixed by core run J's P(family) (core `results/run-j/README.md`).
