# MH370 Rerun checkpoint 4 — exact ERA5 recovery and resampling-boundary audit

Created 2026-09-19T05:53:13Z.

## Outcome

This work unit removed one physical-replay blocker and closed one estimator-bookkeeping question. It did not run a full-aircraft sampler and does not establish a location probability.

1. The exact 337,328,648-byte ERA5 grid was reconstructed from the saved 11-part Drive object. Each part matched the saved manifest, and the concatenated file matches SHA-256 `73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`.
2. The 18:39/19:41 factor exporter's resampling-boundary formula was independently tested. Under the production runner's default within-stratum resampling policy (zero defensive mixture), the next block input weight is exactly

   `log(previous stratum probability mass) - log(new stratum allocation)`.

   Unequal allocations preserve total stratum mass; a zero-mass stratum fails closed. This rules out a missing allocation correction in this particular diagnostic reconstruction.
3. Fifteen Python controls, 15 precompiled SATCOM tests and 73 precompiled particle-filter tests pass: 103 checks total. The later runner-only exporter remains uncompiled, so these results do not substitute for physical replay.

## What this says about the 18:39/19:41 collapse

The source audit confirms that 18:39:55 and 19:41:02 are assimilated in the same BTO-terminated block. The block wrapper does not forward an auxiliary look-ahead guide, but the physical command/time/event proposals remain guided and retain their `log(prior/proposal)` corrections.

The sequential BFO calibration becomes more selective across the bottleneck:

| Contact | Bias SD before update | Measurement SD | Predictive SD | Bias SD after update |
|---|---:|---:|---:|---:|
| 18:39:55 | 4.8555 Hz | 7 Hz | 8.5191 Hz | 3.9897 Hz |
| 19:41:02 | 3.9897 Hz | 7 Hz | 8.0571 Hz | 3.4662 Hz |

That narrowing is a legitimate target feature, but it does not by itself explain 96–98% descent from one root. The new boundary control removes one possible diagnostic-weight artifact. The remaining live hypotheses are still:

- concentrated BTO/BFO likelihood in the physical states that reach these contacts;
- dynamical/support rejection between contacts;
- high-variance command/time/event proposals with inadequate coverage;
- ordinary genealogical loss after a genuinely narrow but not single-root target region.

The opt-in exporter is designed to separate those terms row by row and verify the complete child-weight identity. No physical factor rows exist yet, so none of the four explanations is promoted to a conclusion.

## Source/target and bridge discipline retained

- Historical matching runs still start at 18:01:49 and anchor fuel at 18:28:05.9.
- The separate final-radar configuration implies 18:22:12 at approximately 6.578 N, 96.340 E. Its position/covariance primary provenance is not yet verified.
- Fuel at the 18:28 anchor cannot be relabelled as fuel at radar. Mapping it backward requires the intervening path-dependent affine preimage and its positive Jacobian.
- A uniformly selected terminal point is proposal support, not an observed endpoint and not an implied posterior.
- The user's 00:15–00:17 exhaustion window remains an explicit conditional sensitivity against the broader 00:15–00:19 reference.
- Hydroacoustic evidence remains excluded.

## Environment recovery

The included receipt and reassembly script make the ERA5 recovery auditable without duplicating 674 MB of final-plus-part bytes inside the portable checkpoint. The multipart folder is Drive ID `1kypp3KKFOwnvOieMH4xHlmFtw7yGpqMJ`; its manifest is `1ogAfQ9O2AV2YB4E_NK2uv5XTGjIjnCz3`.

The exact IGRF broad grid remains open: 5,564,268 bytes, SHA-256 `fbedb84fe68c6e547ff484fec47fbc89e28660fb2010ba4f336d0622467c933f`. A prior review authenticated the official 88,618-byte NOAA `pyIGRF14.zip` and its embedded coefficient file, but the exact broad-grid builder/output are absent locally and not separately searchable in Drive. A differently scoped WSPR grid must not be substituted.

The Rust toolchain was also pruned. `cargo` and `rustc` are absent, and a direct official-toolchain request timed out under the current restricted network. Existing test binaries validate the SATCOM and particle-filter changes compiled before the runner integration; they do not prove the runner exporter compiles.

## Ownership and changes

No sampler lane was acquired and no sampler was launched. Missing shared locks/heartbeats were treated as absence of evidence, not permission to reuse another thread's lane. Only the isolated Rerun candidate was changed. Resolution files and automations were not touched.

## Reproduction

From the extracted checkpoint root:

```bash
python candidate-20260919T0334/verify.py
python -m unittest discover -s candidate-20260919T0334 -p 'test_*.py' -v
```

To reconstruct ERA5 after fetching the Drive parts and manifest:

```bash
python recovered-environment/reassemble_multipart.py \
  --manifest recovered-environment/era5-parts/parts-manifest.json \
  --parts-dir recovered-environment/era5-parts \
  --output recovered-environment/mh370-era5-grid.bin \
  --receipt recovered-environment/era5-recovery-receipt.json
```

After restoring a compatible Rust toolchain and the exact IGRF grid:

1. compile the candidate offline against `candidate-20260919T0334/vendor`;
2. run the archived seed with factor diagnostics disabled and compare every scientific output to the archived result;
3. enable only the 18:39/19:41 block exporter and require unchanged scientific outputs plus exact replay checks;
4. repeat for at least two seeds and analyze BTO, BFO, proposal, support, row ESS, root ESS, evidence and marginal CDF shifts;
5. only then implement and test a guided physical boundary/bridge proposal under matched budgets.

## Limitations

- No runner compilation, full-aircraft replay or physical factor export occurred.
- The dominant cause of the archived ancestry collapse remains unresolved.
- The exact final-radar position/covariance source and exact broad IGRF grid are still missing.
- No replacement estimator is validated, and no calibrated probability or solved location is claimed.

