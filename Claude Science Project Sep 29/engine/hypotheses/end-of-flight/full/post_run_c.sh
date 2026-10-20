#!/bin/bash
# End of flight: summaries on the run C sweep, after SWEEP-DONE. Writes $OUT/summary/; does NOT write READY (the module
# session reviews and writes the README with COVERAGE and labels first). 2 threads, outside the heavy lock.
# P_CORE: core's posterior family probabilities through 00:11 for run C, as "stratum=value ..." (from core's run C note).
# Run from engine/:  P_CORE="next-free=... next-repro-radar=... next-descent-climb=... next-routes=..." hypotheses/end-of-flight/full/post_run_c.sh
set -eu
OUT=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c}
export EOF_CORE_RUN=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/next-run-c}
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2
[ -e "$OUT/SWEEP-DONE" ] || { echo "no SWEEP-DONE in $OUT"; exit 2; }
: "${P_CORE:?set P_CORE from the core run C note}"
SUM=$OUT/summary; mkdir -p "$SUM/impact-time"
STRATA=$(for p in $P_CORE; do echo "${p%%=*}"; done)
for st in $STRATA; do $PY $S/smoke/impact_time_shares.py "$OUT/$st" "$SUM/impact-time/$st" | tail -2; done
$PY $S/smoke/family_evidence.py "$OUT" "$SUM/family-evidence-run-c.json" $P_CORE | tail -25
$PY $S/smoke/family_shares.py "$OUT" "$SUM/family-shares-run-c.json" $P_CORE | tail -8
for con in unpowered alive silent; do $PY $S/smoke/same_data_bf.py "$SUM/family-evidence-run-c.json" "$SUM/same-data-bf-run-c-$con.json" $con; done
# G13 (architecture 20:35 -0600): the contact-speed <= 212 m/s version beside every product.
for con in unpowered silent; do $PY $S/smoke/same_data_bf.py "$SUM/family-evidence-run-c.json" "$SUM/same-data-bf-run-c-$con-v212.json" "$con ~v212"; done
$PY $S/smoke/postpred_0019.py "$OUT" "$SUM/postpred-0019-run-c.json" $STRATA | tail -12
echo "POST DONE $(date -u +%FT%TZ)"
