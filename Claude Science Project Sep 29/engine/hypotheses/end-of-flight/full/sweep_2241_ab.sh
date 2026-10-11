#!/bin/bash
# End of flight: the 22:41 A-vs-B runs on core run C's m2241 hand-offs (after the run C sweep; Pete's lock priority).
# For each core stratum, seeds $SEEDS, arms A (smoke/arm-v1.toml) and B (full/arm-b-deliberate.toml): the module flies from
# 22:41 and scores 23:15, 00:11 and 00:19 in-stage (smoke/options-m2241.toml). N = 4 children x 4 descents. Same module recipe as
# run C otherwise (idle floor, v2-broad, family-b-ditching, residual-bank-boeing). Full outputs stay in this workspace.
# Run from engine/:  nohup hypotheses/end-of-flight/full/sweep_2241_ab.sh > /tmp/eof-2241-ab.log 2>&1 &
set -u
CORE=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/next-run-c}
OUTC=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c}
BIN=${EOF_BIN:-/tmp/mh370-eof-runc4}
SEEDS=${EOF_SEEDS:-"1 2 3 4"}
S=hypotheses/end-of-flight
echo "waiting for $OUTC/SWEEP-DONE $(date -u +%FT%TZ)"
while [ ! -e "$OUTC/SWEEP-DONE" ]; do sleep 60; done
COMMON="$S/smoke/snapshot-m2241.toml $S/smoke/terminal.toml $S/smoke/options-m2241.toml $S/smoke/children-4.toml"
MOD="$S/full/descent-idle-floor.toml $S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml"
for SD in "$CORE"/*/; do
  st=$(basename "$SD"); [ -f "$SD/run.json" ] || continue
  CHAIN=$(/Users/pete/.claude-science/conda/envs/eof-sim/bin/python -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
  for k in $SEEDS; do
    if [ -f runs/C2241-$st-s$k-ab.json ] && [ -f runs/C2241-$st-A-s$k/bto-bfo/seed-$k/slim.npz ] && [ -f runs/C2241-$st-B-s$k/bto-bfo/seed-$k/slim.npz ]; then
      echo "$st seed $k already done: skipped"; continue; fi
    H="$SD/bto-bfo/seed-$k/handoff-m2241"; RT=runs/C2241-$st-s$k; d=$RT/bto-bfo/seed-$k; rm -rf $RT; mkdir -p $d
    ln -s "$H/handoff.npy" $d/handoff.npy
    if [ -f "$H/handoff.toml" ]; then ln -s "$H/handoff.toml" $d/handoff.toml; else gzip -dc "$H/handoff.toml.gz" > $d/handoff.toml || continue
      want=$(grep "$st/bto-bfo/seed-$k/handoff-m2241/handoff.toml.gz" "$SD/COMPACT.txt" | sed "s/.*sha256(uncompressed)=\([0-9a-f]*\).*/\1/")
      got=$(shasum -a 256 $d/handoff.toml | cut -c1-64)
      [ -n "$want" ] && [ "$want" != "$got" ] && { echo "SHA MISMATCH $st seed $k"; rm -f $d/handoff.toml; continue; }
    fi
    for arm in A B; do
      [ $arm = A ] && ARM=$S/smoke/arm-v1.toml || ARM=$S/full/arm-b-deliberate.toml
      o=runs/C2241-$st-$arm-s$k; rm -rf $o
      echo "$st seed $k arm $arm lock wait $(date -u +%T)"
      lockf -k /tmp/.mh370-heavy.lock env RAYON_NUM_THREADS=12 $BIN terminal $RT $CHAIN $COMMON $S/full/seed-$k.toml $ARM $MOD $o 2>&1 | tail -1
    done
    [ -L $d/handoff.toml ] || rm -f $d/handoff.toml
    PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python; A=runs/C2241-$st-A-s$k; B=runs/C2241-$st-B-s$k
    OMP_NUM_THREADS=2 $PY $S/smoke/ab_evidence.py $A $B runs/C2241-$st-s$k-ab.json $k | head -3 \
      && OMP_NUM_THREADS=2 $PY $S/smoke/ab_evidence.py slim $A $k && OMP_NUM_THREADS=2 $PY $S/smoke/ab_evidence.py slim $B $k \
      && rm -f $A/bto-bfo/seed-$k/impacts.npy $B/bto-bfo/seed-$k/impacts.npy || echo "  EVIDENCE/SLIM FAILED $st seed $k (full files kept)"
  done
done
echo "2241 A-B DONE $(date -u +%FT%TZ)"; touch runs/C2241-DONE
