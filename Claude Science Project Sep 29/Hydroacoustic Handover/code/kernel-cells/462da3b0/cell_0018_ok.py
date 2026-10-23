os_out={}
for idx in (1576,1578,1580,1584,1586,1588):
    r = host.frames(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", offset=idx, max_results=1)
    m=r["messages"][0]
    for c in m["content"]:
        if c.get("type")=="tool_use":
            os_out[idx]=c["input"].get("code") or c["input"].get("command")
import os
os.makedirs("handoff",exist_ok=True)
json.dump(os_out, open("handoff/module_cells.json","w"), indent=1)
print({k:len(v) for k,v in os_out.items()})