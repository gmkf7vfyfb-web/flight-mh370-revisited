
r=host.frames(frame_id="d74bf70e", pattern=r"scenario_markers\.json", max_results=20)
import json
print(json.dumps(r)[:3000])
