#!/bin/bash
# Build the restrict_to_classes patch, check that default behaviour is unchanged, and time one wide-windage node per ocean model.
set -u
export PATH=$HOME/.cargo/bin:$PATH
C=$HOME/mh370/drift/coef; ENG=$C/engine; D=$ENG/hypotheses/debris-drift; J=$PWD
mkdir -p out
exec 9>$HOME/.mh370-heavy.lock; flock 9
echo "start $(date -u +%FT%TZ)" > out/log.txt
[ -f $C/lib-before-restrict.rs ] || cp $D/lib.rs $C/lib-before-restrict.rs
sha256sum $C/lib-before-restrict.rs | cut -c1-16 > out/lib-sha-before.txt
if ! grep -q restrict_to_classes $D/lib.rs; then python3 $J/patch_lib.py $D/lib.rs > out/patch.log 2>&1 || { echo patch-failed >> out/log.txt; exit 1; }; fi
diff -u $C/lib-before-restrict.rs $D/lib.rs > out/lib-restrict-to-classes.diff
sha256sum $D/lib.rs | cut -c1-16 > out/lib-sha-after.txt
cd $ENG
CARGO_TARGET_DIR=$C/target cargo test --release -p mh370-hypotheses --no-run > $J/out/build.log 2>&1
echo "build exit $?" >> $J/out/build.log
BIN=$(ls -t $C/target/release/deps/mh370_hypotheses-* | grep -v '\.d$' | head -1)
cp $BIN $C/bin-wide; sha256sum $C/bin-wide $C/bin-arr | cut -c1-16 > $J/out/bin-sha.txt
cd $ENG/hypotheses
RAYON_NUM_THREADS=88 timeout 1800 $C/bin-wide debris > $J/out/unit-tests.log 2>&1; echo "unit exit $?" >> $J/out/unit-tests.log
echo "units done $(date -u +%FT%TZ)" >> $J/out/log.txt
run() {  # name bin config-file
  local name=$1 bin=$2 cfg=$3
  cp $J/$cfg debris-drift/$name.toml
  rm -rf $C/smoke/$name
  local s=$(date +%s)
  ( while sleep 5; do ps -o rss= -C $(basename $bin) 2>/dev/null | sort -n | tail -1; done ) > $J/out/$name.rss 2>/dev/null & local MON=$!
  env DRIFT_CONFIG=debris-drift/$name.toml RAYON_NUM_THREADS=88 $bin pilot --ignored --nocapture > $J/out/$name.log 2>&1; local rc=$?
  kill $MON 2>/dev/null
  echo "$name EXIT=$rc wall_s=$(( $(date +%s) - s )) peak_rss_kb=$(sort -n $J/out/$name.rss | tail -1)" >> $J/out/log.txt
}
# identity: same default config, old binary and patched binary
sed 's#wide-ident-all#wide-ident-all-old#' $J/ident-all.toml > $J/ident-all-old.toml
sed 's#wide-ident-all#wide-ident-all-new#' $J/ident-all.toml > $J/ident-all-new.toml
run wide-ident-all-old $C/bin-arr ident-all-old.toml
run wide-ident-all-new $C/bin-wide ident-all-new.toml
run wide-ident-restrict $C/bin-wide ident-restrict.toml
python3 $J/compare_runs.py $C/smoke/wide-ident-all-old $C/smoke/wide-ident-all-new bytes > $J/out/identity-bytes.json 2>&1
python3 $J/compare_runs.py $C/smoke/wide-ident-all-new $C/smoke/wide-ident-restrict class1 > $J/out/identity-class1.json 2>&1
# timing: one wide-windage node pair per ocean model (2 nodes x 2 environments, 6250 particles)
run wide-time-globcurrent $C/bin-wide time-globcurrent.toml
run wide-time-glorys12 $C/bin-wide time-glorys12.toml
for n in wide-time-globcurrent wide-time-glorys12; do mkdir -p $J/out/$n; cp $C/smoke/$n/nodes.csv $C/smoke/$n/summary.toml $C/smoke/$n/coefficients-meta.json $C/smoke/$n/responses.json $J/out/$n/ 2>/dev/null; ls -la $C/smoke/$n > $J/out/$n/ls.txt; done
for n in wide-ident-all-new wide-ident-restrict; do mkdir -p $J/out/$n; cp $C/smoke/$n/nodes.csv $C/smoke/$n/summary.toml $J/out/$n/ 2>/dev/null; done
echo "ALL-DONE $(date -u +%FT%TZ)" >> $J/out/log.txt
