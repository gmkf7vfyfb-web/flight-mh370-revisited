X=/Users/pete/Downloads/mh370-exchange; D=$X/core/run-j/run-j-waypoints/bto-bfo/seed-1/handoff-m0011
python - <<E
import numpy as np,gzip
h=np.load('$D/handoff.npy',mmap_mode='r'); print(h.shape,h.dtype, h.dtype.names); print(np.asarray(h[:2]))
with gzip.open('$D/handoff.toml.gz','rt') as f:
    for i,l in enumerate(f):
        if i<60: print(l.rstrip()[:200])
        else: break
p=np.load('$X/end-of-flight/run-j/run-j-waypoints/seed-1/parents32.npy'); print(p.shape, p[:,0].min(), p[:,0].max(), np.unique(p[:,2:],axis=0)[:5])
E
ls $X/end-of-flight/run-j/summary | head; cat $X/end-of-flight/run-j/run-j-waypoints/README.md | head -60