d = host.frames(frame_id="d74bf70e", max_results=12, offset=3386, include_tool_results=False)
for m in d["messages"]:
    c = m.get("content")
    if isinstance(c, list):
        c = " ".join(str(x.get("text", x)) for x in c if isinstance(x, dict))
    print("=== ", m.get("role"), str(m.get("created_at"))[:19], "len", len(str(c)))
    print(str(c)[:3000])
