cd "repo/Claude Science Project Sep 29/results/drift-runj-2026-10-17"; python3 -c "
import json
d=json.load(open('analysis-runj-waypoints.json'))
c=d['cells']; print(list(c)[:10]); k=list(c)[0]; print(k, json.dumps(c[k])[:3000])
a=json.load(open('aus160-both.json')); print(list(a['models'])[:5] if isinstance(a['models'],dict) else a['models']); ck=list(a['cells']); print(ck[:8]); print(json.dumps(a['cells'][ck[0]])[:2500])
"