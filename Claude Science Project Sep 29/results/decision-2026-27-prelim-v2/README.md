# 2026–27 decision table — preliminary pipeline test v2: with Australian non-finds and under the Pléiades hypothesis (21 Oct 2026)

Status: **pipeline test, before calibration, not for release.** Supersedes `results/decision-2026-27-prelim/` (fc786b5) for interpretation. That version used only the composer product DS (core + drift finds + searched areas), described there as "all evidence"; it left out the Australian non-recovery term. This was an error of labelling in that note.

Pete's decisions, 21 Oct 2026: (1) headline posterior stays DS, and the Australian non-finds are a labelled sensitivity; (2) the 00:19 treatments are shown separately, with held out as the headline and no mixture; (3) "R600 only" means D2 (00:19:29 range and frequency). He also asked for a version under the Pléiades hypothesis H.

## Inputs

- Composer views v3.2 on run J, **re-run privately** with extra maps saved (patch `compose_v3-extra-maps.patch`: adds products ApopS variants, ApopSP and DS/ApopS detection variants given H to the saved maps; no other change). The re-run reproduces the published v3.2 output exactly: 8,808 summary values and every published map, maximum difference 0. Output kept outside the exchange (session workspace); the composer should save these maps itself at its next build.
- Searched-areas per-cell fields `spatial-fields-v2`; planned-block polygon `oi2024_proposed_inboard_northwest` (community tracing, grade C, 6,122 km² on the cell grid; official remainder 7,428.54 km²).

## Four posteriors

| code | contents |
|---|---|
| DS | core + drift finds + searched areas (headline, Pete 21 Oct) |
| ApopS | DS + Australian non-finds on populated coast (city and inner regional at the find-coast level, all other coast off) |
| DSP | DS conditional on H (Pléiades objects are MH370 debris) |
| ApopSP | ApopS conditional on H |

**Australian term, declared deviation.** Pete's ruled scheme (17 Oct: ABS tiers 1 / 0.3 / 0 relative to the find coasts at peak awareness, 2014 level 0.5, range 0.3–0.65) has no level column at the drift arc-latitude nodes that the composer reads. ApopS uses the nearest stored column. On the same (reconstruction) method the ruled scheme shifts the held-out mean latitude by +3.83° against +4.44° for this column (`results/drift-items-2026-10-17/australia-three-tier.csv`), so ApopS probably overstates the ruled Australian pull by up to about 0.6° in mean latitude. Request to drift below.

## Results (detection model V1 central, planning P_D 0.9)

| 00:19 treatment | posterior | median | north of 33 S | on searched ground | planned block P(success) | best unsearched equal area | top-10 blocks searched / partly / unsearched |
|---|---|---|---|---|---|---|---|
| 00:19 values held out | without Australian non-finds | 35.79 S | 0.195 | 0.26 | 0.026 ± 0.005 | 0.065 | 3 / 4 / 3 |
| 00:19 values held out | with Australian non-finds | 33.27 S | 0.487 | 0.21 | 0.032 ± 0.006 | 0.044 | 2 / 4 / 4 |
| 00:19 values held out | without, given Pléiades H | 35.34 S | 0.007 | 0.35 | 0.048 (SD n.a.) | 0.147 | 5 / 3 / 2 |
| 00:19 values held out | with, given Pléiades H | 35.28 S | 0.007 | 0.36 | 0.053 (SD n.a.) | 0.150 | 5 / 3 / 2 |
| 00:19:29 range and frequency only | without Australian non-finds | 36.13 S | 0.177 | 0.42 | 0.009 ± 0.003 | 0.052 | 6 / 3 / 1 |
| 00:19:29 range and frequency only | with Australian non-finds | 32.42 S | 0.516 | 0.32 | 0.011 ± 0.004 | 0.046 | 4 / 4 / 2 |
| 00:19:29 range and frequency only | without, given Pléiades H | 35.58 S | 0.001 | 0.49 | 0.014 (SD n.a.) | 0.081 | 7 / 3 / 0 |
| 00:19:29 range and frequency only | with, given Pléiades H | 35.54 S | 0.001 | 0.50 | 0.016 (SD n.a.) | 0.079 | 7 / 3 / 0 |
| Both 00:19 frequencies as recorded | without Australian non-finds | 36.05 S | 0.182 | 0.59 | 0.004 ± 0.002 | 0.043 | 7 / 3 / 0 |
| Both 00:19 frequencies as recorded | with Australian non-finds | 32.18 S | 0.520 | 0.42 | 0.004 ± 0.003 | 0.073 | 3 / 5 / 2 |
| Both 00:19 frequencies as recorded | without, given Pléiades H | 35.54 S | 0.000 | 0.62 | 0.008 (SD n.a.) | 0.057 | 7 / 3 / 0 |
| Both 00:19 frequencies as recorded | with, given Pléiades H | 35.51 S | 0.000 | 0.63 | 0.009 (SD n.a.) | 0.054 | 7 / 3 / 0 |
| Both 00:19 frequencies, Holland transient bias added | without Australian non-finds | 35.97 S | 0.234 | 0.66 | 0.003 ± 0.002 | 0.037 | 7 / 3 / 0 |
| Both 00:19 frequencies, Holland transient bias added | with Australian non-finds | 30.35 S | 0.611 | 0.47 | 0.003 ± 0.002 | 0.074 | 5 / 3 / 2 |
| Both 00:19 frequencies, Holland transient bias added | without, given Pléiades H | 35.50 S | 0.000 | 0.68 | 0.004 (SD n.a.) | 0.039 | 8 / 2 / 0 |
| Both 00:19 frequencies, Holland transient bias added | with, given Pléiades H | 35.48 S | 0.000 | 0.68 | 0.005 (SD n.a.) | 0.037 | 8 / 2 / 0 |

