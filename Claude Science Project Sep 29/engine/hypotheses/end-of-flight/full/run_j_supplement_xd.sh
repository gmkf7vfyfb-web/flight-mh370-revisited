#!/bin/bash
# Overnight order A step 4 (19 Oct 2026): EXTRA DESCENTS per supplement parent for the both-burst treatments (D2-D5), on the
# K-strided supplement subset flown by run_j_supplement.sh. Recipe = that production recipe with children-64 in place of
# children-16 (256 descents per parent; as the 17 Oct both-burst supplementary pass), on the subset parents with 00:11 latitude
# >= XD_LAT_MIN (default -35.5), in XD_G interleaved parent groups per seed (default 4) so that the transient full file stays
# about 4 GB. Each group gets its OWN terminal seed XD_SEED_BASE (20000; 50000 for the 20 Oct second half, XD_OFFSET=1) + 10 (s - 1000) + g, because the child streams are keyed by
# (seed, purpose, child, row): re-using the hand-off seed would repeat the first pass's descents. Output is Poisson-thinned
# (both_burst_thin.py, cells r600/no-offset, both/*; XD_TARGET rows per group, default 250,000). Same disk guard as the first pass.
set -u
CORE=${SUP_CORE:-/Users/pete/Downloads/mh370-exchange/core}; ROOT=${SUP_ROOT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement}
OUT=${XD_OUT:-$ROOT/north-k2-xd256}; BIN=${SUP_BIN:-/tmp/mh370-eof-rj1}; K=${SUP_K:-2}; THREADS=${SUP_THREADS:-12}
MIN=${SUP_MIN_FREE_GB:-5}; CAP=${SUP_CAP_GB:-40}; OFF=${XD_OFFSET:-0}; XB=${XD_SEED_BASE:-20000}; G=${XD_G:-4}; LATMIN=${XD_LAT_MIN:--35.5}; TARGET=${XD_TARGET:-250000}
SEEDS=${SUP_SEEDS:-"1001 1002 1003 1004 1005 1006 1007 1008 1009 1010 1011 1012 1013 1014 1015 1016"}
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python; SEL=${XD_SELECT_PY:?path to handoff_select.py}
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2
[ "$(shasum -a 256 $BIN | cut -c1-16)" = 19031f41748ecb0c ] || { echo "BINARY SHA MISMATCH"; exit 2; }
CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$CORE/run-j/run-j-waypoints/run.json")
EXTRA="$S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml $S/smoke/trim-at-loss.toml $S/full/pushover.toml $S/full/boeing-sequence.toml $S/full/b-late-onset-proposal.toml $S/full/holland-estimable.toml $S/full/a1-aimed-pitchdown.toml $S/full/piloted-turns.toml $S/full/run-i.toml $S/smoke/within-parent-unnormalised.toml"
EXTRA="$EXTRA $S/full/c2-silent-aim.toml $S/full/dive-branch.toml $S/full/children-64.toml $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml"
echo "extra descents: K=$K groups=$G lat>=$LATMIN target=$TARGET threads=$THREADS out=$OUT"; mkdir -p "$OUT"
for g in $(seq 0 $((G - 1))); do for s in $SEEDS; do
  X=$((XB + 10 * (s - 1000) + g)); D="$OUT/seed-$s/g$g"
  if [ -f "$D/SHA256SUMS" ]; then echo "seed $s group $g done: skipped"; continue; fi
  while :; do free=$(df -g /System/Volumes/Data | tail -1 | awk '{print $4}'); used=$(du -sg "$ROOT" | awk '{print $1}')
    [ "$free" -ge "$MIN" ] && [ "$used" -le "$CAP" ] && break; echo "  PAUSED: ${free} GiB free, order uses ${used} GB ($(date -u +%T))"; sleep 300; done
  H=$CORE/run-j-supplement/north/seed-$s/handoff-m0011-supplement; RT=runs/RJX-$X; d=$RT/bto-bfo/seed-$X; rm -rf $RT; mkdir -p $RT/bto-bfo
  $PY "$SEL" $H $d $K $LATMIN $g $G $OFF || { echo "SELECT FAILED $s $g"; continue; }
  printf '# overnight order A extra descents: supplement seed %s group %s\nseeds = [%s]\n' $s $g $X > $S/full/seed-$X.toml
  o=runs/RJX-o$X; T=runs/RJX-c$X; rm -rf $o $T; echo "seed $s group $g (terminal seed $X) start $(date -u +%T)"
  RAYON_NUM_THREADS=$THREADS $BIN terminal $RT $CHAIN $S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $S/full/reference-289.toml $S/full/descent-idle-floor.toml $S/full/seed-$X.toml $EXTRA $o 2>&1 | tail -1
  $PY $S/smoke/compact_impacts.py write $o $o/bto-bfo/seed-$X $T > /dev/null 2>&1 && rm -f $o/bto-bfo/seed-$X/impacts.npy \
    && mkdir -p "$OUT/seed-$s" && $PY $S/smoke/both_burst_thin.py $T "$D" $TARGET $X > "$D.thin.json" 2>&1 \
    && cp $o/bto-bfo/seed-$X/terminal.json $d/select.json $d/handoff.npy "$D/" && rm -rf $T $d/handoff.toml \
    || echo "  XD FAILED seed $s group $g (files kept)"
  echo "seed $s group $g done $(date -u +%T); $(df -g /System/Volumes/Data | tail -1 | awk '{print $4}') GiB free; order uses $(du -sg "$ROOT" | awk '{print $1}') GB"
done; done
echo "XD SWEEP DONE $(date -u +%FT%TZ)"
