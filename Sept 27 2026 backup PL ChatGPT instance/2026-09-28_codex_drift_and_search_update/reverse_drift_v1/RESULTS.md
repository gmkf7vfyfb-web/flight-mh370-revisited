# Recovered and extended conditional imagery-origin results

The complete three-family transport bundle was recovered and rerun. Iannello used **21 March 2014**, while the supplied Malaysian briefing slide labels the four points **23 March 2014**. The attribution/date discrepancy remains unresolved; both dates are carried separately. See `PROVENANCE_AND_METHODS.md` for verified sources, exact settings and interpretation.

The 21-to-23 March change shifts the equal-model Possible COSMO-SkyMed Radar mean by **29.4 km for three points** and **30.5 km for four**, with total variation about **0.29**. Adding F4 shifts the mean about **64 km westward** and approximately doubles the 90% region. The expanded grid places **13.0% of the Pléiades mixture mass west of the original -100 NM source boundary**. This is why the expanded Pléiades 90% area is larger than the recovered original value, despite reproducing all overlapping transport scores. Individual grid-cell modes are substantially noisier than means.

Display labels now use **Possible COSMO-SkyMed Radar**. Historical slide wording and existing `french4`/F1-F4 machine identifiers are retained for traceability. See the sensor-nationality and handoff note in the atlas and provenance document. Numerical results are unchanged.

## Equal-model results on the expanded source support

Coordinates below are signed decimal degrees (negative latitude = south). Areas are discrete highest-density region areas, not confidence in debris identity. These are normalized conditional source distributions.

| scenario | mode_lat | mode_lon | mean_lat | mean_lon | hpd90_km2 | hpd95_km2 |
|---|---|---|---|---|---|---|
| french4_21 | -35.183 | 92.896 | -35.292 | 91.761 | 46217.956 | 58565.611 |
| eastern3_21 | -35.183 | 92.896 | -35.333 | 92.463 | 23066.104 | 28982.689 |
| pleiades | -35.218 | 92.247 | -34.962 | 91.793 | 46475.199 | 59594.582 |
| french4_23 | -35.187 | 93.040 | -35.268 | 92.095 | 55478.697 | 73142.703 |
| eastern3_23 | -35.187 | 93.040 | -35.391 | 92.779 | 27181.989 | 34813.526 |
| combined50_french4_21 | -35.274 | 92.171 | -35.127 | 91.777 | 57708.135 | 74686.160 |
| combined50_french4_23 | -35.300 | 92.891 | -35.115 | 91.944 | 62167.010 | 80945.734 |
| combined50_eastern3_21 | -35.274 | 92.171 | -35.147 | 92.128 | 39872.634 | 55650.192 |
| combined50_eastern3_23 | -35.244 | 92.965 | -35.176 | 92.286 | 48190.151 | 65253.924 |

`combined50` means a 50:50 pool of Pléiades and Possible COSMO-SkyMed Radar conditional PDFs. The three transport families have fixed equal weights. The date suffix applies only to the Possible COSMO-SkyMed Radar detections; Pléiades is always 23 March.

## Date and fourth-object sensitivity

| first | second | kind | tv | mean_shift_km | mode_shift_km |
|---|---|---|---|---|---|
| french4_21 | french4_23 | date | 0.291 | 30.492 | 13.072 |
| eastern3_21 | eastern3_23 | date | 0.288 | 29.420 | 13.072 |
| combined50_french4_21 | combined50_french4_23 | date | 0.145 | 15.276 | 65.429 |
| combined50_eastern3_21 | combined50_eastern3_23 | date | 0.144 | 14.744 | 72.217 |
| eastern3_21 | french4_21 | fourth_object | 0.262 | 63.883 | 0.000 |
| eastern3_23 | french4_23 | fourth_object | 0.255 | 63.562 | 0.000 |

Total variation ranges from 0 (same cell masses) to 1 (disjoint support). A mean shift can be modest even when the PDF changes appreciably or gains another lobe.

## Pléiades versus Possible COSMO-SkyMed Radar spatial overlap

| first | second | overlap | mean_shift_km | mode_shift_km |
|---|---|---|---|---|
| pleiades | french4_21 | 0.618 | 36.886 | 59.085 |
| pleiades | eastern3_21 | 0.616 | 73.553 | 59.085 |
| pleiades | french4_23 | 0.502 | 43.740 | 72.096 |
| pleiades | eastern3_23 | 0.428 | 101.565 | 72.096 |

