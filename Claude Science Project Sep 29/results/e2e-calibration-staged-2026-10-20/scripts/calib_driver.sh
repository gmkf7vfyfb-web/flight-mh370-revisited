#!/bin/bash
# Staged end-to-end calibration run (Pete, 20 Oct 2026): A1 tier 1a' event, A2 shared pool, A4 data-only drift rule, S2 joint draw; A3 held -> 4 x 3.5 M.
# Detached and RESUMABLE: rerun this script after any stop; finished chunks/cases are skipped. Holds the deskstar heavy lock for the whole run.
# usage: cd ~/mh370/e2e && setsid nohup bash calib_driver.sh > calib-2026-10-20/driver.log 2>&1 < /dev/null &
set -u; cd $HOME/mh370/e2e; . ./env.sh; RUN=$E2E/calib-2026-10-20; export POOL=$E2E/pool; mkdir -p $RUN/case-stats $RUN/claim
export PPM="[500_000, 250_000, 1_250_000, 250_000, 1_250_000]" HR=20000 R=4 ITH=${ITH:-44} TTH=40 CHN=192 MAXC=400 MINDISK=8
CASES="39005 $(seq -s' ' 3001 3030)"      # 39005: generator re-check (seed 9005 stream, corrected generator), reported apart; 3001-3030: tier 1a' short run
STAMP=$(date -u +%FT%TZ); echo "$STAMP driver start pid $$" >> $RUN/driver-starts.txt; tl "calib driver start (pid $$); cases: $CASES"
exec 9>>$HOME/.mh370-heavy.lock; flock -w 86400 9 || { tl "calib driver NO-GO heavy lock busy"; exit 8; }; tl "calib driver heavy lock held"
for cl in $RUN/claim/*; do [ -d "$cl" ] && { n=${cl##*/case-}; [ -f $RUN/case-stats/case-$n/case-stats.json ] || { tl "stale claim case $n removed"; rm -rf $cl; }; }; done
if [ ! -f $RUN/SELFTEST-OK ]; then
  tl "stage 0 self-test start"; rm -rf $E2E/pool-test $E2E/cases/case-99001
  bash build_pool.sh $E2E/pool-test 1000 500 80 > $RUN/selftest-pool.log 2>&1 || { tl "SELF-TEST FAILED: pool"; exit 10; }
  POOL=$E2E/pool-test EVENT="m0011.bto:17540:18540,m0011.bfo:202:302" MAXC=60 CHN=16 PPM="[10_000, 5_000, 25_000, 5_000, 25_000]" HR=1000 R=2 ITH=80 bash case_pipeline2.sh 99001 truth infer score > $RUN/selftest-case.log 2>&1 || { tl "SELF-TEST FAILED: case (see $RUN/selftest-case.log)"; exit 10; }
  $PY -c "import json;S=json.load(open('$E2E/cases/case-99001/case-stats.json'));print('selftest D0|core',S['pooled']['D0|core']['u_lat'],S['drift_rule'])" >> $RUN/selftest-case.log 2>&1 || { tl "SELF-TEST FAILED: stats"; exit 10; }
  echo "$STAMP" > $RUN/SELFTEST-OK; tl "stage 0 self-test OK"; rm -rf $E2E/pool-test
fi
if [ ! -f $POOL/COMPLETE ]; then tl "stage 1 pool build start/resume"; bash build_pool.sh $POOL ${NREP:-300000} 1000 80 >> $RUN/pool.log 2>&1 || { tl "POOL BUILD FAILED"; exit 11; }; fi
finish_case() { n=$1; O=$RUN/case-stats/case-$n; mkdir -p $O; D=$E2E/cases/case-$n
  cp $D/case-stats.json $D/truth.json $D/truth-core.json $D/walltimes.txt $O/ 2>/dev/null; cp $D/hist.json $D/memory-events.txt $D/truth-candidates.json $O/ 2>/dev/null
  $PY -c "import json;c=json.load(open('$O/truth-candidates.json'));[x.pop('epochs',None) for x in c['candidates']];json.dump(c,open('$O/truth-candidates.json','w'))" 2>/dev/null
  grep -q 'oom_kill [1-9]' $D/memory-events.txt 2>/dev/null && tl "WARNING case $n: cgroup oom_kill count non-zero (memory.events)"
  (cd $E2E && $PY py/aggregate.py $RUN > /dev/null 2>&1); tl "case $n finished and archived; $(sed -n 2p $RUN/STATUS.txt)"; }
lane() { L=$1
  for n in $CASES; do
    [ -f $RUN/case-stats/case-$n/case-stats.json ] && continue
    mkdir $RUN/claim/case-$n 2>/dev/null || continue
    tl "lane $L takes case $n"; t0=$(date +%s)
    if bash case_pipeline2.sh $n truth infer score >> $RUN/lane-$L.log 2>&1; then echo "case total $(( $(date +%s)-t0 ))" >> $E2E/cases/case-$n/walltimes.txt; finish_case $n
    else tl "lane $L case $n FAILED rc $? (claim kept; see $RUN/lane-$L.log)"; echo $n >> $RUN/failed.txt; fi
  done; tl "lane $L: no more cases"; }
lane A & sleep 90; lane B & wait
(cd $E2E && $PY py/aggregate.py $RUN > /dev/null 2>&1); tl "calib driver done; $(sed -n 2p $RUN/STATUS.txt)"; echo "$(date -u +%FT%TZ)" > $RUN/DRIVER-DONE
