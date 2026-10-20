#!/bin/bash
# EoF smoke on core run C next-c-free seed 1 (m0011 hand-off): run C module recipe + extra overlays, N = 1 child x 4 descents.
# Usage: eof-smoke-c.sh ENGINE_DIR BIN OUT_NAME [extra overlays...]
cd "$1"; BIN=$2; OUTN=$3; shift 3
S=hypotheses/end-of-flight; CORE=/Users/pete/Downloads/mh370-exchange/core/next-run-d; st=next-d-free; k=1
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python; SD=$CORE/$st
CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
RT=runs/smk-rt-d-free-s1; d=$RT/bto-bfo/seed-$k
if [ ! -f $d/handoff.toml ]; then
  H="$SD/bto-bfo/seed-$k/handoff-m0011"; rm -rf $RT; mkdir -p $d; ln -s "$H/handoff.npy" $d/handoff.npy
  gzip -dc "$H/handoff.toml.gz" > $d/handoff.toml.tmp && mv $d/handoff.toml.tmp $d/handoff.toml
  want=$(grep "$st/bto-bfo/seed-$k/handoff-m0011/handoff.toml.gz" "$CORE/COMPACT.txt" | sed "s/.*sha256(uncompressed)=\([0-9a-f]*\).*/\1/"); got=$(shasum -a 256 $d/handoff.toml | cut -c1-64)
  [ "$want" = "$got" ] || { echo "SHA MISMATCH"; rm -f $d/handoff.toml; exit 1; }
fi
EXTRA="$S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml"
o=runs/$OUTN; rm -rf $o
RAYON_NUM_THREADS=${THREADS:-4} $BIN terminal $RT $CHAIN $S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $S/full/reference-289.toml $S/full/descent-idle-floor.toml $S/full/seed-$k.toml $EXTRA "$@" $S/smoke/children-1.toml $o 2>&1 | tail -1
