# Debris drift: does the production node set cover end of flight's impacts on core (b)?

Ocean Drift Module, 10 Oct 2026 ~08:40 UTC; **confirmed on READY ~09:20 UTC** (READY 08:36:15Z, EoF 3c6319f,
binary bcb6b252, run by an architecture stand-in; the 16 seed files in
`mh370-exchange/end-of-flight/next-run/<stratum>/seed-k/`). The READY recomputation is identical to the
pre-READY one (max difference 0.0000). The CSV now carries all 48 rows: every option x cause, plain and
`+alive`. A support check only: no drift likelihood values are used.

**Inputs and provenance.**
- Impacts: end of flight sweep on core (b) (`a5839adc`, deskstar, track 289.7, internal-v1 fuel, two-tank
  bookkeeping only, core split-half NOT converged); end-of-flight code_revision 3c6319f (seed run.json).
- Posterior per option: end of flight's own recipe (`displacement_hist.py::option_posteriors`, read-only),
  plain and with the `+alive` constraint (end of flight's provisional reference, PROVISIONAL-OVERNIGHT,
  04:05 UTC). Plain held out `none__other`: 83.6% inside, 97.8% with B, 99.2% with A.
- Strata mixed by core's P(family): free 0.69, Davey dynamics + radar 0.15, descent-climb 0.14,
  routes 0.01 (not converged); seeds 1-4 equal within stratum.
- Planned support: the 367 production nodes (count run `debris-drift-production-count-289-30-false`,
  identical to the production chunks' interleave), 30 NM grid from the reference-289 extent map.
- "Covered" = the bilinear cell's four corners are all planned nodes, exactly as `interpolate.rs` needs
  (never extrapolated). Platform Darwin arm64 macOS 27.2.

**Result.** Impact mass inside the planned support is 79-99.8% by option (table:
`debris-drift-support-core-b.csv`). The worst three are the no-00:19-burst-likelihood `other`-cause variants:
held out (`none__other+alive`) 81.8%, `r600-bto__other` 79.3%, `both-bto__other` 81.2%. Fuel-exhaustion
variants are 92-99%. Distance of the outside mass to the nearest planned node (free stratum, seed 1, `+alive`; 50/90/99th percentiles): held out `none__other` 29/109/239 NM; `r600_inflated__other` 19/81/204 NM; `r600_no-offset__other` 14/21/53 NM. About 72-77% of it lies east of the nearest node. 0-0.9% of the mixture mass is off the grid itself (south of 41.2 S or east of 105.6 E).

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

Footnote: impacts core (b) via end of flight sweep (READY 08:36Z), track 289.7, base config davey2016 with
internal-v1 fuel, plain and `+alive`, all 00:19 options shown in the CSV, P(family) mixture (not converged), 16 seeds;
drift support = production plan (GLORYS12 / GlobCurrent, 30 NM, 367 nodes); timing estimates from chunks 0-2.
