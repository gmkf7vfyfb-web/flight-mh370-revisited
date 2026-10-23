
import json
try:
    r = host.mcp("literature","openalex_search_works", query="MH370 end-of-flight descent", per_page=30)
    ws = r.get("results") or r.get("works") or r
    for w in (ws if isinstance(ws,list) else [])[:30]:
        print(w.get("publication_year"), "|", (w.get("doi") or "")[:60], "|", (w.get("title") or "")[:90])
    if not isinstance(ws,list): print(json.dumps(r)[:2000])
except Exception as e:
    print("ERR", type(e).__name__, str(e)[:600])
