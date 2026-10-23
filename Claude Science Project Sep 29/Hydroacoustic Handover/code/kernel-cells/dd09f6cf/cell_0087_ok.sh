du -sh red ocean; ls -la ocean | head -20; df -h /Users/pete/Downloads | tail -1
X=/Users/pete/Downloads/mh370-exchange/searched-areas/kadri-haixun-2026-10-18; mkdir -p $X/per-seed $X/drift
cp red/*.npz $X/per-seed/; cp ocean/drift_*.npz ocean/test_cells.npy ocean/cells_*.npy $X/drift/; cp lib/reduce_kh.py lib/surface_drift.py $X/
(cd $X && find . -type f ! -name SHA256SUMS -exec shasum -a 256 {} \; > SHA256SUMS); du -sh $X