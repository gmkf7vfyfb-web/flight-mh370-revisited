#!/bin/bash
# 6-DOF refit with the 10 Oct objective and optimiser (results/eof-diagnostic-smokes-oct10; coordination ~21:10 UTC).
# Queued behind the heavy lock; run from engine/:  lockf -k /tmp/.mh370-heavy.lock hypotheses/end-of-flight/sim/run_refit_oct10.sh
set -e
cd "$(dirname "$0")"
export PYTHONPATH=. OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1
export EOF_FIT_ALT_GROWTH=0.5 EOF_FIT_VS_SD=1500 EOF_FIT_MASS=172000,178000 EOF_FIT_CASE_METHOD=lsq
OUT=../../../runs/boeing/fit-oct10; mkdir -p "$OUT"
if [ -e "$OUT/STARTED" ]; then echo "refit already started $(cat "$OUT/STARTED")"; exit 0; fi
date -u +%FT%TZ > "$OUT/STARTED"
exec >> "$OUT/run.log" 2>&1
trap 'rc=$?; echo "exit $rc $(date -u +%FT%TZ)" > "$OUT/status"' EXIT
echo "refit start $(date -u +%FT%TZ)"
python fit_all.py "$OUT/full" --rounds 3 --workers 10 --case-iter 200 --shared-iter 400 --shared-method lsq --init ../../../runs/boeing/fit-oct09/full/state.json
python case_by_case.py "$OUT/full/state.json" "$OUT/case-by-case.json"
echo ALLDONE $(date -u +%FT%TZ)
