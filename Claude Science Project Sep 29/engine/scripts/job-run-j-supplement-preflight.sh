set -u
# Light preflight of the run-J northern supplement (NOT under the heavy lock: nice 19, 8 threads, tiny particle counts).
. "$HOME/.cargo/env"; WORK=$PWD; R0=$HOME/mh370; J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b
tl() { echo "$(date -u +%FT%TZ) $*" | tee -a $WORK/timeline.txt; }
git -C $R0/repo fetch -q origin claude-science-sep29 && git -C $R0/repo worktree add -f --detach $WORK/wt $REV > /dev/null 2>&1 || { tl "worktree failed"; exit 2; }
export CARGO_TARGET_DIR=$R0/target-supp
E="$WORK/wt/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"; cd "$E"
tl "build"; nice -n 19 cargo build --release -j 8 > $WORK/build.log 2>&1 || { tl "build failed"; tail -30 $WORK/build.log; exit 3; }
nice -n 19 cargo test --release -j 8 -p mh370-flight -p mh370 2>&1 | grep -E "test result|FAILED|panicked" > $WORK/tests.txt; cat $WORK/tests.txt
BIN=$CARGO_TARGET_DIR/release/mh370; sha256sum $BIN
S=config/sensitivity; X=$S/fuel-fixes; F=$S/early-families; RJ=$S/run-j; SU=$S/run-j-supplement
COMMON="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml"
CX="$X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml"
SAMPLER="$COMMON $CX $F/speed-envelope-throughout.toml $S/handoff-lookahead-d.toml $RJ/obs-bfo432.toml $RJ/kx.toml $F/route-sampler.toml $RJ/size-sampler.toml"
printf 'particles_per_mode = [4000, 2000, 10000, 2000, 10000]\nseeds = [1]\n[output]\nhandoff_rows = 1000\n' > $WORK/tiny.toml
printf '[output.handoff_supplement]\nrows = 2000\n' > $WORK/tiny-supp.toml
printf 'particles_per_mode = [4800, 5200, 4400, 8800, 4800]\nseeds = [1001]\n[output]\nhandoff_rows = 1000\n' > $WORK/tiny-north.toml
O=$WORK/out; mkdir -p $O
tl "tiny flag off"; RAYON_NUM_THREADS=8 nice -n 19 $BIN $SAMPLER $WORK/tiny.toml $O/off > $O/off.log 2>&1; echo "exit $?"
tl "tiny flag on"; RAYON_NUM_THREADS=8 nice -n 19 $BIN $SAMPLER $SU/supplement.toml $WORK/tiny.toml $WORK/tiny-supp.toml $O/on > $O/on.log 2>&1; echo "exit $?"
tl "tiny north"; RAYON_NUM_THREADS=8 nice -n 19 $BIN $SAMPLER $SU/size-north.toml $SU/supplement.toml $WORK/tiny-north.toml $WORK/tiny-supp.toml $O/north > $O/north.log 2>&1; echo "exit $?"
tail -3 $O/on.log
cd $O/off/bto-bfo/seed-1 && for f in $(find . -type f ! -name diagnostics.json | sort); do cmp -s $f $O/on/bto-bfo/seed-1/$f && echo "SAME $f" || echo "DIFF $f"; done
ls -la $O/on/bto-bfo/seed-1/handoff-m0011-supplement $O/north/bto-bfo/seed-1001/handoff-m0011-supplement
cd $WORK; tar czf tiny.tgz -C $O on/bto-bfo/seed-1/handoff-m0011 on/bto-bfo/seed-1/handoff-m0011-supplement north/bto-bfo/seed-1001/handoff-m0011 north/bto-bfo/seed-1001/handoff-m0011-supplement north/bto-bfo/seed-1001/diagnostics.json on/bto-bfo/seed-1/diagnostics.json
git -C $R0/repo worktree remove --force $WORK/wt; git -C $R0/repo worktree prune; rm -rf $O
tl "preflight done"
