ids=['mem_68e3e0f76b2d','mem_fb3e17d86ad7','mem_a46ec557e204','mem_13b941878e9b','mem_958109778b04','mem_b9838afcd7f8','mem_12b6deb56dc1','mem_b14551be66d1','mem_b1e164695d2f','mem_ec430dd813fd','mem_9584a0e155ec']
r=host.query("SELECT id, body FROM memories WHERE id IN (%s)"%",".join("'%s'"%i for i in ids))
open('handoff_mem.txt','w').write("\n\n".join(f"{a} :: {b}" for a,b in r['rows']))
for a,b in r['rows']: print(a,'::',b,'\n')