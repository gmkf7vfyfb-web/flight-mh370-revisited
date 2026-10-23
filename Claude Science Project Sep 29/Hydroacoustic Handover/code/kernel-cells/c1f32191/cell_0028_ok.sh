cd "hydro/Claude Science Project Sep 29/engine/hypotheses/hydroacoustics/prepare/composition_run_j"
for s in run-j-waypoints run-j-free run-j-descent-climb run-j-repro-radar; do python -c "import numpy as np,glob; fs=sorted(glob.glob('/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/$s/seed-*/impacts32.npy')); print('$s', len(fs), [np.load(f,mmap_mode='r').shape[0] for f in fs[:3]])"; done
df -k /System/Volumes/Data | tail -1
mkdir -p /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging
time OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 python worker.py run-j-free 1 /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging 2>&1 | grep -v Warn | tail -5
cat /Users/pete/Downloads/mh370-exchange/hydroacoustics/run-j-gated.staging/_parts/run-j-free_1.json | head -60