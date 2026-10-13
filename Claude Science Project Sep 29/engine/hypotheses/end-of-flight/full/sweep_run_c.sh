#!/bin/bash
# End of flight's sweep on core run C (architecture milestone ruling 15:20 -0600 10 Oct; compact format 14:30 -0600).
# Recipe = eof-289-full (N = 8 x 4 descents, descent idle floor ON) on core's own config chain per stratum (core's order), plus
# EXTRA (v2-broad, family B as ruled, Boeing residual roll direction P(left) = 0.8 PROVISIONAL). Each seed: gunzip + sha256-verify
# the m0011 hand-off, run, convert to the compact float32 format on the exchange (verified at write, then `check`), delete the full
# file. Restart-safe: a seed whose compact output passes `check` is skipped. After each stratum: $OUT/<stratum>/README.md + READY.
# Architecture 18:05 -0600 10 Oct (Pete delegated): run OUTSIDE the heavy lock at 8 threads while the 6-DOF refit holds it:
#   EOF_NOLOCK=1 EOF_THREADS=8 nohup hypotheses/end-of-flight/full/sweep_run_c.sh > /tmp/eof-run-c5.log 2>&1 &
# Default (no env): waits for core READY, takes the heavy lock per stratum, 12 threads.
set -u
CORE=${EOF_CORE:-/Users/pete/Downloads/mh370-exchange/core/next-run-c}
OUT=${EOF_OUT:-/Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c}
BIN=${EOF_BIN:-/tmp/mh370-eof-runc5}
THREADS=${EOF_THREADS:-12}
STRATA=${EOF_STRATA:-"next-c-free next-c-repro-radar next-c-descent-climb next-c-routes"}
S=hypotheses/end-of-flight
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
export PYTHONPATH=$S/smoke OMP_NUM_THREADS=2 NUMBA_NUM_THREADS=2
echo "waiting for $CORE/READY $(date -u +%FT%TZ)"
while [ ! -e "$CORE/READY" ]; do sleep 60; done
echo "core READY seen $(date -u +%FT%TZ); binary $BIN sha256 $(shasum -a 256 $BIN | cut -c1-16); threads $THREADS; lock ${EOF_NOLOCK:+OFF}"; mkdir -p "$OUT"
EXTRA="$S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml"
[ -e "$OUT/USE-TRIM-AT-LOSS" ] && EXTRA="$EXTRA $S/smoke/trim-at-loss.toml" && echo "trim at loss ON"
echo "module overlays: $EXTRA"
run_stratum() {   # st RT CHAIN SD seeds...
  st=$1; RT=$2; CHAIN=$3; SD=$4; shift 4
  for k in "$@"; do
    if [ -f "$OUT/$st/seed-$k/SHA256SUMS" ] && $PY $S/smoke/compact_impacts.py check "$OUT/$st/seed-$k" > /dev/null 2>&1; then
      echo "  $st seed $k already converted and verified: skipped"; continue; fi
    cfg="$S/full/seed-$k.toml"; [ -f "$cfg" ] || { echo "  no $cfg: skipping seed $k"; continue; }
    H="$SD/bto-bfo/seed-$k/handoff-m0011"; d=$RT/bto-bfo/seed-$k; rm -rf $d; mkdir -p $d; ln -s "$H/handoff.npy" $d/handoff.npy
    if [ -f "$H/handoff.toml" ]; then ln -s "$H/handoff.toml" $d/handoff.toml
    else
      gzip -dc "$H/handoff.toml.gz" > $d/handoff.toml || { echo "  GUNZIP FAILED $st seed $k"; continue; }
      want=$(grep "$st/bto-bfo/seed-$k/handoff-m0011/handoff.toml.gz" "$SD/COMPACT.txt" 2>/dev/null | sed "s/.*sha256(uncompressed)=\([0-9a-f]*\).*/\1/")
      got=$(shasum -a 256 $d/handoff.toml | cut -c1-64)
      if [ -n "$want" ] && [ "$want" != "$got" ]; then echo "  SHA MISMATCH $st seed $k: skipped"; rm -f $d/handoff.toml; continue; fi
      echo "  $st seed $k hand-off decompressed, sha256 $([ -n "$want" ] && echo verified || echo NOT-LISTED)"
    fi
    o=runs/C8-$st-s$k; rm -rf $o; mkdir -p "$OUT/$st"
    echo "  $st seed $k start $(date -u +%T)"
    RAYON_NUM_THREADS=$THREADS $BIN terminal $RT $CHAIN $S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $S/full/reference-289.toml $S/full/descent-idle-floor.toml $cfg $EXTRA $o 2>&1 | tail -1
    $PY $S/smoke/compact_impacts.py write $o $o/bto-bfo/seed-$k "$OUT/$st/seed-$k" > "$OUT/$st/seed-$k.convert8.log" 2>&1 \
      && $PY $S/smoke/compact_impacts.py check "$OUT/$st/seed-$k" \
      && cp $o/bto-bfo/seed-$k/terminal.json "$OUT/$st/seed-$k/" && rm -f $o/bto-bfo/seed-$k/impacts.npy \
      || echo "  CONVERT FAILED $st seed $k (full file kept)"
    [ -L $d/handoff.toml ] || rm -f $d/handoff.toml
  done
}
for st in $STRATA; do
  SD="$CORE/$st"; [ -f "$SD/run.json" ] || { echo "no $SD/run.json: skipping $st"; continue; }
  CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
  for f in $CHAIN; do [ -f "$f" ] || { echo "MISSING config $f for $st: merge core first; stopping"; exit 2; }; done
  if echo "$CHAIN" | grep -q "s6-tanks" && ! echo "$CHAIN" | grep -q "inop-flow-fix" && ! grep -q "internal-v1.1" $CHAIN 2>/dev/null; then
    echo "REFUSING $st: two tanks on internal-v1 without the INOP-flow correction (doubled one-engine flow)"; exit 3; fi
  RT=runs/C8-$st; mkdir -p $RT/bto-bfo
  SEEDS=$(ls -d "$SD"/bto-bfo/seed-* 2>/dev/null | sed 's/.*seed-//' | sort -n | tr '\n' ' ')
  echo "$st: seeds $SEEDS chain $(echo $CHAIN | wc -w) files; start $(date -u +%T)"
  if [ -n "${EOF_NOLOCK:-}" ]; then run_stratum "$st" "$RT" "$CHAIN" "$SD" $SEEDS
  else export -f run_stratum; export OUT S PY BIN THREADS EXTRA; lockf -k ${EOF_LOCK:-/tmp/.mh370-heavy.lock} bash -c 'run_stratum "$@"' _ "$st" "$RT" "$CHAIN" "$SD" $SEEDS; fi
  n_ok=0; n=0; for k in $SEEDS; do n=$((n+1)); $PY $S/smoke/compact_impacts.py check "$OUT/$st/seed-$k" > /dev/null 2>&1 && n_ok=$((n_ok+1)); done
  if [ $n_ok -eq $n ]; then
    cat > "$OUT/$st/README.md" <<EOF
