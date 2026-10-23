d = host.frames(frame_id="d74bf70e", max_results=6, offset=3391, include_tool_results=False)
for m in d["messages"]:
    c = m.get("content")
    if isinstance(c, list):
        c = "\n".join(str(x.get("text", x))[:1500] for x in c if isinstance(x, dict))
    print("===", m.get("role"), "len", len(str(c)))
    print(str(c)[:1800])
