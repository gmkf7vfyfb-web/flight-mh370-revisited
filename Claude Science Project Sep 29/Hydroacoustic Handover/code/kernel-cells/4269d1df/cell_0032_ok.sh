cd "repo/Claude Science Project Sep 29/results/drift-runj-2026-10-17"; python3 -c "
import json
for f in ['analysis-runj-waypoints.json','aus160-both.json']:
    d=json.load(open(f)); print(f, type(d), list(d)[:30] if isinstance(d,dict) else len(d))
d=json.load(open('analysis-runj-waypoints.json'))
k=list(d)[0]; print(json.dumps(d[k],indent=0)[:2500])
"; head -c 1500 /Users/pete/Downloads/mh370-exchange/debris-drift/run-j/summary.json; cat /Users/pete/Downloads/mh370-exchange/debris-drift/run-j/run-j-waypoints/seed-1/COLUMNS.txt | head -30