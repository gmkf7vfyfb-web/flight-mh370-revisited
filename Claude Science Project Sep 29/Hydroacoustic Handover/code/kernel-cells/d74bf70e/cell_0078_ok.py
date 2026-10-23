fr = host.frames(frame_id="95790ff1-95f1-4b29-b51a-bed538c1797b", max_results=500, include_tool_results=False)
msgs = fr["messages"]; print(len(msgs), fr.get("truncated"))
texts = []
for i,m in enumerate(msgs):
    c = m.get("content")
    t = c if isinstance(c,str) else " ".join(x.get("text","") for x in (c or []) if isinstance(x,dict) and x.get("type")=="text")
    if m.get("role")=="assistant" and len(t)>1500: texts.append((i,t))
i,t = texts[-1] if texts else (None,"")
print(i); print(t[:9000])