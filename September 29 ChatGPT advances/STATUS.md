# September 29 ChatGPT advances — fuel milestone

## Completed in first implementation increment

- Preserved `ISO Sept 28 Status` as the frozen baseline.
- Added `code/fuel.rs` as a table-agnostic fuel-state core.
- Fuel state carries remaining fuel, particle-level flow calibration factor, and continuous (within-step) exhaustion time.
- Fuel advance accepts the same `dt` used by the aircraft propagation loop.
- Added a `FuelFlowModel` interface so the Ulich 9M-MRO workbook can be supplied by an adapter rather than embedded in flight dynamics.
- Added a deterministic synthetic fuel-flow model for plumbing/regression tests only.
- Added unit tests for exact accounting, within-step exhaustion timing, flow-factor/endurance scaling, zero-dt neutrality, and state-dependent synthetic flow.

## Design constants / provenance to preserve

- Fuel anchor: 43,800 kg at 17:06:43 UTC (approved Sept 28 design; uncertainty to be applied when integrated).
- Particle flow-factor prior: approximately N(1.009, 0.018).
- The 00:19:29 log-on is NOT used to calibrate pre-00:11 fuel state; it belongs to the EOF stage.
- Real table source expected: `ulich-9M-MRO-fuel-model-v5.6-public.xlsm`.

## Not yet claimed

- The Rust tests have not been executed in a compiler/runtime by this ChatGPT harness; the code has been committed but execution remains to be verified.
- The Ulich workbook/table adapter is not implemented because the workbook bytes are not presently available.
- Fuel is not yet patched into the frozen September 28 `flight::Aircraft`; that baseline remains untouched intentionally.
- No fuel-on A/B particle-filter run or 00:11 PDF has been produced yet.

## Next integration increment

1. Copy the active flight/filter source into this September 29 workspace (or patch a working-tree copy, never the frozen baseline).
2. Add optional `FuelState` to each particle/aircraft state.
3. At each existing 5–10 s propagation step, evaluate flow from instantaneous Mach, altitude, gross weight and temperature, then call `FuelState::advance` with exactly that `dt`.
4. Verify fuel-disabled execution is bit-for-bit identical to baseline for a fixed seed.
5. Once the Ulich workbook is available, implement/extract its table adapter and reproduce the Boeing validation cases before the scientific A/B filter run.
6. Run fuel-off vs fuel-on with matched seeds/particle counts; compare posterior geography, Mach distribution, ESS/resampling history, fuel remaining at 00:11, predicted exhaustion distribution, and repeated-seed stability.
