# Product-relative GlobCurrent windage (drift audit F1) on core run C, Pléiades module

11 Oct 2026. Labels: **core run C NOT CONVERGED**; EoF physics PROVISIONAL (G13); conditional on H; strata re-weighted (`family-evidence-run-c.json`),
`unpowered`, after Phase 2 + Bluefin-21 + OI 2018 + 2025-26 (grade C), P + all four COSMO-SkyMed contacts.

**Method.** `prepare/rho_surface.py --gc-dc 0.006,0.00675,0.0075 --models 1`:
- The GlobCurrent windage nodes (0-5 % U10, 0.25 % steps) carry the weights of c − dc, where c is the module's uniform prior and dc is
  drift's run A offset (drawn uniformly from 0.60-0.75 % U10, here by three-point equal-weight quadrature). Mass below 0 is clamped to
  node 0 (declared).
- GLORYS12 is unchanged. The result is published as `joint-surface-rho{0,0.25,0.5}-gcrel` (both column sets;
  `reader.load_rho(..., tag="-gcrel")`).
- **Independent check:** `windage_relative.surfaces`, a separate code path, on 90-94 E, 37-34 S gives the same GlobCurrent likelihood to
  sd 5e-7 in ln (constant 2 ln A_scene), both as run and product-relative.

| 00:19 option | ρ | GLORYS12 only, 90 % km² | both models, as run | both models, GlobCurrent product-relative | GlobCurrent only, as run → product-relative | mean (both, product-relative) | ln S | mean shift NM |
|---|---|---|---|---|---|---|---|---|
| 00:19 R600 BTO + Raw BFO | 0 | 28,478 | 37,887 | 38,090 (+0.5 %) | 44,020 → 44,302 (+0.6 %) | 35.90 S 92.36 E | -0.47 | 41 |
| 00:19 R600 BTO + Raw BFO | 0.25 | 30,998 | 41,597 | 41,798 (+0.5 %) | 49,600 → 49,980 (+0.8 %) | 35.96 S 92.36 E | -0.30 | 38 |
| 00:19 R600 BTO + Raw BFO | 0.5 | 33,493 | 44,750 | 44,951 (+0.4 %) | 54,055 → 54,509 (+0.8 %) | 36.00 S 92.36 E | -0.17 | 36 |
| 00:19 R600 BTO Only | 0 | 32,252 | 45,709 | 46,163 (+1.0 %) | 53,081 → 53,568 (+0.9 %) | 35.93 S 92.40 E | -1.35 | 102 |
| 00:19 R600 BTO Only | 0.25 | 34,997 | 49,540 | 49,944 (+0.8 %) | 58,236 → 59,023 (+1.4 %) | 36.00 S 92.42 E | -1.16 | 99 |
| 00:19 R600 BTO Only | 0.5 | 38,016 | 53,066 | 53,468 (+0.8 %) | 62,595 → 63,602 (+1.6 %) | 36.05 S 92.43 E | -1.00 | 96 |
| 00:19 Held Out | 0 | 67,914 | 82,614 | 82,891 (+0.3 %) | 79,819 → 79,032 (-1.0 %) | 35.37 S 91.62 E | -0.56 | 81 |
| 00:19 Held Out | 0.25 | 77,420 | 92,331 | 92,732 (+0.4 %) | 92,015 → 91,561 (-0.5 %) | 35.44 S 91.66 E | -0.51 | 77 |
| 00:19 Held Out | 0.5 | 85,461 | 100,336 | 100,810 (+0.5 %) | 101,699 → 101,906 (+0.2 %) | 35.50 S 91.69 E | -0.46 | 73 |

## Findings
1. **On run C, making GlobCurrent product-relative changes the two-model 90 % region by only +0.3 to +1.0 %, and moves the mean by ≤ 0.01°.**
   On reference-289 the change was −1.4 to −2.0 %. Either way, F1 is a percent-level effect for this module, because the 15-day transport
   error (~100 km per component) dominates the ~60 km windage mismatch.
2. **The two-model region stays 18-43 % wider than GLORYS12 alone after the fix.** That width is genuine disagreement between GLORYS12 and
   GlobCurrent, not double-counted windage.
3. **With the fix in, ruling 2's condition** ("until your GlobCurrent arm applies the same offset, the headline is GLORYS12 only") **is met for
   this module's conditional.** The ρ 0.25 headline with both models, GlobCurrent product-relative, is: R600 BTO + Raw BFO 41,798 km²;
   R600 BTO Only 49,944 km²; Held Out 92,732 km².
   - The composer's joint ocean-model alternative still waits for drift's run A, so composer passes stay GLORYS12 only.
   - Split-half σ: `splithalf-gcrel.csv`.
