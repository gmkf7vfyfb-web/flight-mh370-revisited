set -u
# Fly-by test part 2 (architecture 18:05Z): track_legs on, 9 single-route arms, 4 seeds x 200k, ad50, turn_backs on.
# fly_by + track_legs: routes 11, 10, 3 and scan points -5, +5, +10, +15 NM; fly_by only: +15 NM; fly-over + track_legs: route 11.
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
J7=/home/pete/.claude-science-scratch/.claude-science/jobs/7ba3b89b-e955-45a6-90d5-a28d3164673b
R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin claude-science-sep29 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; exit 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"
tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION; tl "build $REV"
cargo build --release -j 48 > $WORK/build.log 2>&1 || { tl "BUILD FAILED"; exit 3; }
cargo test --release -j 48 -p mh370-flight -p mh370 2>&1 | grep -E "test result|FAILED|panicked" > $WORK/tests.txt || true
if grep -q FAILED $WORK/tests.txt || ! grep -q "test result: ok" $WORK/tests.txt; then tl "UNIT TESTS FAILED"; exit 3; fi
BIN=$R0/bin-$REV; rm -f $BIN; cp target/release/mh370 $BIN
S=config/sensitivity; F=$S/early-families; X=$S/fuel-fixes
COMMON="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml"
CX="$X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml"
CFG=$WORK/cfg; RUNS=$WORK/runs-flyby2; mkdir -p $CFG $RUNS
sed "s#WAYPOINTS_PSEUDO#$WORK/waypoints-pseudo.csv#" $WORK/routes-pseudo.toml > $CFG/routes-pseudo.toml
ARMS="fbtl-r11:W:11:1:1 fbtl-r10:W:10:1:1 fbtl-r3:W:3:1:1 fbtl-pm05:P:6:1:1 fbtl-pp05:P:12:1:1 fbtl-pp10:P:15:1:1 fbtl-pp15:P:18:1:1 fb-pp15:P:18:1:0 fotl-r11:W:11:0:1"
for a in $ARMS; do n=${a%%:*}; r=$(echo $a | cut -d: -f3); fb=$(echo $a | cut -d: -f4); tl=$(echo $a | cut -d: -f5)
cat > $CFG/$n.toml <<EOT
name = "$n"
particles_per_mode = [30000, 15000, 70000, 15000, 70000]
seeds = [1, 2, 3, 4]

[output]
handoff_rows = 1000

[sampler]
temper_epochs = ["m1839", "m1941", "m2041", "m2141", "m2241", "m0011"]
temper_stages = 16
temper_target_ess = 0.5

[dynamics.early.routes]
only = [$r]
turn_backs = true
EOT
[ "$fb" = 1 ] && echo "fly_by = true" >> $CFG/$n.toml; [ "$tl" = 1 ] && echo "track_legs = true" >> $CFG/$n.toml
done
touch $WORK/STARTED; tl "FLYBY2 START (9 arms x 4 seeds; 8 processes x 11 threads)"
export BIN COMMON CX F RUNS CFG WORK
echo $ARMS | tr ' ' '\n' | xargs -P 8 -I{} sh -c 'a={}; n=${a%%:*}; fam=$(echo $a | cut -d: -f2); if [ $fam = W ]; then RT="$F/waypoints.toml"; else RT="$F/waypoints.toml $CFG/routes-pseudo.toml"; fi; RAYON_NUM_THREADS=11 $BIN $COMMON $CX $RT $CFG/$n.toml $RUNS/$n > $RUNS/$n.log 2>&1; rc=$?; python3 $WORK/route_shares.py $RUNS/$n $RUNS/$n/shares.json >/dev/null 2>&1 && rm -f $RUNS/$n/bto-bfo/seed-*/final.npy $RUNS/$n/bto-bfo/seed-*/early.npy $RUNS/$n/bto-bfo/seed-*/tanks*.npy && rm -rf $RUNS/$n/bto-bfo/seed-*/handoff-*; (exit $rc); echo "$(date -u +%FT%TZ) $n exit $?" >> $RUNS/pilot.log'
touch $WORK/DONE; tl "FLYBY2 END ($(grep -c 'exit 0' $RUNS/pilot.log) of 9 exit 0)"
cd $RUNS && tar czf $WORK/flyby2-results.tar.gz */run.json */summary.json */shares.json */bto-bfo/seed-*/routes.npy pilot.log && tl "packed $(du -h $WORK/flyby2-results.tar.gz | cut -f1)"
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
