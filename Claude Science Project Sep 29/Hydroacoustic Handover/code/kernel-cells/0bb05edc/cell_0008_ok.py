
r = host.mcp("google-drive", "search_files", query="title contains 'Hydroacoustic'")
print(json.dumps(r, indent=1)[:1500])
