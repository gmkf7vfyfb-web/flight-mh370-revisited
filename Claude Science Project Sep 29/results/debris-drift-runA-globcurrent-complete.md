# Debris drift run A, part 1: GlobCurrent with product-relative windage, 710 nodes (complete)

12 Oct 2026, ~00:45 UTC, ocean drift module. Run `debris-drift-runA-globcurrent` (8 chunks, 06:30 11 Oct - 00:24 12 Oct UTC under the heavy
lock, 12 threads; binary rerun-gc-bin e6bb17fe32f22b55; held 21:51-23:15 UTC for end of flight's sweep). Architecture option A (18:35 -0600
10 Oct, Pete delegated).

> **Labels:** GlobCurrent my-p1d 0 m + ERA5, windage offset drawn per particle U(-0.75 %, -0.60 %) of U10 (audit F1, product-relative);
> GLORYS12 comparison uses the production surface (367 planned nodes); GLORYS12 at the 343 extension nodes is run A part 2 (queued);
> recovery bandwidth 50 km; interim per-node surfaces, not composed, not evidence about the impact location.

## Result

- 710 nodes released, 709 scored at 50 km, 1 unresolved (southernmost band, Mossel-Bay-limited), 0 land. Wall time per chunk 4,189-10,039 s.
- **Two-model agreement on the 367 planned nodes** (corrected GlobCurrent against GLORYS12; as-run GlobCurrent in brackets): node correlation
  **0.39** (-0.08); SD of the difference **1.92** (3.14); mean difference -0.31 (+0.44);
  **354 of 367** nodes within 2 sigma of the combined split-half Monte Carlo noise (2 sigma = 3.58; as run 293 of 367 at 3.15).
- Split-half noise: GlobCurrent 1.09 (as run 0.68), GLORYS12 1.42. The lower windage brings fewer particles to the finds, so the noise rises.
- 20 highest nodes: GLORYS12 26.2-34.2 S (median 30.4 S); corrected GlobCurrent 26.2-38.2 S (median 31.4 S). As run, GlobCurrent favoured 35-41 S.
- Extension nodes (GlobCurrent only so far): 343, 342 scored; their maximum -125.69 against -125.19 on the planned nodes.

| latitude band | nodes | corrected: mean diff | SD | as run: mean diff | SD |
|---|---|---|---|---|---|
| (-42, -37] | 82 | +0.69 | 3.31 | +3.68 | 2.92 |
| (-37, -33] | 98 | -0.06 | 1.09 | +1.63 | 1.08 |
| (-33, -30] | 60 | -0.62 | 0.89 | +0.03 | 0.94 |
| (-30, -25] | 89 | -0.81 | 0.88 | -1.41 | 1.08 |
| (-25, -20] | 38 | -1.42 | 1.38 | -4.61 | 3.15 |

Reading (interim): the F1 correction removes most of the between-model latitude trend (about 8 log-likelihood units end to end before,
about 2 now). The south-of-37 S band keeps an SD of 3.3, set by Monte Carlo noise at the Mossel-Bay-limited nodes (split-half noise 2.8
in that band), not by a model difference; the targeted resolution run for the southern nodes (pending Pete) is the fix. North of 25 S
GlobCurrent stays lower by about 1.4.

Figure: `results/debris-drift-two-model-agreement-relwind.png` (+ .pdf); nodes: `results/debris-drift-two-model-nodes-relwind.csv`.

## Exchange (interim, both models)

`debris-drift/next-run-c-gcrel/` and `debris-drift/next-run-d-he-gcrel/`: as the production exports, but `lnL_globcurrent_*` is the
corrected run A surface (710 nodes) and `lnL_glorys12_*` the production surface (367 nodes); `lnL_mean_*` needs both scored, so it is limited
by GLORYS12's support until run A part 2. Replaced by the final re-export after part 2.

## COVERAGE

(a) Feasible set: impact points of the 777-200ER end of flight as in end of flight's runs C and D. (b) Model reach: 710 nodes at 30 NM on the
reference-289 extent (planned 367 + extension 343 from the run C impacts), off-grid weight <= 0.6 % (run C) and <= 0.49 % (H1/H2 sweep);
breakup floating-debris origin not modelled (gap, open). (c) Proposal coverage: per node 10^5 particles (3 windage classes x 8,334 x 4
ocean-error realisations), splitting at Rodrigues and Mossel Bay; min n_eff median 0 in the southernmost band (Mossel-Bay-limited; gap,
targeted run pending Pete). Parameter bounds: windage offset U(-0.75 %, -0.60 %) from the audit F1 fits (undrogued 1.36 % GLORYS12 vs
0.75 % GlobCurrent); other parameters as production.
