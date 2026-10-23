r = host.collect(['72504aac-d56b-47c5-a343-54440d729002'], timeout=60)[0]
json.dump(r, open('handoff/pairmaps_result.json','w'), indent=1, default=str)
so = r.get('structured_output') or {}
print(r.get('status'), '| deviations:', r.get('deviations'))
print('summary:', str(so.get('summary'))[:1500])
for f in so.get('figures', []): print('-', f.get('title'), f.get('version_id'), '|', str(f.get('what_it_shows'))[:200])
print('key:', str(so.get('key_numbers'))[:1200]); print('gaps:', so.get('gaps'))