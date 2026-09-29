# Reproduction guide

Run commands from the capsule root unless a command begins with `cd
workspace`. Always write regenerated outputs to a new empty directory; do not
overwrite the retained release artifacts.

## 1. Verify before running inference

```bash
python3 tools/verify_capsule.py
```

This performs the complete capsule checksum pass, checks the producer binary,
runs the original 70-artifact release validator, and reports the historical
source-lock match count.

For only the original nested release validator:

```bash
cd workspace
python3 -B runs/mh370/release-v0.1/validate-release.py
```

Expected final line:

```text
release validation passed: 70 artifacts; manifest_sha256=b5d89ff95bd26594506674dd51a04b36e23a04946ac0b835f85b5ee1b16db9e1
```

## 2. Runtime prerequisites

The exact producer binary requires x86-64 Linux and glibc 2.35 or newer. It is
dynamically linked only to the loader, `libc`, `libm`, and `libgcc_s`. The
original host was Arch Linux build 20260812 with glibc 2.44.

To build the enclosed current source, install Rust 1.98.0 for
`x86_64-unknown-linux-gnu`. Rust dependencies are vendored, so network access
is not required:

```bash
cd workspace
cargo test --workspace --offline
cargo build --release --offline -p mh370-runner
```

The current source build is useful for code inspection and fresh experiments;
it is not expected to have the historical producer SHA. See `PROVENANCE.md`.

Report regeneration uses Python. The captured environment used Python 3.14.7;
package versions are in `environment/python-requirements.txt`. The release
validator itself uses only the Python standard library.

## 3. Canonical MH370 00:11 production suite

The following is the recorded production command, adapted to the enclosed
producer binary. It evaluates three families times five seeds times 30,000
particles and is intentionally not part of a quick verification pass:

```bash
cd workspace
../bin/linux-x86_64/mh370-v0.1 estimate \
  --config configs/mh370-0011-core-comparison.toml \
  --output /tmp/mh370-v01-core-reproduction \
  --threads 8
```

Compare the new outputs with
`runs/mh370/0011-core-comparison/run-manifest.json`. Deterministic scientific
content should close under the recorded hashes when the compatible runtime
conditions are reproduced.

## 4. Corrected-R600 seventh-arc continuation

This step consumes the five retained medium-BFO 00:11 handoffs:

```bash
cd workspace
../bin/linux-x86_64/mh370-v0.1 continue-to-contact \
  --config configs/mh370-0011-to-0019-seventh-arc-bto.toml \
  --output /tmp/mh370-v01-r600-reproduction
```

Compare against
`runs/mh370/0011-to-0019-seventh-arc-bto/run-manifest.json`.

## 5. End-of-flight family suite and report

```bash
cd workspace
python3 -B crates/runner/scripts/impact_release_suite.py \
  --matrix configs/mh370-impact-release-families.json \
  --runner ../bin/linux-x86_64/mh370-v0.1 \
  --output /tmp/mh370-v01-impact-reproduction \
  --jobs 6

python3 -B crates/reporting/scripts/impact_release_figures.py \
  --suite runs/mh370/release-v0.1/impact/suite-manifest.json \
  --land crates/reporting/assets/ne_110m_land.geojson \
  --output /tmp/mh370-v01-impact-report-reproduction
```

The report command above deliberately regenerates from the frozen suite. Do
not pool the six impact families.

## 6. Full v0.1 overview with arcs, Davey, and searched-area context

After installing the Python packages in the captured requirements file:

```bash
cd workspace
python3 -B crates/reporting/scripts/posterior_search_context.py \
  --core-run runs/mh370/0011-core-comparison \
  --continuation-run runs/mh370/0011-to-0019-seventh-arc-bto \
  --impact-suite runs/mh370/release-v0.1/impact/suite-manifest.json \
  --davey-latitude .sources/davey-2016-bayesian-search/data/davey_fig10_3_digitized_latitude_pdf.csv \
  --search-atlas .sources/mh370-seabed-search-coverage/data/map/search-evidence-atlas.geojson \
  --area-inventory .sources/mh370-seabed-search-coverage/data/area-inventory.json \
  --land crates/reporting/assets/ne_110m_land.geojson \
  --output /tmp/mh370-v01-overview-reproduction
```

The retained output and its lineage are under
`runs/mh370/release-v0.1/posterior-search-context/`.

## 7. MH371 medium-BFO known-flight control

This is fast and was rerun with the exact v0.1 producer binary for the
capsule:

```bash
cd workspace
../bin/linux-x86_64/mh370-v0.1 infer-known-flight \
  --config configs/mh371-analog-medium.toml \
  --inference inputs/controls/mh371-inference.json \
  --weather inputs/environment/mh371-era5-grid.bin \
  --magnetic inputs/environment/mh371-igrf14-grid.bin \
  --output /tmp/mh371-v01-medium-inference \
  --threads 8

../bin/linux-x86_64/mh370-v0.1 score-known-flight \
  --config configs/known-flight-scoring.toml \
  --truth inputs/controls/mh371-truth.csv \
  --run /tmp/mh371-v01-medium-inference/inference-seed-37102001.json \
  --run /tmp/mh371-v01-medium-inference/inference-seed-37102002.json \
  --output /tmp/mh371-v01-medium-assessment
```

The capsule run completed with numerical validity true, minimum final mass
within 100 nautical miles 0.5724, minimum overlap 0.6933, and maximum
Jensen-Shannon divergence 0.078253 nats. The retained run is in
`workspace/runs/mh371/v0.1-medium-control/`.

## 8. Supporting source recreations

Each subdirectory of `workspace/.sources/` contains its own README with source
identity, units, assumptions, commands, results, and limitations. These are
independent investigations rather than runtime dependencies of the estimator.
Do not import their code into the canonical runner during assessment.
