a=host.agents.list()
for p in (a if isinstance(a,list) else a.get('agents',a)):
    print(p if isinstance(p,str) else {k:(str(v)[:160]) for k,v in p.items() if k in('name','description','skills')})