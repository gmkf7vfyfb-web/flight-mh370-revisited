# End of flight: impact times against 00:19:37 and 01:15:56 on core (b) `next-run`, and the late-tail attribution (10 Oct 2026)

These are for Hydroacoustics' validation gate (architecture ~10:08 request). The estimands and JSON keys are those of
`results/eof-impact-time-oct10` (reference-289), so the same gate applies.

**Inputs:**
- `mh370-exchange/end-of-flight/next-run/<stratum>/seed-1..4`, the stand-in sweep on core (b) m0011 hand-offs that I reviewed and accepted
  at ~15:24.
- Code: `smoke/impact_time_shares.py` (end-of-flight `01a5d6b`).

**Labels:**
- core (b), split-half NOT converged;
- two-tank bookkeeping only;
- descent idle floor ON;
- dive class (b) PROVISIONAL;
- right-dry rows flown as a twin-engine continuation on the left pool.

**Strata are reported separately and are not mixed.** Mixing uses the 00:19 re-weighted P(family), ruling C; that factor is my next item.

## Variants

| name | constraint |
|---|---|
| plain | no existence constraint |
| `alive` | airborne at 00:19:37.443 |
| `unpowered` | **new: variant (b) of ruling ~19:10 B.** Airborne at 00:19:37 **and** not powered at 01:15:56: the two directly observed facts |
| `silent` | `unpowered`, plus, under `other` only, no further APU log-on after a later flame-out (Erlang survival). Model-dependent; shown beside (b) |

- **Shares** (before 00:19:37, after 01:15:56, powered at 01:15:56) are seed means under the plain option × cause.
- **Retained** is the seed-mean fraction of plain posterior weight kept by each variant.
- **Median latitude** and **ESS** (summed over 4 seeds) are given for plain / alive / unpowered / silent.

## Core options

The internal arm codes are given here only to map the files to the standard names:

| 00:19 option (standard name) | internal arm |
|---|---|
| 00:19 Held Out | `none__other` |
| 00:19 R600 BTO Only | `r600-bto__other` |
| 00:19 R600 BTO + Raw BFO | `r600_no-offset__other` |
| 00:19 Holland H1 | `both_startup-offset__fuel-exhaustion` |
| 00:19 Holland H2 | `both_no-offset__other` |

Holland H1 and H2 are **not yet estimable (targeted sampler in progress)**: their ESS is 46-344 and the rows are shown only for completeness.

