# Next large run (b), 10 Oct 2026: the updated model with every fix, two tanks as bookkeeping

**Labels: PROVISIONAL-OVERNIGHT (not yet reviewed by Pete); platform x86_64-linux (deskstar); prior track
289.7; split-half NOT converged in any stratum.** One-engine flight before 00:11 is not modelled here; the
companion run (a) models it.

Stack: `config/sensitivity/next-run/README.md` (Inmarsat satellite states; request-17 sampler; internal-v1
fuel with temperature term, kappa N(1.0004, 0.0196), 43,800 - kappa x 7,228 kg, weight-dependent ceiling,
hard reject, two tanks; radar scored inside the likelihood). Four strata x seeds 1-4 x 3.5M particles per
seed, 100,000 hand-off rows at m2241 and m0011. Binaries `45650e2` (Davey dynamics, routes) and `e65b0e7`
(free and descent-climb, relaunched after the four-lane layout was OOM-killed in seed 4; `e65b0e7` adds only
config-gated code that is off here). Outputs: `/Users/pete/Downloads/mh370-exchange/core/next-run/` (READY
written 05:29 UTC). Tables: `results/next-run-b/`.

| Stratum | P(family) | 00:19 median | seed medians | 99% HDI | log Z by seed | split-half mean (range) | weight with right engine dry before 00:11 |
|---|---|---|---|---|---|---|---|
| Davey dynamics + radar | 0.15 | -36.43 | -36.21 -36.42 -36.59 -36.49 | -38.90 .. -24.90 | -137.24 -137.24 -137.20 -137.33 | 0.878 (0.864-0.894) | 29 % |
| free | **0.69** | -37.24 | -36.61 -37.42 -36.63 -37.28 | -38.85 .. -25.10 | -136.45 -135.90 -136.36 -134.98 | 0.709 (0.640-0.751) | 26 % |
| routes | 0.01 | -37.38 | -37.30 -37.29 -37.30 -37.50 | -38.10 .. -25.40 | -139.82 -139.89 -139.82 -139.05 | 0.812 (0.798-0.823) | 37 % |
| descent-climb | 0.14 | -37.31 | -37.34 -37.32 -37.29 -37.36 | -38.90 .. -25.55 | -137.41 -137.64 -137.00 -137.48 | 0.785 (0.750-0.822) | 22 % |
| **mixture** | | **-37.15** (00:11: -36.23) | | | | | |

Split-half floor at four seeds is 0.896. P(family) is equal prior odds on log of the mean evidence over
seeds. The 99% HDIs run far north because of the detached northern mode at the edge of the region, not a
plausible terminus.

**Two-tank diagnostic (C-7(b)).** In every stratum and seed the right engine runs dry first; 22-37 % of the
weight has it dry before 00:11, median about 4 min on one engine before 00:11; no weight has both dry before
00:11 (hard rejection). By autopilot mode the share is 8-41 % (`two-tank-diagnostic.csv`). Because (b) still
flies those paths at twin-engine speed and level, this share is the case for (a).

**Against the 9 Oct family run** (uncorrected fuel, defect sampler, STK ephemeris): P(family) is almost
unchanged (free 0.63 -> 0.69); the mixture median moved south, -37.00 -> -37.15; free moved -36.85 -> -37.24.

**Davey-only baseline** (overnight item 3, run `davey-inmarsat-baseline`, davey2016-inmarsat, seeds 1-4,
7M per seed, binary `632af0b`): 00:19 median -37.95, split-half 0.939 (0.930-0.951) **converged**, overlap
with Davey Fig. 10.3 0.750, shoulder 34.5-36.5 S 0.074 (0.31 of Davey's 0.2406), log Z -97.13.
