export OMP_NUM_THREADS=4 OPENBLAS_NUM_THREADS=4
for s in free descent-climb repro-radar; do
  STRATUM=run-j-$s python3 compose_drift_runj_family.py compose-runj-$s.npz > compose-$s.log 2>&1; echo "EXIT $s $?" >> compose-$s.log
  python3 analyze_runj.py compose-runj-$s.npz analysis-runj-$s.json >> compose-$s.log 2>&1
done
