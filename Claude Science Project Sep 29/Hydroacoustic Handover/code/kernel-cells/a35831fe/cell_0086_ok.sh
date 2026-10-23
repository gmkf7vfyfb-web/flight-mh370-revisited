cd /Users/pete/Downloads/mh370-exchange/core/run-j/run-j-waypoints; python - <<'E'
import json
d=json.load(open('run.json')); 
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if any(s in k.lower() for s in ['column','trace','route','final','layout','fields','schema']): print(p+k, str(v)[:400])
            walk(v,p+k+'.')
walk(d)
E
head -5 bto-bfo/seed-1/route_plan_fixes.txt; cat ../../../end-of-flight/run-j/run-j-waypoints/seed-1/COLUMNS.txt | head -60