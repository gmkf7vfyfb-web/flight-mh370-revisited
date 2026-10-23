ag = host.agents.list()
hs = [a for a in (ag if isinstance(ag, list) else ag.get('agents', ag)) if 'HYDRO' in str(a.get('name', a)).upper()]
print(len(hs))
for a in hs:
    print({k: (v if k != 'system_prompt' else len(v)) for k, v in a.items() if k not in ('connectors',)})
    sp = a.get('system_prompt') or ''
    open('hydro_profile_prompt.md','w').write(sp)
    print(sp[:3000])
