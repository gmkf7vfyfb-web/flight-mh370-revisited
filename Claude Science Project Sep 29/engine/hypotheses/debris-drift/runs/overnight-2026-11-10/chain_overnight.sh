set -u
# Overnight chain, 10 Nov 2026 (v2: higher-windage sensitivity first, at Pete's request). Waits for the wide-windage chain (ALL-DONE in wide-chain.log), runs four quick start-up tests, then
#  run 0: higher-windage sensitivity (exterior c_wind log-normal median 2.4 %, sigma(log) 0.35): 0a = 42 southern points, seeds 217-232 (6 legs); 0b = 84 points, seeds 201-216 (12 legs)
#  run 1: ocean-error length scale 50 and 200 km (wide exterior class, 42 southern points, seeds 217-232)   12 legs
#  run 2: particle-noise check, master seed 23 (legs 2 and 3, both models)                                     4 legs
#  run 3: extra ocean samples, seeds 233-248, all three classes, wide exterior class, 42 southern points       6 legs
# Resumable (a leg with nodes.csv is skipped). Never deletes anything. Stops if free disk space falls below 3 GB or if two legs fail in a row.
C=$HOME/mh370/drift/coef; ENG=$C/engine; BIN=$C/bin-wide
OUT=$PWD/out; mkdir -p $OUT $C/runs $C/overnight2; LOG=$C/runs/overnight2-chain.log
cp $PWD/*.toml $PWD/legs0a.txt $PWD/legs0b.txt $PWD/legs1.txt $PWD/legs2.txt $PWD/legs3.txt $C/overnight2/
echo "gate wait $(date -u +%FT%TZ)" >> $LOG
until grep -q ALL-DONE $C/runs/wide-chain.log 2>/dev/null; do sleep 60; done
while pgrep -f 'bin-arr.*pilot|bin-shadow.*pilot|mh370_hypotheses.*pilot|bin-wide.*pilot' >/dev/null; do sleep 30; done
echo "gate open $(date -u +%FT%TZ)" >> $LOG
echo "start $(date -u +%FT%TZ) bin=$BIN binsha=$(sha256sum $BIN | cut -c1-16)" >> $LOG
# ---- start-up tests: one node, two ocean samples, 100 particles
for S in whigh2-globcurrent-1 wls50-globcurrent-1 wseed23-glorys12-2 wide3-globcurrent-1 wide3-glorys12-1; do
  exec 9>>$HOME/.mh370-heavy.lock; flock 9
  python3 - $C/overnight2/$S.toml $ENG/hypotheses/debris-drift/smoke-$S.toml $C/runs/smoke-$S <<'PY'
import re, sys
t = open(sys.argv[1]).read()
t = re.sub(r'output_dir = "[^"]*"', 'output_dir = "%s"' % sys.argv[3], t)
t = re.sub(r'(?m)^env_seeds = \[(\d+), (\d+),[^\]]*\]', r'env_seeds = [\1, \2]', t)
t = re.sub(r'(?m)^node_subset = \[(\d+),[^\]]*\]', r'node_subset = [\1]', t)
t = re.sub(r'(?m)^particles_per_class = \d+', 'particles_per_class = 100', t)
open(sys.argv[2], 'w').write(t)
PY
  s=$(date +%s); (cd $ENG/hypotheses && env DRIFT_CONFIG=debris-drift/smoke-$S.toml RAYON_NUM_THREADS=88 $BIN pilot --ignored --nocapture > $C/runs/smoke-$S.log 2>&1); rc=$?
  flock -u 9; exec 9>&-
  n=$(( $(wc -l < $C/runs/smoke-$S/nodes.csv 2>/dev/null || echo 0) - 1 ))
  echo "smoke $S EXIT=$rc wall_s=$(( $(date +%s) - s )) nodes=$n" >> $LOG
  if [ $rc -ne 0 ] || [ $n -lt 1 ]; then echo "SMOKE-FAIL $S $(date -u +%FT%TZ)" >> $LOG; cp $LOG $OUT/chain.log; cp $C/runs/smoke-$S.log $OUT/ 2>/dev/null; exit 2; fi
done
FAILS=0
for LEGS in legs0a.txt legs0b.txt legs1.txt legs2.txt legs3.txt; do
while read L; do
  [ -z "$L" ] && continue
  if [ -f $C/runs/$L/nodes.csv ]; then echo "$L SKIP (already done)" >> $LOG; continue; fi
  AV=$(df --output=avail -k $HOME | tail -1 | tr -d ' ')
  if [ "$AV" -lt 3000000 ]; then echo "DISK-LOW avail_kb=$AV before $L $(date -u +%FT%TZ): chain stopped, nothing deleted" >> $LOG; cp $LOG $OUT/chain.log; exit 3; fi
  exec 9>>$HOME/.mh370-heavy.lock; flock 9
  cp $C/overnight2/$L.toml $ENG/hypotheses/debris-drift/$L.toml
  ( while sleep 30; do ps -o rss= -C $(basename $BIN) 2>/dev/null | sort -n | tail -1; done ) > $C/runs/$L.rss 2>/dev/null & MON=$!
  echo "$L start $(date -u +%FT%TZ) cfgsha=$(sha256sum $C/overnight2/$L.toml | cut -c1-16) avail_kb=$AV" >> $LOG
  s=$(date +%s); (cd $ENG/hypotheses && env DRIFT_CONFIG=debris-drift/$L.toml RAYON_NUM_THREADS=88 $BIN pilot --ignored --nocapture > $C/runs/$L.log 2>&1); rc=$?
  kill $MON 2>/dev/null; flock -u 9; exec 9>&-
  n=$(( $(wc -l < $C/runs/$L/nodes.csv 2>/dev/null || echo 1) - 1 ))
  echo "$L EXIT=$rc wall_s=$(( $(date +%s) - s )) end=$(date -u +%FT%TZ) peak_rss_kb=$(sort -n $C/runs/$L.rss | tail -1) nodes=$n" >> $LOG
  if [ $rc -ne 0 ] || [ $n -lt 1 ]; then FAILS=$((FAILS + 1)); else FAILS=0; fi
  if [ $FAILS -ge 2 ]; then echo "STOPPED after two failed legs $(date -u +%FT%TZ)" >> $LOG; cp $LOG $OUT/chain.log; exit 4; fi
  for f in nodes.csv summary.toml coefficients.jsonl coefficients-meta.json responses.json; do cp $C/runs/$L/$f $OUT/$L-$f 2>/dev/null; done
  cp $LOG $OUT/chain.log
done < $C/overnight2/$LEGS
echo "STAGE-DONE $LEGS $(date -u +%FT%TZ)" >> $LOG
done
echo "ALL-DONE $(date -u +%FT%TZ)" >> $LOG; cp $LOG $OUT/chain.log
