r = host.frames(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", offset=1567, max_results=66)
for i,m in enumerate(r["messages"]):
    if m["role"]!="assistant": continue
    for c in m["content"]:
        if c.get("type")=="tool_use":
            inp=c["input"]; code=inp.get("code") or inp.get("command") or ""
            print(1567+i, c["name"], inp.get("human_description"), len(code))