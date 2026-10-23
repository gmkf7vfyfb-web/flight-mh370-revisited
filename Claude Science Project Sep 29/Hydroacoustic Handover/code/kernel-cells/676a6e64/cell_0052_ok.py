r = host.collect(['02f53ca7-66d6-4371-9a5a-275163236205'], timeout=60)[0]
json.dump(r, open('handoff/tlrecal_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1300]}")