r=host.mcp(S,"download_file_content",fileId="1zwSCCwXcsryJdi4kHb4WE13_9-WIb4J4")
print(type(r), (list(r.keys()) if isinstance(r,dict) else None))
b = r.get("content") if isinstance(r,dict) else r
print(type(b), len(b) if b else None, (b[:80] if isinstance(b,str) else None), (b[-80:] if isinstance(b,str) else None))