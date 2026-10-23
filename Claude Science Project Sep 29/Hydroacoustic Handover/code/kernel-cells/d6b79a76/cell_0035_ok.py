res=host.artifacts(search="runj_north_handoff_worker", limit=5)
for a in res['artifacts']: print(a['id'], a['filename'], a['latest_version_id'], a.get('size_bytes'))
res=host.artifacts(search="north of 30S residuals sigma", limit=5)
for a in res['artifacts']: print(a['id'], a['filename'], a['latest_version_id'], a.get('size_bytes'))