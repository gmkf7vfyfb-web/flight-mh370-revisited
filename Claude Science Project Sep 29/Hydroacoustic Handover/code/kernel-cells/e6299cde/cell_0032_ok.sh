cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/searches_run_j"
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
O=/Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-searches/null
for l in 3376 3274 3250; do nohup python null_worker.py $l 0 1 $O/null_$l.npz > $O/null_$l.log 2>&1 & done
sleep 20; tail -n1 $O/*.log