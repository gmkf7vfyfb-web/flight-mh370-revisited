#!/bin/sh
# Both-burst supplement (waypoints, 8 thinned seeds, D2-D5 products) after the main run; then final again (top-level READY last).
WK=/Users/pete/Downloads/mh370-settling-work-j; cd $WK
E=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j-both-burst; C=/Users/pete/Downloads/mh370-exchange/core/run-j; X=/Users/pete/Downloads/mh370-exchange/settling/run-j
export HOME=$WK/home CARGO_HOME=/Users/pete/.cargo CARGO_TARGET_DIR=$WK/target PATH="/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH" XDG_CONFIG_HOME=$WK/home/xdg
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MPLCONFIGDIR=$WK/mpl
export WF_DS=D2,D3,D4,D5 WF_SET_NOTE="both-burst set, 8 thinned seeds, D2-D5 only"
tag=rj_bothburst; label=run-j-both-burst-waypoints; out=$X/run-j-both-burst-waypoints; EOFC=$(cat eof-smoke-commit.txt)
[ -e $out/READY ] && { echo "bb already published"; exit 0; }
echo "== bb prep $(date -u +%T)"
python3 wf_runj.py prep "$E/run-j-waypoints" "$C/run-j-waypoints" $tag > log_${tag}_prep.txt 2>&1 || { echo "BB PREP FAILED"; tail -5 log_${tag}_prep.txt; exit 1; }
tail -2 log_${tag}_prep.txt
python3 check_lnz.py field/${tag}_info.json $E/summary/table-0019-supplementary-8.json || { echo "BB lnZ CHECK FAILED"; exit 1; }
free=$(df -g /Users/pete | awk 'NR==2{print $4}'); [ "$free" -ge 29 ] || { echo "BB STOP: free ${free} GiB"; exit 2; }
echo "== bb settle $(date -u +%T) free ${free} GiB"
( cd settling-engine && RAYON_NUM_THREADS=6 SETTLING_THREADS=6 SETTLING_FIELD_IN=$WK/field/${tag}_impacts.f64 SETTLING_FIELD_OUT=$WK/field/${tag}_elements.f64 cargo test --offline -j 6 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored --nocapture > $WK/log_${tag}_settle.txt 2>&1 )
grep -q "test result: ok" log_${tag}_settle.txt || { echo "BB SETTLE FAILED"; exit 1; }
for w in core cause family; do python3 wf_runj.py render $tag $label 9330d4c $EOFC $w > log_${tag}_render_$w.txt 2>&1 || { echo "BB RENDER $w FAILED"; tail -3 log_${tag}_render_$w.txt; exit 1; }; done
python3 wf_runj.py publish $tag $label $out > log_${tag}_publish.txt 2>&1 && echo "== bb PUBLISHED $(date -u +%T)" || { echo "BB PUBLISH FAILED"; tail -5 log_${tag}_publish.txt; exit 1; }
