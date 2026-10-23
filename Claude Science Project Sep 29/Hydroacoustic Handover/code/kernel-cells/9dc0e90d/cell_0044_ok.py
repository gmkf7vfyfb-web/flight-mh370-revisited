t = arc[arc.position=='track'][['arc_lat','target_lon']]; print(t.arc_lat.min(), t.arc_lat.max(), len(t))
print(type(a), (list(a.keys()) if isinstance(a,dict) else None))
print(str(a)[:600])