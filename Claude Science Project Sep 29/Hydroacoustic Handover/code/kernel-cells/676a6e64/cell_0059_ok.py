r = host.collect(['e6299cde-29fc-43b0-abb6-280a8892ebb3'], timeout=60)[0]
json.dump(r, open('handoff/searches_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1600]}")