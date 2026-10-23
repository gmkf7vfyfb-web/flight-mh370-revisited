D=/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo/seed-1
python - <<E
import numpy as np, json
for f in ['routes','trace','final','early','route_plans','tanks32']:
    a=np.load('$D/'+f+'.npy',mmap_mode='r'); print(f,a.shape,a.dtype, a.dtype.names)
r=np.load('$D/routes.npy'); print(r[0][:12] if r.ndim>1 else r[:2])
t=np.load('$D/trace.npy'); print(t[:2] if t.dtype.names else t[0][:20])
E
cat $D/route_plan_fixes.txt; python -c "import json;d=json.load(open('$D/diagnostics.json'));print(list(d.keys())[:40])"
python -c "import json;d=json.load(open('/Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/run.json'));print(json.dumps(d)[:2500])"