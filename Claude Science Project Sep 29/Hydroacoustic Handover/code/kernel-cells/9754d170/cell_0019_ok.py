
r=host.artifacts(filename="hydroacoustics-noise-vs-impact")
for a in r['artifacts']: print(a['filename'],a['latest_version_id'],a.get('created_at'))
r2=host.artifacts(filename="hydroacoustics-air9-predicted-vs-measured")
for a in r2['artifacts']: print(a['filename'],a['latest_version_id'])
