d = host.frames(frame_id="d17b529c", max_results=1, include_tool_results=False)
print({k: v for k, v in d.items() if k != "messages"})
