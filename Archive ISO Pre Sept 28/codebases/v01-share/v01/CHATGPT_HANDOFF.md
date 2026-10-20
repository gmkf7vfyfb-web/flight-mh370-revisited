# Handoff for an independent ChatGPT or analysis harness

This capsule is intended to be understandable without the conversation that
produced it. Treat files and hashes as authoritative; do not infer scientific
status from filenames, a polished figure, or the historical v0.1 material that
was deliberately excluded.

## Start in this order

1. Run `python3 -B tools/verify_capsule.py` from the `v01` directory.
2. Read [SCIENTIFIC_BOUNDARIES.md](SCIENTIFIC_BOUNDARIES.md).
3. Read [REPRODUCE.md](REPRODUCE.md).
4. Inspect the two native report audits:
   - `workspace/runs/mh371/broad-flight-truth-control/diagnostic-report/broad_snapshot_diagnostic.json`
   - `workspace/runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/broad_snapshot_diagnostic.json`
5. Inspect each adjacent `release-validation.json`, then its runner
   `run-manifest.json` and `summary.json`.
6. Read `workspace/AGENTS.md` and `workspace/README.md` before proposing code
   changes.

The curated PDFs are entry points for humans. The native JSON and manifest
chain is the source of exact numerical and provenance claims.

## Provenance chain

```text
runner TOML + exact binary + frozen scientific inputs
        |
        v
run-manifest.json -> every family/seed snapshot index and CSV + summary
        |
        v
report specification + reporter source + optional MH371 truth
        |
        v
broad_snapshot_diagnostic.json -> PDF and PNG hashes
        |
        v
release-validation.json -> capsule SHA256SUMS
```

Breaking or copying only part of this chain invalidates a reproduction claim.
In particular, do not detach a diagnostic JSON from its native directory: its
paths are deliberately relative to the report audit so the complete workspace
can be relocated as a unit.

## What the current method is

The canonical command is `estimate-broad-flight`, and the required model
family is `broad-powered-marked-jump-v1`. It carries five initial lateral modes
and four recurring-event rate families. Lateral, speed, and altitude events can
occur repeatedly. The displayed equal prior weights are declared and
uncalibrated.

The report keeps BTO-only and BTO-plus-BFO families separate. It may pool
independent deterministic seeds equally inside one named family, but it must
never pool scientific families and call the resulting spread uncertainty.

The runner's built-in posterior PDF/PNG/SVG outputs are disabled for these
release configurations. The only current spatial reports are generated from
the all-epoch snapshot CSVs by `broad_snapshot_report.py`, which refuses
publication language when numerical support fails.

The final-only posterior CSV and posterior-handoff outputs are also
intentionally suppressed in these snapshot-release configurations. The
manifest-hashed all-observation snapshot CSVs are the complete reporting
population; absence of the older final-only files is not evidence of an
incomplete run. The release validator checks that the files present and absent
agree exactly with the recorded output configuration.

## The two flight roles

### MH371

MH371 is a truth-separated known-flight diagnostic at the runner-input level.
Later aircraft state is absent from inference-visible bytes. The reporter alone receives
`workspace/inputs/controls/mh371-truth.csv`, after inference is complete, and
adds per-epoch error and coverage diagnostics. Never pass that file to the
runner, derive a prior from it, or treat its performance as a calibrated
coverage guarantee for MH370.

Do not call this a fully prospective blind trial. A pilot inspection moved the
final selected window from 06:59 to 06:48 to avoid the known descent turn, so
the control-window design was partly truth-informed even though runner inputs
contain no later aircraft state. The selection record in
`workspace/.sources/mh371-known-flight-data/README.md` is authoritative.

MH371 has no fuel anchor. Its source fuel and mass reuse the declared MH370
source proxy as a model-conditional prior; no MH370 Arc-1 fuel anchor may be
imported to make the control appear better.

### MH370

