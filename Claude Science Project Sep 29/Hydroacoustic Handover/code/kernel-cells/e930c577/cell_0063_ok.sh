python -c "
import sys; sys.path.insert(0,'leg'); import levels as L, numpy as np; C=L.pd_curves()
for k,(x,y) in C.items(): print(k, list(zip(x.round(1),y.round(3))))"; cat leg/scan.log