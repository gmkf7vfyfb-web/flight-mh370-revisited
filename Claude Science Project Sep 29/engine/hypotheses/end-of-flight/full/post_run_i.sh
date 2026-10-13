#!/bin/bash
# End of flight, run I summaries: waits for the sweep's SWEEP-DONE, then the 00:19 two-factor table (core-weighted mixture and per
# stratum, for coverage) and the H1/H2 sweep summary. Light (single process, 2 threads), outside the heavy lock. Run from engine/.
OUT=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i}
CORE=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/run-i}
S=hypotheses/end-of-flight
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
# core run I P(family) (core/run-i README, 12 Oct): waypoints 0.9982, free 0.0011, repro-radar 0.0004, descent-climb 0.0002
MIX="next-i-waypoints=0.9982 next-i-free=0.0011 next-i-repro-radar=0.0004 next-i-descent-climb=0.0002"
while [ ! -e "$OUT/SWEEP-DONE" ]; do sleep 120; done
mkdir -p "$OUT/summary"
echo "summaries start $(date -u +%FT%TZ)"
$PY $S/smoke/option_table_0019.py "$OUT" "$CORE" "$OUT/summary/table-0019-mixture.json" $MIX > "$OUT/summary/table-0019-mixture.txt" 2>&1
for st in next-i-waypoints next-i-free next-i-descent-climb next-i-repro-radar; do
  $PY $S/smoke/option_table_0019.py "$OUT" "$CORE" "$OUT/summary/table-0019-$st.json" $st=1.0 > "$OUT/summary/table-0019-$st.txt" 2>&1
done
$PY $S/smoke/holland_sweep_summary.py "$OUT" "$OUT/summary/holland-sweep-summary.json" $MIX > "$OUT/summary/holland-sweep-summary.txt" 2>&1
# Consumer products carried from run C (hydroacoustics' pulse duration; impact-time shares, family evidence, same-data BF,
# posterior predictive). Omitted on run I until 13 Oct (end of flight's error); now part of every sweep's post-processing.
$PY $S/smoke/tau_sidecar.py "$OUT"/next-i-*/seed-[0-9]* > "$OUT/summary/tau-sidecar.log" 2>&1
EOF_CORE=$CORE P_CORE="$MIX" bash $S/full/post_run_c.sh > "$OUT/summary/run-c-style.log" 2>&1
for f in "$OUT"/summary/*-run-c*.json; do cp "$f" "${f/-run-c/-$(basename "$OUT")}"; done
echo "summaries done $(date -u +%FT%TZ)"; touch "$OUT/summary/SUMMARIES-DONE"
