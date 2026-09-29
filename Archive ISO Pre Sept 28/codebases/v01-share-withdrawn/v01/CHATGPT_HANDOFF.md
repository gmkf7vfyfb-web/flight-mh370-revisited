# Handoff for an independent ChatGPT or automated assessment harness

Use the following as the initial task prompt after making this capsule
available to the assessor:

> Audit and reproduce the MH370 Bayesian estimator milestone v0.1 contained in
> this directory. Treat files and hash manifests as evidence; do not trust
> prose without locating the supporting configuration, input, code, or output.
> First run `python3 tools/verify_capsule.py`. Then read `START_HERE.md`,
> `PROVENANCE.md`, `SCIENTIFIC_BOUNDARIES.md`, `workspace/AGENTS.md`,
> `workspace/README.md`, and
> `workspace/runs/mh370/release-v0.1/release-manifest.json`. Trace the central
> inference path from the runner through each selected scientific spoke and
> verify units, coordinate frames, time basis, seeds, input identities,
> executable identity, ESS/convergence reporting, and artifact hashes. Keep
> structural families separate. Never promote a conditional, display-only,
> diagnostic-zero-weight, or provisional result into the central posterior.
> Report independently: (1) integrity and provenance, (2) reproducibility,
> (3) numerical and software correctness, (4) scientific assumptions and
> limitations, (5) whether each published statement is supported, and (6) any
> material defect. Do not rerun the large production suite until the retained
> artifacts and lightweight tests have been assessed.

## Ground truth for orientation

The product is a Rust command-line runner using a hub-and-spoke architecture.
The runner owns deterministic setup and orchestration. Scientific equations
belong to focused crates for flight dynamics, SATCOM, end-of-flight behaviour,
ocean drift, hydroacoustics, antenna gain, particle filtering, and reporting.

The canonical central checkpoint is three separately reported 00:11 UTC model
families, five independent seeds, and 30,000 particles per seed: 450,000 total
evaluated posterior particles. The families are:

- BTO only;
- BTO plus medium BFO;
- BTO plus medium BFO plus conditional antenna gain.

The medium-BFO family is continued through the corrected R600 BTO contact at
00:19:29 using typed posterior handoffs. End-of-flight results are explicit
conditional families and are never pooled into one posterior over structural
models.

The release's reported family means are:

- BTO only: 36.4895 degrees south, 89.3491 degrees east;
- BTO plus medium BFO: 36.4086 degrees south, 89.4961 degrees east;
- conditional gain: 36.4095 degrees south, 89.4923 degrees east;
- primary conditional impact family: 38.1596 degrees south,
  89.4088 degrees east.

These are calculated, model-conditional outputs, not observed crash
coordinates.

## Evidence-status rules

- **Central:** SATCOM estimator outputs and the typed R600 continuation.
- **Conditional:** antenna-gain and end-of-flight families; report separately.
- **Diagnostic, zero weight:** the present ocean-drift and hydroacoustic
  packages; they are not admitted into the central posterior.
- **Display only / unresolved:** Pléiades spatial comparisons at available
  numerical resolution.
- **Provisional:** searched-area planning sensitivities; no calibrated
  negative-search likelihood is present.
- **Control only:** MH371 is a truth-separated known-flight validation. It is
  not evidence about MH370.

## High-value audit entry points

- Product contract: `workspace/AGENTS.md`
- Product overview and exact commands: `workspace/README.md`
- Release record: `workspace/runs/mh370/release-v0.1/release-manifest.json`
- Release verifier: `workspace/runs/mh370/release-v0.1/validate-release.py`
- Producer source lock:
  `workspace/runs/mh370/release-v0.1/impact/source-tree.lock.json`
- Core run manifest:
  `workspace/runs/mh370/0011-core-comparison/run-manifest.json`
- R600 run manifest:
  `workspace/runs/mh370/0011-to-0019-seventh-arc-bto/run-manifest.json`
- Impact suite:
  `workspace/runs/mh370/release-v0.1/impact/suite-manifest.json`
- Full overview lineage:
  `workspace/runs/mh370/release-v0.1/posterior-search-context/run-manifest.json`
- Supporting research recreations: `workspace/.sources/README.md` and each
  child `README.md`.

## Known rejected or deferred work

An exact whole-interval independence-MH source-replay experiment was rejected
after its smoke run failed predeclared acceptance/root-switch mass checks. Its
code was removed and the outcome recorded in `workspace/README.md`. Better
B777 terminal calibration, R1200/startup calibration, ocean-drift likelihood
admission, raw hydroacoustic calibration, and exact probability-of-detection
search modelling remain post-v0.1 research. Their absence is not hidden and
should not be treated as a defect in the stated milestone scope.
