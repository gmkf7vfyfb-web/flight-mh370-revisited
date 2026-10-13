#!/bin/bash
# End of flight, 13 Oct 2026 (work order items 0-2, Pete: "smoke tests and small runs before any major computational effort").
# SMOKE / PILOT SCALE - NEVER EVIDENCE. Two reduced runs on core run I, stratum next-i-waypoints (core P(family) 0.9982), seed 1,
# all 100,000 hand-off parents, N = 4 children x 4 descents (1.6 M descents each), the run-i-dive recipe otherwise:
#   P0011  00:11 hand-off, run-i-dive recipe exactly, N = 4. Child streams are keyed by (seed, child, row), so its rows must equal
#          the first 4 of 16 children of run-i-dive seed 1 in every physics column: an identity check on the rebuilt binary, and the
#          "before" for item 1 at 00:11.
#   P2241  22:41 hand-off (V2 with all three onset mechanisms, so V1b = the flame-out-associated subset and families A and B are
#          estimable from ONE sample set), 23:15 + 00:11 + 00:19 scored in-stage (smoke/options-m2241.toml). Deliberate-onset
#          control weights [1,1,1,1] (coverage, contract section 4: all four outcomes in every family); the legacy [0.6,0.4,0,0] is
#          recovered exactly by re-weighting on latent:control_requested. Gate 4: onset-boundary statistic, support truncation,
#          onset-window length.
# arm-v2 is named BEFORE the recipe so that v2-broad's anticipatory lead support [0, 9000 s] stands (onset uniform on
# [22:41, predicted exhaustion]); arm-v2 then contributes only mechanism_weights [1,1,1].
# Full impacts kept (EOF_KEEP_FULL) under runs/. Run from engine/:
#   nohup hypotheses/end-of-flight/full/pilot_oct13.sh > /tmp/eof-pilot-oct13.log 2>&1 &
set -u
CORE=/Users/pete/Downloads/mh370-exchange/core/run-i
BIN=${EOF_BIN:-/Users/pete/Downloads/mh370-exchange/end-of-flight/bin/mh370-eof-o13}
THREADS=${EOF_THREADS:-12}
ARMS=${EOF_ARMS:-"P0011 P2241"}
st=next-i-waypoints; k=1; S=hypotheses/end-of-flight; SD=$CORE/$st
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
REC="$S/full/reference-289.toml $S/full/descent-idle-floor.toml $S/full/seed-$k.toml $S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml $S/smoke/trim-at-loss.toml $S/full/pushover.toml $S/full/boeing-sequence.toml $S/full/b-late-onset-proposal.toml $S/full/holland-estimable.toml $S/full/a1-aimed-pitchdown.toml $S/full/piloted-turns.toml $S/full/run-i.toml $S/smoke/within-parent-unnormalised.toml $S/full/c2-silent-aim.toml $S/full/dive-branch.toml"
echo "binary $BIN sha256 $(shasum -a 256 $BIN | cut -c1-16); threads $THREADS; $(date -u +%FT%TZ)"
stage() {   # epoch -> run tree with the gunzipped, sha-verified hand-off
  ep=$1; H="$SD/bto-bfo/seed-$k/handoff-$ep"; RT=runs/PO13-$ep; d=$RT/bto-bfo/seed-$k; rm -rf $RT; mkdir -p $d
  ln -s "$H/handoff.npy" $d/handoff.npy; gzip -dc "$H/handoff.toml.gz" > $d/handoff.toml
  want=$(cat "$SD/COMPACT.txt" "$CORE/COMPACT.txt" 2>/dev/null | grep "$st/bto-bfo/seed-$k/handoff-$ep/handoff.toml.gz" | head -1 | sed "s/.*sha256(uncompressed)=\([0-9a-f]*\).*/\1/")
  got=$(shasum -a 256 $d/handoff.toml | cut -c1-64)
  if [ -n "$want" ] && [ "$want" != "$got" ]; then echo "SHA MISMATCH $ep"; exit 4; fi
  echo "hand-off $ep sha256 $([ -n "$want" ] && echo verified || echo NOT-LISTED) $got"
}
for arm in $ARMS; do
  if [ $arm = P0011 ]; then stage m0011; X="$S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $REC $S/smoke/children-4.toml"
  else stage m2241; X="$S/smoke/snapshot-m2241.toml $S/smoke/terminal.toml $S/smoke/options-m2241.toml $S/smoke/arm-v2.toml $REC $S/smoke/children-4.toml $S/smoke/deliberate-control-all4.toml"; fi
  o=runs/PO13-$arm; rm -rf $o
  echo "$arm start $(date -u +%T)"
  lockf -k /tmp/.mh370-heavy.lock env RAYON_NUM_THREADS=$THREADS /usr/bin/time -l $BIN terminal $RT $CHAIN $X $o 2>&1 | grep -E "end of flight|error|Error|maximum resident|real" | tail -4
  echo "$arm done $(date -u +%T)"
done
echo "PILOT DONE $(date -u +%FT%TZ)"; touch runs/PO13-DONE
