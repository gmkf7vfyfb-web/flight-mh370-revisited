cd .tmp; W=$(pwd)
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 MKL_NUM_THREADS=2 RAYON_NUM_THREADS=2
PREP="$W/hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; MOD="$(dirname "$PREP")"
KC="$W/hy/ISO Sept 28 Status/inputs/recovered-v01/.sources/kadri-2024-hydroacoustics/data/kadri-table1-transients.csv"
CR="$W/repo/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke/compact_impacts.py"
cp standin/smoke_tau/summary.json standin/full_tau_summary_seed.json; mkdir -p standin/full_tau; cp standin/smoke_tau/summary.json standin/full_tau/summary.json
cd "$PREP"; date -u +%H:%M:%S; lockf -k /tmp/.mh370-heavy.lock sh -c "date -u +LOCK_ACQUIRED_%H:%M:%S; python '$W/standin/tau_sensitivity.py' '$PREP' '$MOD' /Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c /Users/pete/Downloads/mh370-exchange/hydroacoustics/next-run-c '$W/standin/full_tau' '$KC' '$CR' --no-columns; date -u +DONE_%H:%M:%S" 2>&1 | tail -40