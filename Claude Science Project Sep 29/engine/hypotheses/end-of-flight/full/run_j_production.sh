#!/bin/bash
# Run J PRODUCTION end-of-flight pass (Pete, 16 Oct 2026 ~16:40Z): run-i-dive recipe (C2-silent aim + dive branch, children-16 on
# waypoints) with round-3 laws and the bank limit drawn uniformly on [52, 90] deg (full/bank-cap-uniform.toml).
# One seed per sweep call, with a free-disk guard (EOF_MIN_FREE_GB, default 30) because core's run J is still landing on the same
# disk. Per-seed calls write README/READY, which are removed until the last call; the final call over all seeds (all skipped,
# already verified) writes the stratum README and READY. Usage (from engine/): RJ_WS=<workspace> RJ_STRATA="run-j-waypoints" bash ...
set -u
W=${RJ_WS:?workspace}; STRATA=${RJ_STRATA:-run-j-waypoints}; OUT=${RJ_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j}
S=hypotheses/end-of-flight; MIN=${EOF_MIN_FREE_GB:-30}; CORE=${RJ_CORE:-$W/ob/rjcore2}
for st in $STRATA; do
  X="$S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml"
  [ "$st" = run-j-waypoints ] && X="$S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/smoke/children-16.toml $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml"
  SEEDS=$(ls -d "$CORE/$st"/bto-bfo/seed-* | sed 's/.*seed-//' | sort -n | tr '\n' ' ')
  echo "$st seeds $SEEDS start $(date -u +%T)"
  for k in $SEEDS; do
    while :; do free=$(df -g /Users/pete | tail -1 | awk '{print $4}'); [ "$free" -ge "$MIN" ] && break
      echo "  waiting: ${free} GiB free < $MIN ($(date -u +%T))"; sleep 300; done
    EOF_CORE=$CORE EOF_BIN=${RJ_BIN:-/tmp/mh370-eof-rj1} EOF_EXTRA="$X" EOF_STRATA=$st EOF_SEEDS=$k EOF_THREADS=14 EOF_OUT=$OUT EOF_TAG=RJP \
      bash $S/full/sweep_run_i.sh 2>&1 | grep -E "seed $k start|FAIL|MISMATCH|REFUS|MISSING|rror|skipped"
    rm -f "$OUT/$st/READY" "$OUT/$st/README.md"; echo "  seed $k done $(date -u +%T), $(df -g /Users/pete | tail -1 | awk '{print $4}') GiB free"
  done
  EOF_CORE=$CORE EOF_BIN=${RJ_BIN:-/tmp/mh370-eof-rj1} EOF_EXTRA="$X" EOF_STRATA=$st EOF_SEEDS="$SEEDS" EOF_OUT=$OUT EOF_TAG=RJP bash $S/full/sweep_run_i.sh > /dev/null 2>&1
  [ -f "$OUT/$st/READY" ] && printf '\nRUN J (not run I): hand-offs %s/%s (core run-j); overlays: %s\n' "$CORE" "$st" "$X" >> "$OUT/$st/README.md"
  echo "$st READY: $([ -f "$OUT/$st/READY" ] && echo yes || echo NO) $(date -u +%T)"
done; echo RJP-DONE $(date -u +%T)
