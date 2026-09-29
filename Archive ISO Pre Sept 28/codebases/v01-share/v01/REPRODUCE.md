# Reproducing the v0.1 broad-flight checkpoint

This capsule freezes a milestone implementation of the
`broad-powered-marked-jump-v1` filter and its fail-closed diagnostic reporter.
It supports two different operations:

1. **Exact verification** checks the bytes already in the capsule against its
   ledgers, run manifests, report audits, and release validations.
2. **Scientific regeneration** runs the same seeded model from the frozen
   configuration and inputs. Runtime fields in a newly written run manifest
   can differ even when the scientific outputs agree.

Neither operation turns a conditional model into a calibrated distribution of
the aircraft's true path. Read [SCIENTIFIC_BOUNDARIES.md](SCIENTIFIC_BOUNDARIES.md)
before interpreting the figures.

## Directory convention

Commands below start in `v01/workspace`. The authoritative retained artifacts
remain at these paths:

- `runs/mh371/broad-flight-truth-control`
- `runs/mh370/broad-flight-uncertainty-diagnostic`

Run the inference commands only in a second, disposable extraction of the
capsule. In that extraction, move the retained run tree aside before starting:

```bash
cd v01/workspace
mv runs retained-runs
mkdir -p runs/mh370 runs/mh371
```

This preserves the frozen artifacts under `retained-runs/` while leaving the
report specifications' canonical `runs/...` paths available for regeneration.
Do not do this in the authoritative retained copy. To inspect that copy, use
the verifier and the already-written validation records without rerunning
inference over it.

## 1. Verify the capsule bytes

From `v01`:

```bash
python3 -B tools/verify_capsule.py
```

The verifier checks `SHA256SUMS`, the exact packaged producer, and the nested
release identities. A successful check means that the capsule has not changed;
it is not a numerical-convergence result.

## 2. Check the source and build the runner

Rust 1.98.0 is pinned by `workspace/rust-toolchain.toml`. The capsule includes
vendored crates and `.cargo/config.toml`, so the Rust checks do not need the
network.

From `v01/workspace`:

```bash
cargo fmt --all -- --check
cargo test --workspace --locked --offline
cargo build --release --locked --offline -p mh370-runner
target/release/mh370 estimate-broad-flight --help
```

The exact executable that produced the retained runs is also stored at
`../bin/linux-x86_64/mh370-v0.1`. Its SHA-256 must equal the
`executable_sha256` in each retained `run-manifest.json`. A newly built binary
must not be silently substituted when validating retained artifacts merely
because its version string is the same.

The snapshot reporter requires Python, NumPy, SciPy, and Matplotlib. The exact
producer versions are recorded under `../environment/`. A convenient local
environment can be created with:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --no-index \
  --find-links ../environment/wheelhouse \
  -r ../environment/python-requirements.txt
.venv/bin/python -B -m unittest \
  crates/reporting/scripts/tests/test_broad_snapshot_report.py
.venv/bin/python -B -m unittest \
  crates/reporting/tests/test_validate_broad_release.py
```

The bundled wheels target CPython 3.14 on Linux x86-64. Other platforms need
matching packages from their package index. Use the recorded package versions for byte-oriented comparison of rendered
PDF/PNG output. Other compatible versions can be useful for inspection, but
font and renderer differences may change presentation bytes.

## 3. Regenerate the MH371 truth-separated control

The inference command has no truth argument. It can read only the exposed
initial state, SATCOM and satellite projections containing no later aircraft
state, weather and magnetic grids, and declared conditional priors.

```bash
target/release/mh370 estimate-broad-flight \
  --config configs/mh371-broad-powered-flight-control.toml \
  --output runs/mh371/broad-flight-truth-control \
  --threads 6
```

The runner bytes are truth-separated, but the experiment design was not a
fully prospective blind trial. A pilot inspection moved the final control
window from 06:59 to 06:48 to avoid the known descent turn. That truth-informed
window choice is documented in
`.sources/mh371-known-flight-data/README.md`; it must remain visible when
interpreting the later held-back accuracy scores.

Only after the runner has finalized its artifacts may the reporter open the
held-back aircraft positions:

```bash
.venv/bin/python -B crates/reporting/scripts/broad_snapshot_report.py \
  --spec configs/mh371-broad-snapshot-report.json \
  --truth inputs/controls/mh371-truth.csv \
  --output runs/mh371/broad-flight-truth-control/diagnostic-report
