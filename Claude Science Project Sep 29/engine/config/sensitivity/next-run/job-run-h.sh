set -u
# Run H: fly-by confirmation of run G six routes (3M x seeds 1-8, run C sampler). One process, 88 threads.
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
S=config/sensitivity; R=$S/next-run; DRV=$R/driver.sh; X=$S/fuel-fixes
CX="$X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml"
# Tiny preflight of the exact stack.
sed -e 's/^particles_per_mode.*/particles_per_mode = [4000, 2000, 10000, 2000, 10000]/' -e 's/^seeds.*/seeds = [1]/' -e 's/handoff_rows = 100000/handoff_rows = 1000/' $R/server-h-routes.toml > $R/tiny-h-routes.toml
PF=$WORK/preflight; mkdir -p $PF; EXTRA="$CX" RAYON_NUM_THREADS=40 sh $DRV $BIN tiny-h $PF routes; rm -f $R/tiny-h-routes.toml
G=$(python3 $J7/gocheck2.py $PF next-h-routes); tl "preflight H $G"
[ "$G" = "GO" ] || { tl "NO-GO preflight: run G not started"; exit 5; }
rm -rf $PF/next-h-routes
python3 -c "import json;c=json.load(open('$PF/../preflight.json')) if False else None" 2>/dev/null
AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); tl "disk free ${AV}G"; [ "$AV" -ge 6 ] || { tl "NO-GO disk"; exit 6; }
RUNS=$WORK/runs-h; mkdir -p $RUNS; touch $WORK/STARTED; tl "RUN H START (one process x 88 threads)"
( while [ ! -f $WORK/DONE ]; do echo "$(date -u +%FT%TZ) df $(df -h --output=avail $HOME | tail -1) mem $(( $(cat /sys/fs/cgroup/memory.current) / 1073741824 ))G" >> $WORK/monitor.txt; sleep 300; done ) &
EXTRA="$CX" RAYON_NUM_THREADS=88 sh $DRV $BIN server-h $RUNS routes
touch $WORK/DONE; tl "RUN H END"; cat $RUNS/next-run-driver.log >> $WORK/timeline.txt || true
cd $RUNS && tar czf $WORK/run-h-small.tar.gz next-h-routes/run.json next-h-routes/summary.json next-h-routes/bto-bfo/seed-*/diagnostics.json next-h-routes.log && tl "packed small files"
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
