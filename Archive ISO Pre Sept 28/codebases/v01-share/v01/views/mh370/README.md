# MH370 broad all-epoch diagnostic

This view presents the accident-flight filtering diagnostic from the canonical
`broad-powered-marked-jump-v1` runner.

- [PDF: all physical epochs and structural tables](broad_snapshot_diagnostic.pdf)
- [PNG: all-epoch overview](broad_snapshot_diagnostic.png)
- [Authoritative report audit and exact metrics](../../workspace/runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/broad_snapshot_diagnostic.json)
- [Runner manifest](../../workspace/runs/mh370/broad-flight-uncertainty-diagnostic/run-manifest.json)
- [Suite summary](../../workspace/runs/mh370/broad-flight-uncertainty-diagnostic/summary.json)
- [Release validation](../../workspace/runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/release-validation.json)
- [Runner configuration](../../workspace/configs/mh370-broad-powered-flight-diagnostic.toml)
- [Report specification](../../workspace/configs/mh370-broad-snapshot-report.json)

## What is shown

The PDF preserves the five declared initial lateral modes, four declared
recurring-event rate families, repeated lateral/speed/altitude event summaries,
and independent-seed/root diagnostics. BTO-only and BTO-plus-BFO are never
pooled. In BTO-only, physical rows with no enabled likelihood are retained and
labelled as propagation-only checkpoints.

The configured Arc-1 fuel-state anchor appears as a conditional state reset. It
is not a positional observation. Exact per-epoch values and evidence-component
ledgers are in the companion JSON.

The broad reporter does not emit a separate calculated-arc SVG or GeoJSON. Its
per-epoch PDF pages and all-epoch PNG are the run-produced arc/support views.
The `seventh-arc-fl400.geojson` in the search-area view is independent official
context, not an output of this filter.

## No truth and no impact claim

No truth file is supplied for MH370. The report contains no truth marker,
distance-to-truth value, accuracy claim, or calibrated coverage statement.
Every displayed mass is conditional on the named evidence family and declared,
uncalibrated model support.

The run stops at the configured powered-flight SATCOM checkpoint. This release
does not carry the broad population through fuel exhaustion, terminal descent,
glide, impact, drift, hydroacoustic evidence, or image evidence. It therefore
does not publish a crash-site posterior or operational search plan.

## Validation language

A passed release validation proves provenance and model closure: exact producer,
configuration, inputs, complete family/seed snapshot population, report source,
and output hashes. It does not prove numerical support. The authoritative
report JSON can legitimately fail its ESS, genealogy, or cross-seed criteria
and require the visible `DIAGNOSTIC ONLY` watermark.

## Deliberate exclusions

The prior 00:11 BTO/BFO/gain PDFs, R600 frozen continuation, impact-family
figures, and “full overview” are absent. They descended from a fixed-mode,
one-turn chain and would reintroduce false precision if presented as the
current broad result.