| stratum | arm | before 00:19:37 | after 01:15:56 | powered at 01:15:56 | impact time q05 / q50 / q95 (UTC) | retained alive | retained unpowered | retained silent | median lat plain / alive / unpowered / silent | ESS plain / alive / unpowered / silent |
|---|---|---|---|---|---|---|---|---|---|---|
| next-free | none__other | 0.1006 | 0.0030 | 0.0002 | 00:16:17 / 00:38:44 / 00:57:57 | 0.899 | 0.899 | 0.113 | -37.06 / -37.25 / -37.25 / -36.24 | 12,337,220 / 11,022,154 / 11,020,152 / 1,514,380 |
| next-free | r600-bto__other | 0.0006 | 0.0034 | 0.0002 | 00:23:59 / 00:41:43 / 00:58:53 | 0.999 | 0.999 | 0.089 | -37.91 / -37.91 / -37.91 / -37.10 | 6,949,043 / 6,943,447 / 6,942,452 / 690,379 |
| next-free | r600_no-offset__other | 0.0001 | 0.0000 | 0.0000 | 00:21:36 / 00:34:55 / 00:48:19 | 1.000 | 1.000 | 0.104 | -37.40 / -37.40 / -37.40 / -36.64 | 234,529 / 234,505 / 234,501 / 28,884 |
| next-free | both_startup-offset__fuel-exhaustion | 0.0000 | 0.0000 | 0.0000 | 00:19:59 / 00:26:09 / 00:42:06 | 1.000 | 1.000 | 1.000 | -36.95 / -36.95 / -36.95 / -36.95 | 50 / 50 / 50 / 50 |
| next-free | both_no-offset__other | 0.0000 | 0.0000 | 0.0000 | 00:20:59 / 00:31:35 / 00:43:34 | 1.000 | 1.000 | 0.301 | -37.16 / -37.16 / -37.16 / -36.08 | 67 / 67 / 67 / 27 |
| next-repro-radar | none__other | 0.1031 | 0.0013 | 0.0000 | 00:16:12 / 00:38:12 / 00:57:44 | 0.897 | 0.897 | 0.109 | -36.55 / -36.73 / -36.73 / -35.75 | 12,339,414 / 10,997,088 / 10,996,520 / 1,462,927 |
| next-repro-radar | r600-bto__other | 0.0008 | 0.0016 | 0.0000 | 00:23:35 / 00:41:15 / 00:58:56 | 0.999 | 0.999 | 0.085 | -37.53 / -37.53 / -37.53 / -36.69 | 6,344,202 / 6,338,067 / 6,337,786 / 605,894 |
| next-repro-radar | r600_no-offset__other | 0.0001 | 0.0000 | 0.0000 | 00:21:30 / 00:34:59 / 00:48:15 | 1.000 | 1.000 | 0.084 | -37.07 / -37.07 / -37.07 / -36.10 | 224,950 / 224,930 / 224,930 / 23,675 |
| next-repro-radar | both_startup-offset__fuel-exhaustion | 0.0000 | 0.0000 | 0.0000 | 00:20:16 / 00:26:36 / 00:44:00 | 1.000 | 1.000 | 1.000 | -36.89 / -36.89 / -36.89 / -36.89 | 34 / 34 / 34 / 34 |
| next-repro-radar | both_no-offset__other | 0.0000 | 0.0104 | 0.0000 | 00:20:13 / 00:26:42 / 00:47:43 | 1.000 | 1.000 | 0.479 | -36.20 / -36.20 / -36.20 / -35.49 | 64 / 64 / 64 / 31 |
| next-descent-climb | none__other | 0.0955 | 0.0006 | 0.0000 | 00:16:32 / 00:39:04 / 00:58:00 | 0.904 | 0.904 | 0.112 | -37.29 / -37.49 / -37.49 / -36.53 | 12,336,817 / 11,080,469 / 11,080,186 / 1,497,603 |
| next-descent-climb | r600-bto__other | 0.0006 | 0.0006 | 0.0000 | 00:23:23 / 00:41:54 / 00:58:57 | 0.999 | 0.999 | 0.083 | -38.12 / -38.12 / -38.12 / -37.43 | 7,289,576 / 7,283,785 / 7,283,644 / 682,707 |
| next-descent-climb | r600_no-offset__other | 0.0000 | 0.0000 | 0.0000 | 00:21:43 / 00:36:50 / 00:49:02 | 1.000 | 1.000 | 0.072 | -37.83 / -37.83 / -37.83 / -37.12 | 341,483 / 341,471 / 341,470 / 30,715 |
| next-descent-climb | both_startup-offset__fuel-exhaustion | 0.0000 | 0.0000 | 0.0000 | 00:22:41 / 00:34:28 / 00:42:27 | 1.000 | 1.000 | 1.000 | -38.21 / -38.21 / -38.21 / -38.21 | 125 / 125 / 125 / 125 |
| next-descent-climb | both_no-offset__other | 0.0000 | 0.0000 | 0.0000 | 00:20:58 / 00:35:41 / 00:51:08 | 1.000 | 1.000 | 0.355 | -37.45 / -37.45 / -37.45 / -36.78 | 106 / 106 / 106 / 35 |
| next-routes | none__other | 0.1073 | 0.0009 | 0.0000 | 00:16:19 / 00:37:43 / 00:55:48 | 0.893 | 0.893 | 0.093 | -37.31 / -37.55 / -37.55 / -36.75 | 12,325,581 / 10,934,420 / 10,934,055 / 1,254,061 |
| next-routes | r600-bto__other | 0.0009 | 0.0010 | 0.0000 | 00:23:33 / 00:41:11 / 00:57:15 | 0.999 | 0.999 | 0.072 | -38.16 / -38.16 / -38.16 / -37.47 | 7,451,904 / 7,442,336 / 7,442,140 / 604,364 |
| next-routes | r600_no-offset__other | 0.0000 | 0.0000 | 0.0000 | 00:21:41 / 00:35:59 / 00:48:39 | 1.000 | 1.000 | 0.060 | -37.75 / -37.75 / -37.75 / -37.19 | 272,778 / 272,772 / 272,771 / 17,826 |
| next-routes | both_startup-offset__fuel-exhaustion | 0.0000 | 0.0000 | 0.0000 | 00:20:18 / 00:31:02 / 00:44:05 | 1.000 | 1.000 | 1.000 | -37.40 / -37.40 / -37.40 / -37.40 | 46 / 46 / 46 / 46 |
| next-routes | both_no-offset__other | 0.0000 | 0.0000 | 0.0000 | 00:22:01 / 00:34:30 / 00:53:23 | 1.000 | 1.000 | 0.294 | -37.20 / -37.20 / -37.20 / -36.10 | 73 / 73 / 73 / 26 |

All option × cause rows are in `<stratum>-impact-time-shares.json` and `<stratum>-constraints.json`. The constraints files also carry the
reference-289 keys `median_lat_plain_alive_silent` and `ess_plain_alive_silent`.

## Late-tail attribution

The question: why is the held-out share after 01:15:56 smaller than on reference-289? With `+alive` the mixed figure is 0.26 % (Hydroacoustics);
by stratum here it is 0.06-0.30 %, against 1.87 %.

**Answer: the hand-offs, not the descent idle floor.**

1. **The idle floor has no measurable effect.** On the same reference-289 hand-off (seed 1, N = 1, 400,000 descents), turning it off and on
   gives 1.69 % against 1.72 % after 01:15:56 (`late-tail-idle-floor-on-off-reference-289-n1.json`).
2. **The (b) seeds disagree with each other by more than 100x.** In the free stratum the share is 0.945 %, 0.035 %, 0.214 % and 0.007 %
   (seeds 1-4). Reference-289's seeds give 1.75 %, 1.57 %, 1.94 % and 2.23 %.
3. **The cause is the hand-off population, which differs from seed to seed.**
   - Free-stratum parents with any impact after 01:15:56, by seed: 4,913, 243, 1,394 and 62. Reference-289 has 7,436-10,188 in every seed.
   - The effective parents carrying the tail, by seed: 3,417, 162, 854 and 38.
   - The late-flying states (late flame-out) are present in some seeds' hand-offs and nearly absent from others.
   - This is core (b)'s non-convergence in the free stratum (split-half 0.709). It also matches the 5-10 min seed spread of the tail that
     Hydroacoustics observed.
4. **(b)'s fuel state also flies out slightly earlier.** In seed 1, flame-out after 01:00 carries 0.49 % of the alive weight, against 1.15 % on
   reference-289. The q95 flame-out is 00:44, against 00:48 (`late-tail-flameout-timing-seed1.json`).

**Reading for Hydroacoustics:**
- The late tail on (b) is **not estimable seed to seed**. It is a core-convergence property, not a descent-model property.
- Gate checks on it should use per-seed values with that spread stated.
- The reference-289 tail (1.6-2.2 %, stable over seeds) remains the better-estimated figure for the size of the late tail. It carries its own
  labels (uncorrected fuel, single pool).

- End of flight
