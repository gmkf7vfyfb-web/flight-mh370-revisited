#!/bin/bash
# Regenerate the Pléiades module's release tables and 0.05 deg likelihood surfaces with the module's own
# #[ignore] export tests (hypothesis/pleiades, read-only; output to the clone's gitignored engine/runs/pleiades).
# 2 threads, outside the heavy lock. Usage: export_surfaces.sh <pleiades clone root> <cargo target dir>
set -euo pipefail
CLONE="$1"; export CARGO_TARGET_DIR="$2"
export PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH CARGO_HOME=/Users/pete/.cargo RUSTUP_HOME=/Users/pete/.rustup
export RAYON_NUM_THREADS=2 PLEIADES_OCEAN_DIR=/Users/pete/Downloads/mh370-ocean-data
cd "$CLONE/Claude Science Project Sep 29/engine"
export PLEIADES_EXPORT_DIR="$PWD/runs/pleiades"; mkdir -p "$PLEIADES_EXPORT_DIR"
T="cargo test --offline -j 2 --release -p mh370-hypotheses --lib --"
# 1. release tables: GLORYS12V1 (default) and GlobCurrent daily
[ -f runs/pleiades/release-grid.toml ] || { date; $T --ignored --exact --test-threads 1 pleiades::export::run::pleiades_export_release_grid; }
[ -f runs/pleiades/release-grid-globcurrent-p1d.toml ] || { date; PLEIADES_CURRENT=globcurrent/grid/globcurrent_my_p1d_uo_vo_0m.series.json PLEIADES_EXPORT_TAG=-globcurrent-p1d \
   $T --ignored --exact --test-threads 1 pleiades::export::run::pleiades_export_release_grid; }
# 2. surfaces from run.toml (measured spread, both products)
date; $T --ignored --exact --test-threads 1 pleiades::tests::pleiades_export_likelihood_surface
date; $T --ignored --exact --test-threads 1 pleiades::tests::pleiades_export_cosmo_surface
date; shasum -a 256 runs/pleiades/*.f32; cat runs/pleiades/*.toml
