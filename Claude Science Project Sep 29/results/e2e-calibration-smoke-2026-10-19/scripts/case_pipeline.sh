# usage: bash case_pipeline.sh CASE [stage...]  stages: truth infer score   (smoke scale: R=4, 700k particles per seed, 10k hand-off rows)
set -u; . $HOME/mh370/e2e/env.sh; CASE=$1; shift; STAGES=${*:-truth infer score}; D=$E2E/cases/case-$CASE; mkdir -p $D; WT=$D/walltimes.txt
EVENT="m0011.bto:17540:18540,m0011.bfo:202:302"
for st in $STAGES; do t0=$(date +%s)
case $st in
truth)
  bash $E2E/truth_core.sh $CASE ${NREP:-3000} ${TTH:-32} > $D/truth-stage.log 2>&1
  (cd $E2E && $PY py/pick_truth.py $D $CASE $D/obs-dummy.csv $D/eph-dummy.csv --event $EVENT) >> $D/truth-stage.log 2>&1 || { tl "case $CASE pick_truth failed"; tail -3 $D/truth-stage.log; exit 4; }
  SDIR=$($PY -c "import json;print(json.load(open('$D/truth-core.json'))['chosen']['seed_dir'])"); case "$SDIR" in /*) ;; *) SDIR=$E2E/$SDIR;; esac
  mkdir -p $D/keep && mv $SDIR $D/keep/ && rm -rf $D/truth-core && mkdir -p $D/truth-core/prior && mv $D/keep/* $D/truth-core/prior/ && rmdir $D/keep
  bash $E2E/truth_eof.sh $CASE ${TTH:-32} >> $D/truth-stage.log 2>&1
  (cd $E2E && $PY py/make_synth.py $D $CASE $D/truth-eof "$ENG/data/variants/satcom-observations-bfo432.csv" inputs/fields.npz inputs/debris-evidence-audit.csv $HOME/mh370/drift/arclat) >> $D/truth-stage.log 2>&1 || { tl "case $CASE make_synth failed"; tail -3 $D/truth-stage.log; exit 4; }
  rm -f $D/truth-eof/prior/*/impacts.npy.keep; tl "case $CASE truth ready: $(tail -2 $D/truth-stage.log | head -1 | cut -c1-300)";;
infer)
  bash $E2E/infer_case.sh $CASE ${R:-4} ${ITH:-40} "${PPM:-[100_000, 50_000, 250_000, 50_000, 250_000]}" ${HR:-10000} || exit $?;;
score)
  (cd $E2E && $PY py/score_case.py $D $HOME/mh370/drift/arclat inputs/fields.npz inputs/debris-evidence-audit.csv) > $D/score.log 2>&1; rc=$?; tl "case $CASE score rc $rc"
  [ $rc = 0 ] && { for s in $D/infer-core/bto-bfo/seed-*; do rm -f $s/early.npy $s/final.npy $s/route_plans.npy $s/tanks.npy $s/tanks32.npy $s/trace.npy $s/routes.npy $s/handoff-m0011/handoff.toml $s/handoff-m2241/handoff.toml; done; rm -f $D/infer-eof-*/bto-bfo/seed-*/impacts.npy $D/truth-eof/prior/*/impacts.npy; };;
esac
echo "stage $st $(( $(date +%s)-t0 ))" >> $WT; done
du -sh $D >> $WT; tl "case $CASE stages [$STAGES] done; $(du -sh $D | cut -f1); disk free $(df -h --output=avail $HOME | tail -1)"
