cd .tmp/repo; git sparse-checkout add "/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke/compact-columns.json" 2>&1 | grep -v -E "config|failed to store"; cd ..; W=$(pwd)
export OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 VECLIB_MAXIMUM_THREADS=2 MKL_NUM_THREADS=2
PREP="$W/hy/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare"; MOD="$(dirname "$PREP")"
KC="$W/hy/ISO Sept 28 Status/inputs/recovered-v01/.sources/kadri-2024-hydroacoustics/data/kadri-table1-transients.csv"
CR="$W/repo/Claude Science Project Sep 29/engine/hypotheses/end-of-flight/smoke/compact_impacts.py"
cd "$PREP"; ( time python "$W/standin/tau_sensitivity.py" "$PREP" "$MOD" /Users/pete/Downloads/mh370-exchange/end-of-flight/next-run-c /Users/pete/Downloads/mh370-exchange/hydroacoustics/next-run-c "$W/standin/smoke_tau" "$KC" "$CR" --strata next-c-free --seeds 1 --check-baseline --no-columns ) 2>&1 | tail -8