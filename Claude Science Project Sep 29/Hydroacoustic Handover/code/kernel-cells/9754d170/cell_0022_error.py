
r=host.artifacts(filename="scenario_markers.json")
for a in r['artifacts']: print(a['filename'],a['id'],a['latest_version_id'])
lin=host.lineage[r['artifacts'][0]['latest_version_id']]
open('audit/lineage/markers.py','w').write(lin['code'] or ''); print(len(lin['code'] or ''), [i['filename'] for i in lin['inputs']])
