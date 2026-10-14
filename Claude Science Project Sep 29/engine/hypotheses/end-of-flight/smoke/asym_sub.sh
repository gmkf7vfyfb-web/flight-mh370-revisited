#!/bin/bash
# Item 1 SMOKE (never evidence): 2,000 parents of the run I 00:11 hand-off (seed 1, waypoints stratum), J0011 recipe of
# full/run_joined_v2.sh at N = 8, with and without smoke/asymmetry.toml, binary o14. Two threads, outside the heavy lock (~minutes).
set -u
S=hypotheses/end-of-flight; SD=/Users/pete/Downloads/mh370-exchange/core/run-i/next-i-waypoints; PY=/Users/pete/.claude-science/conda/envs/eof-sim/bin/python
BIN=${EOF_BIN:-/Users/pete/Downloads/mh370-exchange/end-of-flight/bin/mh370-eof-o14}
CHAIN=$($PY -c "import json,sys;print(' '.join(json.load(open(sys.argv[1]))['config_paths']))" "$SD/run.json")
REC="$S/full/reference-289.toml $S/full/descent-idle-floor.toml $S/full/seed-1.toml $S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml $S/smoke/trim-at-loss.toml $S/full/pushover.toml $S/full/boeing-sequence.toml $S/full/b-late-onset-proposal.toml $S/full/holland-estimable.toml $S/full/a1-aimed-pitchdown.toml $S/full/piloted-turns.toml $S/full/run-i.toml $S/smoke/within-parent-unnormalised.toml $S/full/c2-silent-aim.toml $S/full/dive-branch.toml"
printf '[terminal]\nchildren = 8\n' > /tmp/children-8.toml
X="$S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $REC /tmp/children-8.toml $S/smoke/deliberate-control-all4.toml $S/smoke/fuel-cue-exact.toml"
for arm in off on; do
  extra=""; [ $arm = on ] && extra="$S/smoke/asymmetry.toml"
  rm -rf runs/ASYM-sub-$arm; RAYON_NUM_THREADS=2 $BIN terminal runs/ASYM-m0011-sub2k $CHAIN $X $extra runs/ASYM-sub-$arm > runs/ASYM-sub-$arm.log 2>&1 || { echo "FAILED $arm"; tail -3 runs/ASYM-sub-$arm.log; }
done
