# MH370/MH371 public-data particle-filter validation

This repository contains the first executable validation stage for the design in
`MH370_baseline_design_and_evidence_spec_v0.2.md`.

The immediate experiments are deliberately narrower than the eventual MH370
endpoint analysis:

- `MH371-IOR`: sequential inference at each usable Indian Ocean Region BTO
  observation, initialized from a predeclared early known state and scored
  against withheld ACARS positions;
- `MH370-EARLY`: sequential inference over the known pre-loss portion of MH370,
  using actual early SATCOM observations and withheld ACARS/Mode-S positions;
- one density plot per assimilated BTO epoch, with 50%, 90%, and 99% highest
  density contours, plus a combined multi-page PDF for each experiment.

## Scientific status

This is a validation implementation, not yet the production 18:22-to-00:11
endpoint filter. It exercises ingestion, satellite geometry, robust BTO and BFO
likelihoods, AFC reconstruction, persistent sparse control changes, sequential
Monte Carlo, equal-area density estimation, coverage scoring, grid/kernel
diagnostics, and independent-seed comparison. Aircraft-specific performance,
ERA5, fuel exhaustion, magnetic-heading modes, and the later-flight initial
state are deliberately inactive in this validation stage.

For MH371, no public operator-grade morning ephemeris has been located. Runs
therefore retain the public-TLE/STK source identity and treat orbit error as a
shared scenario. No known aircraft position is used to fit satellite state or
the AFC correction.

## Reproduction

The registered first validation run is:

```bash
PYTHONPATH=src python scripts/run_validation.py \
  --flight both \
  --particles 150000 \
  --plot-sample 100000 \
  --offspring-factor 8 \
  --seed 370371 \
  --bto-sigma-us 40 \
  --bfo-sigma-hz 6 \
  --output-dir output/results
```

Each parent supplies eight independent transition-prior children. Children carry
exact parent-weight/8, are weighted globally by the observation, and only then
are contracted by systematic resampling. This is bootstrap SMC enrichment, not
best-child selection. Check `*_diagnostics.csv` and the manifest's
`resolution_diagnostic` before rendering contours; any arc below 100 effective
weighted candidates or 100 unique parent ancestors is flagged for a larger run.

The independent-seed sensitivity run uses 75,000 particles, eight children per
parent, and seed `371370`. It is a geometry check rather than a second primary
estimate. Contour diagnostics compare 2.5/5 km grids and 5/10/20 km declared
display kernels. See `VALIDATION_REPORT.md` for results and interpretation.

The frozen seven-message MH371 subset is `X008` (01:37:12.461), `X012`
(01:55:34.920), `X016` (03:20:21.417), `X019` (03:59:06.915), `X023`
(05:10:27.911), `X029` (06:09:44.409), and `X033` (06:48:30.907), all clean
IOR/R1200 cluster representatives. Early MH370 uses the three parser-declared
representatives at 16:41:52.907, 16:55:23.907, and 17:06:49.406.

MH371's additive oscillator bias is frozen before validation as the median of
22 clean, non-logon, message-leading IOR/R1200 receives between 01:07 and 01:29,
using a stationary aircraft at the approximate mapped Beijing airport position.
The current public orbit/Figure-11 branch gives about 169.33 Hz. Early MH370
uses the ATSB-published 152.5 Hz value. Future ACARS states are not used in
proposals or likelihoods.

The final run manifest records source hashes, timestamps, seed, particle and
offspring counts, transition parameters, measurement uncertainty, software
versions, the gate-calibration records, and every selected observation.

## Diagnostics and PDF rendering

```bash
PYTHONPATH=src python scripts/diagnose_contours.py \
  --particles output/results/mh371_particles.csv \
  --summaries output/results/mh371_summaries.csv \
  --output-dir output/diagnostics \
  --prefix mh371

PYTHONPATH=src python scripts/compare_contour_runs.py \
  --run-a output/results/mh371_particles.csv \
  --run-b output/replicate/mh371_particles.csv \
  --output-dir output/stability \
  --prefix mh371

PYTHONPATH=src python scripts/render_results.py \
  --particles output/results/mh371_particles.csv \
  --summaries output/results/mh371_summaries.csv \
  --truth output/results/mh371_truth.csv \
  --arcs output/results/mh371_arcs.csv \
  --convergence output/diagnostics/mh371_contour_convergence.csv \
  --stability output/stability/mh371.csv \
  --output-dir output/pdf/mh371
```

