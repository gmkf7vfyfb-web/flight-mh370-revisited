cd /Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints/bto-bfo/seed-1; python - <<'E'
import json,numpy as np
d=json.load(open('diagnostics.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if 'route' in k.lower() or 'sample' in k.lower(): print(p+k, str(v)[:300])
            walk(v,p+k+'.')
walk(d)
r=np.load('routes.npy'); print(r[0,:3], r[0,-3:], np.isnan(r).mean())
print(r[:,-1,0].min(), r[:,-1,0].max())
E
grep -rn "route_samples\|routes.npy" /Users/pete/Downloads/flight-mh370-revisited --include=*.md 2>/dev/null | head -5