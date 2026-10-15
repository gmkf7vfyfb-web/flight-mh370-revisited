#!/bin/bash
# Item 8 (work order 15 Oct 2026, Task B): the round-3 laws as a LABELLED SENSITIVITY at run-I scale.
# Same recipe as run-i-dive (arm C + C2-silent aim + dive branch) with full/round3-laws.toml appended last.
# NOT a calibration: the section 8 gate stays FAILED. Outputs are summarised per stratum and the big per-seed
# files are then removed, because the disk cannot hold a second 56 GB sweep (41 GiB free on 15 Oct).
# Usage: bash hypotheses/end-of-flight/full/sweep_round3.sh   (from engine/; set R3_OUT and EOF_BIN; R3_EXTRA = overlays
# appended after round3-laws.toml, e.g. full/bank-cap-sampled.toml or full/bank-cap-90.toml for order (b) item 3)
set -u
S=hypotheses/end-of-flight
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
OUT=${R3_OUT:?set R3_OUT}
BIN=${EOF_BIN:?set EOF_BIN}
CORE=/Users/pete/Downloads/mh370-exchange/core/run-i
THREADS=${EOF_THREADS:-12}
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2
mkdir -p "$OUT/summary"
echo "ROUND-3 SENSITIVITY SWEEP start $(date -u +%FT%TZ); binary $BIN sha256 $(shasum -a 256 $BIN | cut -c1-16); $THREADS threads"
# Small strata first, then waypoints (its eight seeds need about 22 GB at once).
for st in next-i-free next-i-repro-radar next-i-descent-climb next-i-waypoints; do
  echo "=== $st $(date -u +%FT%TZ); free $(df -g /Users/pete | tail -1 | awk '{print $4}') GiB"
  X="$S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/full/round3-laws.toml ${R3_EXTRA:-}"
  [ "$st" = next-i-waypoints ] && X="$S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/smoke/children-16.toml $S/full/round3-laws.toml ${R3_EXTRA:-}"
  EOF_BIN=$BIN EOF_EXTRA="$X" EOF_STRATA=$st EOF_THREADS=$THREADS EOF_OUT="$OUT" EOF_TAG=${R3_TAG:-R3} \
    bash $S/full/sweep_run_i.sh 2>&1 | sed "s/^/  /"
  n=$(ls -d "$OUT/$st"/seed-*/ 2>/dev/null | wc -l | tr -d ' ')
  if [ "$n" -lt 1 ]; then echo "$st: NO SEEDS, stopping"; exit 2; fi
  echo "  $st: $n seeds; sidecar + table $(date -u +%T)"
  $PY $S/smoke/tau_sidecar.py "$OUT/$st"/seed-*/ > "$OUT/summary/$st-tau.log" 2>&1 || echo "  TAU SIDECAR FAILED $st"
  $PY $S/smoke/option_table_0019.py "$OUT" "$CORE" "$OUT/summary/table-0019-$st.json" "$st=1.0" \
    > "$OUT/summary/table-0019-$st.log" 2>&1 || echo "  OPTION TABLE FAILED $st"
  $PY $S/smoke/round3_subsample.py "$OUT/$st" "$OUT/summary/subsample-$st.npz" > "$OUT/summary/$st-subsample.log" 2>&1 \
    || echo "  SUBSAMPLE FAILED $st"
  if [ -s "$OUT/summary/table-0019-$st.json" ] && [ -s "$OUT/summary/subsample-$st.npz" ]; then
    du -sh "$OUT/$st" | sed "s/^/  removing /"; rm -rf "$OUT/$st"; rm -rf runs/${R3_TAG:-R3}-$st runs/${R3_TAG:-R3}-$st-s*
  else
    echo "  KEEPING $st: a summary is missing"; fi
done
echo "ROUND-3 SWEEP DONE $(date -u +%FT%TZ)"
touch "$OUT/SWEEP-DONE"
