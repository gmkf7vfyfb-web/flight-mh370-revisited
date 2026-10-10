#!/bin/sh
# Composer pass 0 driver, one stratum at a time so that at most ~2.2 GB of intermediate data exists at once.
# PIPELINE TEST - core (b) unconverged. Outside the heavy lock: 2 threads (prep, summary), composer single-threaded.
# Usage: sh run_pass0.sh <work dir> <pass0 binary> <python> <stratum> [...]
set -eu
W="$1"; BIN="$2"; PY="$3"; shift 3
HERE="$(cd "$(dirname "$0")" && pwd)"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
for ST in "$@"; do
  echo "== $ST start $(date -u +%T)"
  for k in 1 2 3 4; do "$PY" "$HERE/prep_inputs.py" "$ST" "$k" "$W/work/inputs/$ST" "$W/work/evaluate/seabed-$ST-$k.npy"; done
  "$PY" "$HERE/make_hdr.py" "$ST" "$W/work/inputs/$ST"
  "$BIN" "$W/work/inputs/$ST" "$W/work/rust/$ST"
  "$PY" "$HERE/summarise_stratum.py" "$ST" "$W/work/inputs/$ST" "$W/work/rust/$ST" "$W/work/summary" | tail -1
  rm -rf "$W/work/inputs/$ST" "$W/work/rust/$ST/weights"
  echo "== $ST done $(date -u +%T)"; df -h /Users/pete/Downloads | tail -1
done
