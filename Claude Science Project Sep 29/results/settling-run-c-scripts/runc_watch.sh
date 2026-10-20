#!/bin/sh
# Run C trigger for settling: end of flight writes only <stratum>/READY (sweep_run_c.sh). Check each stratum as it lands; on 4 of 4 run the chain.
W=$(pwd); R=/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c; SM2="$W/wt-base/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke"
DONE=""
for i in $(seq 1 720); do
  for st in next-c-free next-c-repro-radar next-c-descent-climb next-c-routes; do
    case " $DONE " in *" $st "*) continue;; esac
    if [ -e "$R/$st/READY" ]; then echo "$st READY seen $(date -u +%H:%MZ)"; python3 runc_check.py "$SM2" "$R/$st" > "runc_check_$st.log" 2>&1 && echo "$st check ok" || { echo "$st CHECK FAILED"; tail -3 "runc_check_$st.log"; }; DONE="$DONE $st"; fi
  done
  set -- $DONE; if [ $# -eq 4 ]; then echo "4/4 READY $(date -u +%H:%MZ); summary: $(ls $R/../next-run-c/summary 2>/dev/null | tr '\n' ' ')"; sh runc_chain.sh > runc_chain.log 2>&1; tail -12 runc_chain.log; exit 0; fi
  sleep 60
done; echo "timeout; done:$DONE"
