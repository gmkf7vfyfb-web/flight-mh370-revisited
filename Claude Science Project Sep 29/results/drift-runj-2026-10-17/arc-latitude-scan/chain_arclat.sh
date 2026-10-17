#!/bin/bash
# Arc-latitude scan chain (17 Oct 2026). Waits for the drift thread's chain3 to finish, then GlobCurrent south, north, GLORYS12 south, north.
set -u
A=$HOME/mh370/drift/arclat; cd $A
echo "queued $(date -u +%FT%TZ) waiting for chain3 pid ${WAITPID:-none}" >> $A/chain.log
[ -n "${WAITPID:-}" ] && while kill -0 $WAITPID 2>/dev/null; do sleep 60; done
for L in arclat-globcurrent-south arclat-globcurrent-north arclat-glorys12-south arclat-glorys12-north; do
  echo "start $L $(date -u +%FT%TZ)" >> $A/chain.log
  $A/run_arclat.sh $A/$L.toml $L
  echo "end $L $(tail -1 $HOME/mh370/drift/runs/$L.log) $(date -u +%FT%TZ)" >> $A/chain.log
  cp $HOME/mh370/drift/runs/$L/nodes.csv $A/$L-nodes.csv 2>/dev/null; cp $HOME/mh370/drift/runs/$L/summary.toml $A/$L-summary.toml 2>/dev/null
done
echo ALL-DONE $(date -u +%FT%TZ) >> $A/chain.log
