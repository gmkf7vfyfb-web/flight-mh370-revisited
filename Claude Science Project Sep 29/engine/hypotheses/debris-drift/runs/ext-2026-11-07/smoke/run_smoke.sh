#!/bin/bash
# Build the shadow-finds patch and run four smoke tests. Outputs copied to ./out.
set -u
export PATH=$HOME/.cargo/bin:$PATH
C=$HOME/mh370/drift/coef
J=$PWD
mkdir -p out
exec 9>$HOME/.mh370-heavy.lock
flock 9
OLD=$C/target/release/deps/mh370_hypotheses-beedacd1154063da
[ -f $C/bin-old-889c8ef ] || cp $OLD $C/bin-old-889c8ef
sha256sum $C/bin-old-889c8ef | cut -c1-16 > out/old-bin-sha.txt
[ -f $C/lib-before-shadow.rs ] || cp $C/engine/hypotheses/debris-drift/lib.rs $C/lib-before-shadow.rs
cp $J/lib_shadow.rs $C/engine/hypotheses/debris-drift/lib.rs
cd $C/engine
CARGO_TARGET_DIR=$C/target cargo test --release -p mh370-hypotheses --no-run > $J/out/build.log 2>&1
echo "build exit $?" >> $J/out/build.log
BIN=$(ls -t $C/target/release/deps/mh370_hypotheses-* | grep -v '\.d$' | head -1)
echo "$BIN" > $J/out/bin.txt; sha256sum $BIN | cut -c1-16 >> $J/out/bin.txt
cd $C/engine/hypotheses
# unit tests (not ignored), drift module only
$BIN --list > $J/out/unit-list.log 2>&1; RAYON_NUM_THREADS=88 timeout 1800 $BIN debris > $J/out/unit-tests.log 2>&1; echo "unit exit $?" >> $J/out/unit-tests.log
for s in noshadow dateshadow override extended; do
  cp $J/smoke-$s.toml debris-drift/smoke-$s.toml
done
sed 's#/smoke/noshadow"#/smoke/oldbin"#' $J/smoke-noshadow.toml > debris-drift/smoke-oldbin.toml
rm -rf $C/smoke/noshadow $C/smoke/dateshadow $C/smoke/override $C/smoke/extended $C/smoke/oldbin
for s in oldbin noshadow dateshadow override extended; do
  B=$BIN; [ $s = oldbin ] && B=$C/bin-old-889c8ef
  T0=$(date +%s)
  env DRIFT_CONFIG=debris-drift/smoke-$s.toml RAYON_NUM_THREADS=88 $B pilot --ignored --nocapture > $J/out/run-$s.log 2>&1
  echo "exit $? seconds $(( $(date +%s) - T0 ))" >> $J/out/run-$s.log
  mkdir -p $J/out/$s; cp -r $C/smoke/$s/. $J/out/$s/ 2>/dev/null
done
cd $J/out
for s in oldbin noshadow dateshadow override extended; do md5sum $s/nodes.csv 2>/dev/null; done > md5.txt
echo ALL-DONE > done.txt
