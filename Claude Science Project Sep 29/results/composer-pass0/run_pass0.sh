#!/bin/sh
# Composer pass 0/1 driver, one stratum at a time so that at most ~2.2 GB of intermediate data exists at once.
# PIPELINE TEST - core (b) unconverged. Outside the heavy lock: 2 threads (prep, summary), composer single-threaded.
# Source split-half (ruling 3): core (b) report/strata-summary.csv split_half_min (all balanced partitions), floor 0.896.
# Usage: sh run_pass0.sh <work dir> <pass0 binary> <python> <stratum> [...]
set -eu
W="$1"; BIN="$2"; PY="$3"; shift 3
HERE="$(cd "$(dirname "$0")" && pwd)"
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2
source_overlap() {
  case "$1" in
    next-free) echo 0.6403;; next-repro-radar) echo 0.8644;; next-descent-climb) echo 0.7498;; next-routes) echo 0.7977;;
  esac
}
for ST in "$@"; do
  echo "== $ST start $(date -u +%T)"
  for k in 1 2 3 4; do "$PY" "$HERE/prep_inputs.py" "$ST" "$k" "$W/work/inputs/$ST" "$W/work/evaluate/seabed-$ST-$k.npy"; done
  "$PY" "$HERE/make_hdr.py" "$ST" "$W/work/inputs/$ST"
  "$BIN" "$W/work/inputs/$ST" "$W/work/rust/$ST" "$(source_overlap $ST)" "source: core (b) $ST split-half overlap, min over balanced partitions (strata-summary.csv)"
  "$PY" "$HERE/summarise_stratum.py" "$ST" "$W/work/inputs/$ST" "$W/work/rust/$ST" "$W/work/summary" | tail -1
  "$PY" "$HERE/seabed_extract.py" "$ST" "$W/work/inputs/$ST" "$W/work/rust/$ST" "$W/work/seabed"
  rm -rf "$W/work/inputs/$ST" "$W/work/rust/$ST/weights"
  echo "== $ST done $(date -u +%T)"; df -h /Users/pete/Downloads | tail -1
done
