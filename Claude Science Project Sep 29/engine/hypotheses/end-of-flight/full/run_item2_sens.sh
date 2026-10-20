#!/bin/bash
# Item 2 POST-HOC SENSITIVITY (declared; not the approved fit, never the gate): the primary design plus the divergent-spiral bank cap
# as an 8th parameter (sim/eof_point_fit.py --free-cap). Otherwise identical to full/run_item2_fit.sh, which it must follow.
# Primary header follows. Item 2 primary fit (design approved by Pete 14 Oct 2026): the 7 shared parameters against the ten Boeing cases, all data and
# leave-one-out on every case, 11 fits in parallel under ONE heavy-lock acquisition (single-threaded each). Fixed settings:
# 4 Sobol draws of the unfitted aerodynamic parameters, bank grid as in sim/eof_point_fit.py, grid stage + Nelder-Mead (maxiter 200).
# Output: $OUT/{all,loo-Case NN}/fit.json, $OUT/summary.json/.csv (sim/eof_point_fit_summary.py). Boeing traces never copied out.
set -eu
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
TB=${EOF_TEST_BIN:-/Users/pete/Downloads/mh370-exchange/end-of-flight/bin/mh370-eof-test-o14}
OUT=${EOF_OUT:-runs/item2-fit-oct14-freecap}; ZIP="../../ISO Sept 28 Status/inputs/end-of-flight/2018-08-19-eof-sims.zip"
export EOF_OUT=$OUT EOF_TEST_BIN=$TB
if [ "${1:-}" != worker ]; then
  mkdir -p $OUT/sims $OUT/events; unzip -o -q "$ZIP" -d $OUT/sims; $PY $S/sim/boeing_events.py "$ZIP" $OUT/events >/dev/null
  echo "test binary $(basename $TB) sha256 $(shasum -a 256 $TB | cut -c1-16); start $(date -u +%FT%TZ)" | tee $OUT/LOG
fi
if [ "${1:-}" = worker ]; then   # worker: one fit; $2 = output name, $3 = excluded case or empty
  ex=(); [ -n "${3:-}" ] && ex=(--exclude "$3")
  OMP_NUM_THREADS=1 exec $PY $S/sim/eof_point_fit.py fit $OUT/sims $OUT/events/boeing-runs-targets.csv "$OUT/$2" --test-bin $TB --maxiter 200 --nuis 4 --free-cap ${ex[@]+"${ex[@]}"} > "$OUT/$2.log" 2>&1
fi
# Wait for the joined V2 production run to finish first (it takes the lock per seed; without this the fit would interleave).
AFTER=${EOF_AFTER:-}; [ -n "$AFTER" ] && while [ ! -f "$AFTER" ]; do sleep 60; done
lockf -k /tmp/.mh370-heavy.lock bash -c '
  "$0" worker all "" &
  for c in 01 02 03 04 05 06 07 08 09 10; do "$0" worker "loo-Case $c" "Case $c" & done
  wait' "$0"
$PY $S/sim/eof_point_fit_summary.py $OUT > $OUT/summary.txt; rm -rf $OUT/sims
echo "done $(date -u +%FT%TZ)" | tee -a $OUT/LOG
