
import json
try:
    k = host.credentials.request("openalex"); print("key ok", bool(k))
except Exception as e:
    print("nokey", type(e).__name__)
try:
    a = host.mcp("literature","arxiv_search", query="MH370", max_results=30)
    items = a.get("results") or a.get("papers") or a
    for w in (items if isinstance(items,list) else [])[:30]:
        print(w.get("published","")[:10], "|", w.get("id") or w.get("arxiv_id"), "|", (w.get("title") or "")[:95])
except Exception as e:
    print("ERR", type(e).__name__, str(e)[:400])
