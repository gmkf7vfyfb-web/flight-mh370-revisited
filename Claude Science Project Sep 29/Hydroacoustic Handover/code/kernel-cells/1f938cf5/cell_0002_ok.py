q="SELECT id, body FROM memories WHERE id IN (%s)"%",".join("?"*len(ids))
r=host.query(q,ids)
for row in r['rows']: print(row[0],'::',row[1],'\n')
