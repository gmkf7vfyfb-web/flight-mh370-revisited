
r=host.artifacts(search="scenario_markers")
for a in r['artifacts'][:5]: print(a['filename'],a['id'],a['latest_version_id'])
