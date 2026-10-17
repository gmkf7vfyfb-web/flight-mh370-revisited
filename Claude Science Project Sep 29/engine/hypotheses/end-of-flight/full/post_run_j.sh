#!/bin/bash
# End of flight, RUN J summaries (copy of post_run_i.sh for run J): the 00:19 two-factor table (core-weighted mixture and per
# stratum), the H1/H2 sweep summary, the tau sidecar, and the consumer products of post_run_c.sh (impact-time shares, family
# evidence, family shares, same-data Bayes factors, 00:19 posterior predictive). Run from engine/ after all four strata are READY.
# Core run J P(family) at equal prior (core results/run-j/README.md, 16 Oct): waypoints 0.9982, free 0.0013, repro 0.0003, dc 0.0002.
OUT=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j}
CORE=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/run-j}
S=hypotheses/end-of-flight
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=4 NUMBA_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
MIX="run-j-waypoints=0.9982 run-j-free=0.0013 run-j-repro-radar=0.0003 run-j-descent-climb=0.0002"
for st in run-j-waypoints run-j-free run-j-repro-radar run-j-descent-climb; do [ -e "$OUT/$st/READY" ] || { echo "no READY for $st"; exit 2; }; done
mkdir -p "$OUT/summary"; touch "$OUT/SWEEP-DONE"
echo "summaries start $(date -u +%FT%TZ)"
$PY $S/smoke/option_table_0019.py "$OUT" "$CORE" "$OUT/summary/table-0019-mixture.json" $MIX > "$OUT/summary/table-0019-mixture.txt" 2>&1
for st in run-j-free run-j-descent-climb run-j-repro-radar; do
  $PY $S/smoke/option_table_0019.py "$OUT" "$CORE" "$OUT/summary/table-0019-$st.json" $st=1.0 > "$OUT/summary/table-0019-$st.txt" 2>&1
done
$PY $S/smoke/holland_sweep_summary.py "$OUT" "$OUT/summary/holland-sweep-summary.json" $MIX > "$OUT/summary/holland-sweep-summary.txt" 2>&1
$PY $S/smoke/tau_sidecar.py $(for d in "$OUT"/run-j-*/seed-[0-9]*; do [ -d "$d" ] && echo "$d"; done) > "$OUT/summary/tau-sidecar.log" 2>&1
EOF_OUT=$OUT EOF_CORE=$CORE P_CORE="$MIX" bash $S/full/post_run_c.sh > "$OUT/summary/run-c-style.log" 2>&1
for f in "$OUT"/summary/*-run-c*.json; do cp "$f" "${f/-run-c/-run-j}"; done
echo "summaries done $(date -u +%FT%TZ)"; touch "$OUT/summary/SUMMARIES-DONE"
