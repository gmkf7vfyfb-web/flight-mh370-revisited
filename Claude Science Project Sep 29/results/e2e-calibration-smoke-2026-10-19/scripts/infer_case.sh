# usage: bash infer_case.sh CASE R THREADS PARTICLES_SPEC HANDOFF_ROWS -> inference on the synthetic data, under the heavy lock
set -u; . $HOME/mh370/e2e/env.sh; CASE=$1; R=$2; TH=${3:-40}; PPM=${4:-"[100_000, 50_000, 250_000, 50_000, 250_000]"}; HR=${5:-10000}
D=$E2E/cases/case-$CASE; cd "$ENG"; WT=$D/walltimes.txt
SEEDS=$(seq -s, $((CASE*100+1)) $((CASE*100+R)))
cat > $D/infer.toml <<T
name = "e2e-infer-$CASE"
particles_per_mode = $PPM
seeds = [$SEEDS]
[inputs]
observations = "$D/obs-synthetic.csv"
[output]
handoff_rows = $HR
T
exec 9>>$HOME/.mh370-heavy.lock; tl "case $CASE waiting for heavy lock"; flock -w 36000 9 || { tl "case $CASE NO-GO heavy lock busy"; exit 8; }; tl "case $CASE heavy lock held"
AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); [ "$AV" -ge 8 ] || { tl "case $CASE disk ${AV}G < 8G: stop"; exit 6; }
rm -rf $D/infer-core; t0=$(date +%s)
RAYON_NUM_THREADS=$TH $BIN $CHAIN_WP $D/infer.toml $D/infer-core > $D/infer-core.log 2>&1; rc=$?
echo "core $(( $(date +%s)-t0 )) rc $rc" >> $WT; tl "case $CASE core rc $rc $(( $(date +%s)-t0 )) s"
[ -f $D/infer-core/run.json ] || { tl "case $CASE core failed"; tail -5 $D/infer-core.log; exit 3; }
for k in $(echo $SEEDS | tr , ' '); do
  RT=$D/infer-rt; rm -rf $RT; mkdir -p $RT/bto-bfo/seed-$k; H=$D/infer-core/bto-bfo/seed-$k/handoff-m0011
  ln -s $H/handoff.toml $RT/bto-bfo/seed-$k/handoff.toml; ln -s $H/handoff.npy $RT/bto-bfo/seed-$k/handoff.npy
  printf 'seeds = [%s]\n' $k > $D/seed-$k.toml; t1=$(date +%s)
  RAYON_NUM_THREADS=$TH $BIN terminal $RT $CHAIN_WP $D/infer.toml $EOF_A $D/seed-$k.toml $EOF_EXTRA $EOF_RJ $D/infer-eof-$k > $D/infer-eof-$k.log 2>&1; rc=$?
  echo "eof $k $(( $(date +%s)-t1 )) rc $rc" >> $WT; tl "case $CASE eof seed $k rc $rc $(( $(date +%s)-t1 )) s"
done
cat /sys/fs/cgroup/memory.events >> $D/memory-events.txt
exec 9>&-; tl "case $CASE heavy lock released"; du -sh $D >> $WT