Use the corresponding `mh370_early` files for the early-MH370 packet. The
rendered map is in longitude/latitude for interpretability, while the PDF and
HDR thresholds are calculated on a Lambert azimuthal equal-area grid. The fixed
10 km kernel is a declared visualization regularizer, not observation noise.

## Later MH370 provisional posterior (18:22-00:11)

The later-flight branch is deliberately labelled **provisional F0**. It uses
the registered direct-18:22 sensitivity initialization and six stable R1200
observations from 18:28 through 00:10:59.928. The conflicting 18:25 records,
C-channel records, and every 00:19 observable are excluded. See
`data/MH370_LATER_NOTES.md` for the evidence boundary and limitations.

```bash
PYTHONPATH=src python -m mh370_pf.data_mh370_later

PYTHONPATH=src python scripts/run_validation.py \
  --flight mh370-later \
  --particles 100000 \
  --plot-sample 25000 \
  --offspring-factor 4 \
  --seed 370371 \
  --output-dir output/later_results

PYTHONPATH=src python scripts/diagnose_contours.py \
  --particles output/later_results/mh370_later_particles.csv \
  --summaries output/later_results/mh370_later_summaries.csv \
  --output-dir output/later_diagnostics \
  --prefix mh370_later
```

The accepted review package also includes an independent 75,000-particle seed
check. Only the first arc passes every declared cross-seed geometry criterion;
the later inner HDRs are explicitly marked seed-sensitive in the PDFs.

### WSPR diagnostic overlay

The published WSPR-derived Table 5 position indicators can be overlaid without
altering the SATCOM posterior:

```bash
PYTHONPATH=src python scripts/compare_wspr_diagnostic.py \
  --particles output/later_results/mh370_later_particles.csv \
  --summaries output/later_results/mh370_later_summaries.csv \
  --wspr-indicators data/processed/mh370_wspr_published_indicators.csv \
  --output output/wspr_diagnostic/mh370_later_wspr_comparison.csv

PYTHONPATH=src python scripts/render_results.py \
  --particles output/later_results/mh370_later_particles.csv \
  --summaries output/later_results/mh370_later_summaries.csv \
  --truth output/later_results/mh370_later_truth.csv \
  --arcs output/later_results/mh370_later_arcs.csv \
  --convergence output/later_diagnostics/mh370_later_contour_convergence.csv \
  --stability output/later_stability/mh370_later.csv \
  --wspr-indicators data/processed/mh370_wspr_published_indicators.csv \
  --output-dir output/pdf/mh370_later_wspr_primary
```

This is a diagnostic overlay, not a WSPR-weighted posterior. Table 5 positions
are author-derived outputs selected during path construction, and no calibrated
WSPR detection/false-positive likelihood has been supplied. Consequently each
WSPR log-weight increment is fixed at zero.

### QTR901 known-track WSPR calibration

The first calibration gate reproduces the published QTR901 table and then
constructs a score-blind sampling frame from the raw WSPR archive. It retains
the strict <=1 nmi primary endpoint and reports <=5 and <=20 nmi sensitivity
analyses separately:

```bash
PYTHONPATH=src python scripts/run_wspr_calibration.py
PYTHONPATH=src python scripts/render_wspr_calibration.py
```

See `WSPR_CALIBRATION_REPORT.md` and `output/pdf/wspr_calibration/`. The strict
raw endpoint has only two eligible positives, so it does not calibrate
detection sensitivity. This result does not change the zero WSPR likelihood
weight in the MH370 posterior.

## Output integrity and progress

The validation runner prints a flushed progress line after every observation
epoch. Each result CSV is first written to a temporary file in its destination
directory, flushed and synced, checked for the expected data-row count, hashed,
and then atomically renamed into place. The run manifest records each result's
row count, byte size, SHA-256 digest, and publication method. The manifest is
also flushed, synced, and atomically published.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -q
```
