r = host.collect(['ab0373ea-3460-46fd-87d0-112603723552'], timeout=60)[0]
json.dump(r, open('handoff/ram_imos_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1500]}")