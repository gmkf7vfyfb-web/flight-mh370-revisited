# Full-scale rho sweep, variants and Davey eq. (11.2) planning, under `+alive`

10 October 2026, searched-areas module. **PROVISIONAL-OVERNIGHT.**
`search-evidence.pdf` and its five pages, from
`engine/hypotheses/seabed-search/report.py runs/eof-289-full --option none --constraint alive`.

Run `eof-289-full`: 4 seeds x 3.2 x 10^6 impacts, prior track 289.7 deg at 18:01:49 UTC, base config
`config/davey2016.toml`, end-of-flight terminal stage, 00:19 data option **held out**, log-on cause
`other`, with end of flight's `+alive` existence constraint (airborne at 00:19:37.443) imported
read-only from their `smoke/displacement_hist.py`. Labels: uncorrected fuel, dive class (b) and Boeing
glide PROVISIONAL-OVERNIGHT on their side. Split-half agreement 0.972 before the search evidence.

## The sweep

| scenario | Z | median | 2.5 / 97.5 % | share on Phase 2 after | ESS |
|---|---|---|---|---|---|
| **run.toml, rho = 0.05** | **0.7206** | −36.90 | −40.61 / −26.17 | 0.047 | 8,322,028 |
| rho = 0 | 0.7059 | −36.89 | −40.62 / −26.13 | 0.027 | 8,015,062 |
| rho = 0.02 | 0.7118 | −36.89 | | 0.035 | 8,139,253 |
| rho = 0.1 | 0.7353 | −36.90 | | 0.066 | 8,616,404 |
| rho = 0.2 | 0.7647 | −36.91 | | 0.101 | 9,161,420 |
| rho = 0.3 | 0.7941 | −36.92 | | 0.134 | 9,640,362 |
| rho = 0.5 | 0.8529 | −36.93 | −40.48 / −26.47 | 0.194 | 10,379,622 |
| Phase 2 q = 0.90 | 0.7339 | −36.90 | | 0.064 | 8,588,950 |
| Phase 2 q = 0.98 | 0.7103 | −36.89 | | 0.033 | 8,107,232 |
| Phase 2 split, shared misses | 0.7187 | −36.89 | | 0.044 | 8,282,232 |
| Phase 2 split, independent misses | 0.7168 | −36.89 | | 0.042 | 8,241,694 |
| + OI 2025–26 inferred, outboard band | 0.7165 | −36.92 | | 0.047 | 8,292,633 |
| + OI 2018 inferred, coverage 0.889 | 0.6864 | −37.07 | | 0.049 | 8,034,314 |
| + OI 2018 inferred, coverage 0.952 | 0.6840 | −37.08 | | 0.049 | 7,990,653 |

At rho = 0, Phase 2 alone removes **0.2941** of the probability, Ocean Infinity 2018 alone **0.0363**,
and the two together 0.3301. Bluefin-21 removes 0.0000 to four decimals, as it has at every scale:
that search is 2,473 km from the posterior's mass.

**Ocean Infinity coverage is inferred, not official**: a community tracing (MH370-CAPTION, grade C) of
published map imagery and vessel tracks, with a coverage fraction applied to a planning envelope rather
than measured swath coverage. It is reported separately and never merged into the ATSB-only estimate.
See `engine/hypotheses/seabed-search/coverage/PROVENANCE.md`.

## What the sweep says

1. **rho is the headline parameter and the range it spans is modest.** Across 0 to 0.5 — far wider than
   anything defensible — the evidence moves from 0.7059 to 0.8529, and the median moves 0.04 deg. What
   rho really controls is the share of probability left *on searched ground*: 0.027 at rho = 0 against
   0.194 at rho = 0.5. That is the quantity a revisit plan would care about, and it is almost entirely
   an assumption rather than a measurement.
2. **q is worth less than rho.** Taking Phase 2's detection probability from the ATSB-derived 0.945 to
   Stone et al.'s 0.90 cap moves Z by 0.013; pushing it to 0.98 moves it by 0.010. The unverified
   Figure 73 percentages behind 0.945 (ledger A-8) therefore matter less than the fact that rho has no
   published value at all.
3. **Repeat-search dependence is worth 0.002.** Union 0.7206, split with shared misses 0.7187, split
   with independent misses 0.7168. The 15.0 % of Phase 2 ground swept more than once is real, but at
   full scale the choice between the dependence models is an order of magnitude below rho.
4. **Ocean Infinity 2018 is the largest single addition after Phase 2**, worth 0.034–0.037 in Z and
   0.17 deg of median — which is why its grade-C provenance is load-bearing. The 2025–26 band is worth
   0.004.

## Davey eq. (11.2): where to look next

On the residual posterior, 0.5 deg candidate blocks ranked by residual mass, at a planning `P_D` of 0.9
(Stone et al.'s cap for ground not yet searched — **not** this module's own q):

| rank | block | residual mass | P(find) | km² | same block, search disabled |
|---|---|---|---|---|---|
| 1 | 39.00°S 89.00°E | 0.0154 | 0.0138 | 2,411 | 0.0111 |
| 2 | 38.00°S 91.00°E | 0.0149 | 0.0134 | 2,444 | 0.0108 |
| 3 | 38.00°S 90.50°E | 0.0148 | 0.0133 | 2,444 | 0.0112 |
| 4 | 37.50°S 91.50°E | 0.0144 | 0.0130 | 2,461 | 0.0104 |
| 5 | 35.50°S 91.00°E | 0.0138 | 0.0125 | 2,524 | 0.0100 |

**P(find) = 25 % needs the best 24 blocks and 59,005 km²; 50 % needs 70 blocks and 171,921 km²; 75 %
needs 248 blocks and 623,095 km².** Against the plain arm (21 blocks / 51,977 km²; 62 / 152,587;
231 / 580,334) the `+alive` constraint makes the planning problem about 13 % larger in area, which is
the same widening the residual views show.

The cumulative curve is the reportable object. The top-N list above is shown for orientation only: a
0.5 deg block holds about 1.5 % of the residual mass, so block *ordering* is far less resolved than the
cumulative curve or the aggregate evidence, and no search plan should be drawn from the ranking alone.
