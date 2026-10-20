# light side job: score each case-29001 replicate as soon as its end-of-flight pass is logged, then delete that replicate's impacts
# (keeps the case under the 8 GB cap; the final score_case.py call in orderD.sh reuses the cached per-seed results)
set -u; cd ~/mh370/e2e; . ./env.sh; D=cases/case-29001; done_n=0
while [ $done_n -lt 4 ]; do
  for r in 1 2 3 4; do k=$((29001*100+r))
    [ -f $D/seedstats-seed-$k.json ] && continue
    grep -q "^eof $k " $D/walltimes.txt 2>/dev/null || continue
    E2E_ONLY_SEEDS="seed-$k" $PY py/score_case.py $D ~/mh370/drift/arclat inputs/fields.npz inputs/debris-evidence-audit.csv > $D/score-watch-$k.log 2>&1
    [ -f $D/seedstats-seed-$k.json ] && rm -f $D/infer-eof-$k/bto-bfo/seed-$k/impacts.npy && tl "case 29001 seed $k scored early and impacts removed; $(du -sh $D | cut -f1)"
  done
  done_n=$(ls $D/seedstats-seed-*.json 2>/dev/null | wc -l); sleep 30
done
