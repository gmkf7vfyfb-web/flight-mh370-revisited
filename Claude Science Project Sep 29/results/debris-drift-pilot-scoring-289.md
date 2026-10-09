# The drift pilot surface scored on end of flight's reference-289 impacts (seeds 1-4)

Ocean drift module, 9 October 2026, ~15:40 UTC, for the architecture entry of ~14:45 UTC. **This is an
interface diagnostic and never evidence.** The surface is the PROVISIONAL pilot surface
(`results/debris-drift-pilot.md`). It covers 40.7-31.2°S on the 295.66° extent, at 10⁴ particles per
node. As the pilot already reported, none of its nodes resolve at the primary 50 km bandwidth.

**Inputs:**
- end of flight's `eof-289-full-s<k>/bto-bfo/seed-<k>/impacts.npy`, k = 1-4 (3.2 M rows each; seed-1 sha256 `53cefbcf…`, the others in end of flight's README);
- weights per option × log-on cause from end of flight's own `option_posteriors`, imported read-only;
- the merged pilot `nodes.csv`.

**Scorer:** `engine/hypotheses/debris-drift/prepare/pilot/score_impacts.py`.
- It reproduces `interpolate.rs` exactly: bilinear in likelihood, land renormalised out, and the first
  positive-weight unresolved or not-computed corner deciding the point, with no extrapolation.
- Checked on 20,000 random points against the module's scalar formula: identical classification and
  zero value difference.
- Run time is 15 s per seed; all four seeds were scored at 16:46 UTC.

Share of impact-posterior mass by flag, pooled over seeds 1-4 with equal weight per seed (scored /
outside support / Monte Carlo unresolved). The per-seed values are in
`results/debris-drift-pilot-scoring-289.json`. The seed-1 table this replaces is kept as
`debris-drift-pilot-scoring-289-seed1.json`.

| option × log-on cause | impact median lat, seeds 1-4 (°) | 50 km (primary) | 100 km scored | 200 km scored |
|---|---|---|---|---|
| `none__other` | -36.91 to -36.71 | 0.000 / 0.202 / 0.798 | 0.012 | 0.070 |
| `none__fuel-exhaustion` | -37.08 to -36.82 | 0.000 / 0.094 / 0.906 | 0.013 | 0.062 |
| `r600_inflated__other` | -37.67 to -37.49 | 0.000 / 0.141 / 0.859 | 0.006 | 0.034 |
| `r600_inflated__fuel-exhaustion` | -37.60 to -37.32 | 0.000 / 0.076 / 0.924 | 0.007 | 0.039 |
| `r600_no-offset__other` | -37.33 to -37.15 | 0.000 / 0.095 / 0.905 | 0.009 | 0.048 |
| `r600_no-offset__fuel-exhaustion` | -37.37 to -37.11 | 0.000 / 0.085 / 0.915 | 0.009 | 0.047 |
| `r600_startup-offset__other` | -37.39 to -37.06 | 0.000 / 0.102 / 0.898 | 0.012 | 0.061 |
| `r600_startup-offset__fuel-exhaustion` | -37.93 to -37.31 | 0.000 / 0.094 / 0.906 | 0.008 | 0.041 |
| `r1200_inflated__other` | -36.29 to -36.02 | 0.000 / 0.097 / 0.903 | 0.028 | 0.117 |
| `r1200_inflated__fuel-exhaustion` | -36.60 to -36.33 | 0.000 / 0.101 / 0.899 | 0.020 | 0.090 |
| `r1200_no-offset__other` | -36.25 to -36.01 | 0.000 / 0.094 / 0.906 | 0.028 | 0.119 |
| `r1200_no-offset__fuel-exhaustion` | -36.50 to -36.28 | 0.000 / 0.099 / 0.901 | 0.021 | 0.096 |
| `r1200_startup-offset__other` | -36.23 to -35.96 | 0.000 / 0.089 / 0.911 | 0.030 | 0.122 |
| `r1200_startup-offset__fuel-exhaustion` | -36.57 to -36.24 | 0.000 / 0.086 / 0.914 | 0.023 | 0.099 |
| `both_inflated__other` | -36.72 to -36.59 | 0.000 / 0.104 / 0.896 | 0.024 | 0.114 |
| `both_inflated__fuel-exhaustion` | -37.47 to -37.17 | 0.000 / 0.095 / 0.905 | 0.010 | 0.074 |

**Reading:**
- **At 50 km the pilot scores none of the impact mass** (maximum over options and seeds: 0.000). Between 5.1% and 21.1% falls outside the
  pilot's support, north of 31.2°S or outside the band. The rest is Monte Carlo unresolved. This is what the
  pilot predicts, and the interface reports it with the right flags rather than as numbers.
- At 200 km, 2.4%-14.0% is scored (range over options and seeds). That is too little for any reweighting to mean anything, so none is
  quoted. The per-option "after" medians in the JSON are interface checks only.
- **The scorer is ready for the production surface.** Production uses reference-289's extent, 367
  nodes over 40.7-22.2°S, so the support gap closes. On the diagnostic nodes it resolves 81% at 50 km
  (`results/debris-drift-production-sizing.md`).

- Ocean drift
