q="SELECT id, body FROM memories WHERE id IN (%s)"%",".join("'%s'"%i for i in ids)
for row in host.query(q)['rows']: print(row[0], '::', row[1], '\n')
r=host.query("SELECT id, body FROM memories WHERE superseded_by IS NULL AND (body LIKE '%WSPR%' OR body LIKE '%received power%' OR body LIKE '%received-power%') AND id NOT IN (%s) ORDER BY created_at DESC LIMIT 12"%",".join("'%s'"%i for i in ids))
for row in r['rows']: print(row[0], '::', row[1][:600], '\n')