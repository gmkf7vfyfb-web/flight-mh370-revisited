r = host.collect(['d2bd9c3e-51c3-45a1-ab65-1dbe7928c6a8'], timeout=60)[0]
json.dump(r, open('handoff/windows_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','results_notes','exchange_paths','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1100]}")