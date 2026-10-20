# usage: bash case_pipeline2.sh CASE [stage...]  stages: truth infer score   (staged calibration run, 20 Oct 2026: pool truths (A2), joint flight draw (S2), tier 1a' event (A1))
set -u; . $HOME/mh370/e2e/env.sh; CASE=$1; shift; STAGES=${*:-truth infer score}; D=$E2E/cases/case-$CASE; mkdir -p $D; WT=$D/walltimes.txt
export POOL=${POOL:-$E2E/pool}
EVENT=${EVENT:-"m0011.bto:17540:18540,m0011.bfo:202:302,m2241.bto:14040:15040,m2241.bfo:154:254"}
for st in $STAGES; do t0=$(date +%s)
case $st in
truth)
  (cd "$ENG" && $PY $E2E/py/make_dummy.py data/variants/satcom-observations-bfo432.csv data/satellite-ephemeris-inmarsat.csv $D/obs-dummy.csv $D/eph-dummy.csv > /dev/null)
  sed -e "s#^seeds = .*#seeds = [1]#" -e "s#observations = .*#observations = \"$D/obs-dummy.csv\"#" -e "s#ephemeris = .*#ephemeris = \"$D/eph-dummy.csv\"#" -e "s#^name = .*#name = \"e2e-truth-$CASE\"#" $POOL/truthgen-template.toml > $D/truthgen.toml
  (cd $E2E && $PY py/pick_truth_pool.py $D $CASE $POOL $D/obs-dummy.csv --event $EVENT --max-candidates ${MAXC:-400}) > $D/truth-stage.log 2>&1 || { tl "case $CASE pick_truth_pool failed"; tail -3 $D/truth-stage.log; exit 4; }
  bash $E2E/truth_eof_pool.sh $CASE ${TTH:-40} ${CHN:-64} >> $D/truth-stage.log 2>&1 || { tl "case $CASE truth_eof_pool failed"; tail -3 $D/truth-stage.log; exit 4; }
  (cd $E2E && $PY py/pick_flight.py $D) >> $D/truth-stage.log 2>&1 || { tl "case $CASE pick_flight failed"; tail -3 $D/truth-stage.log; exit 4; }
  (cd $E2E && $PY py/make_synth.py $D $CASE $D/truth-eof "$ENG/data/variants/satcom-observations-bfo432.csv" inputs/fields.npz inputs/debris-evidence-audit.csv $HOME/mh370/drift/arclat) >> $D/truth-stage.log 2>&1 || { tl "case $CASE make_synth failed"; tail -3 $D/truth-stage.log; exit 4; }
  CH=$($PY -c "import json;print(json.load(open('$D/truth-core.json'))['chosen']['seed'])")
  for sd in $D/truth-eof/prior/seed-* $D/truth-handoff/seed-*; do [ "$(basename $sd)" = "seed-$CH" ] || rm -rf $sd; done; rm -rf $D/truth-eof-rt
  tl "case $CASE truth ready: $(grep -o '"impact": {[^}]*}' $D/truth-stage.log | head -1 | cut -c1-200) logZ $($PY -c "import json;print(round(json.load(open('$D/truth-core.json'))['flight_draw']['log_Z_chosen'],2))")";;
infer)
  bash $E2E/infer_case_lane.sh $CASE ${R:-4} ${ITH:-44} "${PPM:-[500_000, 250_000, 1_250_000, 250_000, 1_250_000]}" ${HR:-20000} || exit $?;;
score)
  (cd $E2E && $PY py/score_case.py $D $HOME/mh370/drift/arclat inputs/fields.npz inputs/debris-evidence-audit.csv) > $D/score.log 2>&1; rc=$?; tl "case $CASE score rc $rc"
  [ $rc = 0 ] || exit 7
  (cd $E2E && $PY py/hist_case.py $D) >> $D/score.log 2>&1 || true
  for s in $D/infer-core/bto-bfo/seed-*; do rm -f $s/early.npy $s/final.npy $s/route_plans.npy $s/tanks.npy $s/tanks32.npy $s/trace.npy $s/routes.npy $s/handoff-m0011/handoff.toml $s/handoff-m2241/handoff.toml; done
  rm -f $D/infer-eof-*/bto-bfo/seed-*/impacts.npy $D/truth-eof/prior/*/impacts.npy $D/rows-seed-*.npz;;
esac
echo "stage $st $(( $(date +%s)-t0 ))" >> $WT; done
du -sh $D >> $WT; tl "case $CASE stages [$STAGES] done; $(du -sh $D | cut -f1); disk free $(df -h --output=avail $HOME | tail -1)"
