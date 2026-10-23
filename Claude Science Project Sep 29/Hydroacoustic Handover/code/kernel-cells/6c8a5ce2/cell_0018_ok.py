r=host.artifacts(filename="acoustics-toolbox", limit=10)
for a in r['artifacts']: print(a['filename'], a['latest_version_id'], a['size_bytes'])
r=host.artifacts(filename="tau90", limit=10)
for a in r['artifacts']: print(a['filename'], a['latest_version_id'], a['size_bytes'])
