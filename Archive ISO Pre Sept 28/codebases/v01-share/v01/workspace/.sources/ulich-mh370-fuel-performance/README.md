# Ulich MH370 fuel/performance source recreation

This directory is an isolated, clean-room recreation of what can be checked with public equations and safely derived inputs. It is not a transcription of the Ulich workbook, is not a Boeing or Rolls-Royce performance model, and is not eligible to initialize the product estimator.

## Result

The mandatory official anchor is preserved exactly at `2014-03-07T17:06:43Z`: ZFW 174,369 kg, total fuel 43,800 kg, pressure altitude 35,004 ft, Mach 0.821, SAT −43.8 °C.

With scale fixed at 1.0, the public proxy predicts the five ACARS interval burns as:

```text
observed kg   1400.000  1300.000  1100.000   900.000   700.000
predicted kg  1563.867  1256.174  1042.943   867.654   653.642
error kg      +163.867   -43.826   -57.057   -32.346   -46.358
```

The observed total is 5,400 kg and the prediction is 5,384.280 kg: −15.720 kg prediction error with 83.933 kg interval RMSE. That close total is cancellation—the first interval over-burn is offset by four under-burn intervals.

Applied unchanged to the rounded, constant-state segments in official Appendix 1.6E Table 3, the proxy burns 14,502.419 kg and ends at 29,297.581 kg. The official calculated ending fuel is 33,524.105 kg, a calculated burn of 10,275.895 kg. The public model therefore over-burns by **4,226.524 kg**. This discrepancy is reproduced and explained, not tuned away.

The printed durations total 4,878.0 s, while the stated Arc‑1 epoch is 4,882.9 s after the anchor. The 4.9 s difference is retained as a printed-duration rounding limitation.

Open [`outputs/report.html`](outputs/report.html) for the self-contained browser report and [`outputs/results.json`](outputs/results.json) for full-precision values.

## Public model

`src/public_performance.py` combines:

- a two-layer ISA pressure calculation with measured/modelled SAT for density and sound speed;
- a generic B772 parabolic drag polar, `CD = CD0 + k CL²`;
- point-mass climb/descent and acceleration thrust terms;
- linear interpolation through installation-adjusted Trent 892 ICAO LTO certification fuel-flow points; and
- the inverse BFFM2 ambient relation, `Wf = Wf,ref δ / (θ^3.8 exp(0.2 M²))`.

Every scientific coefficient is represented in `data/model_parameters.json` as `measured`, `source-derived`, or `model-choice`, with unit, source reference, and note. There are no hidden tuned factors. The code uses only the Python standard library.

The post-ACARS failure is unsurprising once the proxy's domain is made explicit:

- the small ACARS total error is interval-error cancellation during a climb, not independent level-cruise validation;
- the anchor requires only about 19.5% of static rated thrust in this generic polar, whereas ICAO's cited reduced-takeoff interpolation procedure covers 60–100% and warns against extrapolation;
- BFFM2 is emissions/ambient correction machinery, not a 9M‑MRO Trent 892B cruise deck;
- the generic polar omits exact airframe/engine integration and compressibility/wave-drag behavior; and
- Appendix 1.6E says the official calculation used Boeing 777 performance data and Rolls-Royce left/right engine analysis.

Standard-day post-ACARS temperatures also amplify the proxy's `θ^-3.8` behavior relative to the warm measured anchor. These are plausible mechanisms for the systematic gap, not a claim that any one mechanism uniquely contributes a stated number of kilograms.

## Workbook audit

The preserved workbook is read as a ZIP/XML package. VBA is never executed, formulas are never recalculated, add-ins are never loaded, and the external link is never followed.

Pinned preserved artifact:

```text
SHA-256  a45373a2c1a66e920510145a45bfd576a316deced64dde472f8fbb86971f75a3
size     2,376,741 bytes
version  Version 5.6 (Fuel Flow Model!B9)
```

