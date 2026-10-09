# Settling deliverable 6 on the real ocean

Code: `hypotheses/settling` at `bfb71d5`, generator `settling::tests::report_real` (ignored), with
`SETTLING_REPORT_POINTS="-37.875,88.625;-37.375,89.375;-37.125,89.875;-35.625,92.125"`. Run 9 Oct 2026
outside the heavy lock, 2 threads, 2 min.

**Ocean.** GLORYS12V1 daily column (uo, vo, thetao, so, 50 levels; `GridProfile`) and surface current;
ERA5 10 m wind; seabed AusSeabed MH370 Phase 1 150 m, else GEBCO_2026; in-situ density by TEOS-10 on the
column's own T and S. Ocean error, float phase and Stokes a = 0 are as in `results/settling-d6/`.

**Still PROVISIONAL:** the breakup table (educated estimates). Impact points come from the 295.66° prior
map (`results/no-exhaustion-prior-summary.json`), superseded on re-run. The end-of-flight hand-off
covers the stable-glide regime only, so the dive class is absent (Pete, 9 Oct). Nothing here is
weighted by family.

**Points:** posterior p10, mode, p50 and p90 latitude, taking the highest-density cell in each band:
37.875 S 88.625 E; 37.375 S 89.375 E; 37.125 S 89.875 E; 35.625 S 92.125 E. Median contact depths are
3,769-3,861 m. The GLORYS model floor lies above the seabed by a median of 0-70 m (`hold-deepest-level`).

**Files:**
- `settling-d6-real-ocean.png` / `.pdf`;
- `settling-d6-real-sensitivity.csv`: variant × point × family × class;
- `settling-d6-real-convergence.csv`: baseline p50/p90 from draws 0-511, 512-1023 and all 1,024.

## Results

p90 resting offset at the posterior-median point:

| class | intact | broken | fragmented |
|---|---|---|---|
| engine | 463 m | 220 m | 222 m |
| landing gear | 468 m | 233 m | 226 m |
| wing box | 6.8 km | 776 m | 510 m |
| fuselage section | 6.5 km | 901 m | 518 m |
| flat panel | 1.2 km | 1.2 km | 1.2 km |
| cabin contents | 13.4 km | 13.6 km | 13.7 km |

1. **Swapping in the real ocean confirms the provisional page.** The dense classes are unchanged
   within 2 %. Floated classes spread 5-13 % further on the real ocean, which is the provisional
   page's p90 at 0.88-0.96 of the real one (median over points), and 17 % at most. The conclusions of
   `results/settling-d6/` stand.
2. Density source (GLORYS T, S against WOA23): under 0.01 %. AusSeabed against GEBCO only: under
   0.5 %. The below-floor rule (hold against linear-to-zero): under 0.2 %.
3. Ocean error contributes 5-11 % of the floated and gliding classes' p90.
4. **Monte Carlo.** At 512 draws, the two independent halves differ by a median of 2.4 % in p90 and by
   up to 14 % (heavy-tailed classes: fragmented cabin contents and flat panels). At 1,024 draws the
   standard error is about 1/sqrt(2) of that. Settled-offset statistics quoted to 2 significant figures
   are converged. Floated-class p90s carry about ±7-10 %.
