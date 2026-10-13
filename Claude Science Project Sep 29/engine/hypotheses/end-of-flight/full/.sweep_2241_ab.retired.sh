#!/bin/bash
# End of flight: the 22:41 A-vs-B runs on core run C's m2241 hand-offs (after the run C sweep; Pete's lock priority).
# For each core stratum, seeds $SEEDS, arms A (smoke/arm-v1.toml) and B (full/arm-b-deliberate.toml): the module flies from
# 22:41 and scores 23:15, 00:11 and 00:19 in-stage (smoke/options-m2241.toml). N = 4 children x 4 descents. Same module recipe as
# run C otherwise (idle floor, v2-broad, family-b-ditching, residual-bank-boeing). Full outputs stay in this workspace.
# Run from engine/:  nohup hypotheses/end-of-flight/full/sweep_2241_ab.sh > /tmp/eof-2241-ab.log 2>&1 &
set -u
CORE=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/next-run-c}
OUTC=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c}
BIN=${EOF_BIN:-/tmp/mh370-eof-runc4}
SEEDS=${EOF_SEEDS:-"1 2 3 4"}
S=hypotheses/end-of-flight
echo "waiting for $OUTC/SWEEP-DONE $(date -u +%FT%TZ)"
while [ ! -e "$OUTC/SWEEP-DONE" ]; do sleep 60; done
echo "RETIRED 22:41 A-B watcher exits $(date -u +%FT%TZ)"; exit 0
