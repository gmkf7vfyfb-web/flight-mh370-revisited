ids=['mem_b1e164695d2f','mem_6fd080d653b2','mem_44c1625bddcd','mem_68e3e0f76b2d','mem_3b89bb1f2de8','mem_b93d3ebe3e3a','mem_e67695c1cb11','mem_2a8959fe1d83']
q=host.query("SELECT id, text FROM memories WHERE id IN (%s)" % ",".join("?"*len(ids)), ids)
for r in q["rows"]:
    print("=====", r[0]); print(r[1]); print()
