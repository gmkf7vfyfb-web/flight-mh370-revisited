r=host.query("SELECT * FROM memories WHERE id IN ('mem_def8fcee88b2','mem_94514c70c95c')")
for x in r: print({k:v for k,v in x.items() if k in ('id','text','body','content')})