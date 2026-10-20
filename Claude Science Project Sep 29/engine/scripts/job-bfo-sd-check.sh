set -u
# Run-J item 6 check: davey2016-inmarsat at BFO sd 7, 4.3177 and 4 Hz, 4 seeds x 7M each, under the
# deskstar heavy lock. Uses the binary of the current HEAD (built if absent).
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 5400 9 || { tl "NO-GO heavy lock busy"; touch DONE; exit 8; }
tl "heavy lock held"
J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b; R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin claude-science-sep29 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; touch DONE; exit 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION; BIN=$R0/bin-$REV
if [ ! -x $BIN ]; then cargo build --release -j 48 > $WORK/build.log 2>&1 || { tl "BUILD FAILED"; touch $WORK/DONE; exit 3; }; cp target/release/mh370 $BIN; fi
sha256sum $BIN > $WORK/BIN.sha256; tl "binary $BIN"
S=config/sensitivity/bfo-sd-check
for v in 7 432 4; do
  RAYON_NUM_THREADS=88 $BIN config/davey2016-inmarsat.toml $S/repro-bfo$v.toml $WORK/repro-bfo$v > $WORK/repro-bfo$v.log 2>&1; tl "repro-bfo$v exit $?"
  cp $WORK/repro-bfo$v/summary.json $WORK/summary-bfo$v.json
done
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt; touch $WORK/DONE; tl DONE
