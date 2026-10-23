q="SELECT id, created_at, body FROM memories WHERE id IN (%s)"%(",".join("?"*len(ids)))
r=host.query(q, ids, scope="global")
for row in r['rows']: print(row[0], row[2], "\n")
