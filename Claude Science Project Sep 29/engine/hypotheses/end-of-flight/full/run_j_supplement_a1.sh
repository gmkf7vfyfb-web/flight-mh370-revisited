#!/bin/bash
# Overnight order A add-on (coordination 19 Oct 2026 ~04:20Z, lowest priority): the A1-branch CONDITIONAL pass
# (results/eof-a1-branch-oct18: production recipe + smoke/score-select-0019-raw.toml + smoke/a1-branch.toml, i.e. onset
# flame-out-associated and no intervention only, D3-aimed scored selection K = 8) on the K-strided run-J northern supplement
# parents (the same parents as run_j_supplement.sh). Terminal seed 30000 + (s - 1000) so the streams differ from the first pass.
# Output Poisson-thinned (both_burst_thin.py, THIN_CELLS none,r600/no-offset,both/no-offset,both/startup-offset; A1_TARGET rows).
set -u
CORE=${SUP_CORE:-/Users/pete/Downloads/mh370-exchange/core}; ROOT=${SUP_ROOT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement}
OUT=${A1_OUT:-$ROOT/north-k2-a1branch}; BIN=${SUP_BIN:-/tmp/mh370-eof-rj1}; K=${SUP_K:-2}; THREADS=${SUP_THREADS:-12}
MIN=${SUP_MIN_FREE_GB:-5}; CAP=${SUP_CAP_GB:-40}; TARGET=${A1_TARGET:-500000}
SEEDS=${SUP_SEEDS:-"1001 1002 1003 1004 1005 1006 1007 1008 1009 1010 1011 1012 1013 1014 1015 1016"}
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python; STRIDE=${SUP_STRIDE_PY:?path to handoff_stride.py}
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2 THIN_CELLS=none,r600/no-offset,both/no-offset,both/startup-offset
[ "$(shasum -a 256 $BIN | cut -c1-16)" = 19031f41748ecb0c ] || { echo "BINARY SHA MISMATCH"; exit 2; }
CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$CORE/run-j/run-j-waypoints/run.json")
EXTRA="$S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml $S/smoke/trim-at-loss.toml $S/full/pushover.toml $S/full/boeing-sequence.toml $S/full/b-late-onset-proposal.toml $S/full/holland-estimable.toml $S/full/a1-aimed-pitchdown.toml $S/full/piloted-turns.toml $S/full/run-i.toml $S/smoke/within-parent-unnormalised.toml"
EXTRA="$EXTRA $S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/smoke/children-16.toml $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml $S/smoke/score-select-0019-raw.toml $S/smoke/a1-branch.toml"
echo "A1-branch pass: K=$K target=$TARGET threads=$THREADS out=$OUT"; mkdir -p "$OUT"
for s in $SEEDS; do
  X=$((30000 + s - 1000)); D="$OUT/seed-$s"
  if [ -f "$D/SHA256SUMS" ]; then echo "seed $s done: skipped"; continue; fi
  while :; do free=$(df -g /System/Volumes/Data | tail -1 | awk '{print $4}'); used=$(du -sg "$ROOT" | awk '{print $1}')
    [ "$free" -ge "$MIN" ] && [ "$used" -lt "$CAP" ] && break; echo "  PAUSED: ${free} GiB free, order uses ${used} GB ($(date -u +%T))"; sleep 300; done
  H=$CORE/run-j-supplement/north/seed-$s/handoff-m0011-supplement; RT=runs/RJA-$X; d=$RT/bto-bfo/seed-$X; rm -rf $RT
  $PY "$STRIDE" $H $d $K || { echo "STRIDE FAILED $s"; continue; }
  printf '# overnight order A add-on, A1-branch pass: supplement seed %s\nseeds = [%s]\n' $s $X > $S/full/seed-$X.toml
  o=runs/RJA-o$X; T=runs/RJA-c$X; rm -rf $o $T; echo "seed $s (terminal seed $X) start $(date -u +%T)"
  RAYON_NUM_THREADS=$THREADS $BIN terminal $RT $CHAIN $S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $S/full/reference-289.toml $S/full/descent-idle-floor.toml $S/full/seed-$X.toml $EXTRA $o 2>&1 | tail -1
  $PY $S/smoke/compact_impacts.py write $o $o/bto-bfo/seed-$X $T > /dev/null 2>&1 && rm -f $o/bto-bfo/seed-$X/impacts.npy \
    && $PY $S/smoke/both_burst_thin.py $T "$D" $TARGET $X > "$D.thin.json" 2>&1 \
    && cp $o/bto-bfo/seed-$X/terminal.json $d/stride.json "$D/" && cp $d/handoff.npy "$D/handoff-subset.npy" && rm -rf $T $d/handoff.toml \
    || echo "  A1 FAILED seed $s (files kept)"
  echo "seed $s done $(date -u +%T); $(df -g /System/Volumes/Data | tail -1 | awk '{print $4}') GiB free; order uses $(du -sg "$ROOT" | awk '{print $1}') GB"
done
echo "A1 SWEEP DONE $(date -u +%FT%TZ)"
