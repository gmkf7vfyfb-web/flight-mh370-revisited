
print([n for n in dir(host.agents) if not n.startswith('_')])
for n in ('update','get','set','edit','create','append_instructions'):
    if hasattr(host.agents, n):
        try:
            help(getattr(host.agents,n))
        except Exception as e: print(n,'ERR',e)
a = host.agents.get('HYDROACOUSTIC_MODULE') if hasattr(host.agents,'get') else None
if a:
    print({k:(str(v)[:200]) for k,v in (a.items() if isinstance(a,dict) else [])})
