r = host.collect(['40a42702-247f-4783-9099-c4a7a8bdf78c'], timeout=60)[0]
json.dump(r, open('handoff/injection_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1600]}")