print("ARTIFACTS:", [(a.get("filename"), a.get("version_id")) for a in (lit.get("artifacts_created") or [])])
fr = host.frames(frame_id="43360090-fdd3-4918-a664-de9fef7e80f6", max_results=500, include_tool_results=False)
msgs = fr["messages"]
texts=[]
for i,m in enumerate(msgs):
    c=m.get("content"); t = c if isinstance(c,str) else " ".join(x.get("text","") for x in (c or []) if isinstance(x,dict) and x.get("type")=="text")
    if m.get("role")=="assistant" and len(t)>1500: texts.append((i,t))
print(texts[-1][1][:9000])