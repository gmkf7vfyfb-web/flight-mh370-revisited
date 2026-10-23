for a in 0.012 0.005 0.025; do
 NPART=64 python lib/surface_drift.py ocean/cells_sparse.npy ocean/drift_sparse_$a.npz $a > ocean/log_sparse_$a.txt 2>&1 &
 NPART=256 python lib/surface_drift.py ocean/cells_dense.npy ocean/drift_dense_$a.npz $a > ocean/log_dense_$a.txt 2>&1 &
done; wait; tail -n 2 ocean/log_*.txt