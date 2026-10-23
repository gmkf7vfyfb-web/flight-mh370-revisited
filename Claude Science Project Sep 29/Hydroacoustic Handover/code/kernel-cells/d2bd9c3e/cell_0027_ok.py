for m in r["matches"][:6]:
    print({k: str(v)[:400] for k, v in m.items()})
print(r["total_matches"])
r2 = host.frames(pattern="versus end of flight", max_results=5)
for m in r2["matches"][:6]:
    print({k: str(v)[:400] for k, v in m.items()})