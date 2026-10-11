# Where the wreckage is on the seabed: run C (core run C, 4 strata × 8 seeds)

Ocean settling, 11 Oct 2026 (~07:15 UTC). This is settling's standard result on end of flight's run C, in four forms:
1. the five standard 00:19 options;
2. by type of flight end (A1 / A2 / B, ruling 6 as amended);
3. each of the above with contact speed ≤ 212 m/s and the remaining rows re-weighted (architecture ruling 20:35 -0600, G-H2);
4. drawn from the composer's run C weights (G12).

**UNCONVERGED.** Core run C fails split-half in every stratum: the minimum is 0.82-0.86 against a floor of 0.924. Every number here
inherits that, and none is evidence about where MH370 lies.

**Labels** (carried in every footnote):
- rapid descents above 6,500 ft/min and unloading are not reachable by the model;
- residual roll P(left) = 0.8 PROVISIONAL;
- trim at loss and two-tank takeover NOT applied;
- the breakup table is PROVISIONAL;
- Holland H1/H2 are NOT ESTIMABLE;
- the composed products are a composer PIPELINE TEST (architecture stand-in) with the hydroacoustics L_hyd stand-in, and GlobCurrent is
  excluded (drift audit F1).

## Figures

- `settling-seabed-wreckage-run-c-reweighted.{png,pdf}` (primary) and `-fixed`: the five options, all rows.
- `settling-seabed-wreckage-run-c-speedcap-reweighted.{png,pdf}` and `-speedcap-fixed`: the same with contact speed ≤ 212 m/s.
- `settling-seabed-wreckage-run-c-by-family.{png,pdf}` and `-speedcap-by-family`: rows A1 / A2 / B by columns of the five options.
- `settling-seabed-wreckage-run-c-composed-aimed.{png,pdf}`: Held Out and R600 BTO Only, each with debris and sound and then with the
  searches added, drawn from the composed weights.

## Method

The method is that of `results/settling-core-set-next-run-b/` and `results/settling-family-next-run-b/`, with these changes.
- **Impacts:** `end-of-flight/next-run-c/<stratum>/seed-<1..8>/impacts32.npy` (compact format, read through end of flight's
  `compact_impacts.load`). All 32 seeds passed settling's format check (`results/settling-run-c-scripts/runc_check.py`).
- **Weights:** stratum weights are end of flight's `summary/family-evidence-run-c.json`, using its `+unpowered` keys: core run C
  P(family), re-weighted by Z_00:19. H1/H2 stay at fixed weights. The constraint is `unpowered`.
- **Families:** `family4_code` from `family_labels(..., latent:recovery_attempted)`. Run C has essentially no code 6, because end of
  flight's family-B overlay relabels it.
- **Speed cap:** the option posterior is restricted to rows with |v| ≤ 212 m/s. Stratum weights are multiplied by each stratum's retained
  mass and renormalised; family shares and P(stratum | family) re-weight the same way. For the estimable options settling's capped stratum
  weights agree with end of flight's `~v212` keys to within 1e-4. For H1/H2 they differ by up to 0.04, because settling holds H1/H2 at
  fixed weights times retained mass, while end of flight re-weights them.
- **Aimed resample:** a systematic resample of 40,000 impacts over every row, with probability equal to the composer's per-row mixture
  mass (`mh370-exchange/composer/next-run-c/row-weights/<product>/`). Then one settling draw each. Each outcome has weight 1/40,000.
- **Settling:** hypothesis/settling 9330d4c on the real ocean (75-115 E, 45-10 S), one draw per resampled impact. Grid 0.02°,
  Gaussian 0.1°, HPD; areas on the authalic sphere.

## Areas (thousand km²)

