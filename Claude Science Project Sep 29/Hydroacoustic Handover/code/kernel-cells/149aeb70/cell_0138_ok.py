d = host.frames(frame_id="d17b529c", max_results=3, offset=49, include_tool_results=False)
for m in d["messages"]:
    c = m.get("content")
    if isinstance(c, list):
        c = "\n".join(str(x.get("text", "")) for x in c if isinstance(x, dict))
    print("===", m.get("role"), len(str(c)))
    print(str(c)[:4000])
