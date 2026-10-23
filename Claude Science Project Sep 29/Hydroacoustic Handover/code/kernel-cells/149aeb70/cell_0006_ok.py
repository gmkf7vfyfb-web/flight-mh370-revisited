d = host.frames(frame_id="d74bf70e", max_results=1, offset=3390, include_tool_results=False)
m = d["messages"][0]
c = m.get("content")
if isinstance(c, list):
    c = "\n".join(str(x.get("text","")) for x in c if isinstance(x, dict))
print(c[2500:12000])
