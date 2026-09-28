# Research state update, 28 September 2026

This is a structured handoff, not a verbatim conversation transcript.

## New reproducible computation in this task
- Recovered the prior three-family Pléiades forward inversion, five checksum-matching forcing arrays and prior source/score files. Reproduced the original nine model/seed score arrays to maximum absolute error approximately 9.2e-16.
- Extended to four briefing-slide coordinates and eastern three, using 21 versus 23 March sensitivity, expanded western support, BRAN2016, OSCAR v2 Final and GLORYS12 + WAVERYS. Fixed equal-family pools and 50:50 sensor pools remain explicitly conditional.
- Verified Iannello used 21 March. COSMO-SkyMed is Italian; French supply is consistent with bilateral access. Exact platform/product attribution of all four contacts remains unverified. The display label is Possible COSMO-SkyMed Radar.
- Produced the atlas, observation/combined-density panels, recent and possible future OI search overlays, and search-non-detection sensitivities.
- Approximately 58% of the starting PDF mass overlaps past-search footprints/envelopes; about 87% of mass in its 50% HPD region overlaps them. Illustrative detection/coverage marginalization gives 86-88% residual mass outside those envelopes. These are sensitivities, not calibrated identity or full aircraft-location probabilities.
- Located public GA/ATSB Phase 2 raw and processed sonar catalogues. No new raw sonar re-review was performed.

## Related-task clarification after the September 27 methodology backup
The latest accessible turns of Separate Traffic Thread (conversation 6ab70fcd-8fa4-83ea-b25e-dd8c87026e04) clarify that the complete weighted 00:11 Stage-1 posterior should initialize the EOF stage, preserving feasible states and correlations. Do not substitute hand-set preliminary family percentages (0.7247/0.2750/0.00037 or 0.5076/0.2490/0.2434) as production priors. These remain conditional diagnostic summaries. This clarifies the archived methodology; it is not a new filter result.

## Earlier local work absent from the remote backup
Reproduce Davey latitude posterior generated reconstructed filter runs and assessments; MH370 distributions remain non-converged. The separate Rerun MH370 v12 validation task's earlier blocked status is historical and must not be confused with the later reconstructed runs. Supplementary code/reports/diagnostics are included under earlier_local_filter_work.

## Unresolved
Imagery identity/base-rate denominator; exact possible-COSMO acquisition UTC and fourth target provenance; native OI AUV swaths and spatial detection quality; flight/fuel feasibility of western conditional drift lobes; converged full trajectory/EOF computation; impact-to-wreckage displacement. No acoustic/flight likelihood was fused into the conditional drift PDF.
