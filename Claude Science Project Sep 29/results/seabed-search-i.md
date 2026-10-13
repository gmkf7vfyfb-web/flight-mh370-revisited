# Searched areas on end of flight's run I: the posterior moves onto searched ground

12 October 2026, Searched Areas module. Architecture's instruction of 16:35Z / 17:05Z: score each stratum as its
READY appears. **All four strata are scored.** 4 strata x 8 seeds, **102,399,904 impacts**.

**The result, and it is a large change.** Run I's posterior sits far more on ground the ATSB searched than any
earlier run's. In `next-i-waypoints`, which carries core's posterior share of about 0.998, **0.554 of the
probability lies on searched Phase 2 ground before the searches** under 00:19 Held Out, against 0.332 on run D-he.
Z - the probability that the searches missed the aircraft - falls to **0.5026**: the searches now remove **half**
the probability, against about 30 % on run D-he. Under Holland H1 in the same stratum **0.873** of the probability
is on searched ground and Z is **0.2164**, so the searches remove 78 % of it.

End of flight attribute the shift to the piloted-turn model (the G-turn fix): the roughly 1 degree southward
displacement after 00:19:37 that run H produced is gone, which moves the posterior north into the corridor the
ATSB swept. **That is their finding to defend, not this module's**; what this module can say is how much
probability the searches then remove, and it is now about half.

**Also a first: every 00:19 option is estimable in every stratum on its own.** Effective sample size after the
searches is 1,327 at worst (Holland H2 in descent-climb). On run D-he only the pooled four-stratum set made H1
and H2 estimable; on run H no single stratum did. Run I's 100,000 hand-off rows per seed x 8 seeds is what
changed that.

## Labels — read these before quoting any number

- **Core run I is NOT CONVERGED.** Core's waypoints split-half is 0.916 against the floor, and this module's own
  Z split-half is correspondingly worse than on earlier runs: **0.5224 / 0.4828 for Held Out in waypoints (a gap
  of 0.040) and 0.2384 / 0.1944 for H1 (0.044)**, against 0.003 to 0.008 on run C. Treat the third digit as noise.
- **No four-stratum mixture here, deliberately.** Core has published run I P(family) only between free flight and
  waypoints (ln BF +6.78, so waypoints take 0.999 of those two). The four-family share is not out. **I have not
  invented weights**: every number below is per stratum, and the composer should mix them with core's shares when
  they land.
- End of flight physics PROVISIONAL: piloted turns (Davey turns with each particle's own tau_h, then the 25-minute
  terminal window with random turns, sweep and ditching circuit), INTERIM parametric pitch-down, aimed pitch-down
  for A1, push-over to 40,000 ft/min with VMO 330 KCAS and a load-factor ceiling, C2-silent proposal component,
  residual roll P(left) = 0.8, trim at loss and Boeing sequence applied. Binary mh370-eof-ri1 (aa79d44e).
- Primary arm throughout: the survival factor 1 - P(in-flight breakup before 00:19:37) is applied to the posterior
  weights. The no-survival-factor arm is in the JSON.

## Per stratum, primary arm, +alive, rho = 0.05, Ocean Infinity excluded

| 00:19 option | stratum | Z | Z split-half | on Phase 2 before → after | ESS after (pooled) | estimable |
|---|---|---|---|---|---|---|
| 00:19 Held Out | waypoints | 0.5026 | 0.5224 / 0.4828 | 0.554 → 0.118 | 3,800,340 (3,787,695) | yes |
| 00:19 Held Out | free | 0.5890 | 0.5695 / 0.6086 | 0.458 → 0.086 | 3,593,481 (3,587,315) | yes |
| 00:19 Held Out | descent-climb | 0.6005 | 0.6308 / 0.5701 | 0.445 → 0.082 | 3,688,044 (3,663,804) | yes |
| 00:19 Held Out | repro-radar | 0.5978 | 0.6115 / 0.5841 | 0.448 → 0.082 | 3,022,860 (3,009,567) | yes |
| R600 BTO Only | waypoints | 0.4832 | 0.5029 / 0.4636 | 0.576 → 0.127 | 3,880,526 (3,855,738) | yes |
| R600 BTO Only | free | 0.5576 | 0.5330 / 0.5823 | 0.493 → 0.098 | 3,997,841 (3,978,938) | yes |
| R600 BTO Only | descent-climb | 0.5792 | 0.6115 / 0.5470 | 0.469 → 0.090 | 4,070,099 (4,001,106) | yes |
| R600 BTO Only | repro-radar | 0.5509 | 0.5579 / 0.5438 | 0.500 → 0.099 | 3,495,602 (3,466,415) | yes |
| R600 BTO + Raw BFO | waypoints | 0.3156 | 0.3345 / 0.2967 | 0.762 → 0.256 | 74,406 (74,092) | yes |
| R600 BTO + Raw BFO | free | 0.3906 | 0.3733 / 0.4078 | 0.679 → 0.191 | 87,025 (80,079) | yes |
| R600 BTO + Raw BFO | descent-climb | 0.3967 | 0.4203 / 0.3730 | 0.672 → 0.186 | 55,761 (54,204) | yes |
| R600 BTO + Raw BFO | repro-radar | 0.4016 | 0.4142 / 0.3890 | 0.667 → 0.180 | 55,243 (54,758) | yes |
| Holland H1 | waypoints | 0.2164 | 0.2384 / 0.1944 | 0.873 → 0.429 | 3,481 (2,767) | yes |
| Holland H1 | free | 0.2851 | 0.2664 / 0.3038 | 0.796 → 0.321 | 4,330 (3,403) | yes |
| Holland H1 | descent-climb | 0.2991 | 0.3339 / 0.2642 | 0.781 → 0.293 | 2,621 (2,011) | yes |
| Holland H1 | repro-radar | 0.3081 | 0.3282 / 0.2880 | 0.771 → 0.278 | 2,529 (2,336) | yes |
| Holland H2 | waypoints | 0.2520 | 0.2647 / 0.2393 | 0.833 → 0.351 | 1,699 (1,514) | yes |
| Holland H2 | free | 0.3182 | 0.2955 / 0.3408 | 0.759 → 0.265 | 1,691 (1,655) | yes |
| Holland H2 | descent-climb | 0.3239 | 0.3337 / 0.3140 | 0.753 → 0.255 | 1,327 (1,078) | yes |
| Holland H2 | repro-radar | 0.3336 | 0.3694 / 0.2979 | 0.742 → 0.245 | 1,368 (892) | yes |

