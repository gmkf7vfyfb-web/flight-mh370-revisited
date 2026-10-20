#!/bin/bash
# STAND-IN copy (architecture, 11 Oct 2026, ruling 5e8f13ea) of end of flight's full/sweep_2241_ab.sh. Same recipe, same configs, same
# binary as run C (097a5d77 build, /tmp/mh370-eof-runc5, copied); changes, all disclosed in the results note: input core run D (look-ahead
# hand-offs, read by the binary's handoff::read_corrected); outside the heavy lock at RAYON_NUM_THREADS=8 (ruling); outputs in the
# stand-in workspace; no wait for SWEEP-DONE; strata via env PAIRS; EoF's slim replaced by standin_ab_summary.py's mini npz (disk);
# [stop] block saved per seed. ab_evidence.py runs unchanged.
set -u
ENG="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/83c5d472-a2a6-4ff0-9602-ceefbdadb1ad/repo/Claude Science Project Sep 29/engine"
cd "$ENG" || exit 1
CORE=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/next-run-d}
OUT=${STANDIN_OUT:-/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/abd}
BIN=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/bin/mh370-eof-runc5
PAIRS=${PAIRS:-"next-d-free:1"}
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
COMMON="$S/smoke/snapshot-m2241.toml $S/smoke/terminal.toml $S/smoke/options-m2241.toml $S/smoke/children-4.toml"
MOD="$S/full/descent-idle-floor.toml $S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml"
for pk in $PAIRS; do
  st=${pk%%:*}; k=${pk##*:}; SD="$CORE/$st"
  if [ -f $OUT/ab-$st-s$k-standin.json ]; then echo "$st seed $k already done: skipped"; continue; fi
  CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
  H="$SD/bto-bfo/seed-$k/handoff-m2241"; RT=$OUT/rt-$st-s$k; d=$RT/bto-bfo/seed-$k; rm -rf $RT; mkdir -p $d
  ln -s "$H/handoff.npy" $d/handoff.npy
  gzip -dc "$H/handoff.toml.gz" > $d/handoff.toml || continue
  want=$(grep "$st/bto-bfo/seed-$k/handoff-m2241/handoff.toml.gz" "$CORE/COMPACT.txt" | sed "s/.*sha256(uncompressed)=\([0-9a-f]*\).*/\1/")
  got=$(shasum -a 256 $d/handoff.toml | cut -c1-64)
  [ -n "$want" ] && [ "$want" != "$got" ] && { echo "SHA MISMATCH $st seed $k"; rm -f $d/handoff.toml; continue; }
  echo "$st seed $k handoff sha256 $got (COMPACT: ${want:-none})"
  awk '/^\[lookahead\]/{exit} {print}' $d/handoff.toml > $OUT/stop-$st-s$k.toml
  ok=1
  for arm in A B; do
    [ $arm = A ] && ARM=$S/smoke/arm-v1.toml || ARM=$S/full/arm-b-deliberate.toml
    o=$OUT/$st-$arm-s$k; rm -rf $o
    t0=$(date +%s); echo "$st seed $k arm $arm start $(date -u +%T)"
    env RAYON_NUM_THREADS=8 $BIN terminal $RT $CHAIN $COMMON $S/full/seed-$k.toml $ARM $MOD $o > $OUT/log-$st-$arm-s$k.txt 2>&1
    rc=$?; tail -1 $OUT/log-$st-$arm-s$k.txt | head -c 300; echo
    echo "  rc $rc wall $(( $(date +%s) - t0 )) s"; [ $rc = 0 ] || ok=0
  done
  rm -f $d/handoff.toml
  A=$OUT/$st-A-s$k; B=$OUT/$st-B-s$k
  if [ $ok = 1 ]; then
    OMP_NUM_THREADS=2 $PY $S/smoke/ab_evidence.py $A $B $OUT/ab-$st-s$k.json $k | head -3 \
     && OMP_NUM_THREADS=2 $PY /Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/14a4dd3f-9a30-4bb8-9f1b-d19d4441c1df/standin/standin_ab_summary.py $A $B $k $OUT/ab-$st-s$k-standin.json $S/smoke \
     && rm -f $A/bto-bfo/seed-$k/impacts.npy $B/bto-bfo/seed-$k/impacts.npy || echo "  EVIDENCE/SUMMARY FAILED $st seed $k (full files kept)"
  else echo "  RUN FAILED $st seed $k"; fi
  df -h /Users/pete/Downloads | tail -1 | awk '{print "  disk free " $4}'
done
echo "STANDIN A-B DONE $PAIRS $(date -u +%FT%TZ)"