| 00:19 option | impact ESS | 90 % impact, all rows | 90 %: impacts → seabed (re-weighted) | settling adds, 90 % / 99 % | 90 %: fixed weights | 90 % impact, seeds 1-4 / 5-8 | speed-capped: removed weight; 90 % impacts → seabed | estimable |
|---|---|---|---|---|---|---|---|---|
| 00:19 Held Out | 55.6 M | 598.3 | 595.4 → 596.2 | +0.14 % / +0.22 % | 595.5 → 596.3 | 594.6 / 597.5 | 9.8 %; 605.1 → 606.1 (ESS 50.0 M) | yes |
| 00:19 R600 BTO Only | 37.6 M | 333.7 | 327.9 → 328.8 | +0.25 % / +0.47 % | 328.7 → 329.6 | 329.2 / 335.3 | 10.0 %; 332.9 → 333.8 (ESS 33.8 M) | yes |
| 00:19 R600 BTO + Raw BFO | 1.3 M | 211.0 | 209.1 → 209.6 | +0.25 % / +0.42 % | 210.5 → 211.0 | 209.4 / 210.0 | 11.9 %; 208.6 → 209.2 (ESS 1.1 M) | yes |
| 00:19 Holland H1 | 66 | 49.0 | 48.9 → 50.2 | +2.59 % / +5.20 % | 48.9 → 50.2 | 38.7 / 38.0 | 46.9 %; 50.6 → 52.3 (ESS 39) | **not yet estimable - targeted sampler in progress** |
| 00:19 Holland H2 | 171 | 60.8 | 60.8 → 62.2 | +2.32 % / +4.23 % | 60.8 → 62.2 | 47.4 / 49.3 | 43.5 %; 64.1 → 66.0 (ESS 90) | **not yet estimable - targeted sampler in progress** |

| 00:19 option | settled offset p50 / p90 / p99 (km) | afloat mass | impacts not computed |
|---|---|---|---|
| 00:19 Held Out | 0.41 / 4.42 / 21.66 | 17.0 % | 0 |
| 00:19 R600 BTO Only | 0.41 / 4.52 / 22.35 | 17.0 % | 0 |
| 00:19 R600 BTO + Raw BFO | 0.42 / 4.67 / 21.79 | 16.8 % | 0 |
| 00:19 Holland H1 | 0.33 / 2.81 / 20.76 | 18.8 % | 0 |
| 00:19 Holland H2 | 0.34 / 2.78 / 20.03 | 18.8 % | 0 |

**By family, all rows** (90 % area impacts → seabed, thousand km²; family share; ESS)

| 00:19 option | A1 | A2 | B |
|---|---|---|---|
| 00:19 Held Out | 375 → 376; 12 %; ESS 6.8 M | 680 → 682; 33 %; ESS 18.9 M | 530 → 531; 55 %; ESS 29.9 M |
| 00:19 R600 BTO Only | 216 → 217; 11 %; ESS 4.2 M | 392 → 393; 33 %; ESS 12.6 M | 258 → 258; 56 %; ESS 20.8 M |
| 00:19 R600 BTO + Raw BFO | 72 → 73; 11 %; ESS 124,601 | 293 → 294; 15 %; ESS 210,339 | 167 → 167; 74 %; ESS 929,067 |
| 00:19 Holland H1 | not yet estimable (ESS 38; 0 %) | not yet estimable (ESS 18; 1 %) | not yet estimable (ESS 63; 99 %) |
| 00:19 Holland H2 | not yet estimable (ESS 12; 0 %) | not yet estimable (ESS 36; 9 %) | not yet estimable (ESS 157; 91 %) |

**By family, contact speed ≤ 212 m/s, re-weighted** (90 % area impacts → seabed, thousand km²; family share; ESS; share of the family removed by the cap)

