# Drift-only source map and timing sensitivities (smoke test, 7 November 2026)

Deskstar job ed751059, code commit 3ff4828e on branch `hypothesis/debris-drift-smoke-wide` (output-only options, default off, byte-identical when off:
node table and coefficient files MD5-equal to the 7 Nov binary on `coef/smoke-on.toml`). GlobCurrent 2,939 s, GLORYS12 2,753 s, both exit 0.

## Summary (ASD-STE100)

- Without the satellite data, the debris evidence alone points to a broad band near 25–35° S. It does not select a longitude well.
- With both ocean models at equal weight, the mean is 29.9° S, 81° E (SD 4.9° in latitude). Only 8% of the probability is within 150 NM of the satellite track.
- No debris in Australia moves the mean 0.5–1.7° north (ratio 0.25 to 1).
- The Mossel Bay date of 21 Mar 2016 instead of 23 Dec 2015 changes the mean latitude by less than 0.1° in the wide map, and moves it about 1° south within 150 NM of the track.
- Time ashore is the largest timing lever. If all items could lie ashore 240–365 days, the mean moves about 5–6° north.
- The flaperon and the Mossel Bay cowling were found fresh. If only the other seven items may lie ashore a long time, the mean stays within 1.5° of the current 60-day setting (mixture weight 0.5; 0.4–1.9° over weights 0.25–0.75), slightly to the south.
- Results are not converged (4 environments, 2,000 particles per class). Use the means and broad patterns, not single blocks.

## Files
- smoke-wide-posterior-summaries.csv, smoke-wide-timing-cases.csv, smoke-wide-mossel-arrival-lead.csv, smoke-wide-identified-share-near-track.csv, smoke-wide-node-lnL.csv
- Figures: drift-only-source-map(.png, -jon-word.png, -jon.pdf, -jon-proof.pdf, -jon-caption.txt); drift-timing-sensitivity (same set)
- Raw coefficients: smoke-wide-results.tar.gz (artifact store; ~29 MB)

## Key assumptions and modelling choices
| Item | Value | Status |
|---|---|---|
| Source area | 46–14° S, 64–112° E, 150 NM grid (252 points), uniform prior per unit area | Own choice (Pete asked to disregard the arc) |
| Method | Forward drift likelihood mapped over sources (Bayes inversion), not backward particle tracking | Own choice; project ruling that drift returns a likelihood |
| Sampling | 2,000 particles/class × 4 environments (seeds 201–204) | Own choice, smoke level; not converged |
| Physics, classes, windage, levels | As conv-*-1.toml of 7 Nov (c2f3eb4) | Project convention; provisional |
| Kernel | 50 km (100/200 km stored) | Project convention |
| Delay | Exponential, mean 60 d; 20/120/240/365 d stored | Provisional, not ruled |
| Marine-life split | Mixture weight 0.5 on 20 d; flaperon and Mossel Bay cowling fresh | Own choice; not agreed |
| Australian tiers | city+inner = ratio, outer = 0.3 × ratio, remote = 0 | Pete's ruling 17 Oct; ratio grid is a sensitivity |
| Mossel Bay date | 23 Dec 2015 primary; 21 Mar 2016 as second beaching | Evidence (ATSB Update 2) |
| Block display | 2 × 2 source points, likelihood averaged within block | Own choice, display only |
| Track corridor | 22 points within 150 NM of run J median track | Own choice, crude arc proxy |
