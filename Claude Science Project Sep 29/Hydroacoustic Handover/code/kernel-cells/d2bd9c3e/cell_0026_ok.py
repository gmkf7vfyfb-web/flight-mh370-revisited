r = host.frames(pattern="publication coverage", max_results=5)
for f in r.get("frames", r.get("results", []))[:5]:
    print({k: (str(v)[:300]) for k, v in f.items() if k in ("frame_id","title","snippet","snippets","created_at")})
print(r.keys() if isinstance(r, dict) else type(r))