| 00:19 option | A1 | A2 | B |
|---|---|---|---|
| 00:19 Held Out | 373 → 374; 7 %; ESS 3.4 M; removed 50 % | 689 → 691; 35 %; ESS 18.3 M; removed 3 % | 530 → 531; 58 %; ESS 28.4 M; removed 5 % |
| 00:19 R600 BTO Only | 247 → 248; 5 %; ESS 1.8 M; removed 56 % | 391 → 393; 35 %; ESS 12.2 M; removed 3 % | 260 → 261; 60 %; ESS 19.8 M; removed 5 % |
| 00:19 R600 BTO + Raw BFO | 127 → 128; 4 %; ESS 39,024; removed 69 % | 293 → 294; 16 %; ESS 200,668; removed 5 % | 163 → 164; 80 %; ESS 866,004; removed 5 % |
| 00:19 Holland H1 | not yet estimable (ESS 12; 0 %; removed 100 %) | not yet estimable (ESS 24; 0 %; removed 93 %) | not yet estimable (ESS 39; 100 %; removed 46 %) |
| 00:19 Holland H2 | not yet estimable (ESS 10; 0 %; removed 100 %) | not yet estimable (ESS 29; 11 %; removed 33 %) | not yet estimable (ESS 84; 89 %; removed 45 %) |

**Aimed at the composed weights (G12)** (40,000 draws per product)

| product | row ESS (Kish) | 90 % impact, all rows | 90 %: resampled impacts → seabed | 50 %: impacts → seabed | settled offset p50 / p90 / p99 (km) |
|---|---|---|---|---|---|
| 00:19 Held Out: debris and sound | 4.2 M | 758.2 | 740.2 → 742.3 | 150.4 → 151.0 | 0.43 / 4.36 / 22.10 |
| 00:19 Held Out: debris, sound, searches | 2.8 M | 833.5 | 812.1 → 814.6 | 180.7 → 181.5 | 0.44 / 4.47 / 22.72 |
| 00:19 R600 BTO Only: debris and sound | 2.9 M | 468.1 | 463.9 → 465.1 | 87.0 → 87.4 | 0.43 / 4.55 / 22.96 |
| 00:19 R600 BTO Only: debris, sound, searches | 2.0 M | 502.3 | 495.5 → 497.3 | 95.0 → 95.5 | 0.45 / 4.74 / 23.53 |


**Aimed at the composed H weights: CONDITIONAL on the Pléiades objects being aircraft debris** (added ~08:05 UTC;
`settling-seabed-wreckage-run-c-composed-pleiades-aimed.{png,pdf}`; 40,000 draws per product)

| product | row ESS (Kish) | 90 % impact, all rows | 90 %: resampled impacts → seabed | 50 %: impacts → seabed | settled offset p50 / p90 / p99 (km) |
|---|---|---|---|---|---|
| 00:19 Held Out: debris, sound, Pléiades | 1.95 M | 316.8 | 310.2 → 311.6 | 32.3 → 32.4 | 0.42 / 3.97 / 20.17 |
| 00:19 Held Out: debris, sound, Pléiades, searches | 1.61 M | 405.0 | 389.2 → 391.0 | 35.2 → 35.4 | 0.42 / 4.03 / 20.12 |
| 00:19 R600 BTO Only: debris, sound, Pléiades | 0.79 M | 176.9 | 173.6 → 174.4 | 18.3 → 18.4 | 0.42 / 4.15 / 21.31 |
| 00:19 R600 BTO Only: debris, sound, Pléiades, searches | 0.59 M | 214.1 | 212.3 → 213.4 | 16.7 → 16.8 | 0.43 / 4.32 / 22.08 |

## What it shows

1. **Settling still adds under 1 % to every estimable area:** +0.14 to +0.25 % at 90 %, +0.22 to +0.47 % at 99 %, and +0.25 to +0.37 %
   for the composed products. The seabed PDF is the impact PDF to under 1 % in area, as on core (b) and reference-289.
2. **The kernel is wider than on core (b):** p90 is 4.4-4.7 km, against 3.6-3.9. The cause is the family mix. B now holds 55-74 % of
   the posterior (against 41-57 %) and has the widest kernel (p90 4.9-5.1 km); A1 has p90 2.4-2.9 km. The p99 stays at 21-22 km.
3. **Against core (b),** the 90 % areas are: Held Out 596 (579 on (b)), R600 BTO Only 329 (365), and R600 BTO + Raw BFO 210 (239). The
   seed-half difference of the impact 90 % area is now 0.3-1.8 % for the estimable options, against 6-16 % on core (b). That is an impact
   split-half of this resample, not core's convergence test, which still fails.