# End of flight on core run C, stratum $st ($n seeds, all compact files verified) - $(date -u +%FT%TZ)

Recipe: core's chain for $st (run.json config_paths) + snapshot-m0011 + terminal + reference-289 (N = 8 children x 4 descents) +
descent idle floor + v2-broad + family-b-ditching + residual-bank-boeing (P(left) = 0.8, PROVISIONAL). Binary $(basename $BIN)
(sha256 $(shasum -a 256 $BIN | cut -c1-16), built from 097a5d77). Hand-offs: core m0011, gunzipped and sha256-verified per seed.
Run outside the heavy lock at $THREADS threads (architecture 18:05 -0600 10 Oct, Pete delegated).

Labels (carry them into every product):
- rapid descents above 6,500 ft/min and unloading not reachable by the model (architecture 15:45 -0600);
- residual roll direction P(left) = 0.8 PROVISIONAL (exact re-weighting: latent:residual_bank_sign);
- trim at loss NOT applied; two-tank takeover NOT applied (core flew two tanks to 00:11; the module's onset prediction uses one pool);
- families: compact_impacts.family_labels(..., latent:recovery_attempted) family4_code (ruling 6 as amended 22:45 UTC);
- H1/H2 not estimable (within-parent sampling); core split-half for run C pending (core's report).
Summaries (impact-time shares, family evidence with +alive/+unpowered/+silent, family shares, same-data Bayes factors, posterior-
predictive) follow in ../summary/ after the module session's review. Format: compact float32 v1 (seed-k/run.json "compact").
EOF
    touch "$OUT/$st/READY"; echo "$st READY $(date -u +%T)"
  else echo "$st: only $n_ok of $n seeds verified; no READY"; fi
done
echo "SWEEP DONE $(date -u +%FT%TZ)"
touch "$OUT/SWEEP-DONE"
