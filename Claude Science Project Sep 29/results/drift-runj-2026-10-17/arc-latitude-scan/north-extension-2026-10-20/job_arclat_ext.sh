set -u
LAB="$1"; A=$HOME/mh370/drift/arclat; X=$A/ext; mkdir -p $X
cp ./$LAB.toml $X/$LAB.toml; cp ./arclat-ext-release-points.csv $X/ 2>/dev/null || true
BIN=$(ls -t $HOME/mh370/drift/target/release/deps/mh370_hypotheses-* | grep -v '\.d$' | head -1)
SHA=$(sha256sum "$BIN" | cut -c1-16)
[ "$SHA" = "cbe08758811b00aa" ] || { echo "WRONG BINARY $BIN $SHA"; exit 9; }
df -h ~ | tail -1
OOM0=$(grep oom_kill /sys/fs/cgroup/memory.events | head -1)
echo "queued $(date -u +%FT%TZ) $LAB" >> $X/chain.log
$A/run_arclat.sh $X/$LAB.toml $LAB
OOM1=$(grep oom_kill /sys/fs/cgroup/memory.events | head -1)
echo "oom before: $OOM0 after: $OOM1"
cp $HOME/mh370/drift/runs/$LAB.log ./$LAB.log
cp $HOME/mh370/drift/runs/$LAB/nodes.csv ./$LAB-nodes.csv
cp $HOME/mh370/drift/runs/$LAB/summary.toml ./$LAB-summary.toml
cp ./$LAB-nodes.csv ./$LAB-summary.toml ./$LAB.log $X/
echo "end $LAB $(tail -1 ./$LAB.log) $(date -u +%FT%TZ)" >> $X/chain.log
cat ./$LAB.log | tail -4; df -h ~ | tail -1
grep -q "EXIT=0" ./$LAB.log
ls -l ./$LAB-nodes.csv
