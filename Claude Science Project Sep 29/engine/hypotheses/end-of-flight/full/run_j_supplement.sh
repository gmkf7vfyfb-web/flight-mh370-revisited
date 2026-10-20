#!/bin/bash
# Overnight order A (19 Oct 2026, Pete approved): end of flight's PRODUCTION recipe on core's run-J northern supplement
# (core results/run-j-supplement, 16 seeds 1001-1016, handoff-m0011-supplement, 100,000 rows each).
# Recipe = run_j_production.sh for run-j-waypoints exactly: core run J waypoints chain (run.json config_paths) + snapshot-m0011 +
# terminal + reference-289 + descent-idle-floor + seed-<s>.toml + the sweep_run_i.sh module overlays + c2-silent-aim + dive-branch
# + children-16 + round3-laws + bank-cap-uniform; binary mh370-eof-rj1 (sha256 19031f41748ecb0c); config files at a517deeb (the
# tree the production pass ran from). The supplement's own core overlays (size-north, supplement) set only filter sizes, seeds
# and the supplement flag, which the terminal stage does not read.
# Disk: a fixed every-K-th-row subset (K = SUP_K, default 2; rule B multiplies u2 by K) because all rows (~45 GB) exceed the
# 40 GB order cap. Pauses (never deletes) while df free < SUP_MIN_FREE_GB (5) or the order's own bytes exceed SUP_CAP_GB (40).
# Usage (from the engine tree at a517deeb): SUP_SEEDS="1001 ..." SUP_K=2 bash run_j_supplement.sh
set -u
CORE=${SUP_CORE:-/Users/pete/Downloads/mh370-exchange/core}
OUT=${SUP_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement/north-k2}
BIN=${SUP_BIN:-/tmp/mh370-eof-rj1}; K=${SUP_K:-2}; THREADS=${SUP_THREADS:-12}
MIN=${SUP_MIN_FREE_GB:-5}; CAP=${SUP_CAP_GB:-40}; ROOT=${SUP_ROOT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-supplement}
SEEDS=${SUP_SEEDS:-"1001 1002 1003 1004 1005 1006 1007 1008 1009 1010 1011 1012 1013 1014 1015 1016"}
CHILDREN=${SUP_CHILDREN:-hypotheses/end-of-flight/smoke/children-16.toml}; TAG=${SUP_TAG:-RJS}
S=hypotheses/end-of-flight; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python; STRIDE=${SUP_STRIDE_PY:?path to handoff_stride.py}
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2
[ "$(shasum -a 256 $BIN | cut -c1-16)" = 19031f41748ecb0c ] || { echo "BINARY SHA MISMATCH"; exit 2; }
CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$CORE/run-j/run-j-waypoints/run.json")
EXTRA="$S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml $S/smoke/trim-at-loss.toml $S/full/pushover.toml $S/full/boeing-sequence.toml $S/full/b-late-onset-proposal.toml $S/full/holland-estimable.toml $S/full/a1-aimed-pitchdown.toml $S/full/piloted-turns.toml $S/full/run-i.toml $S/smoke/within-parent-unnormalised.toml"
EXTRA="$EXTRA $S/full/c2-silent-aim.toml $S/full/dive-branch.toml $CHILDREN $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml"
echo "binary $BIN ok; K=$K threads=$THREADS out=$OUT; chain $(echo $CHAIN | wc -w) files; overlays: $EXTRA"
RT=runs/$TAG-supp; mkdir -p $RT/bto-bfo "$OUT"
for s in $SEEDS; do
  if [ -f "$OUT/seed-$s/SHA256SUMS" ] && $PY $S/smoke/compact_impacts.py check "$OUT/seed-$s" > /dev/null 2>&1; then echo "seed $s verified: skipped"; continue; fi
  while :; do free=$(df -g /System/Volumes/Data | tail -1 | awk '{print $4}'); used=$(du -sg "$ROOT" | awk '{print $1}')
    [ "$free" -ge "$MIN" ] && [ "$used" -lt "$CAP" ] && break; echo "  PAUSED: ${free} GiB free, order uses ${used} GB ($(date -u +%T))"; sleep 300; done
  H=$CORE/run-j-supplement/north/seed-$s/handoff-m0011-supplement
  want=$(grep "north/seed-$s/handoff-m0011-supplement/handoff.toml.gz" $CORE/run-j-supplement/SHA256SUMS | cut -c1-64)
  [ "$want" = "$(shasum -a 256 $H/handoff.toml.gz | cut -c1-64)" ] || { echo "SHA MISMATCH seed $s"; continue; }
  d=$RT/bto-bfo/seed-$s; rm -rf $d; $PY "$STRIDE" $H $d $K || { echo "STRIDE FAILED $s"; continue; }
  printf '# overnight order A: run J supplement seed %s (one process per seed)\nseeds = [%s]\n' $s $s > $S/full/seed-$s.toml
  o=runs/$TAG-s$s; rm -rf $o; echo "seed $s start $(date -u +%T)"
  RAYON_NUM_THREADS=$THREADS $BIN terminal $RT $CHAIN $S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $S/full/reference-289.toml $S/full/descent-idle-floor.toml $S/full/seed-$s.toml $EXTRA $o 2>&1 | tail -1
  ls -l $o/bto-bfo/seed-$s/impacts.npy | awk '{print "  full impacts bytes", $5}'
  $PY $S/smoke/compact_impacts.py write $o $o/bto-bfo/seed-$s "$OUT/seed-$s" > "$OUT/seed-$s.convert8.log" 2>&1 \
    && $PY $S/smoke/compact_impacts.py check "$OUT/seed-$s" \
    && cp $o/bto-bfo/seed-$s/terminal.json "$OUT/seed-$s/" && cp $d/handoff.npy "$OUT/seed-$s/handoff-subset.npy" && cp $d/stride.json "$OUT/seed-$s/" \
    && rm -f $o/bto-bfo/seed-$s/impacts.npy $d/handoff.toml \
    || echo "  CONVERT FAILED seed $s (full file kept)"
  echo "seed $s done $(date -u +%T); $(df -g /System/Volumes/Data | tail -1 | awk '{print $4}') GiB free; order uses $(du -sg "$ROOT" | awk '{print $1}') GB"
done
echo "SUPPLEMENT SWEEP DONE $(date -u +%FT%TZ)"
