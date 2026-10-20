# Pléiades module on end of flight's run H (fly-by routes, stratum next-h-routes), BEFORE seabed search

12 Oct 2026, Pléiades module. Columns: `mh370-exchange/pleiades/run-h/` (READY). Script: `prepare/score_dhe_summary.py` (single-stratum
fallback: P = 1). Labels:
- conditional on H; no identity likelihood; no Bayes factor or P(H);
- core run D/H NOT converged; end-of-flight physics PROVISIONAL (end of flight's run H label list);
- survival factor primary;
- **ONE stratum (routes): not a family mixture and not comparable with a four-stratum headline**;
- before seabed search (searched areas have not published run H columns).

| 00:19 option | setting | ESS under H (without H) | mean without H | mean under H | shift NM | ln S (p) | ln E[L_H] vs run D-he same option |
|---|---|---|---|---|---|---|---|
| Held Out | **ρ 0.25, both, product-relative (proposed)** | 84,300 (937,479) | 37.83 S 90.02 E | 35.61 S 91.62 E | 154 | -3.08 (0.07) | -1.09 |
| Held Out | ρ 0.25, GLORYS12 only (in force) | 80,168 (937,479) | 37.83 S 90.02 E | 35.63 S 91.72 E | 156 | -3.01 (0.08) | -1.13 |
| Held Out | ρ 0, both (as run) | 64,598 (937,479) | 37.83 S 90.02 E | 35.51 S 91.73 E | 162 | -3.15 (0.07) | -1.15 |
| R600 BTO Only | **ρ 0.25, both, product-relative (proposed)** | 33,891 (705,866) | 38.20 S 89.87 E | 35.87 S 92.07 E | 175 | -3.92 (0.03) | -1.42 |
| R600 BTO Only | ρ 0.25, GLORYS12 only (in force) | 30,730 (705,866) | 38.20 S 89.87 E | 35.85 S 92.18 E | 179 | -3.74 (0.04) | -1.48 |
| R600 BTO Only | ρ 0, both (as run) | 24,992 (705,866) | 38.20 S 89.87 E | 35.76 S 92.20 E | 184 | -3.99 (0.03) | -1.47 |
| R600 BTO + Raw BFO | **ρ 0.25, both, product-relative (proposed)** | 1,421 (21,452) | 37.73 S 89.90 E | 35.83 S 92.06 E | 154 | -3.49 (0.03) | -1.55 |
| R600 BTO + Raw BFO | ρ 0.25, GLORYS12 only (in force) | 1,633 (21,452) | 37.73 S 89.90 E | 35.78 S 92.22 E | 162 | -3.41 (0.03) | -1.64 |
| R600 BTO + Raw BFO | ρ 0, both (as run) | 1,096 (21,452) | 37.73 S 89.90 E | 35.71 S 92.22 E | 165 | -3.54 (0.03) | -1.62 |
| Holland H1 | **ρ 0.25, both, product-relative (proposed)** | 89 (111) | 37.72 S 89.77 E | 36.03 S 92.08 E | 150 | -3.76 (0.01) | -1.88 |
| Holland H1 | ρ 0.25, GLORYS12 only (in force) | 103 (111) | 37.72 S 89.77 E | 35.90 S 92.40 E | 167 | -3.71 (0.01) | -1.99 |
| Holland H1 | ρ 0, both (as run) | 101 (111) | 37.72 S 89.77 E | 35.90 S 92.28 E | 163 | -3.95 (0.01) | -1.96 |
| Holland H2 | **ρ 0.25, both, product-relative (proposed)** | 26 (386) | 37.72 S 89.86 E | 35.78 S 92.34 E | 167 | -2.25 (n/e) | -1.32 |
| Holland H2 | ρ 0.25, GLORYS12 only (in force) | 23 (386) | 37.72 S 89.86 E | 35.77 S 92.47 E | 172 | -1.76 (n/e) | -1.20 |
| Holland H2 | ρ 0, both (as run) | 23 (386) | 37.72 S 89.86 E | 35.71 S 92.43 E | 173 | -2.29 (n/e) | -1.33 |


## After Phase 2 + Bluefin-21 (searched areas `run-h`, official only), proposed setting, primary
`pleiades-runh-summary-p2bf.json`. OI not included (searched areas' base).

| 00:19 option | ESS under H (without H) | mean without H | mean under H | shift NM | ln S (p) |
|---|---|---|---|---|---|
| Held Out | 62,292 (727,670) | 38.07 S 90.11 E | 35.49 S 91.51 E | 169 | -3.24 (0.08) |
| R600 BTO Only | 26,235 (550,038) | 38.52 S 89.91 E | 35.90 S 92.24 E | 193 | -4.36 (0.03) |
| R600 BTO + Raw BFO | 578 (10,352) | 37.96 S 90.09 E | 35.87 S 92.26 E | 163 | -3.24 (0.04) |
| Holland H1 | 86 (205) | 37.61 S 90.15 E | 35.95 S 92.60 E | 154 | -2.82 (0.03) |
| Holland H2 | 12 (175) | 37.53 S 90.39 E | 35.71 S 92.55 E | 151 | -0.85 (n/e) |

- The tension persists after the searches: ln S −2.8 to −4.4 for the standard options and H1 (H2 not estimable).
- R600 BTO + Raw BFO under H falls to 578 effective impacts, below the gate. H1 has 86 and H2 has 12: GAP.
- **ESS without H against searched areas' README** (H1 288 / H2 221): mine are 205 / 175. They are pooled differently; this is
  raised with searched areas, as for D-he.

## Reading
1. **Run H's routes end far south-west** (about 37.7-38.2 S, 89.8-90.0 E without H). Under H every option moves 150-175 NM
   north-east, to about 35.6-36.0 S, 91.6-92.3 E.
2. **Tension is strong.** ln S is −1.8 to −4.0 over all settings (−2.2 to −3.9 at the proposed one), and p is 0.01-0.08 where it
   can be estimated (not for H2), against about 0 to −0.5 on run D-he. H and the
   run H routes do not agree. Run H's posterior under H is a narrow overlap of the two, which is a **symptom of the tension and not
   of precision**.
3. **Positional compatibility is lower than on run D-he** for the same option (column 8, −1.1 to −2.0 in ln). The run H routes are
   less compatible with H than run D's mixture is.
4. **H1/H2 are not estimable on run H** (111 / 386 effective impacts without H; 89 / 26 under H). R600 BTO + Raw BFO under H has
   1,421 (gate met only just).

## COVERAGE
- (a), (b): end of flight's run H README. (c) Effective impacts above. **GAPs:** H1 and H2 (both, with and without H); every
  family other than routes (by construction of run H).
