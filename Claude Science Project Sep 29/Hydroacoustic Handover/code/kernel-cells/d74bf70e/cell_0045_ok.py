import json
S = json.load(open("repo/Claude Science Project Sep 29/results/no-exhaustion-prior-summary.json"))
print(list(S.keys()))
for k in ["grid","reference","shoulder_interval"]:
    v=S[k]; print(k, json.dumps(v)[:600])
m=S["map"]; print(type(m), (list(m.keys()) if isinstance(m,dict) else len(m)))
print(json.dumps(m)[:800] if not isinstance(m,dict) else {k:(json.dumps(v)[:300]) for k,v in m.items()})
