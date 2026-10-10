#!/bin/bash
# End of flight's sweep on core run C (architecture milestone ruling, 15:20 -0600 10 Oct; compact format 14:30 -0600).
# Waits for core's READY, then for each stratum: one hold of the heavy lock at 12 threads for its seeds, each seed written
# full in this workspace, converted to the compact float32 format on the exchange (smoke/compact_impacts.py, verified at
# write), the full file then removed from THIS workspace. Recipe = eof-289-full (N = 8 x 4 descents, descent idle floor ON)
# on top of core's own config chain for the stratum, read from core's run.json in core's order. Refuses to run if a config
# is missing here (merge core first) or if the chain flies two tanks on internal-v1 without the INOP-flow correction.
# Optional: touch $OUT/USE-TRIM-AT-LOSS before it starts to add smoke/trim-at-loss.toml (ruling item 3) to every seed.
# Run from engine/:  nohup hypotheses/end-of-flight/full/sweep_run_c.sh > /tmp/eof-run-c.log 2>&1 &
set -u
CORE=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/next-run-c}
OUT=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c}
BIN=${EOF_BIN:-/tmp/mh370-eof-runc4}
S=hypotheses/end-of-flight
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2
echo "waiting for $CORE/READY $(date -u +%FT%TZ)"
while [ ! -e "$CORE/READY" ]; do sleep 60; done
echo "core READY seen $(date -u +%FT%TZ)"; mkdir -p "$OUT"
# Recipe additions (architecture 15:45 -0600 10 Oct): the broadened descent envelope (PROVISIONAL-OVERNIGHT option B of 10 Oct)
# and family B as ruled (deliberate onset + approach to ditching; loss en route as a sub-variant).
# Boeing's residual roll direction, P(left) = 0.8 (PROVISIONAL, 22:40 UTC 10 Oct; options posted to Pete): before it every
# free-flight descent turned right. Re-weight exactly with latent:residual_bank_sign.
EXTRA="$S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml"
[ -e "$OUT/USE-TRIM-AT-LOSS" ] && EXTRA="$EXTRA $S/smoke/trim-at-loss.toml" && echo "trim at loss ON"
echo "module overlays: $EXTRA"
for SD in "$CORE"/*/; do
  st=$(basename "$SD"); [ -f "$SD/run.json" ] || continue
  CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
  for f in $CHAIN; do [ -f "$f" ] || { echo "MISSING config $f for $st: merge core first; stopping"; exit 2; }; done
  if echo "$CHAIN" | grep -q "s6-tanks" && ! echo "$CHAIN" | grep -q "inop-flow-fix" && ! grep -q "internal-v1.1" $CHAIN 2>/dev/null; then
    echo "REFUSING $st: two tanks on internal-v1 without the INOP-flow correction (doubled one-engine flow)"; exit 3; fi
  RT=runs/C-$st; mkdir -p $RT/bto-bfo
  SEEDS=$(ls -d "$SD"/bto-bfo/seed-* 2>/dev/null | sed 's/.*seed-//' | sort -n)
  echo "$st: seeds $(echo $SEEDS | tr '\n' ' ') chain $(echo $CHAIN | wc -w) files; lock wait $(date -u +%T)"
  lockf -k ${EOF_LOCK:-/tmp/.mh370-heavy.lock} bash -c '
    st=$1; RT=$2; BIN=$3; CHAIN=$4; EXTRA=$5; OUT=$6; SD=$7; shift 7
    for k in "$@"; do
      ln -sfn "$SD/bto-bfo/seed-$k/handoff-m0011" $RT/bto-bfo/seed-$k
      cfg="hypotheses/end-of-flight/full/seed-$k.toml"; [ -f "$cfg" ] || { echo "  no $cfg: skipping seed $k"; continue; }
      o=runs/C-$st-s$k; rm -rf $o; mkdir -p "$OUT/$st"
      echo "  $st seed $k start $(date -u +%T)"
      RAYON_NUM_THREADS=12 $BIN terminal $RT $CHAIN hypotheses/end-of-flight/smoke/snapshot-m0011.toml hypotheses/end-of-flight/smoke/terminal.toml hypotheses/end-of-flight/full/reference-289.toml hypotheses/end-of-flight/full/descent-idle-floor.toml $cfg $EXTRA $o 2>&1 | tail -1
      /Users/pete/.claude-science/conda/envs/eof-sim/bin/python hypotheses/end-of-flight/smoke/compact_impacts.py write $o $o/bto-bfo/seed-$k "$OUT/$st/seed-$k" > "$OUT/$st/seed-$k.convert.log" 2>&1 \
        && /Users/pete/.claude-science/conda/envs/eof-sim/bin/python hypotheses/end-of-flight/smoke/compact_impacts.py check "$OUT/$st/seed-$k" \
        && cp $o/bto-bfo/seed-$k/terminal.json "$OUT/$st/seed-$k/" && rm -f $o/bto-bfo/seed-$k/impacts.npy \
        || { echo "  CONVERT FAILED $st seed $k (full file kept)"; }
    done' _ "$st" "$RT" "$BIN" "$CHAIN" "$EXTRA" "$OUT" "$SD" $SEEDS
  echo "$st done $(date -u +%T)"
done
echo "SWEEP DONE $(date -u +%FT%TZ) - summaries and READY follow (written by the module session after review)"
touch "$OUT/SWEEP-DONE"
