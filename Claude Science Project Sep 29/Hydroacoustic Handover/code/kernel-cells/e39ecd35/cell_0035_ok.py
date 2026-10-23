
import json
try:
    r = host.mcp("literature","search_works", query="MH370 end of flight descent impact", per_page=25)
    print(json.dumps(r)[:3000])
except Exception as e:
    print("ERR", type(e).__name__, str(e)[:500])
