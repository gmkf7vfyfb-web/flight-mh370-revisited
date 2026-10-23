
import json
try:
    r = host.mcp("literature","openalex_search_works", query="MH370 descent end of flight", per_page=25)
    print(json.dumps(r)[:4000])
except Exception as e:
    print("ERR1", type(e).__name__, str(e)[:400])
