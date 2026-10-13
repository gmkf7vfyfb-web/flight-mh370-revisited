# Next large run (a), 10 Oct 2026: C-7(a) one-engine dynamics, compared with (b)

**Labels: PROVISIONAL-OVERNIGHT (not yet reviewed by Pete); platform x86_64-linux (deskstar); prior track
289.7; split-half NOT converged except routes; one-engine live-engine flow from internal-v1 `grid_inop` AS
DELIVERED, which is 2x its source tables (`results/c7-options-smoke.md`), so every one-engine phase here is
about half its true length.**

(a) = (b) plus `fuel-fixes/s7-single-engine.toml`: after the first flame-out a constant drift-down drawn per path
from U(300, 1000) ft/min to the one-engine ceiling for the weight (derived by core from `grid_inop`; the fuel
session verified it to within ~1,000 ft), at the LRC INOP Mach; lateral mode unchanged. Binary `e65b0e7`, four
strata x seeds 1-4 x 3.5M per seed, 100,000 hand-off rows at m2241 and m0011, job `85a77262`. **Seed 4 of Davey
dynamics and descent-climb failed on a full deskstar scratch disk** and was re-run with the same binary,
checkout and configs (`seeds = [4]`, job `ae844ba2`); seeds 1-3 of those strata are bit-for-bit the first
attempt's files, and their run.json replicates were rebuilt from each seed's diagnostics.json.
Outputs: `/Users/pete/Downloads/mh370-exchange/core/next-run-a/` (READY written). Tables: `results/next-run-a/`.

| Stratum | P(family) (b) -> (a) | log mean Z (b) -> (a) | 00:19 median (b) -> (a) | 00:11 median (b) -> (a) | split-half mean (min) (b) -> (a) | first flame-out before 00:11 (b) -> (a) | median one-engine min (b) -> (a) |
|---|---|---|---|---|---|---|---|
| Davey dynamics + radar | 0.15 -> 0.25 | -137.25 -> -137.21 | -36.39 -> -36.28 | -35.55 -> -35.56 | 0.878 (0.866) -> 0.867 (0.841) | 0.29 -> 0.24 | 3.4 -> 3.4 |
| free | 0.69 -> 0.55 | -135.74 -> -136.42 | -37.13 -> -36.72 | -36.24 -> -35.68 | 0.709 (0.640) -> 0.829 (0.805) | 0.26 -> 0.18 | 3.1 -> 3.2 |
| routes | 0.01 -> 0.02 | -139.58 -> -139.64 | -37.32 -> -37.21 | -36.36 -> -36.36 | 0.811 (0.797) -> 0.946 (0.940) | 0.37 -> 0.28 | 3.8 -> 3.4 |
| descent-climb | 0.14 -> 0.18 | -137.36 -> -137.56 | -37.29 -> -37.18 | -36.38 -> -36.27 | 0.785 (0.749) -> 0.801 (0.767) | 0.22 -> 0.15 | 3.6 -> 2.8 |
| **mixture** | | | **-37.15 -> -36.89** | -36.23 -> -35.96 | | | |

Split-half at four seeds, all three balanced partitions, floor 0.896; from 0.05-deg histograms smoothed 0.1 deg.

**Reading.**
1. Modelling one-engine flight moves the answer north: mixture 00:19 median -37.15 -> -36.89,
   free -37.13 -> -36.72, the other strata by 0.1 deg. The shift is about half the free stratum's
   seed-to-seed spread under (b), so its direction is credible and its size is not yet.
2. The data disfavour flying on one engine before 00:11: the weight whose first flame-out precedes 00:11 falls
   in every stratum (by 0.06-0.09). The 00:11 BFO and BTO see the drift-down and the lower speed.
3. P(family) shifts from free to the others (free 0.69 -> 0.55; Davey dynamics 0.15 -> 0.25) because free's log mean
   Z falls by 0.68 nats while the others move by < 0.21. In (b) one free seed sat at -134.98, 1.5 nats above
   the rest; in (a) the four free seeds agree to 0.3 nats. Treat P(family) as unconverged in both.
4. Convergence improves under (a): free 0.709 -> 0.829, routes 0.811 -> 0.946 (converged), descent-climb
   0.785 -> 0.801; Davey dynamics 0.878 -> 0.867.
5. Not separable here: the doubled live-engine flow. At smoke scale the correction doubles the one-engine time
   and raises the weight with first flame-out before 00:11 to ~0.5, so (a)'s effect on the 00:19 PDF is likely
   to be larger once the flow is corrected.

Report caveat: the summary CSV's 00:19 p95 for routes (a) reads -7.5; the per-seed weighted p95s are -31.9 to
-35.0 and < 0.03 % of weight lies north of -20 deg, so that cell is a report artefact (core to check).
