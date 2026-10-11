#!/bin/sh
# Orchestrate pass 1 over the four strata with at most two strata of inputs on disk (disk cap); poll every 5 min for inputs.
W="$1"; G="$W/glue"; X=/Users/pete/Downloads/mh370-exchange
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
prep() { st="$1"; n="$2"; for k in 1 2 3 4 5 6 7 8; do echo $k; done | (cd "$G" && xargs -P "$n" -I{} python3 prep_inputs_c.py "$st" {} "$W/work/inputs/$st") >> "$W/logs/prep-$st.log" 2>&1; }
ready_inputs() { st="$1"
  [ -e "$X/end-of-flight/next-run-c/$st/READY" ] && [ -e "$X/debris-drift/next-run-c/$st/.exported" ] || return 1
  [ -e "$X/pleiades/hydro-test/next-run-c/READY" ] && return 0
  for k in 1 2 3 4 5 6 7 8; do [ -s "$X/pleiades/hydro-test/next-run-c/$st/seed-$k/pleiades-lnL.npy" ] || return 1; done
  [ -z "$(find "$X/pleiades/hydro-test/next-run-c/$st" -newermt '-5 minutes' 2>/dev/null | head -1)" ]; }
waitfor() { while ! grep -q "== $1 done" "$W/logs/stratum-$2.log" 2>/dev/null; do sleep 30; done; }
waitfor next-c-free free; rm -rf "$W/work/inputs/next-c-free"
prep next-c-descent-climb 2 &
sh "$G/run_stratum_c.sh" "$W" next-c-repro-radar 0.910 0.862 "$W/work/export" > "$W/logs/stratum-repro-radar.log" 2>&1
rm -rf "$W/work/inputs/next-c-repro-radar"
( until ready_inputs next-c-routes; do echo "routes inputs not ready $(date -u +%T)"; sleep 300; done; prep next-c-routes 2 ) >> "$W/logs/chain.log" 2>&1 &
wait %1 2>/dev/null; while [ "$(ls "$W/work/inputs/next-c-descent-climb"/*.json 2>/dev/null | wc -l)" -lt 8 ]; do sleep 20; done
sh "$G/run_stratum_c.sh" "$W" next-c-descent-climb 0.892 0.856 "$W/work/export" > "$W/logs/stratum-descent-climb.log" 2>&1
rm -rf "$W/work/inputs/next-c-descent-climb"
while [ "$(ls "$W/work/inputs/next-c-routes"/*.json 2>/dev/null | wc -l)" -lt 8 ]; do sleep 30; done
sh "$G/run_stratum_c.sh" "$W" next-c-routes 0.850 0.822 "$W/work/export" > "$W/logs/stratum-routes.log" 2>&1
rm -rf "$W/work/inputs/next-c-routes"
echo "chain done $(date -u +%T)" >> "$W/logs/chain.log"