4. **The speed cap removes 10-12 % of the weight for the estimable options, and almost all of it is A1 (50-69 % of A1).** Areas move by
   -0.2 to +1.7 %: Held Out 596 → 606, R600 BTO Only 329 → 334, and R600 BTO + Raw BFO 210 → 209. A1's share falls from about 11 % to
   4-7 %. Its R600 BTO + Raw BFO area grows from 73 to 128 thousand km², because the removed fast A1 rows were concentrated near the arc.
5. **The composed products are now estimable (G12 closed for these four).** With draws aimed at the composed weights, the row ESS is
   2.0-4.2 M and about 39,950 of 40,000 draws are distinct impacts. On core (b) the old resample kept 368-865 effective impacts.
   - Adding drift and sound widens Held Out from 596 to 742 and R600 BTO Only from 329 to 465.
   - Adding the searches widens them again, to 815 and 497.
   - This is the expected effect of a non-detection: it removes mass from the searched corridor and spreads the rest (searched areas'
     note, `results/seabed-search-why-wider.md`).
   - **Conditional on the Pléiades objects being debris (H):** the 90 % region shrinks to 312 (Held Out) and 174 (R600 BTO Only), and to
     391 and 213 after the searches. The region splits into a cluster near 35-37 °S, 91-94 °E and a band east of the 7th arc. Settling
     adds +0.45 to +0.52 % there. Row ESS is 0.59-1.95 M, so all four H products are estimable.
6. **H1 and H2 remain not estimable** (pooled ESS 66 / 171; per family 12-157). Under the speed cap H1 loses 47 % and H2 44 % of its
   weight, and neither has any A1 weight left. The shortage is the within-parent push-over sampling (coverage gap G7), unchanged.

## COVERAGE (ruling ~15:45 -0600)

The sets, gaps and their status are as in `results/settling-core-set-next-run-b/README.md` §COVERAGE, including the impact-pitch
statement for G6: no settling output depends on pitch. Changes for run C:

| set / gap | kind | status on run C | effect |
|---|---|---|---|
| ocean window 75-115 °E × 45-10 °S | reach | every run C impact settles: 0 not computed in all-rows panels; 1 of 199,992 in Held Out under the cap is carried at the impact position | ≤ 5e-6 |
| contact speed above 1.25 VMO (end of flight G13, no structural limit) | reach (upstream) | shown both ways, as ruled; removed weight reported per option and family | areas -0.2 to +1.7 %; A1 share about halves |
| attitude-dependent breakup | reach (settling's family rule) | declared, not closed | only through dense-piece offsets, p90 < 5 km |
| composed products (G and G after searches) | proposal coverage | closed by the aimed resample: row ESS 2.0-4.2 M | — |
| H (Pléiades) composed products | proposal coverage; conditional hypothesis | closed by the aimed resample: row ESS 0.59-1.95 M; every H panel is labelled conditional on the Pléiades objects | — |
| H1 / H2 | proposal coverage (upstream, G7) | not estimable in any family (ESS 4-171) | stamped |

**ESS per option, family and declared region** is given in the tables above. The parameter bounds and their sources are as for core (b)
(`breakup.toml`; `results/settling-references.md`).

## Samples

`mh370-exchange/settling/next-run-c-core-set/`, `next-run-c-core-set-speedcap/`, `next-run-c-by-family/`,
`next-run-c-by-family-speedcap/` and `next-run-c-composed-aimed/`. Each holds README.txt, SHA256SUMS, READY and the source sidecar
(stratum, seed, impacts32.npy row). Key outcomes as row × 2^20 + draw.

## Reproduce

`results/settling-run-c-scripts/` (`runc_par.sh standard|family`, `runc_render.sh`) and the scripts in this folder.
`wf_aimed.py prep <eof smoke> nrca 40000 <row-weights dirs...>` is followed by `settling::tests::wreckage_field` per product and then
`wf_aimed.py render`. Compute: the preps took 10-17 min each at 1 thread; the settling passes 2-8 min each at 1 thread; all outside the
heavy lock and within 2 threads in total.

- Ocean Settling
