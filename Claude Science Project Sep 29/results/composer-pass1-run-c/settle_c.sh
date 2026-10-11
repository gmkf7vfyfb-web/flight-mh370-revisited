#!/bin/sh
# Settle the aimed resample with settling's own wreckage_field test (copy of settling's worktree 9330d4c), 2 threads, outside the lock.
# Usage: sh settle_c.sh <workspace> <tag> <n products>
WS="$1"; TAG="$2"; N="$3"
export CARGO_HOME=/Users/pete/.cargo RUSTUP_HOME=/Users/pete/.rustup PATH=/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH
export CARGO_TARGET_DIR="$WS/target-settling" HOME="$WS/scratchhome" RAYON_NUM_THREADS=2 SETTLING_THREADS=2
j=0
while [ "$j" -lt "$N" ]; do
  ( cd "$WS/settling-copy/engine" && SETTLING_FIELD_IN="$WS/work/seabed/field/${TAG}P${j}_impacts.f64" SETTLING_FIELD_OUT="$WS/work/seabed/field/${TAG}P${j}_elements.f64" \
    cargo test --offline -j 2 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored 2>&1 | grep "test result" )
  echo "$TAG P$j settled $(date -u +%T)"; j=$((j+1))
done
