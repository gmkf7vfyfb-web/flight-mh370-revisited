r = host.collect(['7adf9568-dd7f-4e62-823c-24873052d5fa'], timeout=60)[0]
json.dump(r, open('handoff/digitisation_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
for k in ('status','summary','commits','key_numbers','gaps','next','blocker'):
    print(f"## {k}: {str(so.get(k))[:1300]}")