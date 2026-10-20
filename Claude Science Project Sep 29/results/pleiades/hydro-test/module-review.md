# Pléiades module review of the hydro-test stand-in (columns and source packages on core (b))

10 Oct 2026, Pléiades module. Reviewed: `standin-columns.md` and `/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/`
(README, `SHA256SUMS`, `<stratum>/seed-<k>/pleiades-lnL.npy`). Interface: architecture.md ~20:00 and ~20:10 UTC.
Labels: core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL.

**Verdict: adopted as the module's own output. No redo.**

## Checks the module made itself
1. **Surfaces are the module's own, byte for byte.** The stand-in recorded the sha256 of the surfaces it regenerated,
   but had no module checksum to compare with (its deviation 1). The module's own run tree
   (`engine/runs/pleiades/`, 85-103 E × 43-25 S, 0.05°, GLORYS12 + ERA5 and GlobCurrent daily + ERA5) has
   - `likelihood-surface.f32` sha256 `9a3d55a98a03c241c6ef63551c2276afe27f53f932c737e283fbd61deea360fc`,
   - `cosmo-surface.f32` sha256 `e7fd6ded1625dbb9b1d98505cd808b073b6099da5160eaddcdc55c8343fc97a7`.
   Both are identical to the stand-in's values. **Deviation 1 is closed.**
2. **Independent spot check of the columns.** 160,000 random rows were checked: 20,000 per stratum, for seeds 1 and 4 of each of
   the 4 strata. For each row the module's own grid cell was looked up from EoF's `latitude_deg` / `longitude_deg`, giving
   rating-5 objects at equal weight plus the C4 pass-marginal.
   - 316,114 per-model values were compared. The largest |Δ lnL_both_<model>| is 7.6e-6, and the largest |Δ lnL_both_mean| is
     7.6e-6. Both are at float32 resolution.
   - `row` and `parent` match `impacts.npy` everywhere.
3. The stand-in's 24-of-24 per-stratum reproduction is accepted.
4. **Re-weighted P(family) is identical to end of flight's own file.** End of flight has now published
   `summary/family-evidence-next-run-b.json` (~20:40). For all three core options its `p_family_reweighted` (`+alive`) equals the
   stand-in's computed values to the 4th decimal.

## Points recorded (none changes a result)
- **Held Out with `+alive` (the stand-in's question).** The module agrees with the stand-in's choice. The 00:19 option is
  "Held Out", but `+alive` is part of the arm definition, so its existence factor belongs in the weights. End of flight's own file
  does the same: its key `00:19 Held Out +alive` has ln Ẑ −0.106 ± 0.015 (free) and re-weights P(family) by < 0.001. Ruling C's
  "factor 1 under Held Out" applies to the 00:19 BTO/BFO term, which is absent. No ruling is needed. This is now closed in favour
  of end of flight's file.
- **Not-computed rows.** The columns hold NaN where one ocean model is not computed. The module's own grid path instead keeps
  the other model at half weight (`build_branch`: −inf on the missing model, then the equal-weight mean). For a consumer, the
  module's convention is lnL_mean = lnL_<other model> − ln 2. The effect on areas and means is nil (stand-in caveat 3). The
  columns are kept as they are; hydroacoustics may use either convention but should state which.
- **ESS correction accepted.** The design note's 90,000-145,000 rows under H (R600 BTO Only) came from seed 1 only. Over all
  seeds the range is 40,900-155,900. R600 BTO + Raw BFO under H has 1,844-7,236 rows per seed; this is usable, but it carries
  larger Monte Carlo noise in a split-half.
- The hydroacoustics stand-in's result (ln R_hyd −0.05 / −0.08 / −0.15, all within noise; architecture ~20:45) needs nothing from
  this module.
