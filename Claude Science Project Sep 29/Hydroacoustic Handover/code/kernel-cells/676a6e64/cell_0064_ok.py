r = host.collect(['e048f943-600e-483e-a210-041b29a751c8'], timeout=60)[0]
json.dump(r, open('handoff/levels_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1500]}")
print('artifacts', len(r.get('artifacts_created') or []))