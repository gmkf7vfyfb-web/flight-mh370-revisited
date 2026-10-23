ids=['mem_c72873c0d325','mem_c6aa1daecff1','mem_b686dc9f9382','mem_8c04fab658d9','mem_315437562ce6']
r=host.query("SELECT id, body FROM memories WHERE id IN (%s)"%(",".join("?"*len(ids))), ids, scope="global")
for row in r['rows']: print(row[0], row[1], "\n")