# End of flight on reference-289: evidential sweep (00:11 hand-off)

9 October 2026, End of Flight Module.

- **Scale.** FULL SCALE and COMPLETE: 4 seeds of 4. The run started at 14:45 UTC and finished at 16:42 UTC.
- **Provisional physics.** The results are provisional on two PROVISIONAL-OVERNIGHT choices awaiting Pete: dive
  class (b), and the glide calibrated to Boeing's driftdown.

## Impacts (persisted)

- **Paths.** `/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/83c5d472-a2a6-4ff0-9602-ceefbdadb1ad/repo/Claude Science Project Sep 29/engine/runs/eof-289-full-s<k>/bto-bfo/seed-<k>/impacts.npy`, for k = 1–4.
  - Columns are listed in each `run.json` (`impact_columns`, 90 columns). `weight` is the hand-off weight shared
    among children.
  - Score with `loglik:<option>`, plus the section 6 log-on density for the fuel-exhaustion cause. See
    `engine/hypotheses/end-of-flight/smoke/displacement_hist.py`, `option_posteriors`.
- **Size per seed.** 100,000 parents × 8 children × 4 descents gives 3,200,000 rows and 2.3 GB, about 27.5 min
  at 2 threads.
- **Seed 1.** Done at 15:12:52 UTC. sha256 `53cefbcfa4992e75423556cd1a0e96b85e109f44b52a4887b5a4e6c65ca54320`.
- **Seed 2.** Done at 15:40:29 UTC. sha256 `6b14ff9cd978144ff6a8b37550318e754e02216c4080aab454a05371a71bbe85`.
- **Configs**, in core's order: `davey2016`, `no-exhaustion-prior`, `reference-snapshots`,
  `early-families/overnight/reference-289`, then `smoke/snapshot-m0011`, `smoke/terminal` and
  `full/reference-289` (N = 8).
- **Seed 3.** Done at 16:08:49 UTC. sha256 `dad15481fd38eadac1d4516adaa3f44af0539c3e1c857c865403e85860cdca30`.
- **Seed 4.** Done at 16:42:13 UTC. sha256 `10da1612a11d22b7ce7aa0d3e1bba5021f41c6796090947d9095fd82b6bc41d8`.

## Pooled result (equal weight per seed)

The table is built from `sweep-summary-reference-289.json`, written by
`engine/hypotheses/end-of-flight/smoke/sweep_summary.py`.

- **Latitude density.** A weighted 0.1° histogram of impact latitude, Gaussian-smoothed at 0.1°, as in
  `epoch_map.latitude_density`.
- **Split-half.** Computed over every balanced partition of the 4 seeds (3 partitions). It is compared with the
  project's 4-replicate floor of 0.896, which was calibrated on core's 00:19 position density. Applying that floor
  to impact latitude is an analogy, not a separate calibration.

| option × log-on cause | ESS, 4 seeds (min per seed) | median impact lat, lon (°) | seed medians, lat (°) | latitude HDI 50 / 90 / 99% | split-half, 3 partitions: mean [min, max] | converged (min ≥ 0.896) | divergent share |
|---|---|---|---|---|---|---|---|
| `none__other` | 12,358,800 (3,088,414) | -36.78, 90.99 | -36.91 to -36.71 | 38.2° S–35.6° S / 40.8° S–32.2° S / 41.7° S–24.8° S | 0.975 [0.973, 0.977] | yes | 0.50 |
| `none__fuel-exhaustion` | 1,069,176 (257,497) | -36.94, 90.46 | -37.08 to -36.82 | 38.0° S–35.8° S / 40.2° S–33.5° S / 40.4° S–25.8° S | 0.959 [0.957, 0.961] | yes | 0.49 |
| `r600_inflated__other` | 3,055,333 (748,404) | -37.58, 90.71 | -37.67 to -37.49 | 38.7° S–36.8° S / 40.6° S–26.6° S / 41.2° S–24.6° S | 0.969 [0.965, 0.972] | yes | 0.49 |
| `r600_inflated__fuel-exhaustion` | 402,652 (95,035) | -37.48, 90.20 | -37.60 to -37.32 | 38.5° S–36.6° S / 40.2° S–34.7° S / 40.5° S–25.3° S | 0.953 [0.950, 0.958] | yes | 0.50 |
| `r600_no-offset__other` | 197,569 (47,906) | -37.25, 90.53 | -37.33 to -37.15 | 38.4° S–36.5° S / 40.1° S–26.8° S / 40.3° S–25.2° S | 0.950 [0.940, 0.960] | yes | 0.51 |
| `r600_no-offset__fuel-exhaustion` | 59,512 (13,886) | -37.28, 90.26 | -37.37 to -37.11 | 38.3° S–36.4° S / 40.2° S–27.3° S / 40.4° S–25.2° S | 0.938 [0.935, 0.942] | yes | 0.52 |
| `r600_startup-offset__other` | 173,568 (41,688) | -37.20, 90.50 | -37.39 to -37.06 | 38.2° S–36.2° S / 40.2° S–26.5° S / 40.3° S–25.0° S | 0.931 [0.923, 0.936] | yes | 0.57 |
| `r600_startup-offset__fuel-exhaustion` | 67,598 (15,151) | -37.54, 90.11 | -37.93 to -37.31 | 38.7° S–36.5° S / 40.3° S–27.1° S / 40.5° S–24.9° S | 0.904 [0.892, 0.921] | **no** | 0.59 |
| `r1200_inflated__other` | 69,079 (16,895) | -36.16, 90.77 | -36.29 to -36.02 | 37.5° S–35.4° S / 39.2° S–29.0° S / 39.7° S–25.7° S | 0.939 [0.930, 0.947] | yes | 0.83 |
| `r1200_inflated__fuel-exhaustion` | 19,503 (4,604) | -36.52, 90.51 | -36.60 to -36.33 | 37.7° S–35.6° S / 39.6° S–28.1° S / 39.8° S–24.0° S | 0.916 [0.913, 0.923] | yes | 0.85 |
| `r1200_no-offset__other` | 13,514 (3,275) | -36.11, 90.80 | -36.25 to -36.01 | 37.5° S–35.3° S / 38.9° S–26.5° S / 39.6° S–25.9° S | 0.927 [0.922, 0.937] | yes | 0.85 |
| `r1200_no-offset__fuel-exhaustion` | 3,679 (860) | -36.41, 90.50 | -36.50 to -36.28 | 37.7° S–35.6° S / 39.5° S–27.1° S / 39.7° S–26.0° S | 0.898 [0.890, 0.905] | **no** | 0.88 |
| `r1200_startup-offset__other` | 37,827 (9,199) | -36.08, 90.79 | -36.23 to -35.96 | 37.5° S–35.4° S / 38.4° S–32.2° S / 39.1° S–25.7° S | 0.933 [0.924, 0.946] | yes | 0.90 |
| `r1200_startup-offset__fuel-exhaustion` | 10,065 (2,338) | -36.42, 90.46 | -36.57 to -36.24 | 37.7° S–35.6° S / 38.5° S–27.1° S / 39.5° S–25.9° S | 0.899 [0.893, 0.907] | **no** | 0.94 |
| `both_inflated__other` | 4,784 (1,121) | -36.65, 90.96 | -36.72 to -36.59 | 37.8° S–35.7° S / 39.8° S–26.3° S / 40.1° S–24.5° S | 0.902 [0.883, 0.913] | **no** | 0.57 |
| `both_inflated__fuel-exhaustion` | 2,042 (441) | -37.34, 90.49 | -37.47 to -37.17 | 39.1° S–36.8° S / 39.9° S–26.3° S / 40.3° S–24.4° S | 0.849 [0.835, 0.865] | **no** | 0.60 |

