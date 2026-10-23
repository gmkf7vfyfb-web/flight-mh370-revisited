
import json
p=host.artifact_path("b051343e-45cc-419c-ad4d-0a8c5fc57af3"); j=json.load(open(p))
print(type(j), (list(j.keys()) if isinstance(j,dict) else len(j)))
print(json.dumps(j,indent=0)[:1500])
