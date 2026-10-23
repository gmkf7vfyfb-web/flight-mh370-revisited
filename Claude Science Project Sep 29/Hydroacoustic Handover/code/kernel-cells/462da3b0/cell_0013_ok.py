r = host.frames(frame_id="d74bf70e-a424-46a9-8149-902d027e782a", pattern=r"search_windows\.py --runs")
import json
s=json.dumps(r)[:6000]; print(s)