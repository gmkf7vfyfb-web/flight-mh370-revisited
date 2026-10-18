#!/bin/sh
# Settling on end of flight's run J: four strata in parallel (prep 1 thread each; settle 2 threads, one at a time => <= 5 workers),
# whole run under the project heavy lock. Final README / mixture weights / READY written last, only if all four published.
WK=/Users/pete/Downloads/mh370-settling-work-j; cd $WK; X=/Users/pete/Downloads/mh370-exchange/settling/run-j; mkdir -p $X
echo "start $(date -u +%FT%TZ) free $(df -g /Users/pete | awk 'NR==2{print $4}') GiB"
for st in run-j-waypoints run-j-free run-j-descent-climb run-j-repro-radar; do sh run_j_stratum.sh $st > log_stratum_$st.txt 2>&1 & done
wait
cat log_stratum_*.txt
ok=0; for st in run-j-waypoints run-j-free run-j-descent-climb run-j-repro-radar; do [ -e $X/$st/READY ] && ok=$((ok+1)); done
if [ $ok -eq 4 ]; then
  export HOME=$WK/home MPLCONFIGDIR=$WK/mpl
  python3 wf_runj.py final "$X" '{"run-j-waypoints": 0.9982, "run-j-free": 0.0013, "run-j-descent-climb": 0.0002, "run-j-repro-radar": 0.0003}' && echo "ALL DONE $(date -u +%FT%TZ)"
else echo "INCOMPLETE: $ok of 4 strata published $(date -u +%FT%TZ)"; fi
echo "end free $(df -g /Users/pete | awk 'NR==2{print $4}') GiB"
