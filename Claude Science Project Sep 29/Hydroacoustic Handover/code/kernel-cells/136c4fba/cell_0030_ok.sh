R=/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive
cat $R/next-i-free/seed-1/COLUMNS.txt | tr ',' '\n' | nl | sed -n 40,80p
echo "=== row count ==="; python3 -c "
import numpy as np
a=np.load('$R/next-i-free/seed-1/impacts32.npy',mmap_mode='r'); print(a.shape, a.dtype)
z=np.load('$R/next-i-free/seed-1/tau90_v1.npz'); print(list(z.keys()), [z[k].shape for k in z.keys()][:3])
"