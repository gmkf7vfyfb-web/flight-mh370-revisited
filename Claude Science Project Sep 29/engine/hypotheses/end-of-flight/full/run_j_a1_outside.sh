#!/bin/bash
# Overnight order A item 3 (20 Oct 2026): second A1 conditional pass, A1 OUTSIDE the flame-out / no-intervention branch
# (smoke/a1-outside.toml: onset flame-out-associated, control "upset then recovery"), on run J waypoints seeds 1-8 x 100,000 paths
# (the 18 Oct branch pass's hand-offs), with the production recipe + D3-aimed scored selection (score-select-0019-raw, K = 8) as the
# branch pass. Terminal seeds 60000 + k (not the hand-off seed: descent streams are keyed by (seed, purpose, child, row)).
# Output Poisson-thinned (THIN_CELLS none,r600/no-offset,both/no-offset,both/startup-offset; O2_TARGET rows per seed).
set -u
CORE=${SUP_CORE:-/Users/pete/Downloads/mh370-exchange/core}; ROOT=${SUP_ROOT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement}
OUT=${O2_OUT:-$ROOT/run-j-a1outside}; BIN=${SUP_BIN:-/tmp/mh370-eof-rj1}; THREADS=${SUP_THREADS:-12}
MIN=${SUP_MIN_FREE_GB:-5}; CAP=${SUP_CAP_GB:-60}; TARGET=${O2_TARGET:-400000}; SEEDS=${O2_SEEDS:-"1 2 3 4 5 6 7 8"}
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2 THIN_CELLS=none,r600/no-offset,both/no-offset,both/startup-offset
[ "$(shasum -a 256 $BIN | cut -c1-16)" = 19031f41748ecb0c ] || { echo "BINARY SHA MISMATCH"; exit 2; }
SD=$CORE/run-j/run-j-waypoints; CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
EXTRA="$S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml $S/smoke/trim-at-loss.toml $S/full/pushover.toml $S/full/boeing-sequence.toml $S/full/b-late-onset-proposal.toml $S/full/holland-estimable.toml $S/full/a1-aimed-pitchdown.toml $S/full/piloted-turns.toml $S/full/run-i.toml $S/smoke/within-parent-unnormalised.toml"
EXTRA="$EXTRA $S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/smoke/children-16.toml $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml $S/smoke/score-select-0019-raw.toml $S/smoke/a1-outside.toml"
echo "A1-outside pass: seeds $SEEDS target=$TARGET threads=$THREADS out=$OUT"; mkdir -p "$OUT"
for k in $SEEDS; do
  X=$((60000 + k)); D="$OUT/seed-$k"
  if [ -f "$D/SHA256SUMS" ]; then echo "seed $k done: skipped"; continue; fi
  while :; do free=$(df -g /System/Volumes/Data | tail -1 | awk '{print $4}'); used=$(du -sg "$ROOT" | awk '{print $1}')
    [ "$free" -ge "$MIN" ] && [ "$used" -lt "$CAP" ] && break; echo "  PAUSED: ${free} GiB free, order uses ${used} GB ($(date -u +%T))"; sleep 300; done
  H=$SD/bto-bfo/seed-$k/handoff-m0011; RT=runs/RJO-$X; d=$RT/bto-bfo/seed-$X; rm -rf $RT; mkdir -p $d
  ln -s "$H/handoff.npy" $d/handoff.npy; gzip -dc "$H/handoff.toml.gz" > $d/handoff.toml || { echo "GUNZIP FAILED $k"; continue; }
  want=$(cat "$CORE/run-j/COMPACT.txt" "$SD/COMPACT.txt" 2>/dev/null | grep "run-j-waypoints/bto-bfo/seed-$k/handoff-m0011/handoff.toml.gz" | head -1 | sed "s/.*sha256(uncompressed)=\([0-9a-f]*\).*/\1/")
  got=$(shasum -a 256 $d/handoff.toml | cut -c1-64); [ -n "$want" ] && [ "$want" != "$got" ] && { echo "SHA MISMATCH $k"; continue; }
  echo "  seed $k hand-off sha256 $([ -n "$want" ] && echo verified || echo NOT-LISTED)"
  printf '# overnight order A (20 Oct) A1-outside pass: run J waypoints seed %s\nseeds = [%s]\n' $k $X > $S/full/seed-$X.toml
  o=runs/RJO-o$X; T=runs/RJO-c$X; rm -rf $o $T; echo "seed $k (terminal seed $X) start $(date -u +%T)"
  RAYON_NUM_THREADS=$THREADS $BIN terminal $RT $CHAIN $S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $S/full/reference-289.toml $S/full/descent-idle-floor.toml $S/full/seed-$X.toml $EXTRA $o 2>&1 | tail -1
  $PY $S/smoke/compact_impacts.py write $o $o/bto-bfo/seed-$X $T > /dev/null 2>&1 && rm -f $o/bto-bfo/seed-$X/impacts.npy \
    && $PY $S/smoke/both_burst_thin.py $T "$D" $TARGET $X > "$D.thin.json" 2>&1 \
    && cp $o/bto-bfo/seed-$X/terminal.json "$D/" && rm -rf $T $d/handoff.toml \
    || echo "  A1-OUTSIDE FAILED seed $k (files kept)"
  echo "seed $k done $(date -u +%T); $(df -g /System/Volumes/Data | tail -1 | awk '{print $4}') GiB free; order uses $(du -sg "$ROOT" | awk '{print $1}') GB"
done
echo "A1-OUTSIDE SWEEP DONE $(date -u +%FT%TZ)"
