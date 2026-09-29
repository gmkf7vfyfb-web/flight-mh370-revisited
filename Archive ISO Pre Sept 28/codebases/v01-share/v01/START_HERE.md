# Corrected MH370 estimator release v0.1 — start here

This is the corrected v0.1 milestone capsule for the canonical broad-flight
estimator. It preserves a reproducible calculation, its complete all-epoch
diagnostics, and the evidence needed to audit why the calculation is not yet a
publishable location estimate.

## Release status at a glance

| Flight | Role | Provenance/model closure | Numerical support | Publication status |
| --- | --- | --- | --- | --- |
| MH371 | Known-flight diagnostic; truth read only by the reporter | Validator passed | Failed | Diagnostic only |
| MH370 | Accident-flight all-SATCOM-epoch diagnostic; no truth supplied | Validator passed | Failed | Diagnostic only |

Both native reports carry the watermark
`FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY`. A validator pass means the
producer, configuration, inputs, complete family/seed snapshot set, reporter,
and rendered files agree by hash. It does not mean that the particle
population, root genealogy, or independent seeds support a geographic
probability claim.

Accordingly, this release provides **no MH370 crash coordinate, impact
posterior, credible search box, operational search ranking, or recommended
search area**. Do not extract one from a colour maximum, pooled mean, contour,
or historical file.

## What is corrected

The canonical model is `broad-powered-marked-jump-v1`, run by
`estimate-broad-flight`. It does not assume one lateral-control mode followed
by one turn. The release keeps visible:

- five initial lateral-control modes with declared equal, uncalibrated weight;
- four recurring-event-rate families with declared equal, uncalibrated
  weight;
- repeated lateral, speed, and altitude events;
- independent numerical seeds and prior-root genealogy;
- BTO-only and BTO-plus-BFO as separate scientific families; and
- the spatial consequences of mode and rate choices at every retained epoch.

These alternatives broaden the old support, but they do not constitute an
empirically calibrated probability distribution over every possible control
history.

## Read and verify in this order

1. Read [Scientific boundaries](SCIENTIFIC_BOUNDARIES.md).
2. Open the [artifact guide](ARTIFACT_GUIDE.md) to distinguish human views
   from authoritative native artifacts.
3. Inspect the native report JSON before quoting a map or metric:
   - [MH371 report audit](workspace/runs/mh371/broad-flight-truth-control/diagnostic-report/broad_snapshot_diagnostic.json)
   - [MH370 report audit](workspace/runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/broad_snapshot_diagnostic.json)
4. Inspect each adjacent `release-validation.json` and the parent
   `run-manifest.json`.
5. Follow [REPRODUCE.md](REPRODUCE.md) for byte verification, tests, inference,
   reporting, and validation commands.
6. Use [CHATGPT_HANDOFF.md](CHATGPT_HANDOFF.md) when handing the capsule to an
   independent analysis harness.

The final capsule-wide `SHA256SUMS` ledger and `tools/verify_capsule.py` verify
packaged bytes. The nested run manifests and report audits establish scientific
lineage. Neither substitutes for the report's numerical-support assessment.

## Main human-readable views

- [MH371 broad known-flight PDF](views/mh371/broad_snapshot_diagnostic.pdf)
  and [all-epoch PNG](views/mh371/broad_snapshot_diagnostic.png)
- [MH370 broad all-epoch PDF](views/mh370/broad_snapshot_diagnostic.pdf)
  and [all-epoch PNG](views/mh370/broad_snapshot_diagnostic.png)
- [Davey et al. reference paper](views/reference/davey/davey-2016-bayesian-search-paper.pdf)
- [Posterior-independent search-evidence atlas](views/search-areas/evidence-atlas.pdf)

The MH370 PDF retains every physical SATCOM epoch, including
propagation-only, likelihood-disabled checkpoints where appropriate. It has no
held-back truth and makes no accuracy claim. Its per-epoch support panels and
the PNG overview are the broad run's arc/support views; there is no separate
run-produced arc GeoJSON or SVG.

## MH371 truth boundary

The MH371 runner never reads later aircraft positions. The held-back truth CSV
is opened only by the reporter after the inference artifacts have been
finalized. That is byte-level truth separation, not a fully prospective blind
trial. A pilot inspection moved the final selected control window from 06:59
to 06:48 to avoid the known descent turn. The selection-window design was
therefore partly truth-informed, and all MH371 distance and coverage results
must retain that caveat. One known flight cannot calibrate general coverage for
MH370.

## Context that is not estimator output

The Davey paper and recreation package are methodological and historical
references. The former canonical-versus-Davey plot used the superseded
one-turn chain and is excluded from the corrected release views.

The search-evidence atlas records official, reported, and contextual search
geometry. It is not a searched/not-searched probability mask, is not multiplied
into the broad filter, and is not an operational plan. The old planning tiles
were conditioned on the superseded narrow impact population and are excluded.

## Withdrawn package warning

An earlier package labelled v0.1 was withdrawn after release selection picked
the older one-turn runner and its downstream artifacts instead of the current
broad-flight implementation. Its narrow 00:11, continuation, impact, Davey
comparison, and search-planning products are historical controls only. This
corrected capsule supersedes that package; do not mix files between them.

