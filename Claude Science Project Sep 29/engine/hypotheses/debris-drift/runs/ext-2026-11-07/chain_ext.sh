set -u
# Extended-window drift run (window to 30 Jan 2017, six shadow finds). Stage 1: 84 points x 16 environments (seeds 201-216).
# Stage 2: 42 southern points x 16 more environments (217-232). Same pattern as the run of 7 Nov (jobs 91ee26ce, 272016f7).
C=$HOME/mh370/drift/coef; ENG=$C/engine; BIN=$C/bin-shadow-fresh
OUT=$PWD/out; mkdir -p $OUT $C/runs $C/ext; LOG=$C/runs/ext-chain.log
cp $PWD/ext-*.toml $PWD/ext2-*.toml $PWD/legs.txt $PWD/legs2.txt $C/ext/
echo "gate wait $(date -u +%FT%TZ)" >> $LOG
# Do not compete with other sessions' heavy runs that do not take the shared lock (e.g. job ed751059 smoke-wide, 7 Nov).
while kill -0 1325886 2>/dev/null || pgrep -f 'mh370_hypotheses.*pilot' >/dev/null; do sleep 60; done
echo "gate open $(date -u +%FT%TZ)" >> $LOG
echo "start $(date -u +%FT%TZ) bin=$BIN binsha=$(sha256sum $BIN | cut -c1-16)" >> $LOG
for LEGS in legs.txt legs2.txt; do
while read L; do
  [ -z "$L" ] && continue
  if [ -f $C/runs/$L/nodes.csv ]; then echo "$L SKIP (already done)" >> $LOG; continue; fi
  exec 9>>$HOME/.mh370-heavy.lock; flock 9
  cp $C/ext/$L.toml $ENG/hypotheses/debris-drift/$L.toml
  ( while sleep 30; do ps -o rss= -C $(basename $BIN) 2>/dev/null | sort -n | tail -1; done ) > $C/runs/$L.rss 2>/dev/null & MON=$!
  echo "$L start $(date -u +%FT%TZ) cfgsha=$(sha256sum $C/ext/$L.toml | cut -c1-16)" >> $LOG
  s=$(date +%s); (cd $ENG/hypotheses && env DRIFT_CONFIG=debris-drift/$L.toml RAYON_NUM_THREADS=88 $BIN pilot --ignored --nocapture > $C/runs/$L.log 2>&1); rc=$?
  kill $MON 2>/dev/null; flock -u 9; exec 9>&-
  n=$(( $(wc -l < $C/runs/$L/nodes.csv 2>/dev/null || echo 1) - 1 ))
  echo "$L EXIT=$rc wall_s=$(( $(date +%s) - s )) end=$(date -u +%FT%TZ) peak_rss_kb=$(sort -n $C/runs/$L.rss | tail -1) nodes=$n" >> $LOG
  for f in nodes.csv summary.toml coefficients.jsonl coefficients-meta.json; do cp $C/runs/$L/$f $OUT/$L-$f 2>/dev/null; done
  cp $LOG $OUT/chain.log
done < $C/ext/$LEGS
echo "STAGE-DONE $LEGS $(date -u +%FT%TZ)" >> $LOG
done
echo "ALL-DONE $(date -u +%FT%TZ)" >> $LOG; cp $LOG $OUT/chain.log
