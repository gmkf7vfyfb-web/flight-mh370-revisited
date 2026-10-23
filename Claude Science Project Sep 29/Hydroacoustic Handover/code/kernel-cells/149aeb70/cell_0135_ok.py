r = host.frames(pattern="[Cc]ontext [Mm]anagement", max_results=10)
print("pattern hits:", r.get("count"))
for f in (r.get("frames") or [])[:6]:
    print(" ", f.get("id","")[:8], f.get("name"), "|", str(f.get("snippet",""))[:200].replace("\n"," "))
print("--- all frames")
for f in host.frames(max_results=60)["frames"]:
    print(" ", f["id"][:8], f["status"][:10], (f["agent_name"] or "")[:22], "|", f["name"][:60])
