import sys, numpy as np; sys.path.insert(0, 'scorer')
from compact_impacts import load
import os; sys.path.append(os.getcwd()); import drift_columns_inmem as DC
d = '/Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1'
_, g = load(d); A, s = DC.columns(g('latitude_deg'), g('longitude_deg'), g('parent'))
B = np.load('/Users/pete/Downloads/mh370-exchange/debris-drift/run-j/run-j-waypoints/seed-1/drift-lnL.npy', mmap_mode='r')
bad = 0
for f in A.dtype.names:
    x, y = A[f], np.asarray(B[f])
    eq = np.array_equal(x, y, equal_nan=True) if x.dtype.kind == 'f' else np.array_equal(x, y); bad += not eq
print('rows', len(A), len(B), 'fields', len(A.dtype.names), 'mismatched fields', bad)
