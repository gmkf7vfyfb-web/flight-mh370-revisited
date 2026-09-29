# Artifact guide

This guide distinguishes convenient human views from authoritative native run
artifacts. All links are relative to the `v01` directory.

## MH371 broad known-flight diagnostic

- [Print-layout diagnostic PDF](views/mh371/broad_snapshot_diagnostic.pdf)
- [All-epoch PNG overview](views/mh371/broad_snapshot_diagnostic.png)
- [View notes](views/mh371/README.md)
- [Authoritative report audit and metrics](workspace/runs/mh371/broad-flight-truth-control/diagnostic-report/broad_snapshot_diagnostic.json)
- [Runner manifest](workspace/runs/mh371/broad-flight-truth-control/run-manifest.json)
- [Suite summary](workspace/runs/mh371/broad-flight-truth-control/summary.json)
- [Release validation](workspace/runs/mh371/broad-flight-truth-control/diagnostic-report/release-validation.json)
- [Runner configuration](workspace/configs/mh371-broad-powered-flight-control.toml)
- [Report specification](workspace/configs/mh371-broad-snapshot-report.json)
- [Held-back scorer truth](workspace/inputs/controls/mh371-truth.csv)

The PDF reports each selected SATCOM epoch, held-back truth accuracy, numerical
root/seed diagnostics, recurring event counts, and final structural-sensitivity
tables. It is a known-flight test of the method, not evidence about MH370.

## MH370 broad all-epoch diagnostic

- [Print-layout diagnostic PDF](views/mh370/broad_snapshot_diagnostic.pdf)
- [All-epoch PNG overview](views/mh370/broad_snapshot_diagnostic.png)
- [View notes](views/mh370/README.md)
- [Authoritative report audit and metrics](workspace/runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/broad_snapshot_diagnostic.json)
- [Runner manifest](workspace/runs/mh370/broad-flight-uncertainty-diagnostic/run-manifest.json)
- [Suite summary](workspace/runs/mh370/broad-flight-uncertainty-diagnostic/summary.json)
- [Release validation](workspace/runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/release-validation.json)
- [Runner configuration](workspace/configs/mh370-broad-powered-flight-diagnostic.toml)
- [Report specification](workspace/configs/mh370-broad-snapshot-report.json)

The PDF retains every physical SATCOM epoch, including propagation-only
checkpoints in evidence families where that row's likelihood is disabled. No
truth was supplied, so it contains no accuracy claims. The broad run does not
produce a standalone arc SVG or GeoJSON: the PDF's per-epoch spatial-support
pages and the PNG overview are the run-produced arc/support views.

## Numerical and provenance status

The report JSON is authoritative for exact values and contains:

- the declared five initial lateral modes and four recurring-event rates;
- per-epoch evidence-component and observation-kind ledgers;
- particle ESS, root ESS, maximum root mass, map-capture checks, and seed
  spread;
- recurring lateral, speed, and altitude event counts;
- per-mode and per-rate conditional spatial summaries;
- MH371 truth distance and coverage fields, when applicable;
- exact hashes of the reporter, report spec, source snapshots, summaries,
  truth file, PDF, and PNG; and
- `numerical_support.status`, watermark, criteria, and publication flag.

The adjacent release validation verifies provenance and model closure. Its
`status: passed` must not be reported as a numerical-support pass.

## Davey reference

- [Davey et al., *Bayesian Methods in the Search for MH370*](views/reference/davey/davey-2016-bayesian-search-paper.pdf)
- [Reference notes](views/reference/davey/README.md)
- [Complete local recreation package](workspace/.sources/davey-2016-bayesian-search/README.md)

The earlier canonical-versus-Davey plot is deliberately excluded from the
current views because its canonical curve came from the superseded
one-turn/frozen-continuation chain. It may remain only as explicitly historical
output inside the source-recreation package.

## Search-area context

- [Search-evidence atlas PDF](views/search-areas/evidence-atlas.pdf)
- [PNG](views/search-areas/evidence-atlas.png)
- [SVG](views/search-areas/evidence-atlas.svg)
- [Combined atlas geometry](views/search-areas/search-evidence-atlas.geojson)
- [Official-source FL400 seventh arc](views/search-areas/seventh-arc-fl400.geojson)
- [Area inventory](views/search-areas/area-inventory.json)
- [Evidence register](views/search-areas/evidence-register.json)
- [Readiness record](views/search-areas/readiness.json)
- [Located-passage citation ledger](views/search-areas/citations.json)
- [Source lock](views/search-areas/sources.lock.json)
- [Interpretation notes](views/search-areas/README.md)

These are independent evidence/context products. They are not broad-run output,
not a calibrated negative-search likelihood, and not an operational search
plan. The old baseline planning PDF and selected-tile geometry are excluded
because their input population came from the superseded narrow impact chain.

## Reproduction materials

- [Reproduction commands](REPRODUCE.md)
- [Scientific boundaries](SCIENTIFIC_BOUNDARIES.md)
- [Independent-harness handoff](CHATGPT_HANDOFF.md)
- `workspace/crates/`: complete canonical Rust product and Python reporting
  code
- `workspace/inputs/`: frozen normalized runtime inputs and manifests
- `workspace/.sources/`: selected source recreations and provenance packages
- `workspace/vendor/`: vendored Rust dependencies
- `bin/linux-x86_64/mh370-v0.1`: exact retained-run producer
- `SHA256SUMS`: capsule-wide byte ledger

## Not in the corrected release

Do not look for or substitute, among the current release views, the old
medium-BFO MH371 control, final-arc BFO sensitivity, narrow MH370 00:11
reports, R600 frozen continuation, impact families, old full overview, Davey
comparison, or baseline search tiles. Their exclusion prevents polished
one-turn products from being mistaken for the broad repeated-event result.
Some source-recreation packages can retain historical outputs for audit; those
files are not current result artifacts.
