#!/bin/sh
# Settling on the run J northern supplement, full rule-B set (overnight-2026-10-20 B1): prep -> disk projection -> settle (4 threads) -> render -> publish.
WK=/Users/pete/Downloads/mh370-settling-work-j; cd $WK
X=/Users/pete/Downloads/mh370-exchange/settling/run-j-supplement/ruleB-waypoints
export HOME=$WK/home CARGO_HOME=/Users/pete/.cargo CARGO_TARGET_DIR=$WK/target PATH="/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH" XDG_CONFIG_HOME=$WK/home/xdg
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MPLCONFIGDIR=$WK/mpl
tag=rjs; label=run-j-supplement-waypoints
echo "== prep $(date -u +%T) free $(df -g /Users/pete | awk 'NR==2{print $4}') GiB"
[ -e field/${tag}_impacts.f64 ] && [ -e field/${tag}_info.json ] && echo "prep exists, reused" || { python3 wf_supp.py prep $tag > log_${tag}_prep.txt 2>&1 || { echo "PREP FAILED"; tail -5 log_${tag}_prep.txt; exit 1; }; }
tail -2 log_${tag}_prep.txt
draws=$(python3 -c "import numpy as np; print(int(np.fromfile('field/${tag}_impacts.f64','<f8').reshape(-1,14)[:,12].sum()))")
proj=$((draws * 66 * 64 / 1000000)); echo "draws $draws projected elements ${proj} MB"
[ $proj -le 2700 ] || { echo "STOP: projected ${proj} MB over the 3 GB cap"; exit 3; }
free=$(df -g /Users/pete | awk 'NR==2{print $4}'); [ "$free" -ge 9 ] || { echo "PAUSE: free ${free} GiB < 9 GiB"; exit 2; }
echo "== settle $(date -u +%T) free ${free} GiB"
( cd settling-engine && RAYON_NUM_THREADS=4 SETTLING_THREADS=4 SETTLING_FIELD_IN=$WK/field/${tag}_impacts.f64 SETTLING_FIELD_OUT=$WK/field/${tag}_elements.f64 cargo test --offline -j 4 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored --nocapture > $WK/log_${tag}_settle.txt 2>&1 )
grep -q "test result: ok" log_${tag}_settle.txt || { echo "SETTLE FAILED"; tail -5 log_${tag}_settle.txt; exit 1; }
echo "== render $(date -u +%T)"
for w in core family north other; do python3 wf_supp.py render $tag $label 9330d4c $w > log_${tag}_render_$w.txt 2>&1 || { echo "RENDER $w FAILED"; tail -3 log_${tag}_render_$w.txt; exit 1; }; done
python3 wf_supp.py publish $tag $label $X > log_${tag}_publish.txt 2>&1 && echo "== PUBLISHED $(date -u +%T)" || { echo "PUBLISH FAILED"; tail -5 log_${tag}_publish.txt; exit 1; }
echo "end free $(df -g /Users/pete | awk 'NR==2{print $4}') GiB"
