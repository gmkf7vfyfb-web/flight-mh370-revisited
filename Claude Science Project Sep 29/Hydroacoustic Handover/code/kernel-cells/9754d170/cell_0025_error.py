
r=host.artifacts(filename="scenario_markers",include_intermediate=True)
for a in r['artifacts'][:5]: print(a['filename'],a['id'],a['latest_version_id'])
if r['artifacts']:
    lin=host.lineage[r['artifacts'][0]['latest_version_id']]
    open('audit/lineage/markers.py','w').write(lin['code'] or ''); print(len(lin['code'] or ''), [i['filename'] for i in lin['inputs']])
