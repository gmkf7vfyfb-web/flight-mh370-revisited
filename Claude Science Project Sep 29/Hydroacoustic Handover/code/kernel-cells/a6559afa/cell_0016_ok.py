import re
def all_msgs(fid):
    msgs=[]; off=0
    while True:
        d=host.frames(frame_id=fid, include_tool_results=False, max_results=500, offset=off)
        msgs+=d['messages']; 
        if not d.get('truncated'): break
        off+=len(d['messages'])
    return msgs
store={}
for fid in ['676a6e64-2eac-490f-b67d-6c3f5c82f047','a35831fe-107a-4961-bc9f-e6fd6d255601','d74bf70e-a424-46a9-8149-902d027e782a']:
    store[fid]=all_msgs(fid)
    print(fid[:8], len(store[fid]))
m0=store['a35831fe-107a-4961-bc9f-e6fd6d255601'][0]
print(type(m0), list(m0.keys()) if isinstance(m0,dict) else '', str(m0)[:300])