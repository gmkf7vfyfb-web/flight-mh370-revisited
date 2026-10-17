set -u
J=~/mh370/drift/job3; cd $J
ENG="$HOME/mh370/drift/repo/Claude Science Project Sep 29/engine"; T="$ENG/hypotheses/debris-drift/tests.rs"
grep -q 'fn snapshots_onshore' "$T" || cat $J/snapshots_onshore.rs >> "$T"
python3 $J/mkcfg.py $J/nodes94.json "$ENG/hypotheses/debris-drift" >> $J/chain.log 2>&1 || { echo CFG-FAILED >> $J/chain.log; exit 3; }
exec 9>>$HOME/.mh370-heavy.lock; flock -w 7200 9 || { echo NO-GO >> $J/chain.log; exit 8; }
. ~/.cargo/env; cd "$ENG"
CARGO_TARGET_DIR=$HOME/mh370/drift/target cargo test --release -p mh370-hypotheses --no-run > $J/build.log 2>&1 || { echo BUILD-FAILED >> $J/chain.log; exit 2; }
BIN=$(ls -t $HOME/mh370/drift/target/release/deps/mh370_hypotheses-* | grep -v '\.d$' | head -1); echo "bin $BIN" >> $J/chain.log
cd "$ENG/hypotheses"
for M in glorys12 globcurrent; do for R in off r069 r200; do
  sed -e 's/^particles_per_class = .*/particles_per_class = 834/' ~/mh370/drift/aus160/aus160-$M.toml > $J/rf-$M-$R.toml
  case $R in r069) sed -i 's/^particles_per_class = 834/particles_per_class = 834\nrefloat_per_day = 0.014493/' $J/rf-$M-$R.toml;; r200) sed -i 's/^particles_per_class = 834/particles_per_class = 834\nrefloat_per_day = 0.005/' $J/rf-$M-$R.toml;; esac
  echo "start rf $M $R $(date -u +%FT%TZ) $(grep -c refloat_per_day $J/rf-$M-$R.toml)" >> $J/chain.log
  DRIFT_CONFIG=$J/rf-$M-$R.toml SNAP_SPEC=$HOME/mh370/drift/snap2/snap-spec-core.toml SNAP_OUT=$J/rf-$M-$R.bin RAYON_NUM_THREADS=88 $BIN snapshots_onshore --ignored --nocapture > $J/rf-$M-$R.log 2>&1
  echo "EXIT rf $M $R $? $(date -u +%FT%TZ)" >> $J/chain.log
  (python3 $J/aggregate3.py $J/rf-$M-$R.bin 4 $J/rf-$M-$R.json >> $J/chain.log 2>&1 && gzip -f $J/rf-$M-$R.json) &
done; done
wait
exec 9>&-
for M in glorys12 globcurrent; do
  echo "start refine $M $(date -u +%FT%TZ)" >> $J/chain.log
  ~/mh370/drift/aus160/run.sh "$J/refine-core94-$M.toml" refine-core94-$M
  echo "EXIT refine $M $(tail -1 ~/mh370/drift/runs/refine-core94-$M.log) $(date -u +%FT%TZ)" >> $J/chain.log
done
echo ALL-DONE >> $J/chain.log
