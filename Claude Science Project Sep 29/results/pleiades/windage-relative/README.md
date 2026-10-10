# Sensitivity: product-relative GlobCurrent windage (debris-drift audit F1)

Pléiades module, 10 Oct 2026. Script: `prepare/windage_relative.py`.
Source: reference-289 branch, 00:19 Held Out (unconstrained), Pléiades + all four COSMO-SkyMed contacts, one debris field.
Conditional on H, with no Bayes factor.

GlobCurrent already carries about 0.6-0.75 % of U10 more wind drift than GLORYS12, yet both products here use the same
windage prior. Each GlobCurrent windage node is therefore moved down by Δc and split between its neighbouring nodes;
anything below zero goes to zero (a declared clamp). GLORYS12 is unchanged. With Δc = 0 the recomputed surface
reproduces the exported one (SD of the log ratio 5e-5).

| search | windage | models | 90 % area km² | mean |
|---|---|---|---|---|
| Phase 2 + Bluefin-21 | as run | both, equal weight | 57,306 | 35.20 S 91.54 E |
| Phase 2 + Bluefin-21 | GlobCurrent −0.60 % | both, equal weight | 56,522 | 35.20 S 91.54 E |
| Phase 2 + Bluefin-21 | GlobCurrent −0.75 % | both, equal weight | 56,344 | 35.20 S 91.54 E |
| + OI 2018 + 2025-26 | as run | both, equal weight | 59,316 | 35.22 S 91.43 E |
| + OI 2018 + 2025-26 | GlobCurrent −0.75 % | both, equal weight | 58,127 | 35.21 S 91.44 E |
| + OI 2018 + 2025-26 | as run | GlobCurrent only | 54,516 | 35.13 S 91.36 E |
| + OI 2018 + 2025-26 | GlobCurrent −0.75 % | GlobCurrent only | 51,456 | 35.12 S 91.38 E |

**Finding.** For the Pléiades conditional, F1 is a small effect. The two-model 90 % area falls 1.4-2.0 % and the mean
moves under 1 km; GlobCurrent alone shrinks 4-6 %. The effect is small because the drift is 15 days, not months, and
the transport error (about 100 km per component) dominates the windage mismatch (about 0.7 % × 7 m/s × 15 d ≈ 60 km).
The as-run configuration stays the reference. The product-relative case is reported as a declared sensitivity until
drift's F1 smoke test and Pete's ruling settle the convention for both modules.

— Pléiades
