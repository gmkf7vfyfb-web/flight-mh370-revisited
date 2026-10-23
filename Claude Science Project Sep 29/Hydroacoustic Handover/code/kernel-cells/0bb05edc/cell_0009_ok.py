
qs = ["title contains 'Metz'", "title contains 'Remote Hydroacoustic'", "title contains 'Airplane Crash'", "title contains 'airplane'",
      "fullText contains 'Metz'", "fullText contains 'Remote hydroacoustic detection'", "fullText contains 'F-35A'", "title contains 'Pure and Applied'", "title contains 'pageoph'"]
seen={}
for q in qs:
    try:
        r = host.mcp("google-drive", "search_files", query=q)
    except Exception as e:
        print(q, "ERR", str(e)[:300]); continue
    files = r.get('files', [])
    print(q, '->', len(files))
    for f in files:
        seen[f['id']] = (f.get('title'), f.get('mimeType'), f.get('fileSize'), f.get('modifiedTime'), f.get('parentId'))
for k,v in seen.items(): print(k, v)
