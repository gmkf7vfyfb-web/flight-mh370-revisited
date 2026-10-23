
import json
srv = [s for s in host.mcp.servers()] if hasattr(host.mcp,'servers') else None
print(srv)
