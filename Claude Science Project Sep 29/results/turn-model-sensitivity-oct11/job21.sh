set -u
# Turn-model sensitivity (after run H, 11 Oct): fly-by + leg tracking, 11 single-route arms, 4 seeds x 200k, ad50, turn_backs on.
# Route bank 15 (model) vs 25 deg; fly-by anticipation cap 120 vs 150 deg; routes 43 MEKAR-SAMAK-ISBIX, 19 NILAM-SAMAK-ISBIX, 3, 11;
# Mach prior cap 0.84 vs 0.86 on routes 43 and 3 (route 43's initial Mach sits against 0.84 in run H).
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
CFG=$WORK/cfg; RUNS=$WORK/runs-turnsens; mkdir -p $CFG $RUNS
sed "s#WAYPOINTS_PSEUDO#$WORK/waypoints-pseudo.csv#" $WORK/routes-pseudo.toml > $CFG/routes-pseudo.toml
ARMS="b15c120-r43:W:43:-:- b15c120-r19:W:19:-:- b25-r43:W:43:25:- b25-r19:W:19:25:- b25-r3:W:3:25:- b25-r11:W:11:25:- c150-r43:W:43:-:150 c150-r19:W:19:-:150 b25c150-r43:W:43:25:150 m086-r43:W:43:-:-:086 m086-r3:W:3:-:-:086"
for a in $ARMS; do n=${a%%:*}; r=$(echo $a | cut -d: -f3); bk=$(echo $a | cut -d: -f4); cap=$(echo $a | cut -d: -f5); mx=$(echo $a | cut -d: -f6)
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
echo "fly_by = true" >> $CFG/$n.toml; echo "track_legs = true" >> $CFG/$n.toml; [ "$bk" != - ] && echo "bank_angle_deg = $bk.0" >> $CFG/$n.toml; [ "$cap" != - ] && echo "fly_by_max_turn_deg = $cap.0" >> $CFG/$n.toml; [ -n "$mx" ] && printf "\n[dynamics]\nmach_range = [0.73, 0.%s]\n" "${mx#0}" >> $CFG/$n.toml
done
touch $WORK/STARTED; tl "TURNSENS START (11 arms x 4 seeds; 8 processes x 11 threads)"
export BIN COMMON CX F RUNS CFG WORK
echo $ARMS | tr ' ' '\n' | xargs -P 8 -I{} sh -c 'a={}; n=${a%%:*}; fam=$(echo $a | cut -d: -f2); if [ $fam = W ]; then RT="$F/waypoints.toml"; else RT="$F/waypoints.toml $CFG/routes-pseudo.toml"; fi; RAYON_NUM_THREADS=11 $BIN $COMMON $CX $RT $CFG/$n.toml $RUNS/$n > $RUNS/$n.log 2>&1; rc=$?; python3 $WORK/route_shares.py $RUNS/$n $RUNS/$n/shares.json >/dev/null 2>&1 && rm -f $RUNS/$n/bto-bfo/seed-*/final.npy $RUNS/$n/bto-bfo/seed-*/early.npy $RUNS/$n/bto-bfo/seed-*/tanks*.npy && rm -rf $RUNS/$n/bto-bfo/seed-*/handoff-*; (exit $rc); echo "$(date -u +%FT%TZ) $n exit $?" >> $RUNS/pilot.log'
touch $WORK/DONE; tl "TURNSENS END ($(grep -c 'exit 0' $RUNS/pilot.log) of 11 exit 0)"
cd $RUNS && tar czf $WORK/turnsens-results.tar.gz */run.json */summary.json */shares.json */bto-bfo/seed-*/routes.npy pilot.log && tl "packed $(du -h $WORK/turnsens-results.tar.gz | cut -f1)"
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
