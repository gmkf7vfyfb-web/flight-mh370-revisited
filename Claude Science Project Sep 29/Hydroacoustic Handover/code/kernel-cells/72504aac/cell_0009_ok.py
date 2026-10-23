r = host.frames(pattern=r"D preferred|C · Impact|loci A", project_id=None, max_results=10)
import json
print(json.dumps(r, default=str)[:3000])