#!/bin/bash
# V1a-against-V1b check (contract §8 "validate the modular result against a smaller joint-filter calculation"; results/eof-gates-oct13 §7):
# the 23:15 + 00:11 log-evidence increment from the 22:41 hand-off, estimated by the terminal stage (arm V1b: flame-out onset only, so
# every child cruises on the core dynamics to its flame-out) against the core filter's own increment between the same two hand-offs.
# N = 1 child x 4 descents, all 100,000 parents, seeds $SEEDS. SMOKE SCALE.
set -u
CORE=/Users/pete/Downloads/mh370-exchange/core/run-i; st=next-i-waypoints; SD=$CORE/$st; S=hypotheses/end-of-flight
BIN=${EOF_BIN:-/Users/pete/Downloads/mh370-exchange/end-of-flight/bin/mh370-eof-o13d}; SEEDS=${SEEDS:-"1 2 3 4 5 6 7 8"}
PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
cat > /tmp/children-1.toml <<'T'
[terminal]
children = 1
T
for k in $SEEDS; do
  H="$SD/bto-bfo/seed-$k/handoff-m2241"; RT=runs/CHK-m2241-s$k; d=$RT/bto-bfo/seed-$k; rm -rf $RT; mkdir -p $d
  ln -s "$H/handoff.npy" $d/handoff.npy; gzip -dc "$H/handoff.toml.gz" > $d/handoff.toml
  o=runs/CHK-V1b-s$k; rm -rf $o
  lockf -k /tmp/.mh370-heavy.lock env RAYON_NUM_THREADS=12 $BIN terminal $RT $CHAIN $S/smoke/snapshot-m2241.toml $S/smoke/terminal.toml $S/smoke/options-m2241.toml $S/full/seed-$k.toml $S/smoke/arm-v1.toml $S/smoke/fuel-cue-exact.toml /tmp/children-1.toml $o > /dev/null 2>&1
  echo "seed $k done $(date -u +%T)"
done
echo CHECK DONE
