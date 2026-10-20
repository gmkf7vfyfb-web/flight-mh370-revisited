# Claude Science Project Sep 29

The live working copy. `ISO Sept 28 Status/` is a frozen snapshot and is not edited from here:
`engine/` began as a copy of `ISO Sept 28 Status/code/main` (published head
`f6f8873ca603f3406651b17c8019198f3ef44588`) and development continues in this folder.

Read `AGENTS.md` at the repository root first; it is binding here too. `engine/status.md` and
`engine/README.md` came with the snapshot and describe the estimator as it stood on 2026-09-25.

## Layout

```text
Claude Science Project Sep 29/
  engine/                     working copy of the Rust filter and its report scripts
  results/                    committed run outputs (small files only; runs/ itself is ignored)
```

`engine/.gitignore` keeps `target/`, `runs/` and `data/*.bin` out of Git, so the environment
grids and the multi-gigabyte particle arrays are not committed. Regenerate the grids as below.

## Building and running

The engine pins Rust 1.98. Cargo needs `index.crates.io` and `static.crates.io` reachable.

```bash
cd engine
cargo build --release                                     # ~25 s
cargo test --release                                      # 14 unit checks, under a minute
./target/release/mh370 config/davey2016.toml runs/davey2016      # base estimate
python report/convergence.py runs/davey2016                      # convergence gate
python report/build_report.py runs/davey2016 report.pdf          # the PDF
```

Measured on 18 threads: a smoke run (2 x 100k particles) takes 2.8 s; the `fnl` weather
sensitivity (4 x 7M BTO+BFO and 2 x 7M BTO-only) took 26.7 min wall for 249 min of CPU, 6,954 MiB
peak, and left 2.0 GB in `runs/`. The snapshot's figure of ~93 min was measured on six threads.

## Regenerating the environment grids

`data/era5-wind-temperature.bin` (375 MB) is not in Git. It does not need a Copernicus CDS
account: `extract.py` reads the public ARCO ERA5 Zarr store on Google Cloud anonymously, pinned to
`google-research/arco-era5@8fb5e9b982f489ba91af3ced9ce0b0a8ade8dd7d`.

```bash
cd engine
python .sources/era5-weather/rebuild.py data/era5-wind-temperature.candidate.bin \
    --manifest .sources/era5-weather/mh370-era5-grid.manifest.json
python .sources/era5-weather/extend.py data/era5-wind-temperature.candidate.bin \
    data/era5-wind-temperature.bin 2014-03-08T02:00:00
```

The first step rebuilt the canonical 9-hour global grid in 3m19s and verified
**byte-identical** to the recorded manifest: 337,328,648 bytes, SHA-256
`73a14bf7e931da9f4f3f034b77ac24b9514fdef727b82eb9e30c67df938489f4`, with all three field
statistics equal to the recorded values. The second step re-extracted 2014-03-08T01:00, confirmed
it matched the stored grid byte for byte, and appended 02:00 to give the installed 10-hour grid
(374,809,120 bytes, dims 10 x 12 x 361 x 721).

`data/igrf14-declination.bin` and `data/fnl-wind-temperature.bin` were copied from
`ISO Sept 28 Status/inputs/repo-data/`.

## Changes made in this folder

**Peak memory is recorded on macOS** (`engine/crates/mh370/src/output.rs`). `peak_memory_mib()`
read only `/proc/self/status`, so every macOS run wrote `peak_memory_mib: null` into its manifest
and `build_report.py` then failed to format the last page. It now uses
`getrusage(RUSAGE_SELF).ru_maxrss` on macOS, where Darwin reports bytes and Linux would report
kibibytes. Added `libc` as a `cfg(unix)` dependency and a unit check that the value is reported
and plausible. The numerical path is untouched, so `make regress` still applies.

**The report tolerates a missing manifest field** (`engine/report/build_report.py`). A null
`peak_memory_mib`, from an older run or an unsupported platform, now prints "not recorded by this
run" instead of aborting the page.

**A convergence gate** (`engine/report/convergence.py`, new). Reads a finished run's
`summary.json` and each replicate's `diagnostics.json` and writes `convergence.json` and
`convergence.csv`, exiting non-zero if the run should not be quoted. Two gates, both with a
criterion taken from the project rather than invented:

- *pooling closure* — for every stratum the per-replicate pool factors must sum to one. This is
  the defect class recorded under "Known defect" in `engine/status.md`, where replicate weights
  summed to 0.92–0.96 because rows were pooled by a particle's current autopilot mode instead of
  the mode run it belonged to.
- *split-half overlap* ≥ 0.90 — the threshold `build_report.py` already uses to say a pooled curve
  does not depend materially on the random seed.

Replicate pairwise overlap, the spread of replicate medians, effective sample size by epoch, and
surviving distinct prior draws per mode filter are reported without a pass or fail, because the
project states no threshold for them.

**A local rebuild of the canonical ERA5 grid** (`engine/.sources/era5-weather/rebuild.py`, new,
and a shared store opener added to `extend.py`). `extract.py` retrieves the grid on Modal and
`extend.py` reused its pure functions to append single hours; the whole canonical grid can now be
regenerated locally from the same functions, so a fresh clone is self-sufficient. No new
numerical code: the selection, pressure-altitude interpolation and binary writer are
`extract.py`'s own, which is what makes the SHA-256 comparison meaningful. The opener also gained
a bucket-qualified HTTPS transport and `trust_env=True`, because aiohttp — under both gcsfs and
fsspec — ignores `HTTP(S)_PROXY` unless told to trust the environment, and on a proxied network
without direct DNS the omission fails as if the store were unreachable.

## Observations for the record

**The ERA5 grid already reaches the surface.** `PRESSURE_ALTITUDES_FT` runs 500 ft to 43,000 ft
from source levels 1000 hPa to 150 hPa, and one of the extractor's three spot checks is at 500 ft.
The comment in `crates/flight/src/environment.rs` about the model keeping 25–43 kft describes the
base cruise filter's altitude prior, not the grid's extent.

**Out-of-range environment queries are clamped silently.** `locate()` in
`crates/flight/src/environment.rs` clamps a query outside the time or altitude axes to the nearest
level and records nothing. A particle below 500 ft or after 02:00 therefore receives edge data as
though it were measured. The grid manifest states the opposite contract — "a state outside the
time or altitude axes is a data-coverage failure, not evidence against its control history" — so
the two disagree. This does not affect the 00:11 base run, whose altitude prior is 25–43 kft
inside the window, but it bears on the end-of-flight and settling stages, which fly to the
surface. Not changed here; flagged.

**The BTO-only case is under-replicated as configured.** `config/davey2016.toml` and
`config/sensitivity/fnl.toml` both give BTO-only two seeds, so its split-half overlap compares one
replicate against one and cannot reach the 0.90 threshold: the `fnl` run reports 0.696 for
BTO-only beside 0.924 for BTO+BFO. Quoting a BTO-only number at this configuration is quoting an
unconverged curve. Raising its seed count is a configuration change and has not been made here.
