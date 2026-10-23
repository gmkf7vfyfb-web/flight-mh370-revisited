r = host.collect(['77d06157-117b-4091-a991-cdcae35e10aa'], timeout=60)[0]
json.dump(r, open('handoff/updatedset_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
print('summary:', str(so.get('summary'))[:1600])
for f in so.get('figures', []): print('-', f.get('title'), f.get('version_id'), '|', str(f.get('what_it_shows'))[:200])
print('key:', str(so.get('key_numbers'))[:1200]); print('gaps:', so.get('gaps'))