set -u
# Audit F3 short test: davey2016-inmarsat at 1 s steps, 4 seeds x 7M, under the deskstar heavy lock.
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 7200 9 || { tl "NO-GO heavy lock busy"; touch DONE; exit 8; }
J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b; R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin claude-science-sep29 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; touch DONE; exit 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION; BIN=$R0/bin-$REV
[ -x $BIN ] || { cargo build --release -j 48 > $WORK/build.log 2>&1 && cp target/release/mh370 $BIN || { tl "BUILD FAILED"; touch $WORK/DONE; exit 3; }; }
sha256sum $BIN > $WORK/BIN.sha256; tl "binary $BIN"
RAYON_NUM_THREADS=88 $BIN config/davey2016-inmarsat.toml config/sensitivity/step-check/repro-step1.toml $WORK/repro-step1 > $WORK/repro-step1.log 2>&1; tl "repro-step1 exit $?"
cp $WORK/repro-step1/summary.json $WORK/summary-step1.json; rm -rf $WORK/repro-step1/bto-bfo/seed-*/final.npy $WORK/repro-step1/bto-bfo/seed-*/routes.npy
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt; touch $WORK/DONE; tl DONE
