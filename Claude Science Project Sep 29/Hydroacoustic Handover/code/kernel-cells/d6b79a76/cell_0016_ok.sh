cd scorer; sed -n 1,143p compact_impacts.py | head -143; X=~/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1; wc -l $X/COLUMNS.txt; sed -n 60,200p $X/COLUMNS.txt | tr '\n' ' '; echo; python3 -c "
import numpy as np
for f in ['tau90_v1.npz','attitude_v1.npz']:
  z=np.load('$X/'+f); print(f,{k:(z[k].shape,z[k].dtype) for k in z.files})
a=np.load('$X/impacts32.npy',mmap_mode='r'); print(a.shape); p=np.load('$X/parents32.npy',mmap_mode='r'); print(p.shape,p.dtype)"; head -c 600 $X/terminal.json; echo; du -sh $X