Overlap is sum(min(p_i,q_i)) over the common source grid. It describes these two conditional spatial distributions; it is not a Bayes factor, a probability of shared identity, or independent validation.

## Original-support truncation

| scenario | outside_original_strip_mass | edge_mass |
|---|---|---|
| french4_21 | 0.085 | 0.000 |
| eastern3_21 | 0.000 | 0.000 |
| pleiades | 0.130 | 0.000 |
| french4_23 | 0.082 | 0.000 |
| eastern3_23 | 0.000 | 0.000 |
| combined50_french4_21 | 0.107 | 0.000 |
| combined50_french4_23 | 0.106 | 0.000 |
| combined50_eastern3_21 | 0.065 | 0.000 |
| combined50_eastern3_23 | 0.065 | 0.000 |

`outside_original_strip_mass` counts centers west of -100 NM on the expanded grid. `edge_mass` counts the outer two along/cross bands. The old boundary half-cell is corrected to an interior cell when merging. The new support spans -250 to +100 NM; probability outside it has not been evaluated.

## Reproduction and Monte Carlo checks

The original nine Pléiades model/seed score arrays reproduce with maximum absolute error **9.23e-16**. Every new trajectory returned a valid endpoint. The expanded grid has 9,159 cells, with 192 trajectories per cell per seed and three seeds for each of six model/date combinations. Total new trajectories: **31,653,504** (both date windows). The 21 March Pléiades scores are retained as a diagnostic computation but are not used as the Pléiades observation in any delivered PDF.

| model | scenario | tv | mean_shift_km | mode_shift_km |
|---|---|---|---|---|
| equal_models | F4_21 | 0.125 | 1.096 | 19.082 |
| equal_models | F4_23 | 0.147 | 0.540 | 7.682 |
| equal_models | combined50_eastern3_21 | 0.072 | 0.294 | 13.104 |
| equal_models | combined50_eastern3_23 | 0.073 | 0.476 | 13.095 |
| equal_models | combined50_french4_21 | 0.078 | 0.330 | 9.298 |
| equal_models | combined50_french4_23 | 0.077 | 0.394 | 20.704 |
| equal_models | eastern3_21 | 0.065 | 0.291 | 82.671 |
| equal_models | eastern3_23 | 0.079 | 0.648 | 29.252 |
| equal_models | french4_21 | 0.080 | 0.550 | 82.671 |
| equal_models | french4_23 | 0.094 | 0.389 | 29.252 |
| equal_models | pleiades | 0.106 | 0.705 | 38.250 |

The table shows the largest pairwise difference among individual seed PDFs, not an uncertainty interval for the three-seed average. Grid modes may be noisier than means and broad regions. This sample count reproduces the prior study; it does not establish fully converged point maxima.

## Reusable deliverables

- `conditional_origin_atlas.pdf`: numerical overview, observation map, component and mixed PDF maps, date/subset overlays and latitude marginals.
- `results/summary.csv`: every component/pool, mean/mode, marginal quantiles, HPD areas and edge diagnostics.
- `results/sensitivity_comparisons.csv`: date, fourth-object, sensor overlap and weighting comparisons.
- `results/response_sensitivity.csv`: new 5/20 km kernel and separate windage sensitivities.
- `results/seed_convergence.csv` and `reproduction_checks.csv`: numerical audits.
- `results/source_grid.csv` plus `conditional_pdfs.npz` or `probability_masses.csv.gz`: portable cell probability masses; divide by cell area for density.
- `results/relative_likelihoods.csv.gz`: prior-free transport scores for explicit conditional reuse.
- `runs/`: per-seed source scores, sufficient to rebuild all pools and plots without rerunning transport.
- `code/`: new rerun, aggregation, plotting and audit code.
- `recovered/`: unchanged recovered prior code, arrays, results and provenance.
- `FILE_MANIFEST.csv`: hashes for the complete delivered package.

The principal limitations are unknown sensor provenance/acquisition UTC, uncalibrated identity and response weights, inherited daily-wind timing and boundary clamping, a finite source prior, and lack of the background false-detection denominator. GLORYS12 includes WAVERYS; differences cannot be attributed solely to current-model choice. No probability that these objects are MH370 debris is assigned.