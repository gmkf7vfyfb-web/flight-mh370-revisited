# The drift pilot surface scored on end of flight's reference-289 impacts (seed 1)

Ocean drift module, 9 October 2026, ~15:40 UTC, for the architecture entry of ~14:45 UTC. **This is an
interface diagnostic and never evidence.** The surface is the PROVISIONAL pilot surface
(`results/debris-drift-pilot.md`). It covers 40.7-31.2°S on the 295.66° extent, at 10⁴ particles per
node. As the pilot already reported, none of its nodes resolve at the primary 50 km bandwidth.

**Inputs:**
- end of flight's `eof-289-full-s1/bto-bfo/seed-1/impacts.npy` (sha256 `53cefbcf…`, 3,200,000 rows);
- weights per option × log-on cause from end of flight's own `option_posteriors`, imported read-only;
- the merged pilot `nodes.csv`.

**Scorer:** `engine/hypotheses/debris-drift/prepare/pilot/score_impacts.py`.
- It reproduces `interpolate.rs` exactly: bilinear in likelihood, land renormalised out, and the first
  positive-weight unresolved or not-computed corner deciding the point, with no extrapolation.
- Checked on 20,000 random points against the module's scalar formula: identical classification and
  zero value difference.
- Run time is 15 s per seed.

Share of impact-posterior mass by flag (scored / outside support / Monte Carlo unresolved):

| option × log-on cause | impact median lat (°) | 50 km (primary) | 100 km scored | 200 km scored |
|---|---|---|---|---|
| `none__other` | -36.71 | 0.000 / 0.204 / 0.796 | 0.012 | 0.070 |
| `none__fuel-exhaustion` | -36.82 | 0.000 / 0.100 / 0.900 | 0.014 | 0.065 |
| `r600_inflated__other` | -37.49 | 0.000 / 0.146 / 0.854 | 0.006 | 0.033 |
| `r600_inflated__fuel-exhaustion` | -37.32 | 0.000 / 0.085 / 0.915 | 0.008 | 0.043 |
| `r600_no-offset__other` | -37.15 | 0.000 / 0.101 / 0.899 | 0.009 | 0.048 |
| `r600_no-offset__fuel-exhaustion` | -37.11 | 0.000 / 0.093 / 0.907 | 0.009 | 0.052 |
| `r600_startup-offset__other` | -37.06 | 0.000 / 0.108 / 0.892 | 0.012 | 0.064 |
| `r600_startup-offset__fuel-exhaustion` | -37.31 | 0.000 / 0.108 / 0.892 | 0.009 | 0.047 |
| `r1200_inflated__other` | -36.02 | 0.000 / 0.103 / 0.897 | 0.027 | 0.118 |
| `r1200_inflated__fuel-exhaustion` | -36.33 | 0.000 / 0.116 / 0.884 | 0.019 | 0.094 |
| `r1200_no-offset__other` | -36.01 | 0.000 / 0.098 / 0.902 | 0.026 | 0.118 |
| `r1200_no-offset__fuel-exhaustion` | -36.28 | 0.000 / 0.109 / 0.891 | 0.020 | 0.097 |
| `r1200_startup-offset__other` | -35.96 | 0.000 / 0.096 / 0.904 | 0.030 | 0.120 |
| `r1200_startup-offset__fuel-exhaustion` | -36.24 | 0.000 / 0.093 / 0.907 | 0.024 | 0.098 |
| `both_inflated__other` | -36.64 | 0.000 / 0.102 / 0.898 | 0.022 | 0.110 |
| `both_inflated__fuel-exhaustion` | -37.26 | 0.000 / 0.107 / 0.893 | 0.007 | 0.096 |

**Reading:**
- **At 50 km the pilot scores none of the impact mass.** Between 8.5% and 20% falls outside the pilot's
  support, north of 31.2°S or outside the band. The rest is Monte Carlo unresolved. This is what the
  pilot predicts, and the interface reports it with the right flags rather than as numbers.
- At 200 km, 3-12% is scored. That is too little for any reweighting to mean anything, so none is
  quoted. The per-option "after" medians in the JSON are interface checks only.
- **The scorer is ready for the production surface.** Production uses reference-289's extent, 367
  nodes over 40.7-22.2°S, so the support gap closes. On the diagnostic nodes it resolves 81% at 50 km
  (`results/debris-drift-production-sizing.md`).

Seeds 2-4 (end of flight, about 16:35 UTC) will be added the same way.

- Ocean drift
