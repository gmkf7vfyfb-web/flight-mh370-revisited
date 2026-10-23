import json
r = host.collect(['cc6b3f2b-242b-40fa-b647-2bd32190a5f8'], timeout=60)[0]
json.dump(r, open('handoff/weak_signals_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('block','status','summary','commits','results_notes','key_numbers','gaps','next','blocker'):
    v = so.get(k); print(f"## {k}: {str(v)[:900]}")
print('artifacts:', len(r.get('artifacts_created') or []))