# Debris drift production: complete (both ocean models), 10 Oct 2026 ~17:40 UTC

**Status: complete as configured; the GlobCurrent arm carries "GlobCurrent windage not product-relative (audit F1)"
and is NOT for publication or composition at equal weight.** The GLORYS12 arm is unaffected by F1.

| | GLORYS12V1 + ERA5 | Copernicus-GlobCurrent (my-p1d, 0 m) + ERA5 |
|---|---|---|
| Nodes released / scored at 50 km | 367 / 367 | 367 / 367 |
| Trajectories | 36,702,936 | 36,702,936 |
| Chunk wall (12 threads) | 31,479 s | 25,068 s |
| Split-half noise on node mean (SD / robust) | 1.42 / 0.76 ln | 0.68 / 0.48 ln |
| Nodes with a zero-hit ocean realisation | 61 (34.7-40.7 S) | 0 |
| Left-domain fraction | 0.200 | 0.174 |

**Two-model comparison (all 367 nodes; `debris-drift-two-model-nodes.csv`, `...-comparison.json`; figure
`debris-drift-two-model-agreement.png`, artifact 554654c6 v2).** Node correlation -0.08; SD of the difference
3.14 ln units; 293 of 367 nodes agree within 2x the combined split-half noise (3.15). Median of (GlobCurrent -
GLORYS12) by 2-deg band: +3.9 at 40.5 S, +2.7 at 38.5 S, +2.1 at 36.5 S, +1.6 at 34.5 S, +0.5 at 32.5 S, -0.5 at
30.5 S, -1.1 at 28.5 S, -1.3 at 26.5 S, -3.0 at 24.5 S, -6.2 at 22.5 S. Per the audit, the northern deficit is the F1
windage artefact and most of the southern excess is a real product difference.

**For the F1 smoke review (Pete).** On the full set the as-configured pair already meets the audit's first pass
criterion (SD of the difference north of 30 S 2.43, threshold ~3.1) but not the second (north of 25 S GlobCurrent is
4.61 lower on average). On the smoke's own 92 chunk-0 nodes the baseline is SD 3.28 north of 30 S (32 nodes) and a
mean difference of -5.78 north of 25 S (only 9 nodes); +3.56 south of 37 S. So the SD test is weak, and the
northern-band test is the informative one, on few nodes. The smoke review will report both against this baseline.

**Provenance.** Track 289.7 (reference-289 extent, 99.03% band); configs production-glorys12.toml /
production-globcurrent.toml (hypothesis/debris-drift, d4dc2fd code); binary d24060aa8006d3ce; Darwin arm64 macOS
27.2; merged with merge_chunks.py (labels rebuilt from config). Equal-weight sensitivity mixture written for
diagnostics only (`debris-drift-production-mixture-asconfigured`, combine_models.py); the composer marginalises
`ocean-model`.

## COVERAGE (ruling 15:45 -0600, 10 Oct)

The drift term samples two things: **where debris starts** (the source nodes) and **how each object responds** to
wind and current (the object classes). The three sets for each:

**(a) Feasible set.**
- Start points: any point of the end-of-flight impact posterior, in every 00:19 option and every hypothesis family.
- Object response: the physical range of wind fraction and leeway for the nine identified parts. The sources are
  CSIRO's flaperon trials [griffin2017partii, pp. 10, 17] and CSIRO's 1.2 % / 3 % classes [griffin2017partiii, pp. 6, 8].
- Ocean: the true 2014-2016 surface currents. These are represented by two reanalysis products, with a measured
  ocean-error field.

**(b) Model's reach.**
- Start points: 367 nodes at 30 NM, on the grid built from the reference-289 00:19 position map (99.03 % band,
  40.7-22.2 S). The grid cannot represent a start point outside it.
- Object classes:
  - flaperon: 1.2 % fixed, plus leeway N(0.10, 0.03) m/s at U(-30, 0) deg (sourced);
  - low-exposure exterior parts: N(1.2 %, 0.3 %) truncated to 0.5-2 % (PROVISIONAL bound);
  - high-windage interior parts: log-normal, median 2.5 %, sigma 0.35, truncated to 1-5 % (PROVISIONAL bound;
    brackets CSIRO's 3 %).
- Sub-mesoscale diffusivity K: log-uniform 100-1000 m2/s (PROVISIONAL prior).
- Ocean-error length scale L = 100 km is assumed. It waits for ocean transport's GDP-pair answer, with 50 and
  200 km as sensitivities.
- **GlobCurrent windage is not product-relative** (audit F1). This is a reach defect, not an alternative.

**(c) Proposal coverage.**
- Monte Carlo resolution per node, at the 50 km bandwidth:
  - All 367 nodes are resolved on both models.
  - At 25 km, 6 GLORYS12 nodes are unresolved.
  - On GLORYS12, 61 nodes (34.7-40.7 S) have at least one ocean-error realisation with zero hits for a find
    (Mossel Bay). On GlobCurrent, none do.
  - The weakest find is Paindane: median n_eff 2.4 on GLORYS12 and 6.3 on GlobCurrent.
  - Split-half noise is 1.42 log-likelihood units on GLORYS12 and 0.68 on GlobCurrent.
- Impact mass inside the planned nodes, per standard option, on core (b) with `+alive` and fixed P(family):

| 00:19 option | inside planned nodes | off the grid | with extension B | ESS ratio of drift weighting (GLORYS12) |
|---|---|---|---|---|
| 00:19 Held Out | 0.818 | 0.006 | 0.975 | 0.54 |
| 00:19 R600 BTO Only | 0.793 | 0.009 | 0.983 | 0.53 |
| 00:19 R600 BTO + Raw BFO | 0.967 | 0.001 | 0.999 | 0.54 |
| 00:19 Holland H1 | 0.994 | 0.000 | 1.000 | 0.52 (not yet estimable upstream) |
| 00:19 Holland H2 | 0.987 | 0.000 | 1.000 | 0.66 (not yet estimable upstream) |

**Gaps and status.**
1. **Support gap**: 3-21 % of impact mass lies outside the planned nodes, most for 00:19 Held Out and R600 BTO Only.
   The fix is extension B (186 nodes, about 9 h; held for the windage smoke test and Pete). Meanwhile the scored
   fraction is shown beside every number and the unscored mass is excluded, never set to zero.
2. **Off-grid mass** (up to 0.9 %, south of 41.2 S or east of 105.6 E): the grid would need enlarging, which is a
   code change. Declared.
3. **GlobCurrent windage** (audit F1): smoke arm 1 at -0.60 % passes the audit criterion on its 92 nodes; arm 2 is
   running. The fix is a GlobCurrent re-run with product-relative windage, after Pete's review.
4. **Mossel Bay resolution south of 34.7 S on GLORYS12**: zero-hit realisations bias those nodes low and inflate
   the GLORYS12 split-half noise. The proposed fix is targeted extra particles at the 61 nodes (a new run, for Pete).
5. **PROVISIONAL bounds** (low-exposure and high-windage windage ranges, K, L): sensitivities are planned
   (methods draft §8); each is declared in every result's label.
6. **Hypothesis families A1/A2/B**: the drift term is evaluated per start point, so it covers every family whose
   impacts fall inside the nodes. The family split is inherited from end of flight, with the same support caveat.
