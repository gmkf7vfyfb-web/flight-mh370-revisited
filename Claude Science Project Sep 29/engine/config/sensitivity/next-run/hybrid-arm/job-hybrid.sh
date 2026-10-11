set -u
# Audit arms (architecture audit 11 Oct ~11:20 UTC): pseudo-fix scan along NILAM-ANOKO (12 turn points -15..+40 NM)
# x 3 end fixes (ISBIX, +-0.5 deg lon) = 36 routes; matched-volume = mean evidence over the grid. turn_backs on: 48 single-route runs,
# run C stack (routes family), 200k particles per route, seeds 1-2, ad50 tempering, 8 processes x 11 threads.
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
CFG=$WORK/cfg; RUNS=$WORK/runs-hybrid; mkdir -p $CFG $RUNS
sed "s#WAYPOINTS_HYBRID#$WORK/waypoints-hybrid.csv#" $WORK/routes-hybrid.toml > $CFG/routes-hybrid.toml
for r in $(seq 0 25); do cat > $CFG/route-$r.toml <<EOT
name = "route-$r"
particles_per_mode = [30000, 15000, 70000, 15000, 70000]
seeds = [1, 2, 3, 4]

[output]
handoff_rows = 1000

[sampler]
temper_epochs = ["m1839", "m1941", "m2041", "m2141", "m2241", "m0011"]
temper_stages = 16

[dynamics.early.routes]
only = [$r]
turn_backs = true
EOT
done
touch $WORK/STARTED; tl "PILOT START (26 hybrid routes x 4 seeds, run C sampler; 8 processes x 11 threads)"
export BIN COMMON CX F RUNS CFG WORK
seq 0 25 | xargs -P 8 -I{} sh -c 'RAYON_NUM_THREADS=11 $BIN $COMMON $CX $F/waypoints.toml $CFG/routes-hybrid.toml $CFG/route-{}.toml $RUNS/route-{} > $RUNS/route-{}.log 2>&1; rc=$?; python3 $WORK/route_shares.py $RUNS/route-{} $RUNS/route-{}/shares.json >/dev/null 2>&1 && rm -f $RUNS/route-{}/bto-bfo/seed-*/final.npy $RUNS/route-{}/bto-bfo/seed-*/early.npy $RUNS/route-{}/bto-bfo/seed-*/tanks*.npy && rm -rf $RUNS/route-{}/bto-bfo/seed-*/handoff-*; (exit $rc); echo "$(date -u +%FT%TZ) route-{} exit $?" >> $RUNS/pilot.log'
touch $WORK/DONE; tl "PILOT END ($(grep -c 'exit 0' $RUNS/pilot.log) of 36 exit 0)"
cd $RUNS && tar czf $WORK/hybrid-arm-results.tar.gz route-*/run.json route-*/summary.json route-*/shares.json route-*/bto-bfo/seed-*/routes.npy pilot.log && tl "packed $(du -h $WORK/hybrid-arm-results.tar.gz | cut -f1)"
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
