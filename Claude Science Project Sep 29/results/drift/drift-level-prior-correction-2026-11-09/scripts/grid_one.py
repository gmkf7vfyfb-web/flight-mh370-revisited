"""Local driver for one windage target (10 Nov 2026): unpack the reweighted class-1 coefficients, build the hybrid coefficient folder, run stage 1 (head configuration).
Usage: grid_one.py TAG SEEDS(comma-separated)   Inputs: reweight/<TAG>__<leg>.jsonl.gz (from reweight_rescore.py), rescore/x/out/R3-allcoasts-4periods (production R3).
Writes rescore/x/out/RG-<TAG>/ (hybrid) and res-grid/<TAG>/lm-head-s<seed>.npz ."""
import sys, os, glob, shutil, subprocess, time
TAG = sys.argv[1]; SEEDS = sys.argv[2].split(',')
t0 = time.time(); HY = f'rescore/x/out/RG-{TAG}'; RWD = f'rescore/x/rw/{TAG}'; os.makedirs(RWD, exist_ok=True); os.makedirs(f'res-grid/{TAG}', exist_ok=True)
for f in glob.glob(f'reweight/{TAG}__*.jsonl.gz'): shutil.copy(f, os.path.join(RWD, os.path.basename(f).split('__', 1)[1]))
shutil.copy('rescore/x/cfg/R3H-meta.json', f'rescore/x/cfg/RG-{TAG}-meta.json')
print(subprocess.run(['python', 'offline/build_hybrid_grid.py', 'rescore/x/out/R3-allcoasts-4periods', RWD, HY] + (['ext-=whigh-', 'ext2-=whigh2-'] if TAG.startswith('h_') else ['ext-=wide-', 'ext2-=wide2-', 'ext3-=wide3-']), capture_output=True, text=True).stdout.strip(), flush=True)
env = dict(os.environ, LEVELS='ramp', VARIANT=f'RG-{TAG}', OUTD=f'res-grid/{TAG}')
p = subprocess.run(['python', 'offline/grid_stage1.py', 'head'] + SEEDS, env=env, capture_output=True, text=True)
print(p.stdout[-600:], p.stderr[-400:], flush=True)
shutil.rmtree(HY, ignore_errors=True)       # the hybrid folder is large and can be rebuilt
print('done', TAG, round(time.time() - t0), 's')
