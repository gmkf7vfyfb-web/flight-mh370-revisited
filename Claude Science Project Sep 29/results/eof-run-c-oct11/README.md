# End of flight on core run C: impact samples and 00:19 evidence (11 Oct 2026)

**PROVISIONAL. Core run C NOT converged** (8-seed split-half floor 0.924: free 0.918, Davey dynamics + radar 0.910, descent-climb 0.892, routes 0.850; core ~00:12 UTC).
**Labels on every number:** rapid descents above 6,500 ft/min and unloading not reachable by the model (reach gap); contact speeds above about 1.25 VMO not physically credible (G13, no structural limit; the `~v212` version is shown beside); residual roll direction P(left) = 0.8 PROVISIONAL (Boeing's system sequence, sampled wider); trim at loss NOT applied; two-tank takeover NOT applied in the module's onset prediction (core flew two tanks to 00:11); Holland H1/H2 NOT estimable (within-parent sampling); family shares from the 00:11 hand-off are mostly prior and are not an A-vs-B test.

## Inputs and provenance
- Core run C (`mh370-exchange/core/next-run-c/`, READY 23:42:53 UTC 10 Oct): 4 strata x 8 seeds, m0011 hand-offs gunzipped and sha256-verified per seed against core's COMPACT.txt.
- Module recipe: core's chain per stratum + snapshot-m0011 + terminal + reference-289 (N = 8 children x 4 descents) + descent idle floor + v2-broad + family-b-ditching + residual-bank-boeing. Binary `/tmp/mh370-eof-runc5` (sha256 15ba109827a135af..., built from 097a5d77). Sweep 00:23-04:44 UTC, outside the heavy lock at 8 threads (architecture 18:05 -0600, Pete delegated).
- Output: `mh370-exchange/end-of-flight/next-run-c/<stratum>/seed-k/` compact float32 v1 (all 32 pass `compact_impacts.py check`), τ sidecars `tau90_v1.npz` (method `results/eof-impact-tau-method-oct11.md`), summaries in `summary/`. P(family) for the mixtures from core: free 0.589, Davey dynamics + radar 0.252, descent-climb 0.135, routes 0.024.

## 1. 00:19 evidence per core family and the re-weighted mixture (`+unpowered`, the reference constraint)
| 00:19 option | ln Ẑ per stratum (free / Davey + radar / descent-climb / routes) ± seed s.e. | P(family) re-weighted | impact latitude q05 / q50 / q95 | q50 with contact speed ≤ 212 m/s |
|---|---|---|---|---|
| Held Out | -0.03 ± 0.00 / -0.03 ± 0.00 / -0.03 ± 0.00 / -0.04 ± 0.00 | 0.589 / 0.252 / 0.135 / 0.024 | -39.81 / -37.50 / -29.07 | -37.59 |
| R600 BTO Only | -5.69 ± 0.01 / -5.74 ± 0.01 / -5.62 ± 0.02 / -5.59 ± 0.01 | 0.590 / 0.239 / 0.145 / 0.027 | -40.03 / -37.99 / -29.02 | -38.09 |
| R600 BTO + Raw BFO | -12.44 ± 0.03 / -12.61 ± 0.03 / -12.34 ± 0.04 / -12.58 ± 0.02 | 0.606 / 0.218 / 0.154 / 0.022 | -39.16 / -37.49 / -28.94 | -37.60 |
| Holland H1 | -32.67 ± 0.20 / -32.46 ± 0.31 / -32.56 ± 0.16 / -32.44 ± 0.27 | 0.545 / 0.288 / 0.139 / 0.028 | -38.24 / -36.50 / -27.53 | -36.69 |
| Holland H2 | -24.51 ± 0.09 / -24.73 ± 0.08 / -24.65 ± 0.11 / -24.53 ± 0.14 | 0.632 / 0.216 / 0.126 / 0.025 | -38.01 / -36.57 / -28.61 | -36.38 |

Minimum effective parents per seed (free / Davey + radar / descent-climb / routes): R600 BTO Only 69,993 / 65,826 / 74,370 / 78,444; R600 BTO + Raw BFO 24,312 / 19,798 / 23,953 / 21,459; Holland H1 2 / 3 / 1 / 3; Holland H2 6 / 7 / 6 / 8. H1/H2 rest on a handful of parents: not estimable.

Reading: the 00:19 data hardly separate core's strata (ln Ẑ agrees across strata to within 0.3 nat), so P(family) barely moves.

## 2. Same-data Bayes factors against 00:19 Held Out (central anomalous widths BFO 700 Hz, BTO 20,000 µs, log-on 3,896 s; range over 27 width settings)
| 00:19 option | unpowered | alive | silent | unpowered ~v212 | silent ~v212 |
|---|---|---|---|---|---|
| R600 BTO Only | +4.24 [+1.9, +5.3] | +4.24 [+1.9, +5.3] | +4.23 [+1.9, +5.3] | +4.24 [+1.9, +5.3] | +4.26 [+2.0, +5.4] |
| R600 BTO + Raw BFO | +4.02 [+1.0, +5.8] | +4.02 [+1.0, +5.8] | +3.99 [+1.0, +5.8] | +3.99 [+1.0, +5.8] | +3.33 [+0.3, +5.1] |
| Holland H1 | -1.29 [-5.7, +1.8] | -1.29 [-5.7, +1.8] | +1.98 [-2.5, +5.1] | -1.77 [-6.2, +1.3] | +2.13 [-2.3, +5.2] |
| Holland H2 | -1.54 [-5.2, +0.9] | -1.54 [-5.2, +0.9] | +0.72 [-3.0, +3.2] | -2.02 [-5.7, +0.5] | -0.21 [-3.9, +2.3] |

Reading: **the R600 BTO is supported as a real observation** (ln BF about +4.2, at least +1.9 at every width, every constraint). **The raw R600 BFO is indeterminate** against the BTO alone (difference −0.2 to −0.9). H1/H2 are not estimable; their numbers are shown, not read.

## 3. Four end-to-end families (ruling 6 as amended), mixture with core's P(family) fixed
| 00:19 option, constraint | A1 | A2 | B | outside B |
|---|---|---|---|---|
| Held Out +unpowered | 0.119 | 0.330 | 0.550 | 0.000 |
| R600 BTO Only +unpowered | 0.111 | 0.326 | 0.563 | 0.000 |
| R600 BTO + Raw BFO +unpowered | 0.108 | 0.149 | 0.743 | 0.000 |
| Held Out +unpowered ~v212 | 0.066 | 0.354 | 0.580 | 0.000 |
| R600 BTO Only +unpowered ~v212 | 0.054 | 0.350 | 0.597 | 0.000 |
| R600 BTO + Raw BFO +unpowered ~v212 | 0.039 | 0.162 | 0.800 | 0.000 |
| Held Out +silent | 0.113 | 0.000 | 0.887 | 0.000 |
| R600 BTO Only +silent | 0.126 | 0.000 | 0.873 | 0.000 |

Weight removed by the 212 m/s cap (free stratum, share of each family): Held Out +unpowered: total 0.099, A1 0.50, A2 0.03, B 0.05; R600 BTO + Raw BFO +unpowered: total 0.118, A1 0.68, A2 0.05, B 0.05.

Reading: the shares are mostly the module's prior (about 56 % B by construction). The raw R600 BFO moves weight from A2 to B; `silent` removes A2 entirely by construction (a long glide after exhaustion would be followed by an APU log-on). Not an A-vs-B test; that is the 22:41 runs (running; small ESS without core request 10).

## 4. Impact time, posterior-predictive check, τ
- Impact time, 00:19 Held Out plain: before 00:19:37 3.0 % / 3.2 % / 2.9 % / 3.8 %; after 01:15:56 0.058 % / 0.070 % / 0.052 % / 0.045 % (free / Davey + radar / descent-climb / routes); q05 / q50 / q95 (free) 00:22:09 / 00:40:08 / 00:56:24.
- Posterior-predictive (per seed, all strata): p(R600 BFO | R600 BTO) 0.010-0.014 with no offset, 0.14-0.18 with inflated noise, 0.004-0.006 with the startup offset; p(R1200 BFO | R600) about 1e-4 to 8e-4 under every model - this measures the model's reach (no unloading), not the aircraft.
- τ90 (unweighted per row, first-order model): q05 / q50 / q95 ≈ 0.12 / 3.7 / 10.5 s in every stratum.

## COVERAGE
**(a) Feasible set.** The 777-200ER's kinematically feasible end-of-flight space from the 00:11 hand-off: onset at or before fuel exhaustion; uncontrolled, controlled-then-lost, arrested or ditching descents; either roll direction; dives to the structural limit; impact at any time from 00:11 until the fuel and glide allow.
**(b) Model reach (gaps, status):** commanded rates above 6,500 ft/min and unloading (OPEN; capability built default off, ruling item 4 plan posted); no structural limit / transonic drag rise, contact speeds > 212 m/s not credible (G13, OPEN; `~v212` shown); residual roll direction (CLOSED for run C: P(left) = 0.8); in-flight breakup end state (OPEN, ruling 1(A)); right flame-out during a module-flown powered descent and the two-tank onset prediction (OPEN, built default off); impact attitude = flight-path angle (pass-1 stand-in, labelled); τ first-order (method 1, no full-scale validation); 6-DOF for uncontrolled periods (OPEN, gate fails: `results/eof-6dof-refit-oct11/`).
**(c) Proposal coverage:** 3.2 M descents per seed, 25.6 M per stratum; the R600 options have tens of thousands of effective parents per seed; the push-over coincident with the 8-s burst interval is a sampling gap (H1/H2 rest on a few parents: OPEN, targeted sampler needs core request 9); the 22:41 A-vs-B test has a small ESS (uniform 22:41 hand-offs; core request 10).
**Parameter bounds and sources:** residual bank |φ| U[0, 35] deg (module), P(left) 0.8 (Boeing SIR App. 1.6E p. 8); descent envelope v2-broad (module, PROVISIONAL); family B control [ditching 0.5, maintained-then-lost 0.5] (ruled 15:45 -0600); log-on lag Erlang(8, 14.875 s); speed cap 212 m/s = 1.25 VMO (VMO 330 kt; ruling 20:35 -0600); τ: ā U[0.75, 3] g, L_eff U[0.5, 1] x 63.7 m (method note).

- End of flight
