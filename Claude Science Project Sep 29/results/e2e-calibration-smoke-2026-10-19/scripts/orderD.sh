# 20 Oct order D: case 5 and case 1 at 4 x 3.5M (case 1 with the corrected 00:19 BFO-model draw)
set -u; cd ~/mh370/e2e; . ./env.sh
PPM="[500_000, 250_000, 1_250_000, 250_000, 1_250_000]"
# free my own finished intermediates (statistics and histograms already extracted and committed at d7c73576)
rm -f cases/case-*/rows-seed-*.npz; tl "order D start; e2e $(du -sh . | cut -f1); disk free $(df -h --output=avail ~ | tail -1)"
# case 1 corrected: rebuild the truth descent table (deleted after scoring), then the synthetic data with the fixed draw
bash truth_eof.sh 9001 16 > cases/case-9001/truth-eof-rerun.log 2>&1
D=cases/case-29001; rm -rf $D; mkdir -p $D; cp cases/case-9001/truth-core.json cases/case-9001/obs-dummy.csv $D/
$PY py/make_synth.py $D 9001 cases/case-9001/truth-eof "$ENG/data/variants/satcom-observations-bfo432.csv" inputs/fields.npz inputs/debris-evidence-audit.csv ~/mh370/drift/arclat > $D/synth.log 2>&1; tl "case 29001 truth: $(head -c 400 $D/synth.log)"
rm -f cases/case-9001/truth-eof/prior/*/impacts.npy
D=cases/case-19005; rm -rf $D; mkdir -p $D; cp cases/case-9005/truth.json cases/case-9005/obs-synthetic.csv $D/
for K in 19005 29001; do D=cases/case-$K; t0=$(date +%s)
  bash infer_case_lowdisk.sh $K 4 40 "$PPM" 20000 || { tl "case $K inference stopped rc $?"; continue; }
  $PY py/score_case.py $D ~/mh370/drift/arclat inputs/fields.npz inputs/debris-evidence-audit.csv > $D/score.log 2>&1; tl "case $K score rc $?"
  $PY py/hist_case.py $D >> $D/score.log 2>&1
  rm -f $D/infer-eof-*/bto-bfo/seed-*/impacts.npy; rm -f $D/rows-seed-*.npz
  echo "case total $(( $(date +%s)-t0 ))" >> $D/walltimes.txt; tl "case $K done; $(du -sh $D | cut -f1); disk free $(df -h --output=avail ~ | tail -1)"
done
tar czf /home/pete/.claude-science-scratch/e2e/stats-orderD.tgz cases/case-19005 cases/case-29001 --exclude='*/infer-core/*' --exclude='*/infer-eof-*/*' --exclude='*/infer-rt*' cases/case-9001/hist.json cases/case-9002/hist.json cases/case-9003/hist.json cases/case-9004/hist.json cases/case-9005/hist.json cases/case-19001/hist.json cases/case-19002/hist.json cases/case-900*/case-stats.json cases/case-1900[12]/case-stats.json cases/case-*/truth.json timeline.txt
tl "order D finished"
