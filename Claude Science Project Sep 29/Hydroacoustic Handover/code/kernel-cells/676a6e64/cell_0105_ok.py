r = host.collect(['5e788282-a899-406d-be81-a794b69469f6'], timeout=60)[0]
json.dump(r, open('handoff/metz_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
print('summary:', str(so.get('summary'))[:2500])
for c in so.get('changed_numbers', []): print('*', c)
for f in so.get('figures', []): print('-', f.get('title'), f.get('version_id'))
print('reruns:', so.get('reruns_needed')); print('gaps:', so.get('gaps')); print('commits:', so.get('commits'))