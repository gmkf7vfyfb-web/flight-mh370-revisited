#!/bin/sh
# Composer pass 1 (run C) driver for one stratum: the six terminal columns (three 00:19 options x {all rows, contact speed <= 212 m/s}),
# one composer invocation each (peak RAM), summarised at once and the composed weights deleted (disk).
# run C NOT CONVERGED. Outside the heavy lock: composer single-threaded, summariser 2 threads.
# Usage: sh run_stratum_c.sh <work dir> <stratum> <source split-half mean> <min> [<export dir>]
set -eu
W="$1"; ST="$2"; SH="$3"; SHMIN="$4"; EX="${5:-}"
HERE="$(cd "$(dirname "$0")" && pwd)"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
UNP="m0019b.burst-exists,m0115.handshake-unanswered"
if ! mkdir "$W/work/lock-$ST" 2>/dev/null; then      # one composer per stratum (a duplicate orchestrator waits here)
  while [ ! -e "$W/work/done-$ST" ]; do sleep 20; done; exit 0
fi
for OPT in r600-bto+unpowered heldout+unpowered r600-bfo+unpowered r600-bto+unpowered-v212 heldout+unpowered-v212 r600-bfo+unpowered-v212; do
  case "$OPT" in
    heldout*) OBS="$UNP";; r600-bto*) OBS="m0019a.bto,$UNP";; r600-bfo*) OBS="m0019a.bto,m0019a.bfo,$UNP";;
  esac
  echo "== $ST $OPT start $(date -u +%T)"
  "$W/bin/pass1" "$W/work/inputs/$ST" "$W/work/rust/$ST/$OPT" 8 "$OPT" "$OBS" "$SH" 0.924 \
    "source: core run C $ST split-half overlap, mean over 35 balanced partitions (min $SHMIN), floor 0.924 for 8 replicates (CORE_STAGES ~00:12 UTC)" 2> "$W/logs/pass1-$ST-$OPT.err"
  if { [ "$OPT" = "r600-bto+unpowered" ] || [ "$OPT" = "heldout+unpowered" ]; } && [ -n "$EX" ]; then
    python3 "$HERE/summarise_stratum_c.py" "$ST" "$W/work/inputs/$ST" "$W/work/rust/$ST/$OPT" "$W/work/summary" "$OPT" --export "$EX" o-G,o-H
  else
    python3 "$HERE/summarise_stratum_c.py" "$ST" "$W/work/inputs/$ST" "$W/work/rust/$ST/$OPT" "$W/work/summary" "$OPT"
  fi
  rm -rf "$W/work/rust/$ST/$OPT/weights"
done
touch "$W/work/done-$ST"; echo "== $ST done $(date -u +%T)"; df -h /Users/pete/Downloads | tail -1
