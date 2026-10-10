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

**Facts after 00:19 (architecture ruling ~19:10 UTC, part B).** The intended core constraint is (b): the aircraft
was transmitting at 00:19:37 **and** was not powered at 01:15:56. End of flight has not yet exposed (b) as a variant,
so this note uses **(a), transmitting at 00:19:37 only** (`+alive`), as the ruling directs. (c) (`+silent`, which
adds "no second APU log-on" under `other`) is shown beside it as a declared, model-dependent variant.

**Flight families (ruling part C).** The strata here are mixed with P(family) **held fixed** across options. The
ruling makes the re-weighted mixture, P0 × Z_core × Ẑ_00:19(family, option), the target. That needs end of flight's
Ẑ_00:19, which has not been published. When it is, both mixtures will be shown, labelled. Under 00:19 Held Out the
two are identical.

## Predicted SOFAR arrivals, core (b) mixture, transmitting at 00:19:37 (UTC, 8 Mar 2014)

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

| receiver | core (b), (a) transmitting at 00:19:37 | core (b), (c) `+silent` | reference-289, (a) |
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

## Update (10 Oct, ~22:30 UTC): variant (b) `unpowered`, the re-weighted families, and the validation gate

**Run:** `search_windows_mixture.py` with amendment 1 (`929acc0`), outputs `results-data/search_windows/next-run-b-v2/` (`3731d09d`).
- **Inputs:** EoF `displacement_hist.py` at `43262c3`; family factors from `family-evidence-next-run-b.json`.
- **Validation gate: PASSED** against end of flight's next-run impact-time shares. That is 24 of 24 arms in each of the
  four strata, with worst Δshare 1.4e-17 and worst Δq 1.0 s. The label "validation gate not run" is withdrawn.
- **Facts after 00:19, now (b), as ruled:** transmitting at 00:19:37 and not powered at 01:15:56. It changes the
  quantiles by ≤ 10 s. For example, 00:19 Held Out at H01W: the 99.5 % arrival is 01:34:52, against 01:35:02 under (a).
- **Families re-weighted by the 00:19 evidence** (ruling C), shown beside the fixed weights. Changes are ≤ 8 s. The
  largest is 00:19 R600 BTO + Raw BFO, where the H01W median goes 00:59:04 → 00:59:12 and the ESS 449 k → 510 k.
- **Request windows for options 1–3 are unchanged** under (b) and under both weightings: H01W 00:25–02:05 and
  H08S/H08N 00:50–02:30 UTC. Under `+silent`, the declared variant (c), they are 00:25–01:50 and 00:50–02:15.
- The end edges are still unconverged for 00:19 Held Out and 00:19 R600 BTO Only.

- Hydroacoustic Module


## COVERAGE

See `hydroacoustics-coverage.md` for the three sets, ESS per option and family, the gaps and the parameter bounds. Specific to this note: Windows are the union over the arms with ESS ≥ 1,000 (options 1-3). Holland H1/H2 (G1) are NOT estimable; their provisional impact ranges end by 02:25 at H08S, inside the request windows. Families are fixed and re-weighted as stated above.
