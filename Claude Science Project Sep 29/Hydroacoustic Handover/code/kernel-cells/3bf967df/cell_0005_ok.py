ids=['mem_4bdce496f7a6','mem_2f93e44158f7','mem_2a942e3769d1','mem_fce7744cc1b8','mem_b52c68761a47','mem_63f62921d7f9','mem_03c5e0223ece','mem_8789591e1a19','mem_bca1d4ab7616','mem_1bc8d0e64388','mem_734597aeb50c','mem_db98f08508fb','mem_5e559775a7d5','mem_107c4ef987b2','mem_0da601680eeb','mem_5d370d325009','mem_bdbdba5fbc87']
r=host.query("SELECT id, body, created_at FROM memories WHERE id IN (%s)"%",".join("'%s'"%i for i in ids))
txt="\n\n".join(f"{a} :: {b}" for a,b,c in r['rows'])
open('mem_dump.txt','w').write(txt); print(len(txt))