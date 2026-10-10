#!/bin/sh
# Stand-in runner: the Pleiades module's own recipe (prepare/rerun_next.py at ed85311), one stratum at a time.
# Usage: sh run_streams.sh <stratum> [<stratum> ...]   (each stream single-threaded; two streams = 2 threads total)
set -eu
WS="$(cd "$(dirname "$0")" && pwd)"
ENG="$WS/pl/Claude Science Project Sep 29/engine"
export XDG_CONFIG_HOME="$WS/xdg" PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH CARGO_HOME=/Users/pete/.cargo CARGO_TARGET_DIR="$WS/target"
export RAYON_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
LAB="core (b) split-half NOT converged; two-tank bookkeeping only; PROVISIONAL-OVERNIGHT; EoF sweep run by a stand-in; run by an architecture stand-in on the Pleiades module's behalf, module to review"
for s in "$@"; do
  echo "=== $s start $(date -u +%FT%TZ)"
  cd "$ENG/hypotheses/pleiades/prepare"
  "$WS/.venv/python/bin/python" rerun_next.py "/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run/$s" "next-run-b-standin/$s" "$LAB; stratum $s"
  echo "=== $s done $(date -u +%FT%TZ)"
done
