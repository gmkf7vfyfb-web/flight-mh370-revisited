# Ocean drift: status (updated 7 November 2026)

Read after `threads/master-prompts/ocean-drift.md`. Replace entries when they change; history is in git and in `coordination/OCEAN_DRIFT.md`.
Supersedes the 17 October draft (`threads/drafts/ocean-drift-status-DRAFT.md`).

## Current base
- Impact samples: core run J, end of flight run J, families pooled; 00:19 data held out unless stated.
- Drift code: `hypothesis/debris-drift` at c2f3eb4 (adds `write_coefficients`; default off, node tables byte-identical).
- Drift surfaces: the 84 arc-latitude release points (20–40° S), both ocean models, 16 environments (32 south of 33.25° S), coefficients stored.
  Results and scripts: `results/drift-convergence-2026-11-07/`. Every detection ratio, find subset and kernel width is an exact offline re-scoring
  (`drift_coef.py`, validated to 1.3 × 10⁻⁶).

## Headline numbers (mean impact-latitude shift, two models, 50 km kernel)
| Quantity | Value |
|---|---|
| Nine finds | +0.61° (not converged; falls as environments are added) |
| Flaperon alone | +0.02° |
| All finds except Mossel Bay | −0.09° |
| Nine finds and Australian non-finds, ratio 0.25 / 0.5 / 1 | +1.89° / +2.55° / +3.49° |
| ln R, core vs uniform on the arc: nine finds / ratio 0.25 / ratio 1 | −0.39 / −1.11 / −1.79 |

## Open items
1. Convergence of the Mossel Bay and Paindane terms: environment-to-environment spread about 4 and 3 ln units; more environments and more
   particles per environment for the low-exposure class are needed before a converged nine-find value can be quoted.
2. Posterior predictive misfit: three early finds in southern Mozambique and South Africa against 0.22 expected; cause not separated
   (windage of exterior panels, transport speed, search effort, impact latitude).
3. Headline Australian detection ratio: Pete's decision. Equal detection (ratio 1) is his stated starting point, with a lower value for the
   effect of private searchers on the find coasts.
4. Suspiciousness and evidence-ledger figures still use the earlier four-environment drift surfaces; recompute with the new surfaces.
5. Biofouling (18 °C) term: not built; the released shell record covers only the last 4–6 months of drift and constrains no arc latitude.
6. Paper equation (21) must be generalised to per-class λ, latent detection levels and the environment average (see results note, section 6).
7. GlobCurrent v202411 retires on 24 November 2026: local copies on the Mac and on deskstar match the SHA-256 list (48 of 48).
