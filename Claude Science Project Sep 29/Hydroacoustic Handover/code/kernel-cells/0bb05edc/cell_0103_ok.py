
print(host)
try:
    ag = host.agents.list()
    for a in (ag if isinstance(ag,list) else ag.get('agents',ag)):
        if isinstance(a,dict): print(a.get('name'), '|', (a.get('description') or '')[:70], '|', a.get('skill_names') if 'skill_names' in a else '')
        else: print(a)
except Exception as e:
    print('agents.list ERR', str(e)[:200])
