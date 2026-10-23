python -c "
import numpy as np; z=np.load('/Users/pete/Downloads/mh370-exchange/pleiades/hydro-test/next-run-b/sources.npz', allow_pickle=False)
for k in z.files: a=z[k]; print(k, a.dtype, a.shape, (a.dtype.names[:20] if a.dtype.names else ''))
"