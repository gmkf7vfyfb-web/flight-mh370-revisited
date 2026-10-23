
import json,re
r = host.frames(frame_id='d74bf70e', pattern=r"Metz", include_tool_results=True, max_results=500)
print(r.keys())
print(len(r['messages']), r.get('truncated'), r.get('total_messages'))
m=r['messages'][0]; print(type(m), (list(m.keys()) if isinstance(m,dict) else str(m)[:300]))
print(json.dumps(m)[:600])
