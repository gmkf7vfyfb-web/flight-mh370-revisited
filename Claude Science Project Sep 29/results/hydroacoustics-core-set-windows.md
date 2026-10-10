# Hydroacoustics: request windows for the standard 00:19 option set (plain names) - PROVISIONAL-OVERNIGHT

**Status:** This note relabels and re-unions existing per-arm results under architecture's ruling (~16:30 UTC,
10 Oct) on the standard 00:19 options. No weights or quantiles are recomputed.
**Script:** `prepare/core_set_windows.py` (`820f48d`, branch `hypothesis/hydroacoustics`).
**Outputs:** `results-data/search_windows/core_set/{next-run-b-mixture,reference-289}/`.
**Inputs:**
- core (b): the stand-in mixture `results/hydroacoustics-next-run-b-standin/mixture/windows_by_arm.csv`, adopted by
  the module at `2152191`;
- reference-289: `438c9e9`.
**Labels (core (b)):** core (b) split-half NOT converged; two-tank bookkeeping only; P(family) held fixed (0.6948 /
0.1527 / 0.1376 / 0.0149); validation gate not run (EoF's next-run shares not yet available); uncorrected fuel;
provisional sampler; PROVISIONAL-OVERNIGHT. Prior track 289.7° ± 1.0°.

## Predicted SOFAR arrivals, core (b) mixture, airborne at 00:19:37 (UTC, 8 Mar 2014)

| # | option | ESS | H01W 0.5 / 50 / 99.5 % | H08S 0.5 / 50 / 99.5 % |
|---|---|---|---|---|
| 1 | 00:19 Held Out | 21.0 M | 00:41 / 01:04 / 01:35 † | 01:01 / 01:22 / 01:57 † |
| 2 | 00:19 R600 BTO Only | 13.0 M | 00:41 / 01:06 / 01:35 † | 01:02 / 01:24 / 01:58 † |
| 3 | 00:19 R600 BTO + Raw BFO | 449 k | 00:39 / 00:59 / 01:18 | 01:02 / 01:17 / 01:36 |
| 4 | 00:19 Holland H1 | 86 | not yet estimable - targeted sampler in progress | |
| 5 | 00:19 Holland H2 | 124 | not yet estimable - targeted sampler in progress | |

† The late tail is unconverged: the replicate spread at the 99.5 % quantile exceeds 5 min.

Options 1–3 use the log-on cause with no lag term, as the ruling sets. Per-receiver rows for every option, including
H1 and H2 for orientation, are in `core_windows_by_option.csv`.

## Request windows: the union of options 1–3 (SOFAR, UTC)

| receiver | core (b), +alive | core (b), +silent | reference-289, +alive |
|---|---|---|---|
| H01W | 00:25–02:05 | 00:25–01:50 | 00:25–02:20 |
| H08S | 00:50–02:30 | 00:50–02:15 | 00:50–02:45 |
| H08N | 00:50–02:30 | 00:50–02:15 | 00:50–02:50 |
| IMOS 3315, 3376 (Perth Canyon) | 00:25–02:05 | 00:25–01:55 | 00:25–02:20 |
| IMOS 3250 (Scott Reef) | 00:40–02:25 | 00:35–02:10 | 00:35–02:40 |
| IMOS 3274, 3275 (Portland) | 00:55–02:30 | 00:55–02:20 | 00:55–02:45 |

- The AGW allowance does not move these windows at the IMS stations.
- **The raw IMS request is unchanged** (H01W 00:25–02:20, H08S/H08N 00:45–02:50). It covers the core set on both
  impact sets, and also H1 and H2's provisional ranges, which end by 02:25 at H08S.
- **End edges are unconverged** in options 1 and 2 under `+alive`.
- Against the earlier 20-arm envelope, the core set narrows only the H08S start (00:45 → 00:50) and the Scott Reef
  start. The optional arms are no longer reported by default; they remain in the per-arm tables.

- Hydroacoustic Module, 10 Oct 2026
