# Fuel-model session: master prompt

Modular Architecture, 9 October 2026. Pete Large approved a separate fuel session that builds the two
fuel models. It follows from the fuel-model audit, `results/fuel-model-audit-architecture.md` (commit
`bffbe1a`), and core request 16 part C in `coordination/CORE_STAGES.md`.

## Why

The fuel model is the largest single difference from Davey et al. (2016). Core's ladder shows it moves
the 00:19 median about 2° north. The audit found its direction physically right, but its size
untrustworthy:
- F1: the calibration factor is inverted.
- F2: there is no temperature correction.
- F3 and F4: lookup edges and extrapolation.
- F5 and F6: states above the ceiling and extrapolated Mach.
- F14: provenance. About 22% of the used flow cells are confidential FPPM values.

Pete's direction: **first use all the available information, for the most accurate filter.** For
publication, fit a formal public model, then check and calibrate it against the internal model.

## What you build

You own the folder `Claude Science Project Sep 29/engine/fuel-model/` (Python) and
`results/fuel-model/`. **Do not edit `crates/`.** Core integrates your outputs into `crates/flight`
(`fuel.rs`) under core request 16.

**1. Internal model, using all data.**
- Inputs:
  - every table class in Ulich's 9M-MRO fuel model v5.6 workbook. The repo copy is under
    `library_full_audit/MH370/`, read with `.sources/fuel-performance/extract.py`. Include the
    confidential cells and the one-engine-inoperative tables (`lrc_inop`, `holding_inop`), which
    `fuel-tables.json` holds but the engine does not load;
  - Boeing SIR Appendix 1.6E, Tables 3 and 4 (27 numbers);
  - the ACARS fuel state.
- Corrections:
  - the temperature effect on flow (FPPM +3% per +10 °C);
  - the factor defined the right way round (model ÷ Boeing, then divided out);
  - weight dependence, if the residuals call for it.
- Uncertainty: give it from the calibration residuals, not assumed.
- Output: a revised local table file plus calibration parameters, in the schema core's `FuelFlow` reads
  (`fuel_flow_kg_h(FL, weight_t, mach) → kg/h, extrapolated, below_tables, above_ceiling`), with a
  temperature input added. Declare any schema change as a core request.
- **Confidential cells are never committed** and never uploaded to a third-party service. Keep them in
  the git-ignored `data/`, and record their use in `results/restricted-sources-ledger.md`.

**2. Public model, for the paper.**
- A small parametric law FF(FL, W, M, ΔISA) with physically motivated terms: thrust-specific fuel
  consumption against Mach and temperature ratio, and drag polar against weight, Mach and pressure ratio.
- Fit it to public data only: SIR Appendix 1.6E Tables 3 and 4, the ACARS state, and openly published
  FPPM values.
- No licensed performance databases (for example, EUROCONTROL BADA) unless their licence allows
  publication.

**3. Each model checked against the other.**
- Compare the flows on a grid over the flight envelope the posterior visits.
- Compare exhaustion times along a sample of `reference-289` paths (the hand-off and route files in the
  core workspace, read-only).
- Report the differences and say where they come from.

**4. Single engine.** Supply the INOP data, and a short note on how core could model the right engine
flaming out first, up to 15 min before the left (ATSB AE-2014-054 p. 9; audit F11). Core writes the
design note; you supply the data.

**5. Descent and climb flow.** Give core a recommendation for F10, consistent with end of flight's
thrust-scaled burn with an idle floor (`results/eof-descent-fuel-oct09/README.md`).

## Rules

- Light compute only. Take no heavy lock; use at most 4 threads.
- Every result note opens with its sources and declared deviations.
- Every chart carries a footnote beneath it: data, parameters, assumptions.
- Cite printed pages. Never cite an unauthorised copy of a copyrighted manual.
- Record every use of confidential or unverified material in `results/restricted-sources-ledger.md`.
- Commit as `MH370-iso-agents` / `mh370-iso@invalid` on branch `claude-science-sep29`.
- **The target is the bundled core re-run** (about 10-11 October). If the internal model is ready
  before core's smoke tests finish, core may use it in that run.
  - Deliver in this order: (1) the internal model's tables and calibration, (2) the cross-check,
    (3) the public model.
  - Post each piece to `coordination/CORE_STAGES.md` when it is ready.
