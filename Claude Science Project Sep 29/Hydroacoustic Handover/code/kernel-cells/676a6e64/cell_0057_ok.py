r = host.collect(['fd3a09d3-4e0f-4f0c-9e05-c56066b94f5f'], timeout=60)[0]
json.dump(r, open('handoff/tlgrid_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','exchange_paths','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1400]}")