c = S["cases"]; print(type(c), len(c))
c0 = c[0] if isinstance(c,list) else list(c.values())[0]
print(list(c0.keys()) if isinstance(c0,dict) else type(c0))
for k,v in c0.items():
    print(k, type(v).__name__, json.dumps(v)[:250])