```

This produces:

- `diagnostic-report/broad_snapshot_diagnostic.pdf`
- `diagnostic-report/broad_snapshot_diagnostic.png`
- `diagnostic-report/broad_snapshot_diagnostic.json`

The JSON is the authoritative per-epoch accuracy, structural-sensitivity,
root-ESS, seed-spread, and source-hash record. The prose documentation does not
copy its changing numerical values.

The release configurations intentionally suppress the runner's ungated
built-in report graphics and its final-only posterior CSV/handoff. Reporting
instead consumes the complete manifest-hashed all-observation snapshot set.
The validator checks these output switches and refuses both missing required
files and unexpected suppressed files.

Validate a regenerated run against the binary that produced it:

```bash
.venv/bin/python -B crates/reporting/scripts/validate_broad_release.py \
  --manifest runs/mh371/broad-flight-truth-control/run-manifest.json \
  --summary runs/mh371/broad-flight-truth-control/summary.json \
  --config configs/mh371-broad-powered-flight-control.toml \
  --binary target/release/mh370 \
  --report-audit runs/mh371/broad-flight-truth-control/diagnostic-report/broad_snapshot_diagnostic.json \
  --output runs/mh371/broad-flight-truth-control/diagnostic-report/release-validation.json
```

For an exact-producer regeneration, replace `target/release/mh370` with the
packaged producer:

```text
../bin/linux-x86_64/mh370-v0.1
```

## 4. Regenerate the MH370 all-epoch diagnostic

MH370 has no held-back truth input. Do not add `--truth` to its reporting
command.

```bash
target/release/mh370 estimate-broad-flight \
  --config configs/mh370-broad-powered-flight-diagnostic.toml \
  --output runs/mh370/broad-flight-uncertainty-diagnostic \
  --threads 6

.venv/bin/python -B crates/reporting/scripts/broad_snapshot_report.py \
  --spec configs/mh370-broad-snapshot-report.json \
  --output runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report

.venv/bin/python -B crates/reporting/scripts/validate_broad_release.py \
  --manifest runs/mh370/broad-flight-uncertainty-diagnostic/run-manifest.json \
  --summary runs/mh370/broad-flight-uncertainty-diagnostic/summary.json \
  --config configs/mh370-broad-powered-flight-diagnostic.toml \
  --binary target/release/mh370 \
  --report-audit runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/broad_snapshot_diagnostic.json \
  --output runs/mh370/broad-flight-uncertainty-diagnostic/diagnostic-report/release-validation.json
```

Again, use `../bin/linux-x86_64/mh370-v0.1` when regenerating with the exact
retained producer rather than a local rebuild. For the untouched retained
capsule, `python3 -B tools/verify_capsule.py` checks the already-written
validation records without modifying them.

## 5. What the validator establishes

Exit status zero from `validate_broad_release.py` establishes a closed chain
among the canonical broad configuration, producer binary, scientific inputs,
all configured families and seeds, every manifest-listed snapshot, the report
specification, the reporter source, and the rendered output hashes. It also
rejects substitution of a one-turn, fixed-track, fixed-waypoint, or fixed-route
artifact.

It does **not** mean that the particle or root effective sample size passed,
that independent seeds agree geographically, or that a report is eligible for
publication as a probability map. Those decisions live in the report JSON at
`numerical_support.status`, `numerical_support.criteria`,
`numerical_support.watermark`, and `numerical_support.publication_eligible`.
A provenance-valid release can correctly contain a report marked
`FAILED NUMERICAL SUPPORT — DIAGNOSTIC ONLY`.

## 6. Rebuild contextual Davey and search-area material

These commands are independent of the broad-flight estimator and do not update
its posterior:

```bash
.venv/bin/python -B \
  .sources/mh370-seabed-search-coverage/code/build.py check
```

The Davey package documents its own historical recreation commands at
`.sources/davey-2016-bayesian-search/README.md`. The old
canonical-versus-Davey figure compared Davey with the superseded one-turn
chain, so it is excluded from the current views and result manifest. Likewise,
the old search-planning tiles were conditioned on the superseded narrow impact
population and are not published as current results. A complete
source-recreation package can retain such files only as clearly identified
historical research output.

## Reproduction boundary

The normalized inference inputs needed to rerun both filters are bundled and
hash-pinned. Some upstream MH371 workbooks are restricted, and the underlying
ERA5 service is a mutable public store; their source packages preserve exact
identities and retrieval/audit instructions, but the capsule does not claim
that every upstream raw byte can be reacquired indefinitely. This does not
weaken exact verification of the frozen runtime inputs used by the runner.
