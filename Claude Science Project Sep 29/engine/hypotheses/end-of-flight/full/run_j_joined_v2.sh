#!/bin/bash
# RUN J joined V2 (16 Oct 2026): copy of run_joined_v2.sh on core run J, stratum run-j-waypoints, with the run-J production laws
# (round-3 + bank limit uniform on [52, 90] deg, Pete ~16:40Z) and, in J2241, the clock-time onset proposal window
# (smoke/onset-window-2241.toml; Pete's item 4 ruling, 02:08Z: the direct 22:41-arm run belongs to run J's end-of-flight pass).
# Joined V2 production (Pete's ruling 14 Oct 2026: "join with the 00:11 run"; approved budget ~4 h). Core run I, stratum
# next-i-waypoints (core P(family) 0.9982), seeds $SEEDS, binary mh370-eof-o13d, under the heavy lock at 12 threads.
#   J0011: 00:11 hand-off, run-i-dive recipe + exact fuel cue + all-four deliberate control, N = 8 x 4. Families A1/A2 (all of them)
#          and deliberate onsets after 00:11.
#   J2241: 22:41 hand-off, same recipe + deliberate onsets only (mechanism_weights [1, 1, 0], exact pi factor in the join) + scored
#          candidate selection aimed at m0011 (K = 8, defensive 0.2), N = 8 x 4. Deliberate onsets before 00:11.
# Each seed: run, slim (float32, times offset; verified), delete the full file. Output: mh370-exchange/end-of-flight/run-i-joined-v2/.
set -u
CORE=${RJ_CORE:-/Users/pete/Downloads/mh370-exchange/core/run-j}; st=run-j-waypoints; SD=$CORE/$st; S=hypotheses/end-of-flight
BIN=${EOF_BIN:-/tmp/mh370-eof-rj1}; SEEDS=${SEEDS:-"1 2 3 4 5 6 7 8"}
OUT=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-joined-v2}; ARMS=${ARMS:-"J0011 J2241"}
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
REC="$S/full/reference-289.toml $S/full/descent-idle-floor.toml SEEDCFG $S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml $S/smoke/trim-at-loss.toml $S/full/pushover.toml $S/full/boeing-sequence.toml $S/full/b-late-onset-proposal.toml $S/full/holland-estimable.toml $S/full/a1-aimed-pitchdown.toml $S/full/piloted-turns.toml $S/full/run-i.toml $S/smoke/within-parent-unnormalised.toml $S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml"
cat > /tmp/children-8.toml <<'T'
[terminal]
children = 8
T
cat > /tmp/deliberate-only.toml <<'T'
[hypotheses.end-of-flight.onset]
mechanism_weights = [1.0, 1.0, 0.0]
T
mkdir -p $OUT; echo "binary $(basename $BIN) sha256 $(shasum -a 256 $BIN | cut -c1-16); seeds $SEEDS; $(date -u +%FT%TZ)" | tee -a $OUT/LOG
for arm in $ARMS; do for k in $SEEDS; do
  [ -f $OUT/$arm/seed-$k/SHA256SUMS ] && { echo "$arm seed $k done: skipped"; continue; }
  if [ $arm = J0011 ]; then ep=m0011; X="$S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml ${REC/SEEDCFG/$S/full/seed-$k.toml} /tmp/children-8.toml $S/smoke/deliberate-control-all4.toml $S/smoke/fuel-cue-exact.toml"
  else ep=m2241; X="$S/smoke/snapshot-m2241.toml $S/smoke/terminal.toml $S/smoke/options-m2241.toml $S/smoke/arm-v2.toml ${REC/SEEDCFG/$S/full/seed-$k.toml} /tmp/children-8.toml $S/smoke/deliberate-control-all4.toml $S/smoke/fuel-cue-exact.toml /tmp/deliberate-only.toml $S/smoke/score-select-2241.toml $S/smoke/onset-window-2241.toml"; fi
  H="$SD/bto-bfo/seed-$k/handoff-$ep"; RT=runs/RJV2-$ep-s$k; d=$RT/bto-bfo/seed-$k; rm -rf $RT; mkdir -p $d
  ln -s "$H/handoff.npy" $d/handoff.npy; gzip -dc "$H/handoff.toml.gz" > $d/handoff.toml
  want=$(cat "$SD/COMPACT.txt" "$CORE/COMPACT.txt" 2>/dev/null | grep "$st/bto-bfo/seed-$k/handoff-$ep/handoff.toml.gz" | head -1 | sed "s/.*sha256(uncompressed)=\([0-9a-f]*\).*/\1/")
  got=$(shasum -a 256 $d/handoff.toml | cut -c1-64); [ -n "$want" ] && [ "$want" != "$got" ] && { echo "SHA MISMATCH $arm $k"; continue; }
  while :; do free=$(df -g /Users/pete | tail -1 | awk '{print $4}'); [ "$free" -ge "${EOF_MIN_FREE_GB:-15}" ] && break
    echo "  waiting: ${free} GiB free ($(date -u +%T))"; sleep 300; done
  o=runs/RJV2-$arm-s$k; rm -rf $o
  echo "$arm seed $k start $(date -u +%T)" | tee -a $OUT/LOG
  lockf -k /tmp/.mh370-heavy.lock env RAYON_NUM_THREADS=14 $BIN terminal $RT $CHAIN $X $o > $o.log 2>&1 || { echo "RUN FAILED $arm $k"; tail -3 $o.log; continue; }
  OMP_NUM_THREADS=2 PYTHONPATH=$S/smoke $PY $S/smoke/slim_impacts.py $o $k $OUT/$arm/seed-$k && cp $o/bto-bfo/seed-$k/terminal.json $OUT/$arm/seed-$k/ \
    && rm -f $o/bto-bfo/seed-$k/impacts.npy || echo "SLIM FAILED $arm $k (full file kept)"
  rm -f $d/handoff.toml
  echo "$arm seed $k done $(date -u +%T)" | tee -a $OUT/LOG
done; done
echo "JOINED V2 RUNS DONE $(date -u +%FT%TZ)" | tee -a $OUT/LOG; touch $OUT/RUNS-DONE
