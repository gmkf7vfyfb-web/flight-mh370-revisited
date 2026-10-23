ids=['mem_68e3e0f76b2d','mem_fb3e17d86ad7','mem_a46ec557e204','mem_13b941878e9b','mem_958109778b04','mem_b9838afcd7f8','mem_12b6deb56dc1','mem_b14551be66d1','mem_b1e164695d2f','mem_6b9dc509ab29']
r=host.query("SELECT id, text FROM memories WHERE id IN (%s)"%",".join("'%s'"%i for i in ids))
for row in (r if isinstance(r,list) else r.get('rows',r)):
    print(row.get('id') if isinstance(row,dict) else row[0], '::', (row.get('text') if isinstance(row,dict) else row[1]), '\n')