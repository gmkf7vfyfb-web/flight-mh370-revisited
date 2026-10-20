# usage: bash infer_case_lowdisk.sh CASE R THREADS PPM HR  (20 Oct order D: one core process per replicate, pruned at once, for the 8 GB cap)
set -u; . $HOME/mh370/e2e/env.sh; CASE=$1; R=$2; TH=${3:-40}; PPM=$4; HR=$5
D=$E2E/cases/case-$CASE; cd "$ENG"; WT=$D/walltimes.txt; mkdir -p $D/infer-core/bto-bfo
exec 9>>$HOME/.mh370-heavy.lock; tl "case $CASE waiting for heavy lock"; flock -w 36000 9 || { tl "case $CASE NO-GO heavy lock busy"; exit 8; }; tl "case $CASE heavy lock held"
for r in $(seq 1 $R); do k=$((CASE*100+r))
  AV=$(df -BG --output=avail $HOME | tail -1 | tr -dc 0-9); [ "$AV" -ge 10 ] || { tl "case $CASE disk ${AV}G < 10G: stop"; exit 6; }
  cat > $D/infer-$k.toml <<T
name = "e2e-infer-$CASE-$k"
particles_per_mode = $PPM
seeds = [$k]
[inputs]
observations = "$D/obs-synthetic.csv"
[output]
handoff_rows = $HR
T
  rm -rf $D/core-$k; t0=$(date +%s)
  RAYON_NUM_THREADS=$TH $BIN $CHAIN_WP $D/infer-$k.toml $D/core-$k > $D/infer-core-$k.log 2>&1; rc=$?
  s=$D/core-$k/bto-bfo/seed-$k; [ -f $s/handoff-m0011/handoff.npy ] || { tl "case $CASE core seed $k failed rc $rc"; tail -3 $D/infer-core-$k.log; exit 3; }
  rm -rf $s/early.npy $s/final.npy $s/route_plans.npy $s/tanks.npy $s/tanks32.npy $s/trace.npy $s/routes.npy $s/handoff-m2241
  rm -rf $D/infer-core/bto-bfo/seed-$k; mv $s $D/infer-core/bto-bfo/; cp $D/core-$k/summary.json $D/infer-core/summary-$k.json; rm -rf $D/core-$k
  echo "core $k $(( $(date +%s)-t0 )) rc $rc" >> $WT; tl "case $CASE core seed $k rc $rc $(( $(date +%s)-t0 )) s; $(du -sh $D | cut -f1)"
done
for r in $(seq 1 $R); do k=$((CASE*100+r))
  RT=$D/infer-rt; rm -rf $RT; mkdir -p $RT/bto-bfo/seed-$k; H=$D/infer-core/bto-bfo/seed-$k/handoff-m0011
  ln -s $H/handoff.toml $RT/bto-bfo/seed-$k/handoff.toml; ln -s $H/handoff.npy $RT/bto-bfo/seed-$k/handoff.npy
  printf 'seeds = [%s]\n' $k > $D/seed-$k.toml; t1=$(date +%s); rm -rf $D/infer-eof-$k
  RAYON_NUM_THREADS=$TH $BIN terminal $RT $CHAIN_WP $D/infer-$k.toml $EOF_A $D/seed-$k.toml $EOF_EXTRA $EOF_RJ $D/infer-eof-$k > $D/infer-eof-$k.log 2>&1; rc=$?
  rm -f $H/handoff.toml; echo "eof $k $(( $(date +%s)-t1 )) rc $rc" >> $WT; tl "case $CASE eof seed $k rc $rc $(( $(date +%s)-t1 )) s; $(du -sh $D | cut -f1)"
done
cat /sys/fs/cgroup/memory.events >> $D/memory-events.txt
exec 9>&-; tl "case $CASE heavy lock released"
