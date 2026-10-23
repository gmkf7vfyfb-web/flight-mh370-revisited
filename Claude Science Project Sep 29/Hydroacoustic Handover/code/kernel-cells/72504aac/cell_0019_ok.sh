X=/Users/pete/Downloads/mh370-exchange
python -c "
import json;d=json.load(open('$X/core/run-j/run-j-waypoints/run.json'));
def f(o,p=''):
  if isinstance(o,dict):
    for k,v in o.items():
      if k in('output','trace','prior') or 'route' in k or 'unix' in k: print(p+k, json.dumps(v)[:800])
      else: f(v,p+k+'.')
f(d)"
ls -la $X/core/run-j/run-j-waypoints/bto-bfo/seed-1/handoff-m0011 $X/core/run-j/run-j-waypoints/bto-bfo/seed-1/handoff-m2241
cat $X/end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt; python -c "
import numpy as np; p=np.load('$X/end-of-flight/run-j/run-j-waypoints/seed-1/parents32.npy',mmap_mode='r'); print(p.shape,p.dtype,p[:5]); i=np.load('$X/end-of-flight/run-j/run-j-waypoints/seed-1/impacts32.npy',mmap_mode='r'); print(i.shape)"
cat $X/end-of-flight/run-j/run-j-waypoints/seed-1/run.json | head -c 1500