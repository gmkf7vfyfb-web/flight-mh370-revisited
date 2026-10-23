print(host.query("SELECT sql FROM sqlite_master WHERE name='memories'")["rows"][0][0][:600])
ids=['mem_b1e164695d2f','mem_6fd080d653b2','mem_44c1625bddcd','mem_68e3e0f76b2d','mem_3b89bb1f2de8','mem_b93d3ebe3e3a']
q=host.query("SELECT id, content FROM memories WHERE id IN (%s)" % ",".join("?"*len(ids)), ids)
for r in q["rows"]:
    print("=====", r[0]); print(r[1]); print()