## Reading

- **Converged.** 11 of the 16 option × cause rows clear the floor on every partition. These include held-out,
  R600 inflated and no-offset, and R1200 inflated with both causes.
- **Unconverged, quoted as such.**
  - `both/inflated`, both causes; with fuel-exhaustion the mean is 0.849.
  - R1200 no-offset with fuel-exhaustion, R1200 startup-offset with fuel-exhaustion, and R600 startup-offset with
    fuel-exhaustion. For these three the minimum partition is 0.890–0.893.
  - **Direction of the shift from 295.66° to 289.7°.** It is robust for three of these rows: R1200 no-offset
    with fuel-exhaustion, R1200 startup-offset with fuel-exhaustion, and `both/inflated` with the other cause.
    In each, all four seed medians lie north of the 295.66 value.
  - It is **not** robust for the other two:
    - R600 startup-offset with fuel-exhaustion: the seed medians run 37.93–37.31° S against 37.90° S.
    - `both/inflated` with fuel-exhaustion: 37.47–37.17° S against 37.35° S.
  - The 295.66 comparator is seed 1 at smoke scale (`eof-glideB-n16-s1`), so it carries its own seed noise.
  - **Magnitudes are not estimates for any of the five.**
  - ESS is not the limit: it clears the pooled 1,000 target everywhere, the minimum being 2,042. The limit is
    seed-to-seed spread in the hand-off itself.
- **Every option except `both/inflated` with fuel-exhaustion sits north of its 295.66° smoke counterpart.** That row is at 37.34° S against 37.35° S.
  - The held-out median is 36.78° S, against 37.32° S at 295.66 (seed 1, smoke).
  - R600 inflated with fuel-exhaustion is at 37.48° S.
  - R1200 inflated with fuel-exhaustion is at 36.52° S.
- **The 99% bounds run north to about 24–26° S.** That is the northern tail core reports at 00:19 (95% bound
  29.8° S), carried through to impact, at the edge of the region. It is not a plausible terminus in its own
  right, and its mass should be quoted directly rather than read off the contour.
- **Figures** (project convention: greyscale HPD bands at 50/90/99%):
  - `impact-map-reference-289-greyscale.pdf`, in latitude and longitude with the 6th and 7th arcs.
  - `displacement-reference-289-greyscale.pdf`, displacement from the own 00:19:37 position.
- **For Pléiades.** `results/eof-displacement-oct09/displacement-reference-289-dive-on-160.{npz,json}` holds
  the 4 seeds pooled at ±160 NM, dive class on (the current default).
  - A dive-off counterpart on reference-289 was **not run**. It would be another 2 h; say if it is wanted.
  - Under held-out with the other cause, 52.8% of the weight has a 00:19:37 position. The rest was down before
    the burst, and the JSON carries that share.

**Update 9 Oct 19:50 UTC.** The reference-289 summary/histogram files here were regenerated with all 24 option x cause arms (both/no-offset and both/startup-offset had been dropped by a hard-coded OPTIONS list; r600-bto and both-bto added, derived from BTO residual columns). 15 of 24 converge. Evidence per option and Holland H1:H2: results/eof-two-burst-oct09/README.md.