## Ordered budget, `next-i-waypoints` (the 0.998 stratum)

| 00:19 option | rho 0 to 0.5 | Ocean Infinity 2018 in or out | q 0.90 to 0.98 | repeat search |
|---|---|---|---|---|
| 00:19 Held Out | 0.2618 | 0.0268 | 0.0421 | 0.0044 |
| R600 BTO Only | 0.2720 | 0.0184 | 0.0437 | 0.0049 |
| R600 BTO + Raw BFO | 0.3602 | 0.0270 | 0.0579 | 0.0070 |
| Holland H1 | 0.4124 | 0.0218 | 0.0663 | 0.0066 |
| Holland H2 | 0.3937 | 0.0207 | 0.0633 | 0.0067 |

**rho now matters more than it ever has**: 0.26 for Held Out rising to **0.41 for Holland H1**, against 0.150 and
0.33 on run D-he and 0.150 on run C. The reason is direct - rho is the only thing that keeps probability alive on
ground that was searched, and run I puts far more probability there. Every headline this module reports on run I
is conditional on a parameter with **no published value**, and more strongly so than before.

## Published for the other modules

`mh370-exchange/searched-areas/run-i/` (READY, SHA256SUMS, README.md): per stratum and seed,
`seabed-lnL.npy` (float64) plus the two raw coverage columns, row-aligned with
`end-of-flight/run-i/<stratum>/seed-<k>/impacts32.npy`. **102,399,904 rows. Not-computed weight 0.000** - the
column is finite on every row.

## COVERAGE

**(a) Feasible set.** All 777-200ER end-of-flight states after 00:11, including the piloted turns and rapid
descents run I now samples, and for this module a wreckage field rather than only a point; detection is a
two-part event, a detectable class then recognition at campaign level.

**(b) Model's reach.** End of flight's run I physics as they label them (above). This module: ATSB Phase 2 union
and Bluefin-21 only in the base, rho a single value at the base, shared miss dependence, point target, coverage
raster 0.01 deg bilinear. Ocean Infinity 2018 and 2025-26 are computed as labelled variants.

**(c) Proposal's coverage.** 102,399,904 impacts, 25.6 M per stratum. Effective sample size after the searches,
per stratum: 3.0-4.1 M (Held Out, R600 BTO Only), 55k-87k (raw BFO), 2,529-4,330 (H1), 1,327-1,699 (H2).
**Every option clears the 1,000 floor in every stratum** - the first run for which that is true.

**Gaps and status.**

| Gap | Type | Status |
|---|---|---|
| Core run I not converged (waypoints split-half 0.916); this module's Z split-half gap 0.040-0.044 | source | OPEN (core). The dominant uncertainty in these numbers. |
| Four-stratum P(family) not published | source | OPEN (core). No mixture computed here; per-stratum only. |
| Family A1 within H1/H2 | coverage (c) | End of flight report 351 / 1,358 / 252 effective impacts for A1 under D3/D4/D5 x C1 on waypoints; A1 below the gate under D3 and D5. Any family statement inside H1/H2 names it. |
| D3 x C2-silent 275 and D5 x C2-silent 831 below the gate | coverage (c) | End of flight's two-factor cells; this module's five 00:19 options are a different cut and all clear the gate |
| Wreckage field not applied on run I | reach (b) | OPEN. Settling has no run I samples on the exchange. Point target only; on runs C, D-he and H the field was worth -0.0011 to +0.0025. |
| rho a single value at the base | parameter bound, no source | Swept 0 to 0.5 and reported. Worth 0.26-0.41 on run I, more than on any earlier run. |
| ATSB Figure 73's three percentages (A-8) | provenance | BLOCKED after five failed fetches; q stays 0.945, bound 0.940-0.945 |

**Parameter bounds and sources.** q 0.945 (Phase 2) and 0.900 (Bluefin-21) from `run.toml`, derived in
`seabed-search-methods-draft.md` from ATSB Figure 73 (A-8 unverified in primary form); rho = 0.05 stated in
`run.toml`, no published value; ESS floor 1,000, this module's `ESS_FLOOR`; Ocean Infinity coverage fractions
0.889 / 0.952 and 0.7808 from the module's own TOML, resting on COMMUNITY TRACINGS, grade C.

## Method

One `mh370 evaluate` pass per seed over all eight coverage layers; every scenario is then exact algebra on the raw
coverage columns, **checked against evaluate's own `no_find_probability` on every one of the 32 seeds**
(max |delta| < 1e-12). Drivers `sweep_release.py` and `publish_columns.py`. Run detached, outside the heavy lock,
at 2 threads.

- Searched Areas Module
