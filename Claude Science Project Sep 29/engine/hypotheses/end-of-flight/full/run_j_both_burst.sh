#!/bin/bash
# Run J both-burst SUPPLEMENTARY pass (Pete approved 16 Oct ~03:40Z; results/eof-both-burst-oct16 section 4b).
# Per seed: run-i-dive recipe + children-64 (256 descents per parent) on the run-J m0011 hand-off, compact, then unbiased
# Poisson thinning to 1M rows over the both-burst cells (smoke/both_burst_thin.py), then delete the 11 GB compact file.
# Usage: RJ_STRATUM=run-j-waypoints RJ_SEEDS="1 2 ..." bash run_j_both_burst.sh   (run from engine/)
set -u
W=${RJ_WS:?workspace}; ST=${RJ_STRATUM:-run-j-waypoints}; SEEDS=${RJ_SEEDS:-"1 2 3 4 5 6 7 8"}
OUT=${RJ_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-both-burst}; TMP=$W/ob/rjbb-tmp
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
# Recipe = run J production (round-3 laws + uniform bank limit, Pete 16 Oct ~16:40Z) with children-64 in place of children-16.
# Seed 1 on the old production laws is kept, labelled, in end-of-flight/run-j-both-burst-production-laws/.
X="$S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/full/children-64.toml $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml"
for k in $SEEDS; do
  if [ -f "$OUT/$ST/seed-$k/SHA256SUMS" ]; then echo "seed $k done: skipped"; continue; fi
  while :; do free=$(df -g /Users/pete | tail -1 | awk '{print $4}'); [ "$free" -ge "${EOF_MIN_FREE_GB:-40}" ] && break
    echo "  waiting: ${free} GiB free ($(date -u +%T))"; sleep 300; done
  echo "seed $k start $(date -u +%T)"
  EOF_CORE=$W/ob/rjcore2 EOF_BIN=${RJ_BIN:-/tmp/mh370-eof-rj1} EOF_EXTRA="$X" EOF_STRATA=$ST EOF_SEEDS=$k EOF_THREADS=14 EOF_OUT=$TMP EOF_TAG=RJBB \
    bash $S/full/sweep_run_i.sh 2>&1 | grep -E "start|FAIL|MISMATCH|REFUS|MISSING|rror"
  PYTHONPATH=$S/smoke $PY $S/smoke/both_burst_thin.py $TMP/$ST/seed-$k "$OUT/$ST/seed-$k" 1000000 $k > "$OUT/$ST/seed-$k.thin.json" 2>&1 \
    && cp $TMP/$ST/seed-$k/terminal.json "$OUT/$ST/seed-$k/" && rm -rf $TMP/$ST/seed-$k && echo "seed $k thinned $(date -u +%T)" \
    || echo "THIN FAILED seed $k (compact kept)"
done; echo RJBB-DONE $(date -u +%T)
