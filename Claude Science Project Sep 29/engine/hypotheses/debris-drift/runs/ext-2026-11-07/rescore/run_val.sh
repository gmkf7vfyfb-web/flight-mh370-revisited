#!/bin/bash
set -u
export PATH=$HOME/.cargo/bin:$PATH
C=$HOME/mh370/drift/coef; J=$PWD; mkdir -p out $C/rescore
exec 9>>$HOME/.mh370-heavy.lock; flock 9
cp $C/engine/hypotheses/debris-drift/lib.rs $C/lib-before-rescore.rs
cp $J/lib_rescore.rs $C/engine/hypotheses/debris-drift/lib.rs
cd $C/engine && CARGO_TARGET_DIR=$C/target cargo test --release -p mh370-hypotheses --no-run > $J/out/build.log 2>&1; echo "build exit $?" >> $J/out/build.log
BIN=$(ls -t $C/target/release/deps/mh370_hypotheses-* | grep -v '\.d$' | head -1)
cp $BIN $C/bin-rescore; sha256sum $C/bin-rescore | cut -c1-16 > $J/out/bin.txt
cp $J/val-gc1.toml $C/rescore/
cd $C/engine/hypotheses
RAYON_NUM_THREADS=88 timeout 1800 $C/bin-rescore debris > $J/out/unit.log 2>&1; echo "unit exit $?" >> $J/out/unit.log
T0=$(date +%s); DRIFT_RESCORE=$C/rescore/val-gc1.toml $C/bin-rescore rescore_entry --ignored --nocapture > $J/out/rescore.log 2>&1; echo "exit $? seconds $(( $(date +%s) - T0 ))" >> $J/out/rescore.log
ls -la $C/rescore >> $J/out/rescore.log
cd $C/rescore && gzip -kf val-gc1.jsonl && echo ALL-DONE > $J/out/done.txt
