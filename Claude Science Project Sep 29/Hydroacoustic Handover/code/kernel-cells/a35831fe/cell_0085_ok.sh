cd /Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo/seed-1; ls -la; python - <<'E'
import numpy as np,glob,os
for f in glob.glob('*.npz')+glob.glob('*.npy'):
    try:
        d=np.load(f,mmap_mode='r',allow_pickle=False)
        if hasattr(d,'files'): print(f,{k:(d[k].shape,d[k].dtype) for k in d.files})
        else: print(f,d.shape,d.dtype)
    except Exception as e: print(f,e)
E
ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/ | head; ls /Users/pete/Downloads/mh370-exchange/end-of-flight/run-j/run-j-waypoints/seed-1 | head -30