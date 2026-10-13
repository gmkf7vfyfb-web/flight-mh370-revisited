set -u
# Run I, ONE stratum per job (disk: each stratum is staged back to the Mac and deleted before the next).
# usage (job command): STRATUM=<free|sampler|dc|repro> sh job-run-i.sh      Needs Pete's GO (results/run-i-proposal.md).
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
J7=/home/pete/.claude-science-scratch/.claude-science/jobs/7ba3b89b-e955-45a6-90d5-a28d3164673b
R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin claude-science-sep29 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; exit 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"
tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION; tl "build $REV stratum $STRATUM"
cargo build --release -j 48 > $WORK/build.log 2>&1 || { tl "BUILD FAILED"; exit 3; }
cargo test --release -j 48 -p mh370-flight -p mh370 2>&1 | grep -E "test result|FAILED|panicked" > $WORK/tests.txt || true
if grep -q FAILED $WORK/tests.txt || ! grep -q "test result: ok" $WORK/tests.txt; then tl "UNIT TESTS FAILED"; exit 3; fi
BIN=$R0/bin-$REV; rm -f $BIN; cp target/release/mh370 $BIN
S=config/sensitivity; R=$S/next-run; DRV=$R/driver.sh; X=$S/fuel-fixes
# Pete 12 Oct ~02:00Z: the reproduction stratum stays exactly Davey (Mach 0.73-0.84 throughout, no cruise CAS clip).
SPEED="$S/early-families/speed-envelope-throughout.toml"; [ "$STRATUM" = repro ] && SPEED=""
CX="$X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml $SPEED $S/handoff-lookahead-d.toml"
# Tiny preflight of the exact stack.
sed -e 's/^particles_per_mode.*/particles_per_mode = [4000, 2000, 10000, 2000, 10000]/' -e 's/^seeds.*/seeds = [1]/' -e 's/handoff_rows = 100000/handoff_rows = 1000/' $R/server-i-$STRATUM.toml > $R/tiny-i-$STRATUM.toml
PF=$WORK/preflight; mkdir -p $PF; EXTRA="$CX" RAYON_NUM_THREADS=40 sh $DRV $BIN tiny-i $PF $STRATUM; rm -f $R/tiny-i-$STRATUM.toml
NM=$(grep '^name' $R/server-i-$STRATUM.toml | cut -d'"' -f2)
[ -f $PF/$NM/run.json ] && [ -f $PF/$NM/bto-bfo/seed-1/trace.npy ] || { tl "NO-GO preflight ($NM: run.json or trace.npy missing)"; exit 5; }
tl "preflight GO"; rm -rf $PF/$NM
AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); tl "disk free ${AV}G"; [ "$AV" -ge 12 ] || { tl "NO-GO disk (need 12G)"; exit 6; }
RUNS=$WORK/runs-i; mkdir -p $RUNS; touch $WORK/STARTED; tl "RUN I $STRATUM START (one process x 88 threads)"
( while [ ! -f $WORK/DONE ]; do echo "$(date -u +%FT%TZ) df $(df -h --output=avail $HOME | tail -1) mem $(( $(cat /sys/fs/cgroup/memory.current) / 1073741824 ))G" >> $WORK/monitor.txt; sleep 300; done ) &
EXTRA="$CX" RAYON_NUM_THREADS=88 sh $DRV $BIN server-i $RUNS $STRATUM
touch $WORK/DONE; tl "RUN I $STRATUM END"; cat $RUNS/next-run-driver.log >> $WORK/timeline.txt || true
cd $RUNS && tar czf $WORK/run-i-$STRATUM-small.tar.gz $NM/run.json $NM/summary.json $NM/bto-bfo/seed-*/diagnostics.json $NM.log && tl "packed small files"
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt || true
