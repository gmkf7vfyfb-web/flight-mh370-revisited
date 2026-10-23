d = host.frames(frame_id="d74bf70e", max_results=1, include_tool_results=False)
print({k:v for k,v in d.items() if k!="messages"})
print(len(d.get("messages",[])))
