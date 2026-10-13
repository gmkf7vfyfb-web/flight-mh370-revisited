#!/bin/bash
# End of flight's sweep on core run C (architecture milestone ruling, 15:20 -0600 10 Oct; compact format 14:30 -0600).
# Waits for core's READY, then for each stratum: one hold of the heavy lock at 12 threads for its seeds, each seed written
# full in this workspace, converted to the compact float32 format on the exchange (smoke/compact_impacts.py, verified at
# write), the full file then removed from THIS workspace. Recipe = eof-289-full (N = 8 x 4 descents, descent idle floor ON)
# on top of core's own config chain for the stratum, read from core's run.json in core's order. Refuses to run if a config
# is missing here (merge core first) or if the chain flies two tanks on internal-v1 without the INOP-flow correction.
# Optional: touch $OUT/USE-TRIM-AT-LOSS before it starts to add smoke/trim-at-loss.toml (ruling item 3) to every seed.
# Run from engine/:  nohup hypotheses/end-of-flight/full/sweep_run_c.sh > /tmp/eof-run-c.log 2>&1 &
set -u
CORE=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/next-run-c}
OUT=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c}
BIN=${EOF_BIN:-/tmp/mh370-eof-merge}
S=hypotheses/end-of-flight
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2
echo "waiting for $CORE/READY $(date -u +%FT%TZ)"
while [ ! -e "$CORE/READY" ]; do sleep 60; done
echo "RETIRED watcher exits $(date -u +%FT%TZ) (superseded: residual bank direction)"; touch /tmp/eof-retired2-watcher-exited; exit 0
