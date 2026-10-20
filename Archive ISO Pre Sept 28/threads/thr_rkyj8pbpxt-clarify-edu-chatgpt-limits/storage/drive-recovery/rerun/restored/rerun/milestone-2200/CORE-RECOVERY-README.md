# Early core recovery package — not the final global handoff

This is a content-addressed backup of every available local Rerun non-build
file, plus the exact Rust 1.98.0 Linux x86_64 toolchain and Cargo dependency
cache. Identical historical snapshots are stored once and reconstructed as
independent files. Build target folders, Python caches and VCS metadata are
excluded; original checkpoint ZIPs, sources, configs, data, logs, failures,
figures, reports, continuation files and environment grids are retained.

This does NOT assert completeness of the absent original-review workspace,
IGOGU multipart archive bytes, or the separate Resolution investigation. The
final 22:00 milestone must reconcile those existing archive inventories. Do
not label this core-only preparation a complete download of all research.

## Recovery

Download all parts, CORE-RECOVERY-PARTS.json and restore_core_recovery.py into
one directory. Run:

```text
python3 restore_core_recovery.py downloads restored
```

Every part, the reconstructed ZIP, and every unique file blob is SHA-256
verified. Restoration refuses a nonempty destination and unsafe paths.
Full restoration requires considerably more disk space than the deduplicated
archive because historical snapshots become independent files.

## Offline Rust build

On compatible Linux x86_64 with a C linker and system libraries:

```sh
cd restored
ROOT="$PWD"
export PATH="$ROOT/runtime/rust-toolchain/bin:$PATH"
export RUSTC="$ROOT/runtime/rust-toolchain/bin/rustc"
export CARGO_HOME="$ROOT/runtime/cargo-home"
export CARGO_TARGET_DIR="$ROOT/build-target"
cd rerun/coupled-trace-20260919T2040/source
cargo test --offline --locked -p mh370-dynamics -p mh370-end-of-flight -p mh370-estimator -p mh370-particle-filter
cargo test --offline --locked --workspace
```

The toolchain is included to avoid the original Rust download blocker. Platform
compatibility is not guaranteed on macOS/Windows or incompatible Linux hosts.
Python 3.12.14 was used. The new exact control and recovery scripts require
only Python's standard library. Earlier plotting/scientific scripts also use
numpy, scipy, matplotlib and other packages recorded in python-environment.txt;
third-party Python wheel bytes are not bundled.

## Scientific/code boundary

Checkpoint 20 adds an experimental stochastic prefix from 18:22:12 to
18:28:05.9, with current mass supplied to each dynamics step. It is not a
complete aircraft bridge, an endpoint proposal, or a weighted posterior.
The baseline sampler is not replaced. Read checkpoint20's report and newest
numbered continuation. Top-level rerun/continuation.json is stale checkpoint12.

IGOGU remains optional future integration, not a baseline change. Exact original
artifacts remain in folder 1E2wMSGz-MF_zFZ2GDvRZ1fO9aqQTT23F. Its original
through-00:11 posterior and later R600-conditioned sensitivity must remain
separate. Never treat either prior posterior as independent new evidence.
Hydroacoustic observations remain excluded pending core adequacy.
