A="$(pwd)/audit/repo/Claude Science Project Sep 29/results/hydroacoustics-audit"; S="$(pwd)/audit/repo/Claude Science Project Sep 29/results/hydroacoustics-pleiades-test-standin"; M="$(pwd)/audit/hb/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics"; X=/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b; cd audit/work/sens; export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONPATH="$M/prepare" N_SYN=1000
jobs1=""; for v in base lvl-8 lvl+8 tilt+ tilt- emp emp-recal; do jobs1="$jobs1 held-out:$v"; done
for o in r600-bto-only r600-bto-raw-bfo; do for v in base emp emp-recal lvl-8 tilt+; do jobs1="$jobs1 $o:$v"; done; done
echo $jobs1 | tr ' ' '\n' > joblist.txt
run(){ o=${1%%:*}; v=${1##*:}; AUDIT_VARIANT=$v python "$A/scripts/sens.py" power "$S/standin-scripts" "$A/data/air9_residuals.csv" "$M" "$S/imos_events_searched.json" kadri.csv $X/sources-0019-$o.npz out/$o/$v > log_${o}_$v.txt 2>&1; echo done $1; }
export -f run; export A S M X
cat joblist.txt | xargs -P 2 -I{} bash -c 'run {}' 2>&1 | tail -20