import json
r = host.frames(max_results=60)
print(json.dumps(r.get("frames", [])[:3], indent=1)[:2000])
