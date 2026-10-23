cd .tmp/standin; python -c "
import json; d=json.load(open('smoke_tau/summary.json'))
r=d['next-c-free/seed-1']
for k,v in r.items(): print(k, {a:(round(b,4) if isinstance(b,float) else b) for a,b in v.items()} if isinstance(v,dict) else v)
"; lockf -t 0 /tmp/.mh370-heavy.lock true 2>&1 && echo FREE