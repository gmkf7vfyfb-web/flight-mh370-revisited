r = host.frames(max_results=60)
for f in r.get("frames", []):
    print(f.get("frame_id","")[:8], "|", f.get("status"), "|", (f.get("agent_name") or "")[:28], "|", (f.get("title") or f.get("task") or "")[:90].replace("\n"," "))
