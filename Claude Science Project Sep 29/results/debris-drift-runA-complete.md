# Debris drift run A complete: both ocean models at 710 nodes; final per-impact exports

12 Oct 2026 ~09:35 UTC, ocean drift module. Architecture option A (18:35 -0600 10 Oct, Pete delegated).

> **Labels:** interim per-node surfaces; not composed; not evidence about the impact location by themselves. GLORYS12 extension chunks 2-3
> were run by the architecture stand-in (06:13-09:13 UTC, identical configs except output_dir) after drift's driver died mid chunk 2.

## Result

- GLORYS12 710 nodes (production 367 + extension 343): 704 scored, 6 unresolved (41.2-39.2 S). GlobCurrent (windage product-relative) 710: 709 scored.
- Extension chunk times (GLORYS12): 5,081 / 7,101 / 7,208 / 3,476 s.
- **Two-model agreement on the 703 nodes scored by both:** correlation 0.34; 669 of 703 within 2 sigma of the combined split-half Monte
  Carlo noise (sigma 1.61 GLORYS12, 1.17 GlobCurrent). On the 367 planned nodes: correlation 0.39, 354 of 367 (as run before F1: -0.08, 293).
- 20 highest nodes: GLORYS12 26.2-39.2 S (median 29.7 S; one noisy southern extension node at 39.2 S); GlobCurrent 26.2-38.2 S (median 32.7 S).
- South of 37 S both surfaces are Mossel-Bay-limited (GLORYS12 extension chunk 0: split-half noise 3.78, 67 of 96 nodes with zero-environment
  fraction > 0). The targeted resolution run for the southern nodes (pending Pete) is the fix.

Figure: `debris-drift-two-model-agreement-710.png` (+ .pdf).

## Exports (exchange, READY)

`debris-drift/next-run-c-runA/` (32 seeds) and `debris-drift/next-run-d-he-runA/` (16 seeds): both models on 710 nodes; supersede the
production and `-gcrel` sets. `run-h`: not exported (end of flight's run-h has SWEEP-DONE but no READY at 09:20 UTC).

## COVERAGE

(a) Feasible set: end of flight's impacts (runs C and D-he; see their READMEs for reach labels). (b) Model reach: 710 nodes at 30 NM on the
reference-289 extent; off-grid <= 0.59 %; breakup floating-debris origin not modelled (open). (c) Coverage of the posteriors (+unpowered;
not computed including off-grid): run C Held Out 0.74-0.81 %, R600 BTO Only 0.50-0.64 %, Raw BFO 0.03-0.17 %, H1/H2 0.00 %; H1/H2 sweep
Held Out 0.51-0.64 %, R600 BTO Only 0.39-0.52 %, Raw BFO 0.01-0.16 %, H1 0.00-0.10 %, H2 0.00-0.29 %. Target (< 1 %) met in every stratum x
option. MC-unresolved rows: GLORYS12 0.67 % of run C rows, GlobCurrent 0.01 %. Per-node proposal: 10^5 particles, splitting at Rodrigues
and Mossel Bay; southern nodes under-resolved (gap, targeted run pending Pete). Parameter bounds: windage offset U(-0.75 %, -0.60 %) from
audit F1; others as production.
