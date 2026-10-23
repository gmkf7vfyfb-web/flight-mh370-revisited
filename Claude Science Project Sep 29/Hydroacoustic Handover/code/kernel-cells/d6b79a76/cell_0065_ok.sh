WS=$(pwd); cat > kh/targeted_seed.sh <<'E'
#!/bin/bash
# One targeted seed: build subset hand-off -> engine (fresh seed 1000+k, N children) -> compact -> tau sidecar -> combine/reduce -> delete bulk.
# Usage: targeted_seed.sh K TDIR CHILDREN_TOML [MAXP]
set -eu
K=$1; T=$2; CH=$3; MAXP=${4:-}
WS=/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/d6b79a76-addc-42aa-84ad-897b9904c0cb
E_DIR="/Users/pete/.claude-science/orgs/9db41e8b-db54-4736-82b9-d77e2a9ad222/workspaces/370552c2-5cc9-44d0-86c9-507ea022948e/repo/Claude Science Project Sep 29/engine"
PY=python; S=hypotheses/end-of-flight; NS=$((1000+K))
mkdir -p $T/RT $T/rows
$PY $WS/kh/targeted_build.py $K $T/RT ${MAXP:+--max-parents $MAXP}
printf 'seeds = [%d]\n' $NS > $T/seed-$NS.toml
CHAIN=$($PY -c "import json;print(' '.join(json.load(open('/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/run.json'))['config_paths']))")
EXTRA="$S/smoke/v2-broad.toml $S/full/family-b-ditching.toml $S/full/residual-bank-boeing.toml $S/smoke/trim-at-loss.toml $S/full/pushover.toml $S/full/boeing-sequence.toml $S/full/b-late-onset-proposal.toml $S/full/holland-estimable.toml $S/full/a1-aimed-pitchdown.toml $S/full/piloted-turns.toml $S/full/run-i.toml $S/smoke/within-parent-unnormalised.toml $S/full/c2-silent-aim.toml $S/full/dive-branch.toml $CH $S/full/round3-laws.toml $S/full/bank-cap-uniform.toml"
O=$T/full-seed-$K; rm -rf $O
( cd "$E_DIR" && RAYON_NUM_THREADS=${TG_THREADS:-12} /tmp/mh370-eof-rj1 terminal $T/RT $CHAIN $S/smoke/snapshot-m0011.toml $S/smoke/terminal.toml $S/full/reference-289.toml $S/full/descent-idle-floor.toml $T/seed-$NS.toml $EXTRA $O 2>&1 | tail -1 )
C=$T/compact-seed-$K; rm -rf $C
( cd $WS/scorer && $PY compact_impacts.py write $O $O/bto-bfo/seed-$NS $C > $T/convert-$K.log 2>&1 && $PY compact_impacts.py check $C && $PY tau_sidecar.py $C > /dev/null )
rm -f $O/bto-bfo/seed-$NS/impacts.npy
( cd $WS/kh && $PY flight_leg_worker.py targeted $K $T 2>&1 | grep -v -i "pyproj\|ca_bundle" )
rm -f $C/impacts32.npy
echo "seed $K done $(date -u +%T) $(df -g /Users/pete | tail -1 | awk '{print $4}') GiB free"
E
chmod +x kh/targeted_seed.sh; rm -rf kh/tgt/smoke-out kh/tgt/smokeRT
time bash kh/targeted_seed.sh 1 $WS/kh/tgt/smoke $WS/kh/tgt/children-16.toml 40 2>&1 | tail -8; ls kh/tgt/smoke kh/tgt/smoke/compact-seed-1