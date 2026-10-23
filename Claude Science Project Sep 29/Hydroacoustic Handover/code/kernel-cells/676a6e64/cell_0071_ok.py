r = host.collect(['c1f32191-7101-489b-8677-1367fdb83543'], timeout=60)[0]
json.dump(r, open('handoff/composition_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1700]}")