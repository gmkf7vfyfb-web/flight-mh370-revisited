# Drift review of composer pass 1 (run C): carry rule and drift-surface sensitivity

11 Oct 2026, ~08:20 UTC, ocean drift module. Review requested by architecture (stand-in for the composer), OCEAN_DRIFT.md ~08:10 UTC.

> **Labels:** run C NOT CONVERGED; EoF physics provisional, no structural limit (G13); hydro stand-in, not calibrated; drift GLORYS12
> production surface (367 nodes; not the run A extension); GlobCurrent row is the as-run surface with the F1 windage bias, shown as an
> illustration only; H conditional on the Pléiades objects being MH370 debris. Products: 00:19 R600 BTO Only and 00:19 Held Out, G,
> all rows (no 212 m/s filter), strata re-weighted by the 00:19 evidence. Nothing here is a result; it is a sensitivity of pass 1.

## Method

Exact re-weighting of the composer's published G row weights (`mh370-exchange/composer/next-run-c/row-weights/<option>-G/`): divide out the
drift factor the composer used (GLORYS12 h50; unscored rows divided by the seed's carry value D), multiply in an alternative drift surface
with its own carry value, re-pool within each stratum and restore the stratum weight W_Q. With the original surface this returns the
composer's weights exactly: G medians −37.173 (−40.267 to −25.690) R600 BTO Only and −36.279 Held Out, equal to the note's −37.17 / −36.28.
ln R = ln E_G[L_P] − ln E_P1[L_P], with E_P1 from the composer's PE increments per stratum (they do not depend on drift); L_P =
`lnL_pleiades_glorys12`. Script: `engine/hypotheses/debris-drift/prepare/pilot/surface_sensitivity.py` (module branch). 2 threads, outside
the heavy lock, 5 min.

## 1. Carry rule (finding for the composer)

compose `lib.rs` carries a row that **any** factor did not compute at the mean **joint** likelihood of the computed rows. In H, a row that drift
did not score therefore loses its own Pléiades (and hydro) value and takes the scored rows' mean. The drift export README and the 16:25 −0600
ruling read "carry at the neutral value" per factor: only the drift likelihood is replaced; the other factors still apply.

| quantity | joint carry (pass 1) | drift-only carry | composer, as published |
|---|---|---|---|
| ln R, R600 BTO Only (mixture) | +0.537 | **+0.312** | +0.543 |
| ln R, Held Out (mixture) | +0.328 | **+0.171** | +0.336 |
| per stratum R600 BTO Only (free / Davey + radar / descent-climb / routes) | +0.54 / +0.46 / +0.68 / +0.72 | +0.31 / +0.24 / +0.44 / +0.55 | +0.545 / +0.466 / +0.695 / +0.741 |

The joint-carry column reproduces the composer to ≤ 0.02 nat per stratum (the residual is seed pooling). About 40 % of pass 1's ln R
comes from giving the 19-20 % of weight that drift did not score the Pléiades mean of the scored rows. It also explains why "not-computed
excluded" moved ln R by only −0.007: under the joint rule carrying and excluding are nearly the same for a normalised expectation. The same
rule applies to searches in Ga/Ha and to hydro in G (not assessed here; hydro is weak). Proposal: carry per factor (replace only the
missing factor's likelihood by its own D, keep the row's other factors). This is core-owned (`crates/compose`); I have not changed it.

## 2. Drift-surface sensitivity (drift-only carry)

| drift surface | R600 BTO Only: G median (95 %) | share 33-36 °S | unscored share | ln R | Held Out: G median | ln R |
|---|---|---|---|---|---|---|
| GLORYS12 h50 (pass 1) | −37.17 (−40.27 to −25.69) | 0.090 | 0.204 | +0.31 | −36.28 | +0.17 |
| particle half A, h50 | −36.92 (−40.27 to −25.99) | 0.075 | 0.240 | +0.11 | −36.61 | +0.06 |
| particle half B, h50 | −36.74 (−40.27 to −25.51) | 0.094 | 0.335 | +0.44 | −35.87 | +0.18 |
| bandwidth 25 km | −36.99 (−40.27 to −25.44) | 0.108 | 0.316 | +0.50 | −35.78 | +0.42 |
| bandwidth 100 km | −37.65 (−40.27 to −25.98) | 0.073 | 0.204 | +0.13 | −36.92 | +0.04 |
| bandwidth 200 km | −37.83 (−40.27 to −26.28) | 0.067 | 0.204 | +0.07 | −37.23 | +0.05 |
| GlobCurrent as run (F1 bias; illustration) | −37.88 (−40.27 to −28.59) | 0.067 | 0.203 | +0.19 | −37.30 | +0.20 |

Reading (provisional):
- **Drift transport Monte Carlo noise is the largest drift term in ln R.** The two independent particle halves differ by 0.34 nat (R600 BTO
  Only); the full surface has about half that standard deviation (≈ ±0.17 nat). The composer's factor split-half (seeds 1-4 against 5-8)
  cannot see it, because every seed uses the same drift surface. The half surfaces also leave more nodes unresolved (unscored 0.24 / 0.34
  against 0.20), so part of the half difference is a support change.
- **Bandwidth.** ln R falls monotonically with the kernel bandwidth (+0.50 at 25 km to +0.07 at 200 km); the median moves 0.84° south from
  25 to 200 km. ln R stays positive in every variant: drift does not conflict with the Pléiades area, but the size of the support it gives is
  not resolved (0.07 to 0.50 nat for R600 BTO Only).
- **Ocean model.** GlobCurrent as run moves the G median 0.7° south and lowers ln R to +0.19; the F1-corrected GlobCurrent surface (run A) replaces
  this row.
- **G medians.** Within ±0.5° of pass 1 for half-surfaces, h25 and h100, and down to −37.8/−37.9° for h200 and GlobCurrent. The 2.5 % limit is
  fixed by the support's south edge (−40.27) in every row; the 97.5 % limit moves with the north tail.

## 3. Requests

1. Composer: carry per factor (section 1), or label pass 1's ln R as "joint carry" and quote the drift-only carry value beside it.
2. Composer: propagate drift transport noise into ln R (compose with the two half surfaces, or use the half difference as a stated
   systematic). Drift can add half-surface columns to the run C export on request (the node tables already hold them).
3. Pass 2 after run A (F1-corrected GlobCurrent at 710 nodes, GLORYS12 at 710): drift will re-export; the unscored share falls to ≤ 1 %, which
   makes the carry rule nearly moot.

## COVERAGE

(a) Feasible set and (b) model reach: as in composer pass 1 section 5 and `debris-drift-production-complete.md`. Drift-specific reach: 367
GLORYS12 nodes at 30 NM; unscored weight 0.20 (R600 BTO Only, h50), up to 0.34 on half surfaces and 0.32 at h25 (more unresolved nodes); gap
G10, closed by run A (extension 343 nodes, ≥ 99.06 % of each stratum × option scored). (c) Proposal coverage: the composer's G weights, ESS as
in pass 1 table 5(c); this re-weighting changes only the drift factor, and no product here falls below the composer's ESS floor (R600 BTO + Raw
BFO, which does, is not included). Holland H1/H2 not estimable in run C (G7), not included. Parameter bounds: bandwidths 25-200 km as declared
in the drift brief; no new bounds.