Planned-block mass is the composer's exact outcome-level value. Approximate SD by design effect; not assessed for the H-conditional posteriors (the north-of-33 S share they are estimated from is near zero). "Best unsearched equal area" = the top cells with existing coverage below 0.1 totalling 6,122 km², not contiguous (upper bound).

## What this shows

1. **The planned block ranks below the best unsearched ground of equal area in every one of the 16 cases** (four treatments × four posteriors), and at every detection level tried (ρ 0, ρ 0.5, V2; `next-area-summary.csv`).
2. **Adding the Australian non-finds moves weight off searched ground and north**, as Pete expected: held out 0.26 → 0.21 on searched ground, median 35.79 → 33.27 S; under D2 0.42 → 0.32. The modal block under the Australian term is partly searched ground near 36.0 S 92.75 E (held out) or 36.0 S 92.25 E (D2–D3); under D4 it is 25.6 S 101.25 E.
3. **Under H the posterior collapses to 35–36 S, 91–93 E**, mass north of 33 S ≤ 0.007, and the Australian term barely changes it (median 35.34 → 35.28 S held out). The planned block's P(success) roughly doubles under held out (0.026 → 0.048), but the best unsearched cells nearby give 0.147–0.150, about three times more. Five of the top ten blocks under H are on searched ground (coverage ≥ 0.5), because the H region overlaps the Phase 2 / Ocean Infinity strip at 35.4 S.
4. **"Mostly on searched ground" was a property of DS under the both-frequency treatments**, not of the evidence as a whole. With the 00:19 values held out, the top ten is mixed in every version (3 / 4 / 3 without the Australian term, 2 / 4 / 4 with it).

## Requests

1. **Ocean drift:** add Pete's 17 Oct scheme (tiers 1 / 0.3 / 0, levels 0.3 / 0.5 / 0.65) as level alternatives at the arc-latitude nodes (no transport cost; config `levels.alternatives`), so the composer can carry the ruled term exactly instead of the populated-only column.
2. **Composer:** at the next views build, save maps for the Australian products (the ruled scheme when it exists; ApopS meanwhile) and for every H-conditional product, and emit block and named-polygon masses per bootstrap replicate.
3. **Searched areas (open from v1):** how to carry the gap between the 6,122 km² tracing and the official 7,428.54 km² remainder.
4. **Option B design (Pete leans to it):** a second-pass detection probability for searched blocks, conditioned on the first-miss cause (terrain, holiday, interpretation). To be designed with the searched-areas thread.

## Files

`next-area-summary.csv` (6 treatments × 4 posteriors × detection variants), `ranked-blocks-top15.csv`, `widening-response.csv` (DS and ApopS), `rank-stability-top5-<posterior>.csv`, `fig1-planned-block-vs-best-unsearched.(png|pdf)`, `fig2-ranked-blocks-map-held-out.(png|pdf)`, `make_prelim_v2.py`, `compose_v3-extra-maps.patch`.

---
Footnote, STE100: this is a test of the method. The calibration run can change the numbers. In all 16 cases, the planned search block gives a lower chance of a find than the best unsearched ground of the same size. When we add the absence of debris on populated Australian coasts, less of the probability is on ground that was searched. When we assume that the Pléiades objects are debris, the probability is near 35–36 S, partly on searched ground.
Technical: composer views v3.2 (run J, settled seabed, searched areas V1 central, OI 2018/2025–26 grade C coverage 0.889/0.7808, drift finds two-model, hydroacoustics zero weight) re-run with extra maps; Australian term = populated-only level-1 column (ln_l_lev_populated), not the ruled three-tier scheme; Davey eq. 11.2, P_D 0.9; 769 km² equal-area cells, 2 × 2-cell blocks; SD ≈ sqrt(deff · m(1−m)/ESS_Kish), deff from the composer's north-of-33 S seed bootstrap, not estimated where that share is outside 0.05–0.95.
