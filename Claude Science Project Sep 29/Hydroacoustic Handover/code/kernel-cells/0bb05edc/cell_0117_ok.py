
r = host.artifacts(search='operating-note', limit=50)
for a in r['artifacts']: print(a['filename'], a['id'][:8], a['latest_version_id'][:8], a.get('size_bytes'))
r2 = host.artifacts(search='operating note', limit=50)
for a in r2['artifacts']:
    if 'operating' in a['filename'].lower(): print('2:', a['filename'], a['id'][:8], a['latest_version_id'][:8])
