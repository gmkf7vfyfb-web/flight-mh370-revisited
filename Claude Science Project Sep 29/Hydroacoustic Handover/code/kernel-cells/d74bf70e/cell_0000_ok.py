import json
ags = host.agents.list()
for a in (ags.get("agents") if isinstance(ags, dict) else ags):
    if isinstance(a, dict):
        print(a.get("name"), "|", a.get("display_name") or a.get("title"), "|skills:", (len(a.get("skill_names")) if a.get("skill_names") is not None else "ALL"))
