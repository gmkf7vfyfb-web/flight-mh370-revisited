# Debris drift: does the production node set cover end of flight's impacts on core (b)?

Ocean Drift Module, 10 Oct 2026 ~08:40 UTC. **PRELIMINARY (pre-READY)**: computed on the 16 seed files in
`mh370-exchange/end-of-flight/next-run/<stratum>/seed-k/` before end of flight wrote `READY`; recomputed
when it does. A support check only: no drift likelihood values are used.

**Inputs and provenance.**
- Impacts: end of flight sweep on core (b) (`a5839adc`, deskstar, track 289.7, internal-v1 fuel, two-tank
  bookkeeping only, core split-half NOT converged); end-of-flight code_revision 3c6319f (seed run.json).
- Posterior per option: end of flight's own recipe (`displacement_hist.py::option_posteriors`, read-only)
  with the `+alive` constraint (end of flight's provisional reference, PROVISIONAL-OVERNIGHT, 04:05 UTC).
- Strata mixed by core's P(family): free 0.69, Davey dynamics + radar 0.15, descent-climb 0.14,
  routes 0.01 (not converged); seeds 1-4 equal within stratum.
- Planned support: the 367 production nodes (count run `debris-drift-production-count-289-30-false`,
  identical to the production chunks' interleave), 30 NM grid from the reference-289 extent map.
- "Covered" = the bilinear cell's four corners are all planned nodes, exactly as `interpolate.rs` needs
  (never extrapolated). Platform Darwin arm64 macOS 27.2.

**Result.** Impact mass inside the planned support is 79-99.8% by option (table:
`debris-drift-support-core-b.csv`). The worst three are the no-00:19-burst-likelihood `other`-cause variants:
held out (`none__other+alive`) 81.8%, `r600-bto__other` 79.3%, `both-bto__other` 81.2%. Fuel-exhaustion
variants are 92-99%. The outside mass lies mostly within 15-30 NM (median) of the band edge, about
three-quarters of it east of the nearest node, out to ~100-240 NM at the 90-99th percentile; 0-0.9% is off
the grid itself (south of 41.2 S or east of 105.6 E).

**Extension options (not run; needs Pete):**

| Option | Extra nodes | Est. time, both models, 12 threads | Coverage after |
|---|---|---|---|
| A | 412 | ~20 h | >= 99.0% every option |
| B (recommended) | 186 | ~9 h | >= 99.3% all but the three `other` no-burst variants (97.5-98.5%) |
| C | 0 | 0 | as now; unscored mass excluded and disclosed per option |

Node lists: `hypotheses/debris-drift/data/coverage-extension-core-b-alive.csv` (in_option_A, in_option_B);
configs `extension-glorys12.toml` / `extension-globcurrent.toml` (option A list, marked NOT RUN), using the
new opt-in `node_subset_outside_extent` (9977f1f, default off, unit-tested). Same grid, so values merge
cell-for-cell with production. Off-grid mass (<= 0.9%) would need the grid enlarged in whole cells (code
change, not tonight).

Footnote: impacts core (b) via end of flight sweep (pre-READY), track 289.7, base config davey2016 with
internal-v1 fuel, `+alive`, all 00:19 options shown in the CSV, P(family) mixture (not converged), 16 seeds;
drift support = production plan (GLORYS12 / GlobCurrent, 30 NM, 367 nodes); timing estimates from chunks 0-2.
