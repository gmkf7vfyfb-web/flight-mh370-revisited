a = [x for x in host.agents.list() if x["name"]=="HYDROACOUSTIC_MODULE"][0]
print(a.get("displayName"), "| unrestricted:", a.get("unrestricted"), "| connectors:", len(a.get("connectors") or []))
print("---SYSTEM PROMPT---")
print(a.get("systemPrompt"))
