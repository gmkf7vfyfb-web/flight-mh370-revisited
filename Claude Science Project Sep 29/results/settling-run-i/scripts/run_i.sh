#!/bin/sh
# Ocean settling on end of flight's run I, one stratum at a time as each READY lands (detached; restart-safe: a stratum whose
# exchange folder has READY is skipped). <= 2 threads outside the heavy lock: prep 1 thread, then settling 2 threads, in series.
WK=/Users/pete/Downloads/mh370-settling-work; cd $WK
E=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i; C=/Users/pete/Downloads/mh370-exchange/core/run-i; X=/Users/pete/Downloads/mh370-exchange/settling/run-i
export HOME=$WK/home CARGO_HOME=/Users/pete/.cargo CARGO_TARGET_DIR=$WK/target PATH="/Users/pete/.rustup/toolchains/1.98.0-aarch64-apple-darwin/bin:$PATH"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 MPLCONFIGDIR=$WK/mpl
mkdir -p $HOME field $X mpl
EOFC=$(cat eof-smoke-commit.txt)
echo "start $(date -u +%FT%TZ)"
for i in $(seq 1 600); do
  left=0
  for st in next-i-waypoints next-i-free next-i-descent-climb next-i-repro-radar; do
    [ -e "$X/$st/READY" ] && continue
    if [ ! -e "$E/$st/READY" ]; then left=$((left+1)); continue; fi
    tag=ri_$(echo $st | sed 's/next-i-//; s/-//g'); label=run-i-$(echo $st | sed 's/next-i-//')
    echo "== $st prep $(date -u +%T)"
    python3 wf_runi.py prep "$E/$st" "$C/$st" $tag > log_${tag}_prep.txt 2>&1 || { echo "$st PREP FAILED"; tail -5 log_${tag}_prep.txt; left=$((left+1)); continue; }
    tail -2 log_${tag}_prep.txt
    echo "== $st settle $(date -u +%T)"
    ( cd settling-engine && RAYON_NUM_THREADS=2 SETTLING_THREADS=2 SETTLING_FIELD_IN=$WK/field/${tag}_impacts.f64 SETTLING_FIELD_OUT=$WK/field/${tag}_elements.f64 \
        cargo test --offline -j 2 --release -p mh370-hypotheses settling::tests::wreckage_field -- --ignored > $WK/log_${tag}_settle.txt 2>&1 )
    grep -q "test result: ok" log_${tag}_settle.txt || { echo "$st SETTLE FAILED"; tail -5 log_${tag}_settle.txt; left=$((left+1)); continue; }
    echo "== $st render $(date -u +%T)"
    for w in core cause family; do python3 wf_runi.py render $tag $label 9330d4c $EOFC $w > log_${tag}_render_$w.txt 2>&1 || { echo "$st RENDER $w FAILED"; tail -3 log_${tag}_render_$w.txt; }; done
    python3 wf_runi.py publish $tag $label "$X/$st" > log_${tag}_publish.txt 2>&1 && echo "== $st PUBLISHED $(date -u +%T)" || { echo "$st PUBLISH FAILED"; tail -5 log_${tag}_publish.txt; }
  done
  if [ $left -eq 0 ]; then
    python3 wf_runi.py final "$X" '{"next-i-waypoints": 0.9982, "next-i-free": 0.0011, "next-i-descent-climb": 0.0002, "next-i-repro-radar": 0.0004}' && echo "ALL DONE $(date -u +%FT%TZ)"; exit 0
  fi
  sleep 60
done
echo "timeout $(date -u +%FT%TZ)"
