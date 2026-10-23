ids=['mem_e7a6c75a6d21','mem_8b868291ced6','mem_7fdb871a839b','mem_eafed062c92b','mem_63f62921d7f9','mem_958109778b04','mem_11c337fa84b6','mem_7090302f8585']
q="SELECT id, body FROM memories WHERE id IN (%s)"%",".join("'%s'"%i for i in ids)
for row in host.query(q)['rows']: print(row[0], '::', row[1], '\n')