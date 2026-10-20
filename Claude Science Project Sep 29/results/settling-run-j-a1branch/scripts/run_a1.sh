#!/bin/sh
# Settling on the A1-branch conditional pass + run J waypoints production (stratified), work order overnight-2026-10-19 B1.
# pass0 (estimator terms) is run first; this script: prep (1 thread) -> settle (4 threads) -> render core, a1 -> publish (READY written after checks).
WK=/Users/pete/Downloads/mh370-settling-work-j; cd $WK
C=/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints; X=/Users/pete/Downloads/mh370-exchange/settling/run-j-a1branch/run-j-waypoints
export HOME=$WK/home CARGO_HOME=/Users/pete/.cargo CARGO_TARGET_DIR=$WK/target PATH="/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH" XDG_CONFIG_HOME=$WK/home/xdg
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MPLCONFIGDIR=$WK/mpl
tag=rja1; label=run-j-a1branch-waypoints; EOFC=$(cat eof-smoke-commit.txt)
echo "== prep $(date -u +%T) free $(df -g /Users/pete | awk 'NR==2{print $4}') GiB"
python3 wf_a1branch.py prep $C $tag > log_${tag}_prep.txt 2>&1 || { echo "PREP FAILED"; tail -5 log_${tag}_prep.txt; exit 1; }
tail -2 log_${tag}_prep.txt
free=$(df -g /Users/pete | awk 'NR==2{print $4}'); [ "$free" -ge 9 ] || { echo "PAUSE: free ${free} GiB < 9 GiB (5 GB floor + 4 GB cap) before settle"; exit 2; }
echo "== settle $(date -u +%T) free ${free} GiB"
( cd settling-engine && RAYON_NUM_THREADS=4 SETTLING_THREADS=4 SETTLING_FIELD_IN=$WK/field/${tag}_impacts.f64 SETTLING_FIELD_OUT=$WK/field/${tag}_elements.f64 cargo test --offline -j 4 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored --nocapture > $WK/log_${tag}_settle.txt 2>&1 )
grep -q "test result: ok" log_${tag}_settle.txt || { echo "SETTLE FAILED"; tail -5 log_${tag}_settle.txt; exit 1; }
echo "== render $(date -u +%T)"
for w in core a1; do python3 wf_a1branch.py render $tag $label 9330d4c $EOFC $w > log_${tag}_render_$w.txt 2>&1 || { echo "RENDER $w FAILED"; tail -3 log_${tag}_render_$w.txt; exit 1; }; done
python3 wf_a1branch.py publish $tag $label $X > log_${tag}_publish.txt 2>&1 && echo "== PUBLISHED $(date -u +%T)" || { echo "PUBLISH FAILED"; tail -5 log_${tag}_publish.txt; exit 1; }
echo "end free $(df -g /Users/pete | awk 'NR==2{print $4}') GiB"