The audit finds 24 sheets, 165 OOXML members, an unsigned VBA project, one external link, a calculation chain, @RISK/Solver names, 2,406 `BicubicInterpolation` formula calls, and Boeing-confidential notices. It exposes only safe metadata, cell locators for calibration indicators, and cryptographic hashes.

A side-by-side, non-executing local audit used the public V5.6 artifact pinned as SHA‑256 `42d150e36a79e2b9493680128e4833f14eebd6c1cc9551c66d00e0c7127d92a4`. All 19 selected performance-range cached/constant value digests are identical between public and preserved artifacts, while 39 OOXML parts differ overall. The range digest scheme and pins are in `data/workbook_pins.json`; no table value is retained here.

The workbook tables remain `audit-only-not-integrated` because confidential notices and mixed provenance prevent safe redistribution, and its endurance model contains event-linked calibration. Even identical hashes do not establish a legal or scientific right to use those tables canonically.

## Circular quantities excluded

The executable inputs contain none of the following:

- the legacy 18:22 fuel quantity;
- the legacy 0.45 t standard deviation; or
- an exhaustion target at 00:17:30.

The official report models about one minute from dual-engine flameout to APU availability and about another minute for SDU startup to the 00:19 handshake. A 00:17:30 exhaustion time back-solved from that event is therefore not independent evidence. `src/recreate.py` checks the executable JSON fixtures for these prohibited literals on every run.

## Pulau Perak stress family

`data/stress_families.json` contains three deliberately broad descent/reclimb counterfactuals. All waypoint values are model choices, all likelihood weights are exactly zero, and `initializer_eligible` is false. Their burns appear only in the stress section; they do not participate in validation, calibration, probability, or initialization.

## Initializer contract and blocker

[`INITIALIZER_CONTRACT.md`](INITIALIZER_CONTRACT.md) and `data/initializer_contract.json` define the implementation interface. Canonical integration is blocked because:

1. the public proxy has an unexplained 4.2265 t level-cruise discrepancy; and
2. the total-fuel anchor does not identify left/right engine-accessible tank/feed state needed for engine-specific flameout.

Resolution requires legally usable, independently validated Trent 892B/B772-relevant cruise performance evidence without fitting Arc 1 or a later event, plus an independently supported tank/feed allocation and uncertainty model for end-of-flight use.

## Reproduce locally

From any directory, the complete deterministic run is one command:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 /jackbox/home/MH370/.sources/ulich-mh370-fuel-performance/src/recreate.py --workbook '/jackbox/home/.iso/thread-storage/MH370-legacy-pre-refactor-20260824/corpus/repositories/flight-mh370-revisited-e0115e817975d073bdf2b09a428fbce62aeda35c/downloads/MH370/9M-MRO Fuel Model V5.X.xlsm'
```

It validates the workbook hash/range pins, recreates the ACARS and post-ACARS comparisons, evaluates the zero-weight stress family, checks 2 s/1 s/0.5 s convergence, generates JSON and HTML outputs, records wall time/peak RSS, and refreshes `SHA256SUMS`. Run-specific performance metrics are intentionally excluded from the scientific fingerprint.

Focused checks:

```bash
cd /jackbox/home/MH370
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s .sources/ulich-mh370-fuel-performance/tests -v
```

The report is deterministic for fixed inputs. `outputs/execution_metrics.json` and its checksum vary with the host/run; the scientific fingerprint in `outputs/results.json` does not.

## Contents

```text
data/                    provenance-tagged parameters, fixtures, pins, contract
src/public_performance.py public clean-room equations
src/workbook_audit.py     non-executing OOXML audit
src/recreate.py           deterministic runner
src/report.py             self-contained HTML renderer
tests/                    focused anchor, discrepancy, audit, and exclusion tests
outputs/                  generated results, audit, metrics, and browser report
citation-ledger.md        passage-located claim ledger
SHA256SUMS                source and artifact hashes
```

Source identities, retrieval URLs, PDF locators, and hashes are in `data/source_manifest.json`; the passage-level evidence trail is in [`citation-ledger.md`](citation-ledger.md). No PDF, workbook, virtual environment, cache, or confidential table is packaged.
