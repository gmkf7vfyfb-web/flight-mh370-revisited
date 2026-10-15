set -u
# Islands check (see config/sensitivity/islands-check/README.md), under the deskstar heavy lock.
. "$HOME/.cargo/env"
WORK=$PWD; tl() { echo "$(date -u +%FT%TZ) $*" >> $WORK/timeline.txt; }
exec 9>>$HOME/.mh370-heavy.lock; tl "waiting for heavy lock"; flock -w 10800 9 || { tl "NO-GO heavy lock busy"; touch DONE; exit 8; }
J=/home/pete/.claude-science-scratch/.claude-science/jobs; J7=$J/7ba3b89b-e955-45a6-90d5-a28d3164673b; R0=$HOME/mh370
git -C $R0/repo fetch -q --depth 1 origin claude-science-sep29 && git -C $R0/repo reset -q --hard FETCH_HEAD || { tl "FETCH FAILED"; touch DONE; exit 2; }
E="$R0/repo/Claude Science Project Sep 29/engine"; tar xzf $J7/engine-data.tar.gz -C "$E" --exclude='data/._*'
mkdir -p "$E/data/external/fuel-model" && cp $J7/internal-v1.json "$E/data/external/fuel-model/"
cd "$E"; REV=$(git rev-parse --short HEAD); echo $REV > $WORK/REVISION; BIN=$R0/bin-$REV
[ -x $BIN ] || { cargo build --release -j 48 > $WORK/build.log 2>&1 && cp target/release/mh370 $BIN || { tl "BUILD FAILED"; touch $WORK/DONE; exit 3; }; }
sha256sum $BIN > $WORK/BIN.sha256; tl "binary $BIN"
S=config/sensitivity; X=$S/fuel-fixes; F=$S/early-families
CHAIN="config/davey2016-inmarsat.toml $S/no-exhaustion-prior.toml $X/s1-factor.toml $X/s2-temperature.toml $X/s3-internal.toml $X/s4-ceiling.toml $X/s5-hard-reject.toml $X/s6-tanks.toml $S/reference-snapshots.toml $F/radar-full.toml $X/s7-single-engine.toml $X/s8-hold-taper.toml $X/inop-flow-fix.toml $F/speed-envelope-throughout.toml $F/route-sampler.toml"
for n in 4 8; do
  RAYON_NUM_THREADS=88 $BIN $CHAIN $S/islands-check/islands-$n.toml $WORK/islands-$n > $WORK/islands-$n.log 2>&1; tl "islands-$n exit $?"
  cp $WORK/islands-$n/summary.json $WORK/summary-islands-$n.json
  for f in $WORK/islands-$n/bto-bfo/seed-*/final.npy; do k=$(basename $(dirname $f)); cp $f $WORK/final-islands-$n-$k.npy; done
  rm -rf $WORK/islands-$n/bto-bfo/seed-*/routes.npy $WORK/islands-$n/bto-bfo/seed-*/trace.npy $WORK/islands-$n/bto-bfo/seed-*/final.npy
done
cat /sys/fs/cgroup/memory.events >> $WORK/timeline.txt; touch $WORK/DONE; tl DONE
