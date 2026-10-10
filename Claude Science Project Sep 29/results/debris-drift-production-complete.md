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
