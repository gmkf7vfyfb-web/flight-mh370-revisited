#!/bin/sh
# One run J stratum: prep (1 thread) -> settle (2 threads, serialised by $WK/.settle.lock) -> render x3 -> publish. Restart-safe (skips if published).
st=$1; WK=/Users/pete/Downloads/mh370-settling-work-j; cd $WK
E=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j; C=/Users/pete/Downloads/mh370-exchange/core/run-j; X=/Users/pete/Downloads/mh370-exchange/settling/run-j
export HOME=$WK/home CARGO_HOME=/Users/pete/.cargo CARGO_TARGET_DIR=$WK/target PATH="/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH" XDG_CONFIG_HOME=$WK/home/xdg
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MPLCONFIGDIR=$WK/mpl
[ -e "$X/$st/READY" ] && { echo "$st already published"; exit 0; }
[ -e "$E/$st/READY" ] || { echo "$st: end-of-flight READY missing"; exit 1; }
tag=rj_$(echo $st | sed 's/run-j-//; s/-//g'); label=$st; EOFC=$(cat eof-smoke-commit.txt)
echo "== $st prep $(date -u +%T)"
python3 wf_runj.py prep "$E/$st" "$C/$st" $tag > log_${tag}_prep.txt 2>&1 || { echo "$st PREP FAILED"; tail -5 log_${tag}_prep.txt; exit 1; }
tail -2 log_${tag}_prep.txt
free=$(df -g /Users/pete | awk 'NR==2{print $4}'); [ "$free" -ge 29 ] || { echo "$st STOP: free ${free} GiB < 29 GiB before settle"; exit 2; }
echo "== $st settle wait $(date -u +%T) free ${free} GiB"
lockf -k $WK/.settle.lock sh -c "cd settling-engine && echo '== $st settle start' \$(date -u +%T) && RAYON_NUM_THREADS=2 SETTLING_THREADS=2 SETTLING_FIELD_IN=$WK/field/${tag}_impacts.f64 SETTLING_FIELD_OUT=$WK/field/${tag}_elements.f64 cargo test --offline -j 2 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored --nocapture > $WK/log_${tag}_settle.txt 2>&1"
grep -q "test result: ok" log_${tag}_settle.txt || { echo "$st SETTLE FAILED"; tail -5 log_${tag}_settle.txt; exit 1; }
echo "== $st render $(date -u +%T)"
for w in core cause family; do python3 wf_runj.py render $tag $label 9330d4c $EOFC $w > log_${tag}_render_$w.txt 2>&1 || { echo "$st RENDER $w FAILED"; tail -3 log_${tag}_render_$w.txt; exit 1; }; done
python3 wf_runj.py publish $tag $label "$X/$st" > log_${tag}_publish.txt 2>&1 && echo "== $st PUBLISHED $(date -u +%T)" || { echo "$st PUBLISH FAILED"; tail -5 log_${tag}_publish.txt; exit 1; }
