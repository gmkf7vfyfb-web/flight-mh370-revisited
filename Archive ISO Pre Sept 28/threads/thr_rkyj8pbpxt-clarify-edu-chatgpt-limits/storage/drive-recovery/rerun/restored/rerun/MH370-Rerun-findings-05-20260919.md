# MH370 Rerun checkpoint 5 — exact magnetic-input recovery and source-role correction

Created 2026-09-19T06:44:24Z.

## Outcome

This work unit removes the remaining environmental-data blocker and corrects a source-role error in checkpoint 4. It does not run a full-aircraft sampler and does not establish a location probability.

1. The exact MH370 magnetic grid named by the archived physical and synthetic run configurations was recovered from the preserved Drive extraction: 12,497,900 bytes, SHA-256 `ad71fa679c7933858e8748fa34b124f4e405921b337c92aeb7efeb1002ac6ac1`.
2. Its exact manifest was recovered and authenticated: 3,158 bytes, SHA-256 `6539167e7c8dcac8d6007517eca41aa3987b367791fa40bb768a37bb1b703b16`.
3. The 5,564,268-byte `fbedb8…33f` grid discussed in checkpoint 4 is real and authenticated, but it is `mh371-igrf14-grid.bin`, built for the separate broad repeated-manoeuvre MH371 control. It is not the input named by the MH370 run configurations and must not be substituted.
4. The exact toolchain specification was also recovered: Rust 1.98.0 minimal profile. No compiler binaries are in the preserved upload inventory or local workspace, so candidate compilation remains blocked.

## Evidence for the correction

All eight recovered resolved configs—six production histories and the two 500,000-candidate synthetic histories—name `mh370-igrf14-grid.bin`. Two separately packaged sources agree:

- the bounded-ancestry diagnostic archive;
- the independent synthetic-pair evidence archive.

The two manifests also encode materially different roles:

| Input | Bytes | SHA-256 prefix | Manifest purpose | Reference time |
|---|---:|---|---|---|
| `mh370-igrf14-grid.bin` | 12,497,900 | `ad71fa…6ac1` | repeated-manoeuvre MH370 inference, M1822–M0011 | 2014-03-08 00:00 UTC |
| `mh371-igrf14-grid.bin` | 5,564,268 | `fbedb8…33f` | broad repeated-manoeuvre MH371 control | 2014-03-07 04:00 UTC |

Checkpoint 4's statement that the `fbedb8…33f` grid was the missing physical-replay input was therefore wrong. The correction is now encoded in `test_environment_identity.py`, which checks exact bytes/hashes, manifest roles, all eight recovered configs, and two independent archives.

## What is now ready—and what is not

The exact physical environment inputs are now present:

- ERA5: 337,328,648 bytes, SHA-256 `73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`;
- MH370 IGRF: 12,497,900 bytes, SHA-256 `ad71fa679c7933858e8748fa34b124f4e405921b337c92aeb7efeb1002ac6ac1`.

Nineteen Python/source checks, 15 precompiled SATCOM tests, and 73 precompiled particle-filter tests pass: 107 checks total. The runner-only 18:39/19:41 exporter still has not been compiled. The precompiled Rust binaries predate that integration and cannot prove it builds or preserves scientific outputs.

The only remaining environment blocker to physical replay is the compatible Rust 1.98.0 compiler. Until it is restored, the run-by-run decomposition of BTO, BFO, proposal correction, support rejection, row ESS, and root ESS cannot be produced. Therefore the relative contribution of legitimate likelihood concentration, proposal undercoverage, support loss, and ordinary genealogical loss remains unresolved.

## Ownership and scientific boundaries

No sampler lane was acquired or launched. Missing shared locks/heartbeats were not treated as permission to reuse another thread's lane. The work was confined to the isolated Rerun candidate and recovered environment files; the Resolution investigation was not touched.

The source/target distinctions remain unchanged:

- historical matching runs start at 18:01:49 and anchor fuel at 18:28:05.9;
- the separate final-radar target implies 18:22:12 near 6.578 N, 96.340 E, but its primary position/covariance provenance is still unresolved;
- fuel at the 18:28 anchor cannot be relabelled as radar fuel without a path-dependent inverse and Jacobian;
- endpoint bands are proposals, not observations;
- 00:15–00:17 remains a conditional hypothesis to compare against 00:15–00:19;
- hydroacoustics remains excluded.

## Reproduction

From the extracted checkpoint root:

```bash
python candidate-20260919T0334/verify.py
python -m unittest discover -s candidate-20260919T0334 -p 'test_*.py' -v
sha256sum recovered-environment/mh370-igrf14-grid.bin
```

`verify.py` returns the documented blocked status while Cargo is absent, but its executable Python and source-audit stages pass. The exact magnetic inputs and recovery receipt are included in this portable checkpoint; the much larger exact ERA5 file remains referenced by its authenticated multipart receipt and reassembly script.

After restoring Rust 1.98.0:

1. compile the isolated candidate offline against its vendored dependencies;
2. replay an archived seed with factor diagnostics disabled and require scientific-output identity;
3. enable only the 18:39/19:41 exporter and require unchanged scientific outputs plus child-weight identity;
4. repeat for at least two seeds, then attribute concentration to measurement, proposal, support, and resampling terms;
5. only then implement and compare a valid guided boundary/bridge proposal under matched budgets.

## Limitations

- No runner compilation, new full-aircraft replay, or physical factor export occurred.
- The dominant cause of the archived ancestry collapse remains unresolved.
- The exact final-radar position/covariance primary source remains missing.
- No replacement estimator is validated; no calibrated probability or solved location is claimed.