MH370 has no truth file. Its reporter invocation deliberately omits `--truth`.
The report must not contain accuracy, distance-to-truth, or empirical coverage
claims. In the BTO-only family, physical epochs carrying no active BTO
likelihood remain visible as propagation-only checkpoints rather than being
dropped or mislabeled.

The configured fuel-state anchor is a conditional reset, not a positional
measurement. Terminal flight and impact modelling are withheld from this
release.

## How to interpret pass and fail

`validate_broad_release.py` is a provenance and model-closure validator. A pass
means, among other things, that:

- the canonical broad command and model family were used;
- multiple seeds, initial modes, and recurring-event families are present;
- input, binary, configuration, snapshot, summary, report-source, and output
  hashes close;
- every configured family and seed is represented; and
- no legacy fixed-route artifact has been substituted.

A validator pass is compatible with a failed numerical-support assessment.
The latter is recorded under `numerical_support` in the diagnostic JSON and is
printed as a watermark in the PDF/PNG. Never translate “release validation
passed” into “posterior converged,” “location probability is accurate,” or
“ready for operational search.”

When reporting exact values, read them programmatically from the native JSON.
Do not copy a number from this handoff, infer it from a plot, or reuse a value
from a prior narrow-model report.

## Non-negotiable scientific rules

- Do not describe equal structural weights as empirically calibrated.
- Do not average BTO-only and BTO-plus-BFO geography.
- Do not hide initial-mode or maneuver-rate geographic consequences inside a
  pooled contour.
- Do not use later MH371 aircraft truth during inference.
- Do not call display smoothing a credible region calculation; exact metrics
  use unsmoothed weights.
- Do not interpret root descendants as independent particles.
- Do not infer an impact location from a powered-flight checkpoint.
- Do not apply searched-area polygons as binary exclusion or a negative
  likelihood without a calibrated detection model.
- Do not substitute an old one-turn, fixed-track, fixed-waypoint, or
  frozen-continuation artifact when the broad result is unresolved.

## Intentionally excluded historical products

The prior public capsule contained polished but scientifically narrower
products. They are not current v0.1 results:

- the MH371 “medium-BFO control” and final-arc BFO sensitivity;
- the MH370 00:11 BTO/BFO/gain PDFs;
- the R600 frozen continuation and seventh-arc PDF;
- downstream impact-family PDFs and the old full overview;
- the canonical-versus-Davey latitude comparison; and
- the baseline search-planning sensitivity and selected tiles.

Those products assumed a fixed mode, one turn, or a downstream population
derived from that chain. A source-recreation directory or private history may
preserve them with explicit historical labels, but a harness must not expose
them as corrected release views or list them in the current result manifest.

## Reference material

The curated Davey view contains the original paper, not the stale comparison.
Its complete reproduction materials live at
`workspace/.sources/davey-2016-bayesian-search`.

The search-area view is posterior-independent context. Its complete source and
evidence ledger lives at
`workspace/.sources/mh370-seabed-search-coverage`. The official-source seventh
arc there is context for mapped search activity, not a trajectory or arc
generated by the broad run.

Upstream source packages for SATCOM, MH371 selection, ERA5, IGRF, powered
feasibility, and fuel are retained under `workspace/.sources`. Restricted or
bulky raw upstream datasets may be identified by hash rather than redistributed;
the normalized runner inputs themselves are present.

## Safe assessment procedure

An independent harness should:

1. verify the capsule ledger;
2. run both release validators against the exact packaged binary;
3. confirm each diagnostic's `probability_interpretation`, family separation,
   truth role, numerical-support status, and publication flag;
4. confirm all manifest-listed snapshots exist and hash correctly;
5. compare per-epoch mode/rate spatial summaries and independent-seed spread;
6. report limitations before quoting accuracy or geography; and
7. identify the release as a milestone diagnostic, not a final crash-site
   estimate.

If any required file or hash fails, stop. Do not repair the capsule by mixing
files from another run, regenerating one panel only, or weakening a threshold.
