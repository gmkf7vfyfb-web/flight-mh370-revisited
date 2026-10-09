#!/bin/bash
# Full fit of the 6-DOF to the ten Boeing cases, then leave-one-out refits of the shared physics.
# Queued behind the project's heavy-compute lock; run from engine/:  lockf -k /tmp/.mh370-heavy.lock hypotheses/end-of-flight/sim/run_fit.sh
set -e
cd "$(dirname "$0")"
export PYTHONPATH=. OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
OUT=../../../runs/boeing/fit-oct09; mkdir -p "$OUT"
# Idempotent: a second queued copy (a guard against a lost first one) exits at once if a fit has started.
# Pete's lock order (architecture ~19:50, 9 Oct): drift's production waits for /tmp/mh370-eof-fit.DONE, so it
# is touched on ANY exit, failure included, with the exit status recorded in $OUT/status.
if [ -e "$OUT/STARTED" ]; then echo "fit already started $(cat "$OUT/STARTED"); this copy exits"; exit 0; fi
date -u +%FT%TZ > "$OUT/STARTED"
exec >> "$OUT/run.log" 2>&1
trap 'rc=$?; echo "exit $rc $(date -u +%FT%TZ)" > "$OUT/status"; touch /tmp/mh370-eof-fit.DONE' EXIT
echo "full fit start $(date -u +%FT%TZ)"
python fit_all.py "$OUT/full" --rounds 3 --workers 10 --case-iter 200 --shared-iter 300
echo "full fit end $(date -u +%FT%TZ)"
for c in case01 case02 case03 case04 case05 case06 case07 case08 case09 case10; do
  python fit_all.py "$OUT/loo-$c" --rounds 1 --workers 10 --case-iter 150 --shared-iter 200 --exclude "$c" --init "$OUT/full/state.json"
  echo "loo $c end $(date -u +%FT%TZ)"
done
echo ALLDONE
