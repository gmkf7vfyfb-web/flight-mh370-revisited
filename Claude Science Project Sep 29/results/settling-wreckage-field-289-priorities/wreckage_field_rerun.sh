#!/bin/sh
# Settling's standard result on a new impact set (overnight 10-11 Oct, pre-approved on end-of-flight/next-run/READY).
# Usage: sh wreckage_field_rerun.sh <end-of-flight smoke dir> <runs root> <core run.json with reference_arcs> <engine dir>
# Env passed through: WF_RUN_PATTERN, WF_SEED_PATTERN, WF_SEEDS, WF_LABEL, WF_OUTSTEM, WF_RUN_LABELS, WF_KEYS.
# Two threads (the Mac is drift's); if the settling pass would exceed ~10 min, wrap the cargo line in lockf -k /tmp/.mh370-heavy.lock.
set -eu
PWD_OLD=$(pwd)
SM="$1"; RUNS="$2"; ARCS="$3"; ENG="$4"; HERE=$(cd "$(dirname "$0")" && pwd)
python3 "$HERE/wreckage_field_prep_keys.py" "$SM" "$RUNS" A none__other 50000 20261010
python3 "$HERE/wreckage_field_prep_keys.py" "$SM" "$RUNS" B r600_no-offset__fuel-exhaustion,both_startup-offset__fuel-exhaustion,both_no-offset__other 10000 20261011
for T in A B; do
  ( cd "$ENG" && RAYON_NUM_THREADS=2 SETTLING_THREADS=2 SETTLING_FIELD_IN="$PWD_OLD/field/${T}_impacts.f64" SETTLING_FIELD_OUT="$PWD_OLD/field/${T}_elements.f64" \
      cargo test --offline -j 2 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored 2>&1 | grep "test result" )
done
python3 "$HERE/wreckage_map_priorities_run.py" "$SM" "$RUNS" "$ARCS"
