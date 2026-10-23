E=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i; du -sh $E/*/ ; echo ===; ls -la $E/next-i-free/seed-1/; echo ===; python3 -c "
import numpy as np,glob,os
for f in sorted(glob.glob('$E/*/seed-*/impacts32.npy'))[:3]:
    a=np.load(f,mmap_mode='r'); print(f.split('run-i/')[1], a.shape, a.dtype)
print('n files', len(glob.glob('$E/*/seed-*/impacts32.npy')))
z=np.load('$E/next-i-free/seed-1/tau90_v1.npz'); print('tau90 keys', z.files, [z[k].shape for k in z.files])
"