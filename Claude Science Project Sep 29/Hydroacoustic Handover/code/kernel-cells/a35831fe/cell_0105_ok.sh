cd /Users/pete/Downloads/mh370-exchange/composer/run-j-views-v3.2; python - <<'E'
import json,numpy as np
d=json.load(open('views-v3-run-j.json'))
m=d['meta']; print(list(m.keys())[:50])
for k in m:
    if any(s in k.lower() for s in ['grid','lat','lon','map','cell','extent']): print(k, str(m[k])[:500])
z=np.load('maps-v3.npz'); print(int(z['NY']),int(z['NX']))
print([k for k in z.files if k.startswith('D0|')][:40])
E
grep -n -i "grid\|maps-v3\|NY\|extent" results-note.md | head -20