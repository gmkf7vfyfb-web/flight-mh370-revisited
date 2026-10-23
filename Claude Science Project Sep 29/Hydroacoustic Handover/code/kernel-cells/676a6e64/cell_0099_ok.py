r = host.collect(['31b10b13-11b6-43d0-8f68-8bdb177bde4c'], timeout=60)[0]
json.dump(r, open('handoff/ranking_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
print('summary:', str(so.get('summary'))[:1800])
for f in so.get('figures', []): print('-', f.get('title'), f.get('version_id'), '|', str(f.get('what_it_shows'))[:220])
for t in so.get('tables', []): print('T', t)
print('key:', str(so.get('key_numbers'))[:2200]); print('gaps:', so.get('gaps'))