S="directory-386b459a-697f-4d1c-9f1e-712c3841fada"
import json
out={}
for q in ["title contains 'Blackman'", "title contains 'IMOS'", "title contains '3376'", "title contains 'hydroacoustic'"]:
    try:
        r = host.mcp(S, "search_files", query=q, excludeContentSnippets=True)
    except Exception as e:
        r = {"error": str(e)[:300]}
    out[q]=r
    files = r.get("files") if isinstance(r,dict) else None
    print("##", q, "->", (len(files) if files is not None else r)[:400] if not files else len(files))
    for f in (files or [])[:12]:
        print("  ", f.get("title"), "|", f.get("mimeType"), "|", f.get("fileSize"), "|", f.get("id"))
