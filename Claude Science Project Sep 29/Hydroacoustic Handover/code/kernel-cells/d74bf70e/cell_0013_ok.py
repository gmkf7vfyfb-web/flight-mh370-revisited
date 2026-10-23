for q in ["title contains 'extracted'", "title contains 'air8'", "title contains 'shot'", "'1uhPUyBSyhOmvgT7asQNhmZ3mqA1XGq5_' in parents", "'1S0KerTH3YIsTVukBVJOj1T_HHJtvQ3Dl' in parents"]:
    try:
        r = host.mcp(S, "search_files", query=q, excludeContentSnippets=True)
        files = r.get("files") or []
    except Exception as e:
        files=[]; print("ERR", q, str(e)[:200])
    print("##", q, len(files))
    for f in files[:12]:
        print("  ", f.get("title"), "|", f.get("mimeType","")[-20:], "|", f.get("fileSize"), "|", f.get("parentId"))
