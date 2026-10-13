# Physics items 3 and 4: smoke results (end of flight, 11 Oct 2026)

**SMOKE (N = 1 child x 4 descents, one seed). NOT EVIDENCE.** Core run C `next-c-free` seed 1, m0011 hand-off (100,000 parents, sha256 verified), run C module recipe (reference-289, idle floor, v2-broad, family-b-ditching, residual-bank-boeing), constraint `unpowered`. Plan accepted 01:45 -0600 11 Oct (5e8f13ea). Labels: no structural limit (G13; share above 212 m/s shown); Holland H1/H2 not estimable (effective parents shown); Boeing system sequence (item 2) not yet in.

Binaries: base and item 3 `/tmp/mh370-eof-runc5.real` (run C build, 097a5d77); item 4 and items 3+4 `/tmp/mh370-eof-item4` (this change, sha256 9048294b...). With the push-over off, the item-4 binary equals the run C binary in every existing column except 15 columns in at most 2 of 399,996 rows, by rounding (not byte-identical; declared).

## Prior push-over tail and the 00:19 evidence

| run | P(vertical-speed change 00:19:29 to 00:19:37 <= -10,450 ft/min, airborne) | ln Z H1 (eff. parents) | ln Z H2 (eff. parents) | ln Z R600 BTO Only | ln Z R600 BTO + Raw BFO | Held Out median latitude |
|---|---|---|---|---|---|---|
| Run C recipe (base) | 0.106 % | -39.25 (1.9) | -24.39 (2.0) | -5.672 | -12.487 | -37.58 |
| + item 3, trim at loss | 0.090 % | -39.68 (1.0) | -41.17 (1.0) | -5.673 | -12.480 | -37.59 |
| + item 4, push-over | 0.162 % | -29.08 (8.1) | -23.65 (3.5) | -5.673 | -12.704 | -37.54 |
| + items 3 and 4 | 0.125 % | -29.12 (7.6) | -23.94 (2.4) | -5.674 | -12.699 | -37.54 |

## Item 4 cells: posterior share in push-over rows, and ln Z as a function of the prior push-over probability q

| run | option | share in push-over rows | eff. parents in push-over rows | ln Z at q = 0 | q = 0.25 | q = 0.5 (U[0,1] marginal) | q = 1 |
|---|---|---|---|---|---|---|---|
| + item 4, push-over | Held Out | 0.144 | 38907.4 | -0.03 | -0.03 | -0.04 | -0.04 |
| + item 4, push-over | R600 BTO Only | 0.152 | 28474.8 | -5.67 | -5.67 | -5.67 | -5.67 |
| + item 4, push-over | R600 BTO + Raw BFO | 0.095 | 615.3 | -12.49 | -12.59 | -12.70 | -12.98 |
| + item 4, push-over | Holland H1 | 0.964 | 7.6 | -32.40 | -29.74 | -29.08 | -28.41 |
| + item 4, push-over | Holland H2 | 0.760 | 2.5 | -24.38 | -23.95 | -23.65 | -23.23 |
| + items 3 and 4 | Held Out | 0.143 | 38772.0 | -0.03 | -0.03 | -0.04 | -0.04 |
| + items 3 and 4 | R600 BTO Only | 0.152 | 28399.5 | -5.67 | -5.67 | -5.67 | -5.67 |
| + items 3 and 4 | R600 BTO + Raw BFO | 0.094 | 613.6 | -12.48 | -12.59 | -12.70 | -12.97 |
| + items 3 and 4 | Holland H1 | 1.000 | 7.6 | -39.68 | -29.82 | -29.12 | -28.43 |
| + items 3 and 4 | Holland H2 | 1.000 | 2.4 | -41.17 | -24.63 | -23.94 | -23.25 |

Prior: eligible descents 28.9 % of the weight (powered emergency shape and unpowered controlled glides), push-over drawn in 14.5 %.

## Families (four, ruling 6 as amended), `unpowered`

| run | option | A1 | A2 | B |
|---|---|---|---|---|
| Run C recipe (base) | R600 BTO + Raw BFO | 0.092 | 0.144 | 0.763 |
| Run C recipe (base) | Holland H1 | 0.653 | 0.000 | 0.347 |
| Run C recipe (base) | Holland H2 | 0.000 | 0.000 | 1.000 |
| + item 3, trim at loss | R600 BTO + Raw BFO | 0.092 | 0.145 | 0.764 |
| + item 3, trim at loss | Holland H1 | 1.000 | 0.000 | 0.000 |
| + item 3, trim at loss | Holland H2 | 0.000 | 0.000 | 1.000 |
| + item 4, push-over | R600 BTO + Raw BFO | 0.117 | 0.204 | 0.680 |
| + item 4, push-over | Holland H1 | 0.000 | 0.679 | 0.321 |
| + item 4, push-over | Holland H2 | 0.000 | 0.263 | 0.737 |
| + items 3 and 4 | R600 BTO + Raw BFO | 0.116 | 0.204 | 0.680 |
| + items 3 and 4 | Holland H1 | 0.000 | 0.705 | 0.295 |
| + items 3 and 4 | Holland H2 | 0.000 | 0.353 | 0.647 |

## Reading (smoke)
1. **Item 3 (trim at loss) removes an artefact.** The push-over tail falls 0.106 % → 0.090 %, and Holland H2 loses its support: ln Z −24.4 → −41.2. H2's
   mass came from the load-factor step when a commanded descent switched to a trim referenced to the takeover state (architecture
   push-over study: 91 % of H2). The R600 options and the impact latitude do not change (≤ 0.01 nat, ≤ 0.01°).
2. **Item 4 (bounded push-over, piloted only) makes the Holland options reachable by physics.** The tail rises 0.106 % → 0.162 %. With
   items 3 and 4 together, **all** of the H1 and H2 posterior is in push-over rows: at q = 0 ln Z is −39.7 (H1) and −41.2 (H2); at the
   U[0, 1] marginal −29.1 and −23.9. H1's posterior moves from A1 (no intervention) to A2 (a controlled glide after exhaustion, pushed
   over) and B.
3. **H1/H2 stay NOT ESTIMABLE:** 2.4–7.6 effective parents. The push-over exists in the prior now, but its coincidence with the 8-s
   burst interval is rarely sampled. This is the proposal gap that the targeted sampler (core request 9; Pete's go) is meant to close.
4. R600 BTO + Raw BFO mildly disfavours push-overs (ln Z −12.48 at q = 0, −12.97 at q = 1); R600 BTO Only and Held Out are indifferent.

## COVERAGE
(a) Feasible set: deliberate push-overs by a pilot at any rate up to the speed limits and down to the certified −1 g; any time after
the onset. (b) Model reach, item 4: commanded rate U[6,500, 30,000] ft/min, floor U[−1.0, 0.8] g, hold U[0, 300] s, in the powered
emergency shape and unpowered controlled glides (sources in `full/pushover.toml`: Holland Table VII; CS-25.335(b); CS-25.337(c);
Boeing SIR App. 1.6E). Not reached: deliberate dives faster than 30,000 ft/min (only free dynamics reach them; partial gap, declared);
push-overs in powered continuous or stepped descents (declared; the emergency shape is the powered push-over shape). Item 3: trim at
the state at loss. (c) Proposal: p0 = 0.5, exact re-weighting to any q; the coincidence with the bursts is a sampling gap (OPEN).
Parameter bounds and sources as above; P(left) 0.8 (Boeing, PROVISIONAL).

- End of flight

