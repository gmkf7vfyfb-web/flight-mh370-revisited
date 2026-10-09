# End of flight on reference-289: evidential sweep (00:11 hand-off)

9 October 2026, End of Flight Module. **FULL SCALE, IN PROGRESS. Seed 1 of 4 so far.** The physics is provisional
on two PROVISIONAL-OVERNIGHT choices awaiting Pete: dive class (b), and the glide calibrated to Boeing's
driftdown.

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

## Seed 1 summary, against the 295.66° smoke run with the same physics

The comparison run is `eof-glideB-n16-s1`: 20,000 parents, N = 16.

| option × log-on cause | ESS seed 1 (100k × 8) | median impact lat, lon (°) | 295.66 smoke median lat, lon (°) | divergent share | displacement from 00:19:37, 50/90% (NM) |
|---|---|---|---|---|---|
| `none__other` | 3,090,011 | -36.71, 91.05 | -37.32, 89.52 | 0.50 | 48/117 |
| `none__fuel-exhaustion` | 257,497 | -36.82, 90.65 | -37.41, 89.47 | 0.49 | 44/119 |
| `r600_inflated__other` | 759,248 | -37.49, 90.83 | -38.24, 89.32 | 0.49 | 61/122 |
| `r600_inflated__fuel-exhaustion` | 95,035 | -37.32, 90.46 | -37.99, 89.39 | 0.50 | 50/120 |
| `r600_no-offset__other` | 47,906 | -37.15, 90.69 | -37.87, 89.33 | 0.51 | 45/104 |
| `r600_no-offset__fuel-exhaustion` | 13,886 | -37.11, 90.48 | -37.70, 89.45 | 0.52 | 41/113 |
| `r600_startup-offset__other` | 41,797 | -37.06, 90.72 | -37.63, 89.30 | 0.57 | 37/110 |
| `r600_startup-offset__fuel-exhaustion` | 15,151 | -37.31, 90.57 | -37.90, 89.48 | 0.59 | 48/119 |
| `r1200_inflated__other` | 16,895 | -36.02, 90.87 | -37.03, 89.44 | 0.83 | 2/61 |
| `r1200_inflated__fuel-exhaustion` | 4,668 | -36.33, 90.68 | -37.07, 89.57 | 0.84 | 3/94 |
| `r1200_no-offset__other` | 3,275 | -36.01, 90.84 | -37.02, 89.46 | 0.84 | 2/48 |
| `r1200_no-offset__fuel-exhaustion` | 894 | -36.28, 90.52 | -37.09, 89.54 | 0.86 | 2/87 |
| `r1200_startup-offset__other` | 9,199 | -35.96, 90.90 | -36.95, 89.44 | 0.91 | 2/10 |
| `r1200_startup-offset__fuel-exhaustion` | 2,338 | -36.24, 90.67 | -37.02, 89.58 | 0.95 | 2/6 |
| `both_inflated__other` | 1,121 | -36.64, 90.86 | -37.24, 89.52 | 0.57 | 11/100 |
| `both_inflated__fuel-exhaustion` | 441 | -37.26, 90.66 | -37.35, 89.52 | 0.62 | 59/103 |

## Reading (one seed; the pooled four-seed table replaces this)

- **Every option moves north and east with the 289.7° prior**, as core's 00:19 median does (37.27° S → 36.42° S).
  - Held-out, R600 and R1200 move about 0.6–1.0° north and 1.1–1.5° east.
  - R1200's median is about 36.0–36.3° S.
  - `both/inflated` moves least: 0.1–0.6°.
- **ESS on seed 1 already exceeds the per-seed share of the E2 target** (125 of the pooled 1,000) for every
  option. The smallest is `both/inflated` with fuel-exhaustion, at 441.
- **The dive-class posterior share is unchanged in character.** It sits at the prior (0.5) for held-out and R600,
  and at 0.83–0.95 for R1200.
