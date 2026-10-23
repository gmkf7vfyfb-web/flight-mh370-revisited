h = host.frames(pattern="hydro", max_results=30)
print(h.get("count"))
for f in h.get("frames", [])[:30]:
    print(f.get("frame_id","")[:8], "|", f.get("status"), "|", (f.get("agent_name") or "")[:30], "|", str(f.get("snippet",""))[:160].replace("\n"," "))
