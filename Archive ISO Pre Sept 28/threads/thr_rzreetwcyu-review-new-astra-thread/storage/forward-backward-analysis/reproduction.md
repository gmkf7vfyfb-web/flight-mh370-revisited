# Reproducing the bounded through-00:11 investigation

The canonical Rust executable owns flight and observation equations. The
external ordered-control sampler remains an experiment; no production
probability handoff has been accepted from it. Fixed command counts, initial
Mach/altitude densities, equal navigation-mode probabilities and the fuel
anchor are model conditions. The later exhaustion-time condition is disabled.

Build and verify the canonical product from the MH370 workspace:

```bash
cargo build --release -p mh370-runner --bin mh370 --jobs 4
cargo test --workspace --release --jobs 4
```

All retained numerical run directories contain exact commands and source/input
hashes in `run-manifest.json`; guide construction records its command and
hashes in `summary.json`. Main runs use the same proposal artifact for an
independent-seed comparison. Do not overwrite a retained run directory when
reproducing it. Use a fresh external output directory and preserve the seed,
configuration, proposal and source identities.

The current sampling command has this form (paths abbreviated here; the run
manifest is the exact command):

```bash
PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 python sampler.py \
  --output NEW_OUTPUT --counts 1 0 0 --particles 1024 --seed 37091201 \
  --moves 1 --seconds 1100 --workers 4 --no-fuel-condition \
  --forward-backward --mode-updates 1 --mode-refresh .5 --block-scales \
  --joint-controls --surrogate-config mh370-screening-flight.toml \
  --proposal one-direction-guides/proposal.npz
```

The accurately integrated target determines every importance weight. The
coarse integration configuration is only a corrected acceptance screen and
must differ from the target configuration in numerical settings alone.
`--moves 1` means one complete forward/reverse block pair. These are control
updates inside SMC, not ordinary forward-filter/backward-state simulation.

The bounded command limits and compute ledger record numerical elapsed time,
including failed trials. They do not include the longer engineering, review
and reporting time. No failed pilot is a posterior sample. No finite guide
span is a certified support boundary.

Generate the browser and server-independent ISO report from artifacts:

```bash
python crates/reporting/scripts/flight_assumption_report.py \
  /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/flight-assumption-preanalysis \
  --progress-from /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/overnight-analysis \
  --sampler-from /jackbox/home/.iso/thread-storage/thr_rzreetwcyu/forward-backward-analysis \
  --inline-page flight-sampling.html --inline-output mh370-report-preview.html
```

For a focused numerical replay check:

```bash
python crates/controls/flight_evidence.py flight-refinement \
  --refine-from SAVED_RUN --output NEW_REFINEMENT_OUTPUT
```

This replays representative saved trajectories at the configured step, half
steps and quarter steps. It checks numerical integration, not independent
Boeing performance calibration. The independent mathematical control is
`forward_backward_control.py NEW_CONTROL_OUTPUT`; its exact Gaussian oracle
also does not establish full-flight mixing or repeated-data coverage.

The final source archive is `source-snapshot.tar.gz`, with `canonical/` and `experiment/` members. `source-manifest.json` records its SHA-256, per-file identities, executable identity and toolchain versions. Restore the experimental files from that archive if the temporary directory is no longer present. The final accurate 1/0/0 independent pair uses this sampler source; earlier trials use their separately retained source archives. The comparison failed, so this is reproducibility material, not a released estimator.
