a = host.agents.list()
for x in (a["agents"] if isinstance(a, dict) and "agents" in a else a):
    print(x if isinstance(x, str) else {k: x.get(k) for k in ("name", "display_name", "description") if k in x})
