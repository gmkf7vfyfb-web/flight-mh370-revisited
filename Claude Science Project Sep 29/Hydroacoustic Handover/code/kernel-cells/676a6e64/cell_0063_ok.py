r = host.collect(['1814d527-d9b6-410a-a48a-1b497eabc73d'], timeout=60)[0]
json.dump(r, open('handoff/kadri_pkg_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1200]}")