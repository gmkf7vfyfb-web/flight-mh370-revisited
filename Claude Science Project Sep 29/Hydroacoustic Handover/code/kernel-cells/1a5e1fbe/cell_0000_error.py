ids=['mem_2fce8482ae57','mem_9ea5ee4e2518','mem_63f62921d7f9','mem_2a29d573585c','mem_6655276f6a45','mem_15b33243c74f','mem_ec430dd813fd','mem_dc36360d6cbd','mem_aa436b9ac0ea','mem_bc3a7380aa85','mem_afa55b5f572f','mem_b7d613398c2c']
q="SELECT * FROM memories WHERE id IN (%s)"%",".join("'%s'"%i for i in ids)
r=host.query(q)
for row in r:
    d=dict(row) if not isinstance(row,dict) else row
    print(d.get('id'), '|', d.get('text') or d.get('body') or d)
    print('---')