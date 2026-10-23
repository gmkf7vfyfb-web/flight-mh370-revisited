
import json
qs = ["title contains 'Hydroacoustic'", "title contains 'hydroacoustic'", "title contains 'Kadri'", "title contains 'Airplane'",
      "fullText contains 'Remote hydroacoustic detection of an airplane crash'", "fullText contains 'Kadri'"]
seen={}
for q in qs:
    try:
        r = host.mcp("google-drive", "search_files", query=q)
    except Exception as e:
        print(q, "ERR", str(e)[:400]); continue
    files = r.get('files', r) if isinstance(r, dict) else r
    if isinstance(files, str):
        print(q, '->', files[:300]); continue
    for f in files:
        seen[f.get('id')] = (f.get('name'), f.get('mimeType'), f.get('size'), f.get('modifiedTime'))
    print(q, '->', len(files))
for k,v in seen.items(): print(k, v)
