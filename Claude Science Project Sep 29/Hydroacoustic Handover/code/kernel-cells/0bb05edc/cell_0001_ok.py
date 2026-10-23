
r = host.artifacts(search="hydroacoustic")
print(type(r), len(r) if hasattr(r,'__len__') else '')
print(repr(r)[:800])
