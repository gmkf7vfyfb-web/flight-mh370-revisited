import numpy as np, json
z=np.load("/Users/pete/Downloads/mh370-exchange/end-of-flight/run-i-dive/run-i-dive-subsample.npz", allow_pickle=True)
print(list(z.keys()))
for k in z.keys():
    a=z[k]
    print(k, a.shape, a.dtype, (a.ravel()[:3] if a.dtype.kind in 'fiu' else str(a)[:200]))
